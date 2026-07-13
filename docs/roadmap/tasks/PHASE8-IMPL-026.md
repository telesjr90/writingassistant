# PHASE8-IMPL-026 — Project Memory and Plan Integrity

## Status

Published/active as a parallel governance, documentation, and developer
infrastructure workstream. Not an application feature.

The application implementation frontier remains PHASE8-IMPL-024-T003A.
PHASE8-IMPL-025 remains published/planned and inactive.

T001 — Project Memory authority, lifecycle, and provenance foundation —
is complete/PASS.

Next Project Memory task: PHASE8-IMPL-026-T002 — Schema and normalized-registry
architecture.

## Classification

Hybrid governance, documentation, and developer infrastructure. This workstream
defines controlling policies, normalized registries, deterministic scanners,
human-readable Project Memory, context-tool integration, retrieval pilots,
shared agent guidance, a Plan Integrity engine, specialized reviewers, and
operational synchronization and CI.

None of the workstream replaces the application roadmap, and none implements
application features.

## Controlling Decision

`docs/roadmap/decisions/PHASE8-IMPL-026-T001-project-memory-authority-lifecycle-provenance-foundation.md`

## Goal

Provide a normalized, machine-readable, commit-bound system that:

1. Records the accepted plan.
2. Compares the plan with the actual implementation.
3. Explains discrepancies with evidence.
4. Surfaces confidence, uncertainty, and provenance for owner review.
5. Maintains freshness bound to repository commits.
6. Refuses to silently override the authoritative roadmap or live code.

## Repository locations

- Decisions: `docs/roadmap/decisions/` (current)
- Future tracked documentation and registries: `docs/project-memory/`
- Future implementation code: `scripts/project_memory/`
- Future tests: `tests/project_memory/`
- Future shared skills: `.agents/skills/`
- Future OpenCode agents: `.opencode/agents/`
- Generated evidence and indexes: `.codex-context/project-memory/`

Generated documentation sites and indexes are ignored build output and are not
authority. None of these future directories are created by T001.

## Child workstream hierarchy

Indexed workstreams are planned. Lettered slices are not yet defined. Tool
installation work is contingent on later provenance tasks and benchmark
decisions. Serena, LlamaIndex, and Qdrant are not approved dependencies.

### PHASE8-IMPL-026-T001 — Authority, lifecycle, provenance, and roadmap foundation

Status: complete/PASS.

Published the controlling decision defining the authority hierarchy, trust
classes, freshness model, commit binding, supersession, conflicting-evidence
resolution, owner-decision representation, generated-evidence requirements,
memory-update approval, roadmap synchronization, stale-index behavior, tool
provenance, prompt-injection boundaries, branch synchronization policy, and
product boundaries.

### PHASE8-IMPL-026-T002 — Schema and normalized-registry architecture

Status: planned. Depends on T001.

Define machine-readable schemas for Project Memory records, registry storage
format, normal form, ID governance, and cross-record linking before any
scanner, renderer, or retrieval tool exists.

### PHASE8-IMPL-026-T003 — Deterministic scanners and convergence

Status: planned. Depends on T002.

Implement read-only deterministic scanners that inspect the repository state
(code, tests, roadmap decisions, task records, enrichment data) and produce
normalized evidence records. Define convergence criteria that detect when
plan and implementation agree, disagree, or have insufficient evidence.

### PHASE8-IMPL-026-T004 — Human-readable Project Memory

Status: planned. Depends on T003.

Render normalized registries and scanner output into human-readable
documentation that explains what is implemented, what is planned, what is
missing, what conflicts exist, and what requires owner attention. Generated
sites are build output and are not authority.

### PHASE8-IMPL-026-T005 — Existing context-tool integration

Status: planned. Depends on T003.

Integrate existing context tools (Repomix, Graphify, CCE) as evidence
producers under the Project Memory provenance and freshness model without
requiring new tool installation. Existing generated packs under
`.codex-context/` and `ai_context/` are consumed as `generated_evidence`.

### PHASE8-IMPL-026-T006 — Serena read-only pilot

Status: planned. Depends on T005. Contingent on Serena provenance and
benchmark approval.

Evaluate Serena as a read-only retrieval surface over Project Memory
registries. Produce a bounded pilot with provenance, freshness, and stale-index
reporting before any persistent integration.

### PHASE8-IMPL-026-T007 — LlamaIndex / local-embedding / Qdrant Local pilot

Status: planned. Depends on T005. Contingent on provenance and benchmark
approval for each dependency.

Evaluate local embedding and vector retrieval over Project Memory registries
with provenance, freshness, stale-index, and trust-class filtering before any
persistent integration.

### PHASE8-IMPL-026-T008 — Shared agent guidance and Project Memory Ask

Status: planned. Depends on T004.

Define shared agent guidance that explains how to query Project Memory, what
trust classes mean, when to escalate to owner review, and how to interpret
freshness, supersession, conflict, and uncertainty signals. Define the
Project Memory Ask protocol for agents to request and receive authoritative
answers with provenance.

### PHASE8-IMPL-026-T009 — Deterministic Plan Integrity engine

Status: planned. Depends on T003.

Implement a deterministic engine that compares the accepted plan (task
records, enrichment data, decision log, implementation status) with the
actual implementation (code, tests, schemas) and produces a Plan Integrity
report with evidence, confidence, and unresolved discrepancies.

### PHASE8-IMPL-026-T010 — Specialized Plan Integrity reviewers

Status: planned. Depends on T009.

Implement specialized reviewer agents that inspect specific domains (backend
contracts, frontend UI, test coverage, roadmap consistency, enrichment
accuracy, decision coherence) and produce evidence-backed review findings.
Reviewers may propose findings but may not change authoritative state.

### PHASE8-IMPL-026-T011 — Synchronization, CI, rebuild, and operational rollout

Status: planned. Depends on T010.

Define the operational cadence for branch synchronization, deterministic
memory refresh, CI integration, rebuild triggers, and stale-index detection.
Document the operator's manual for Project Memory maintenance.

## Implementation sequence

```text
T001 (authority foundation) — complete/PASS
  -> T002 (schemas and registries)
  -> T003 (deterministic scanners)
  -> T004 (human-readable memory)
  -> T005 (context-tool integration)
  -> T006 (Serena pilot) [contingent]
  -> T007 (LlamaIndex/Qdrant pilot) [contingent]
  -> T008 (agent guidance and Ask)
  -> T009 (Plan Integrity engine)
  -> T010 (specialized reviewers)
  -> T011 (synchronization and rollout)
```

T006 and T007 are contingent on provenance and benchmark approval for their
respective dependencies. They are not blocked by T002–T005 but must not
describe their dependencies as already approved.

## Product boundaries

- Analysis-only — Project Memory analyzes and explains; it does not produce
  story prose or application features.
- Candidate-first — no automatic truth or approval.
- Evidence/provenance-backed — every claim traces to a source.
- Owner-controlled — no automatic mutation of authoritative state.
- No generated prose — structured metadata only.
- No confidence-as-truth — scores are metadata.
- No automatic Memory/Canon mutation — read/explain layer over plan and code.
- No automatic promotion or apply-promotion — explicitly owner-gated.
- Model output is not canon — generated explanations are not authoritative.

## Validation

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json >/dev/null
python3 -m json.tool docs/roadmap/roadmap_index.yaml >/dev/null
git diff --check
git status --short --branch
```
