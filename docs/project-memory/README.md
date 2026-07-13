# Project Memory

## What Project Memory Is

Project Memory is a normalized, machine-readable, commit-bound system that:

1. Records the accepted plan (roadmap tasks, decisions, capabilities, boundaries).
2. Compares the plan with the actual implementation (code, tests, schemas).
3. Explains discrepancies with evidence.
4. Surfaces confidence, uncertainty, and provenance for owner review.
5. Maintains freshness bound to repository commits.

Project Memory is a parallel governance, documentation, and developer infrastructure workstream. It is **not** an application feature.

## What Project Memory Is Not

- Not an application feature or runtime component.
- Not an automatic truth, approval, or promotion engine.
- Not a replacement for the application roadmap.
- Not a story-prose generator, editor, or validator.
- Not a model orchestrator or AI agent controller.

## Authority Hierarchy

Project Memory must distinguish and reconcile seven tiers of authority:

| Tier | Authority class | Description |
| --- | --- | --- |
| 1 | Accepted roadmap and decision records | `roadmap_index.yaml`, `implementation_status.md`, decision records |
| 2 | Live code and schemas | Backend and frontend source, data schemas, contract modules |
| 3 | Automated tests | Test files that validate contract and behavior |
| 4 | Accepted manual validation | Evidence artifacts classified as accepted validation |
| 5 | Exact Git history | Commit hashes, author, timestamps, commit messages |
| 6 | Normalized Project Memory registries | Machine-readable records under `docs/project-memory/` |
| 7 | Generated context, indexes, retrieval results, AI summaries | Artifacts under `.codex-context/`, `ai_context/`, `graphify-out/` |

Conflict resolution: higher tiers are authoritative. A registry (tier 6) conflicting with the roadmap (tier 1) or live code (tier 2) is stale or invalid.

See the [T001 decision record](../roadmap/decisions/PHASE8-IMPL-026-T001-project-memory-authority-lifecycle-provenance-foundation.md) for the full authority foundation.

## Trust Classes

| Class | Meaning | Can update registries? |
| --- | --- | --- |
| `authoritative` | Owner-accepted decision, code, or test suite | Yes |
| `accepted_evidence` | Owner-accepted manual validation or deterministic output | Yes (when consistent) |
| `generated_evidence` | Context-tool output, AI summary, or index build | No |
| `historical` | Superseded decision or pre-refactor record | No |
| `superseded` | Explicitly replaced by a later record | No |
| `uncertain` | Conflicting or ambiguous unresolved evidence | No |
| `owner_pending` | Proposed change awaiting owner decision | No |
| `untrusted` | Unknown provenance or failed safety check | No |

## Tracked Registries vs. Generated Snapshots

**Tracked normalized registries** live under `docs/project-memory/registries/`. They:
- Express accepted normalized records.
- Carry source locators and authority/lifecycle metadata.
- Are changed only through owner-approved implementation tasks.
- Do not need to be rewritten solely because repository HEAD advances.

**Generated commit-bound snapshots** will live under `.codex-context/project-memory/`. They:
- Bind tracked registries and discovered repository state to an exact commit.
- Carry `bound_commit`, source hashes, tool/version, generation time, scope, exclusions, and freshness.
- Are generated evidence (`generated_evidence`), not authoritative.
- Are not yet created (planned for T003/T004).

## Registry File Roles

| Registry | Record type | Required | Purpose |
| --- | --- | --- | --- |
| `manifest.json` | manifest | Yes | Declares all registry files, their properties, and cross-reference policy. |
| `projects.json` | project | Yes | Application and infrastructure projects. |
| `features.json` | feature | Yes | Top-level features and their implementation status. |
| `boundaries.json` | boundary | Yes | Non-negotiable product safety and governance boundaries. |
| `tasks.json` | task | Yes | Roadmap tasks with dependencies and lifecycle. |
| `decisions.json` | decision | Yes | Accepted decisions with rationale and affected tasks. |
| `capabilities.json` | capability | Yes | Implemented and planned capabilities with validation status. |
| `assets.json` | asset | Yes | Repository assets, fixtures, and data artifacts. |
| `evidence.json` | evidence | Yes | Accepted evidence records (manual validation, commits, defects). |
| `dependencies.json` | dependency | Yes | Dependency edges between records (task, capability, boundary). |
| `tools.json` | tool | Yes | Known tools with provenance state. |
| `owner-decisions.json` | owner_decision | Yes | Owner-controlled decisions with rationale. |

## Stable Identifiers

Every record has a stable, immutable, namespaced identifier:

```text
project:<slug>
feature:<slug>
boundary:<slug>
task:<authoritative-task-id>
decision:<authoritative-decision-id>
capability:<slug>
asset:<slug>
evidence:<slug>
dependency:<slug>
tool:<slug>
owner-decision:<slug>
```

IDs are unique across all registries, immutable after acceptance, and cannot contain path traversal, whitespace, control characters, absolute paths, or platform-specific separators. Display labels may change without changing IDs.

## Validation

Run the dependency-free standard-library validator:

```bash
python3 scripts/project_memory/validate_registries.py
```

For machine-readable output:

```bash
python3 scripts/project_memory/validate_registries.py --json
```

Run focused tests:

```bash
python3 -m pytest tests/project_memory/test_validate_registries.py -q -p no:cacheprovider
```

## How Later Scanners Will Extend the Seed

Future T003 deterministic scanners will:
1. Read the existing tracked registries as a known-good baseline.
2. Inspect live repository state (code, tests, roadmap files, enrichment data).
3. Produce generated evidence records in a commit-bound snapshot under `.codex-context/project-memory/`.
4. Report convergence, divergence, staleness, and conflicts without mutating tracked registries.

Scanners will extend records by adding new entries; they will not replace existing identifiers or create a competing roadmap.

## How Later MkDocs Rendering Will Consume Registries

Future T004 MkDocs rendering will:
1. Read tracked registries and generated snapshots.
2. Produce human-readable documentation explaining what is implemented, planned, missing, or conflicting.
3. Surface freshness, trust class, and authority level in every rendered view.
4. Treat generated rendered output as non-authoritative build output.

## Why Generated Indexes and AI Summaries Remain Non-Authoritative

Generated context packs, AI summaries, vector indexes, and retrieval results are `generated_evidence`. They:
- May contain plausible-looking but incorrect information.
- Cannot be treated as default authority without explicit owner review.
- Must report their `bound_commit`, `generated_at`, and freshness state in every response.
- Must not silently answer as current truth when stale.

## Current Limitations

- Minimal representative seed only; not a complete repository inventory.
- No scanners or repository discovery yet (T003).
- No human-readable rendered output (T004).
- No context-tool integration (T005).
- No retrieval or AI agent integration (T006-T008).
- No Plan Integrity engine (T009).
- No generated snapshots exist yet.
- No branch synchronization performed yet.

## Next Task

`PHASE8-IMPL-026-T003` — Deterministic scanners and convergence. Will implement read-only deterministic scanners that inspect repository state and produce normalized evidence records with convergence criteria.
