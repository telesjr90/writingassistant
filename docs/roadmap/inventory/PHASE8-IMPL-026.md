# PHASE8-IMPL-026 Inventory

## Parent

- ID: `PHASE8-IMPL-026`
- Title: Project Memory and Plan Integrity
- Classification: hybrid governance, documentation, and developer infrastructure
- Status: complete/closed as complete/PASS-WITH-FINDINGS
- Application frontier and sole next application implementation focus: PHASE8-IMPL-024-T003B
- Next Project Memory implementation task: none
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
   - T004C2 (generated-evidence authority semantics and publication-acceptance repair) — complete/PASS.
   - First publication snapshot at `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T033724Z/`.
   - First publication render at `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T033724Z/`.
   - Post-closeout clean-HEAD refresh at `20260714T042826Z` bound to `a415270` produced structurally valid packages but was not accepted (renderer hardcodes index status table).
   - T004C1 repaired: task-registry synchronization, renderer hardcodes removed, registry-derived task status, semantic validator, fail-closed semantic publication gate, focused regression tests.
   - T004C1 refresh `20260714T213628Z` was current and task-state convergent but rejected by a false-positive page-wide authority-keyword rule.
   - T004C2 repaired authority semantics with subject-aware rules and page/line diagnostics; renderer wording was unchanged.
   - Accepted current publication: `20260714T221454Z`, bound to `8961b35`.
5. `PHASE8-IMPL-026-T005` — Existing context-tool integration (complete/PASS).
   - Standard-library-only read adapters for Repomix, Graphify, and CCE evidence.
   - Unknown, ambiguous, stale, historical, unsafe, and provenance-incomplete artifacts are quarantined.
   - No context tool installation or execution; generated output remains `generated_evidence`.
6. `PHASE8-IMPL-026-T006` — Serena read-only pilot (owner-deferred;
   planned/contingent/inactive/unimplemented; no measured capability gap).
7. `PHASE8-IMPL-026-T007` — LlamaIndex / local-embedding / Qdrant Local pilot
   (owner-deferred; planned/contingent/inactive/unimplemented; no measured
   capability gap).
8. `PHASE8-IMPL-026-T008` — Shared agent guidance and Project Memory Ask
   (complete/PASS).
   - Deterministic Ask protocol, shared read skill, read-only OpenCode agent,
     standard-library contract validator, and focused tests.
   - Ordinary read-only repository access only; no retrieval pilot required.
9. `PHASE8-IMPL-026-T009` — Deterministic Plan Integrity engine
   (complete/PASS).
   - Exact Q151 classifications, readiness tri-state, six deterministic rule
     groups, and atomic clean-HEAD generated-evidence reporting.
10. `PHASE8-IMPL-026-T010` — Specialized Plan Integrity reviewers
    (complete/PASS; six read-only reviewer domains, shared protocol/skill,
    deterministic guidance validation and finding normalization; no reviewer
    or model invoked).
11. `PHASE8-IMPL-026-T011` — Synchronization, CI, rebuild, and operational
    rollout (complete/PASS; Q154 resolved by event-driven commit-bound policy).
12. `PHASE8-IMPL-026-T012` — Remaining-MVP current-truth,
    execution-routing, and shared UI-guidance maintenance (complete/PASS;
    explicit post-closeout governance maintenance, no application scope).

T006 and T007 are owner-deferred because no benchmarkable symbol-navigation,
retrieval-quality, citation, scale, latency, or maintainability gap has been
measured. They remain contingent and may be reconsidered only after a documented
benchmarkable gap and a future owner-approved provenance/benchmark task. Serena,
LlamaIndex, and Qdrant are not approved dependencies.

## Dependencies

```text
PHASE8-IMPL-026-T001 (complete/PASS)
  -> T002 (complete/PASS) -> T003 -> T004 -> T005 (complete/PASS) -> T006 [contingent]
                                   -> T007 [contingent]
                            -> T008 -> T009 -> T010 -> T011 -> T012
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
- Read-only context-tool evidence import exists; no retrieval tool or live context-tool runner exists.
- Shared agent guidance and deterministic Project Memory Ask exist (T008); the
  OpenCode agent is read-only and all answers fail closed on unsupported truth
  claims.
- No retrieval pilot or Plan Integrity reviewer exists; the deterministic T009 engine exists without reviewer agents.
- T001, T002, T003A, T003B, T004B, T004C, T004C1, T004C2, T005, T008, and T009 are delivered.
- The accepted current T004C2 publication is the `20260714T221454Z` set bound to `8961b35`.
- T006/T007 remain owner-deferred, planned/contingent/inactive, and unimplemented.
- T010/T011 are complete/PASS. T012 is owner-authorized bounded post-closeout
  maintenance in progress/validation pending. PHASE8-IMPL-026 remains
  complete/closed as complete/PASS-WITH-FINDINGS. T012 is not an application
  implementation frontier; after acceptance, maintenance returns to the T011
  operational procedure. The application
  frontier `PHASE8-IMPL-024-T003B` is the sole next application implementation
  focus.
