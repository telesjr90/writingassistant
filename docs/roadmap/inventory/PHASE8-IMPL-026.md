# PHASE8-IMPL-026 Inventory

## Parent

- ID: `PHASE8-IMPL-026`
- Title: Project Memory and Plan Integrity
- Classification: hybrid governance, documentation, and developer infrastructure
- Status: published/active (parallel governance workstream)
- Application frontier: unchanged — PHASE8-IMPL-024-T003A
- PHASE8-IMPL-025: unchanged — published/planned, inactive
- Controlling decision: `docs/roadmap/decisions/PHASE8-IMPL-026-T001-project-memory-authority-lifecycle-provenance-foundation.md`

## Relationship to application roadmap

PHASE8-IMPL-026 is a parallel workstream. It does not replace, activate,
close, or reorder application tasks. The `active_frontier` in
`roadmap_index.yaml` continues to track the application implementation
frontier. Project Memory normalizes and explains the roadmap; it must not
silently override it.

## Repository locations

| Content | Path | Created by T001 |
| --- | --- | --- |
| Decisions | `docs/roadmap/decisions/` | No (existing convention) |
| Future documentation and registries | `docs/project-memory/` | No |
| Future implementation | `scripts/project_memory/` | No |
| Future tests | `tests/project_memory/` | No |
| Future shared skills | `.agents/skills/` | No |
| Future OpenCode agents | `.opencode/agents/` | No |
| Generated evidence and indexes | `.codex-context/project-memory/` | No |

## Authority hierarchy

1. Accepted roadmap and decision records — authoritative.
2. Live code and schemas — authoritative for implementation behavior.
3. Automated tests — authoritative for contract validation.
4. Accepted manual validation — authoritative within recorded scope.
5. Exact Git history — authoritative for provenance.
6. Normalized Project Memory registries — explain and cross-reference tiers
   1–5; stale when conflicting.
7. Generated context, indexes, retrieval results, and AI summaries —
   evidence only; never authoritative.

## Trust classes

| Class | May update registries | Default retrieval |
| --- | --- | --- |
| `authoritative` | Yes | Included |
| `accepted_evidence` | Yes (when consistent) | Included |
| `generated_evidence` | No | Excluded from default |
| `historical` | No | Excluded from default |
| `superseded` | No | Excluded from default |
| `uncertain` | No | Included with warning |
| `owner_pending` | No | Included with warning |
| `untrusted` | No | Excluded |

## Indexed workstreams

1. `PHASE8-IMPL-026-T001` — Authority, lifecycle, provenance, and roadmap
   foundation (complete/PASS).
2. `PHASE8-IMPL-026-T002` — Schema and normalized-registry architecture
   (complete/PASS).
3. `PHASE8-IMPL-026-T003` — Deterministic scanners and convergence (complete/PASS-WITH-FINDINGS).
   - T003A (scanner implementation and testing) — complete/PASS.
   - T003B (clean-HEAD snapshot, convergence validation, closeout) — complete/PASS-WITH-FINDINGS.
4. `PHASE8-IMPL-026-T004` — Human-readable Project Memory (complete/PASS-WITH-FINDINGS).
   - T004A (convergence remediation and rendering architecture) — complete/PASS-WITH-FINDINGS.
   - T004B (Markdown renderer implementation) — complete/PASS.
   - T004C (clean-HEAD documentation generation, offline site quality gate, and T004 closeout) — complete/PASS-WITH-FINDINGS.
   - T004C1 (post-closeout task-registry synchronization and current-truth quality-gate repair) — complete/PASS.
   - First publication snapshot at `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T033724Z/`.
   - First publication render at `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T033724Z/`.
   - Post-closeout clean-HEAD refresh at `20260714T042826Z` bound to `a415270` produced structurally valid packages but was not accepted (renderer hardcodes index status table).
   - T004C1 repaired: task-registry synchronization, renderer hardcodes removed, registry-derived task status, semantic validator, fail-closed semantic publication gate, focused regression tests.
   - No accepted current publication exists yet; a post-T004C1 clean-HEAD refresh is required.
5. `PHASE8-IMPL-026-T005` — Existing context-tool integration (planned).
6. `PHASE8-IMPL-026-T006` — Serena read-only pilot (planned; contingent).
7. `PHASE8-IMPL-026-T007` — LlamaIndex / local-embedding / Qdrant Local pilot
   (planned; contingent).
8. `PHASE8-IMPL-026-T008` — Shared agent guidance and Project Memory Ask
   (planned).
9. `PHASE8-IMPL-026-T009` — Deterministic Plan Integrity engine (planned).
10. `PHASE8-IMPL-026-T010` — Specialized Plan Integrity reviewers (planned).
11. `PHASE8-IMPL-026-T011` — Synchronization, CI, rebuild, and operational
    rollout (planned).

T006 and T007 are contingent on provenance and benchmark approval. Serena,
LlamaIndex, and Qdrant are not approved dependencies.

## Dependencies

```text
PHASE8-IMPL-026-T001 (complete/PASS)
  -> T002 (complete/PASS) -> T003 -> T004 -> T005 -> T006 [contingent]
                                   -> T007 [contingent]
                            -> T008 -> T009 -> T010 -> T011
```

## Safety inventory

- Analysis-only — Project Memory analyzes and explains; no application features.
- Candidate-first — registries are evidence, not truth.
- Evidence/provenance-backed — every claim traces to a source.
- Owner-controlled — no automatic mutation.
- No generated prose — structured metadata only.
- No confidence-as-truth.
- No automatic Memory/Canon mutation.
- No automatic promotion or apply-promotion.
- Model output is not canon.
- Registries do not silently override the roadmap or live code.

## T001 decision scope

The controlling decision (`PHASE8-IMPL-026-T001-project-memory-authority-lifecycle-provenance-foundation.md`)
defines:

1. Authority hierarchy (7 tiers).
2. Trust classes (8 classes).
3. Freshness model (commit-bound, not time-bound).
4. Commit binding requirements.
5. Supersession fields and behavior.
6. Conflicting-evidence resolution.
7. Owner-decision representation.
8. Generated-evidence requirements.
9. Memory-update approval rules.
10. Roadmap synchronization policy.
11. Stale-index and retrieval behavior.
12. Tool provenance and security requirements.
13. Prompt-injection trust boundaries.
14. Branch synchronization policy.
15. Product boundaries for Project Memory.

No schema, scanner, registry, renderer, retrieval tool, or reviewer is
implemented by T001.

## Current state

- Project Memory schemas exist (JSON Schema Draft 2020-12).
- Registry architecture and tracked seed registries exist (12 registries + manifest).
- Dependency-free standard-library validator exists.
- Deterministic repository-state scanner, convergence checker, and snapshot builder exist (T003A).
- First clean-HEAD publication snapshot exists at `.codex-context/project-memory/PHASE8-IMPL-026-T003B/20260713T230207Z/` bound to `a04b65c` (T003B), 14 findings, none blocking.
- Deterministic Markdown renderer exists (`scripts/project_memory/render_docs.py`) with 71 focused tests and deterministic/atomic output (T004B). 148 total Project Memory tests pass.
- First clean-HEAD publication snapshot exists at `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T033724Z/` bound to `3f09420` (T004C), 4 findings, none blocking.
- First publication render exists at `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T033724Z/` (14 Markdown pages, offline quality gate PASS_WITH_FINDINGS).
- No retrieval tools exist.
- No reviewers exist.
- T001, T002, T003A, T003B, T004B, T004C, and T004C1 are the delivered artifacts.
- The next operational step is a post-T004C1 clean-HEAD refresh. No accepted current publication exists yet for the current clean HEAD.
- The next Project Memory task is PHASE8-IMPL-026-T005 (Existing context-tool integration), planned/inactive.
