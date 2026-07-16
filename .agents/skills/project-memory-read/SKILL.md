---
name: project-memory-read
description: Read-only, evidence-backed consultation of tracked Project Memory sources and current generated publications.
---

# Project Memory Read

Use this skill only for bounded, read-only Project Memory questions. Follow
`docs/project-memory/ask-protocol.md` for the request and response contract.

## Source consultation order

1. Verify the requested repository root, current branch, full HEAD, staged and
   worktree state, worktree identity, and active task/frontier with read-only Git
   inspection. Require a clean worktree, empty staging, `FRESH` Project Memory,
   and zero Plan Integrity blockers for the exact commit.
2. Read `AGENTS.md`, `docs/roadmap/roadmap_index.yaml`, and the relevant section
   of `docs/roadmap/implementation_status.md`.
3. Read the scoped task record under `docs/roadmap/tasks/` and accepted decision
   records under `docs/roadmap/decisions/`.
4. Inspect relevant live code, schemas, tests, accepted validation, and exact Git
   history only as the question requires.
5. Use `docs/project-memory/registries/manifest.json` to locate normalized
   records. Read the complete matching records in the relevant registries.
6. Use a current validated publication under `.codex-context/project-memory/`
   only as a navigation and cross-reference aid.
7. Use historical or other generated evidence only when requested and label it
   non-authoritative.

The authority hierarchy and lifecycle vocabulary are defined by
`docs/roadmap/decisions/PHASE8-IMPL-026-T001-project-memory-authority-lifecycle-provenance-foundation.md`.
Do not copy the roadmap or schema into this skill.

## Bounded procedure

- Start with paths and symbols named by the request. Use repository read/search
  tools only within `maximum_scope`; do not broadly scan the repository.
- Verify task status and the application frontier against accepted roadmap and
  decision records before consulting registries or rendered summaries.
- Verify dependency eligibility and resolve execution-related questions through
  `docs/project-memory/registries/execution-routing.json`. Fail closed rather
  than selecting an executor from historical routing, a generated source, or
  model judgment.
- For any frontend/UI/UX question, use
  `.agents/skills/writing-assistant-ui-execution/SKILL.md` in audit mode and
  apply the installed Impeccable guidance within the request scope.
- Read registry records by stable `id`/`task_id`/`decision_id`; check lifecycle,
  authority class, provenance locators, dependencies, and owner-decision refs.
- Treat a registry conflict with a higher-tier source as stale or invalid.
- For a rendered publication, inspect `build-manifest.json`, the bound snapshot,
  `SHA256SUMS`, publication eligibility, freshness, convergence, authority, and
  semantic-validation result before using its pages.
- Cite tracked sources as repository-relative `path:line_start-line_end` or a
  stable registry record ID. Cite generated evidence with package path, run ID,
  authority `generated_evidence`, freshness, and full bound commit.
- Separate facts from inference. State uncertainty, conflict, missing evidence,
  and every `owner_pending` decision explicitly.

Always distinguish implemented from planned; automated-test PASS from accepted
live validation; runtime assets from fixtures/training data; authoritative
records from generated evidence; and current records from historical or
superseded information.

## Stop conditions

Return `BLOCKED` when the repository/task gate fails or a protected path/tool is
required. Return `INSUFFICIENT_EVIDENCE`, `CONFLICT`, or `OUT_OF_SCOPE` as
defined by the Ask protocol when evidence is stale, missing, contradictory,
untrusted, quarantined, owner-pending, or outside scope. Never fill gaps with
model knowledge or promote an inference into project truth.

## Prohibited actions

This skill grants no write, edit, install, network, model, server, external
worktree, or retrieval-system authority. Never activate, close, reorder,
rewrite, or amend roadmap tasks; change normalized registries; mutate
Memory/Canon; promote candidates; apply promotion; create training data; or
write, rewrite, continue, imitate, polish, improve, expand, or extend story
prose. Model output and generated evidence are never truth.
