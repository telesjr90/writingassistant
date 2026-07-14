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

## Deterministic Scanners

T003A implemented deterministic read-only scanners that inspect repository state
and produce normalized evidence records. The scanners use only the Python standard
library and read-only Git commands.

### Scanner Modules

- **`scripts/project_memory/repository_state.py`** — Collects Git repository state
  (branch, HEAD, staged, clean/dirty, tracked files, worktrees), hashes tracked
  sources (SHA-256), parses roadmap state, and validates registry source locators
  against the filesystem.
- **`scripts/project_memory/convergence.py`** — Computes structured convergence
  findings from registry validation, repository state, roadmap state, and source
  locator validation. Produces 20 finding codes across four severity levels.
- **`scripts/project_memory/build_snapshot.py`** — Builds complete generated snapshot
  packages into `.codex-context/project-memory/<TASK_ID>/<RUN_ID>/`. Produces JSON
  evidence files, SHA256SUMS, FILE-INVENTORY.txt, and a human-readable summary.md.

### Convergence Results

| Result | Meaning |
| --- | --- |
| `PASS` | No findings requiring owner attention or repair. |
| `PASS_WITH_FINDINGS` | Warnings or non-blocking errors detected; scan completed correctly. |
| `BLOCKED` | Registries invalid, worktree dirty (for publication), frontier silently changed, or other critical condition. |

### T003A / T003B Split

T003 is decomposed into two bounded children:

- **T003A** — Implements and tests the scanners and snapshot builder. Does not
  create a final publication snapshot from the dirty implementation worktree.
- **T003B** — Runs the scanner against a clean committed HEAD, creates the first
  generated evidence under `.codex-context/project-memory/`, validates convergence,
  and closes T003.

### Publication Snapshot Command (T003B)

After T003A is committed and the worktree is clean:

```bash
python3 scripts/project_memory/build_snapshot.py \
  --repo-root . \
  --output-root .codex-context/project-memory \
  --task-id PHASE8-IMPL-026-T003B
```

### Generated Snapshot Package Structure

```text
.codex-context/project-memory/
  <TASK_ID>/
    <RUN_ID>/
      run-metadata.json
      repository-state.json
      roadmap-state.json
      registry-validation.json
      source-inventory.json
      source-hashes.json
      convergence-findings.json
      snapshot.json
      summary.md
      FILE-INVENTORY.txt
      SHA256SUMS
```

### Clean-HEAD Requirement

Publication snapshots require a clean committed HEAD (no modified files, no
staged changes). A `--nonpublication` testing mode exists for temporary test
repositories but marks output as `publication_eligible: false`.

### Why Generated Snapshots Remain Non-Authoritative

Generated snapshots carry `authority_class: generated_evidence`. They:
- Are bound to an exact commit but are not project authority.
- Report convergence without claiming to be authoritative.
- Surface findings for owner review without automatically mutating tracked sources.
- Must not be treated as the source of truth for task status, dependencies, or
  roadmap decisions.

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
python3 -m pytest tests/project_memory/ -q -p no:cacheprovider
```

Run individual scanner modules:

```bash
python3 scripts/project_memory/repository_state.py --repo-root . --json
python3 scripts/project_memory/convergence.py --repo-root . --json
```

## Current Limitations

- Minimal representative seed only; not a complete repository inventory.
- No MkDocs integration or published documentation site (T004C).
- No context-tool integration (T005).
- No retrieval or AI agent integration (T006-T008).
- No Plan Integrity engine (T009).
- No generated publication snapshot existed at T003A. T003B created the first clean-HEAD generated snapshot.
- No publication render existed at T004B. T004C generated the first publication render against a clean-HEAD snapshot bound to the T004B commit.
- No branch synchronization performed yet.
- Stale memory detection requires future operational automation.

## First Publication Render (T004C)

T004C generated the first publication-mode human-readable Project Memory
documentation from a clean-HEAD snapshot bound to the T004B commit:

- **Snapshot path:** `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T033724Z/`
- **Render path:** `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T033724Z/`
- **Bound commit:** `3f094205253652a14a90a66a7294841af68ff630`
- **Convergence result:** PASS_WITH_FINDINGS (4 source_missing, none blocking)
- **Quality result:** PASS_WITH_FINDINGS
- **Page count:** 14
- **Authority class:** `generated_evidence` (non-authoritative)
- **Freshness limitation:** current only for the T004B commit; the T004C closeout
  commit will make the generated packages historical. A post-closeout clean-HEAD
  operational refresh is required for a current-documentation snapshot and render.
- **T004 closeout status:** complete/PASS-WITH-FINDINGS
- **T004A:** complete/PASS-WITH-FINDINGS
- **T004B:** complete/PASS
- **T004C:** complete/PASS-WITH-FINDINGS
- **Next:** T005 (existing context-tool integration)

## Deterministic Markdown Renderer

T004B implemented a deterministic, standard-library-only renderer:

- **Module:** `scripts/project_memory/render_docs.py`
- **Tests:** `tests/project_memory/test_render_docs.py`
- **CLI shape:**

```bash
python3 scripts/project_memory/render_docs.py \
  --repo-root . \
  --snapshot-dir <SNAPSHOT_DIR> \
  --output-root <OUTPUT_ROOT> \
  --task-id <TASK_ID> \
  --run-id <RUN_ID> \
  --generated-at <RFC3339_UTC> \
  --mode {publication,historical_preview} \
  --json
```

- **Output package:** 14 Markdown pages under `docs/` plus `build-manifest.json`, `source-snapshot.json`, `FILE-INVENTORY.txt`, and `SHA256SUMS`.

### 14-Page Set

1. `index.md` — Project Memory overview
2. `application-overview.md` — Application description
3. `product-boundaries.md` — Non-negotiable safety boundaries
4. `features.md` — Implemented, partial, and planned features
5. `capabilities.md` — Implemented and planned capabilities
6. `current-roadmap.md` — Accepted roadmap with active frontier
7. `remaining-work.md` — Incomplete and blocked work
8. `dependencies.md` — Dependency edges
9. `decisions.md` — Accepted and owner decisions
10. `assets.md` — Repository assets and fixtures
11. `evidence.md` — Evidence records
12. `risks-and-open-questions.md` — Active risks and open questions
13. `convergence-findings.md` — Snapshot findings
14. `technical-annex.md` — Schemas, versions, and determinism rules

### Modes

- **publication** — Requires clean worktree, matching HEAD, publication-eligible snapshot. Output under `.codex-context/project-memory/rendered/`. Rejects stale snapshots.
- **historical_preview** — Accepts valid stale snapshots. Output marked as historical and non-publication. Must not output under publication root.

### Key Behaviors

- **Generated evidence:** Every page carries a banner stating "Generated evidence — not project authority."
- **Freshness:** Stale snapshots rendered in historical_preview mode display a prominent "Historical preview" banner.
- **Unavailable sources:** Missing source locators are explicitly labeled rather than silently omitted.
- **Atomic output:** Built in a temporary directory and atomically renamed. Refuses to overwrite existing runs.
- **Determinism:** Identical inputs produce byte-identical output. UTF-8, LF endings, sorted JSON keys, stable record ordering.
- **No external dependencies:** Standard library only.

### T004 Status

- **T004A:** Complete/PASS-WITH-FINDINGS
- **T004B:** Complete/PASS
- **T004C:** Complete/PASS-WITH-FINDINGS — Clean-HEAD documentation generation, offline site quality gate, and T004 closeout.
- **T004:** Complete/PASS-WITH-FINDINGS.

First publication render at `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T033724Z/`.

No publication render exists yet. No MkDocs site, external tool, model, dependency, MCP server, plugin, index, or retrieval system was installed or used.

## Next Task

`PHASE8-IMPL-026-T005` — Existing context-tool integration. Planned/inactive.

T004 is closed as complete/PASS-WITH-FINDINGS.

## First Clean-HEAD Snapshot

T003B generated the first publication snapshot against the clean committed
T003A implementation HEAD:

- **Snapshot path:** `.codex-context/project-memory/PHASE8-IMPL-026-T003B/20260713T230207Z/`
- **Bound commit:** `a04b65cc42ba37fe1357272416828e49479cbce1`
- **Convergence result:** PASS_WITH_FINDINGS (14 findings, none blocking)
- **Authority class:** `generated_evidence` (non-authoritative)
- **Freshness:** current only for the bound T003A commit

The snapshot represents the T003A implementation commit, not the later
documentation-closeout commit. Future commits require a new snapshot before
being described as fresh.

T003 is complete/PASS-WITH-FINDINGS. T003A is complete/PASS.
T003B is complete/PASS-WITH-FINDINGS.

## Next Task

`PHASE8-IMPL-026-T005` — Existing context-tool integration. Planned/inactive.

T004 is complete/PASS-WITH-FINDINGS. T004C is complete/PASS-WITH-FINDINGS.

T004 is decomposed into three bounded children:

- **T004A** — Convergence remediation and human-readable Project Memory
  architecture. Complete/PASS-WITH-FINDINGS.
- **T004B** — Deterministic Markdown renderer implementation. Complete/PASS.
- **T004C** — Clean-HEAD documentation generation, offline site quality gate,
  and T004 closeout. Complete/PASS-WITH-FINDINGS.

T004 is complete/PASS-WITH-FINDINGS. T005 remains planned and inactive.
