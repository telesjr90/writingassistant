# Human-Readable Rendering Architecture

This is a tracked architecture and contributor contract, not generated documentation output.

## Purpose

The renderer converts tracked normalized registries and a selected generated snapshot
into human-readable Markdown documentation that explains what is implemented, what
is planned, what is missing, what conflicts exist, and what requires owner attention.

## Canonical Inputs

The renderer consumes exactly these inputs in order:

1. Tracked registry manifest (`docs/project-memory/registries/manifest.json`)
2. Tracked normalized registries (all 12 registry files)
3. Project Memory schema (`docs/project-memory/schemas/project-memory.schema.json`)
4. One explicitly selected generated snapshot (complete package under
   `.codex-context/project-memory/<TASK_ID>/<RUN_ID>/`)
5. Snapshot convergence findings (`convergence-findings.json`)
6. Snapshot source inventory and hashes (`source-inventory.json`, `source-hashes.json`)

The renderer does not independently scan the repository. It must reuse T003 scanner
output rather than create a second competing discovery system.

## Input Acceptance Rules

The renderer rejects these inputs:

- Invalid registries (any `validate_registries.py` failure)
- Malformed snapshot JSON
- Snapshot authority other than `generated_evidence`
- Missing full bound commit (`bound_commit` absent, empty, or non-hex)
- Nonpublication snapshots for publication output (`publication_eligible: false`)
- Snapshot task/run identity mismatch
- Missing required package files
- Invalid package hashes (any SHA256SUMS mismatch)
- Absolute or traversal paths in any input
- Unsupported schema or architecture versions

### Convergence Rules

- A `BLOCKED` convergence snapshot cannot be rendered as current documentation.
- A `PASS_WITH_FINDINGS` snapshot may be rendered only when:
  - `publication_eligible` is `true`
  - No `critical` or `blocks_publication: true` finding exists
  - Every finding is displayed prominently on the `convergence-findings.md` page
  - The output status remains `PASS_WITH_FINDINGS`

## Freshness Rules

Every generated page displays:

- `authority_class: generated_evidence`
- Bound commit (full 40-char SHA)
- Branch
- Generation timestamp (ISO 8601 with timezone)
- Snapshot run ID
- Snapshot path or identifier
- Convergence result
- Freshness state (`current` or `stale`)
- Known limitations

A snapshot is "current" only when its `bound_commit` exactly matches the target
repository commit. Stale snapshots may be rendered only as explicitly historical views.
The renderer cannot infer freshness from timestamps alone.

## Generated Output Boundary

```text
.codex-context/project-memory/rendered/
  <TASK_ID>/
    <RUN_ID>/
      build-manifest.json
      source-snapshot.json
      docs/
      FILE-INVENTORY.txt
      SHA256SUMS
```

Generated pages and built sites are:

- Generated evidence (`generated_evidence`, never `authoritative`)
- Git-ignored (never tracked)
- Reproducible (identical inputs produce identical outputs)
- Never manually edited
- Never authoritative

## Renderer Implementation (T004B)

T004B implemented the deterministic Markdown renderer according to the committed
T004A architecture contract.

- **Module:** `scripts/project_memory/render_docs.py`
- **Tests:** `tests/project_memory/test_render_docs.py` (71 tests)
- **Renderer name:** `project_memory_markdown_renderer`
- **Renderer version:** `project_memory_markdown_renderer.v1`

The renderer is standard-library-only. No dependencies were added.

### CLI Contract

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

### Implementation Status

T004B is complete/PASS. No publication render exists yet.

## Deterministic Page Set

T004B must generate at least these 14 pages in stable navigation order:

1. `index.md` — Project Memory overview
2. `application-overview.md` — application description and boundaries
3. `product-boundaries.md` — non-negotiable safety and governance
4. `features.md` — implemented, partially implemented, and planned features
5. `capabilities.md` — implemented and planned capabilities with validation status
6. `current-roadmap.md` — accepted roadmap with active frontier
7. `remaining-work.md` — planned, blocked, and inactive work
8. `dependencies.md` — dependency edges and contingent workstreams
9. `decisions.md` — accepted decisions with rationale
10. `assets.md` — repository assets, fixtures, and data artifacts
11. `evidence.md` — accepted evidence records
12. `risks-and-open-questions.md` — active risks and unresolved questions
13. `convergence-findings.md` — snapshot findings with severity and disposition
14. `technical-annex.md` — schemas, registry structure, scanner architecture

### Plain-English Requirements

The primary pages must explain:

- What application is being built
- What the product does
- What it must never do
- What currently exists
- What has been validated
- What remains planned
- What is blocked or unavailable
- What the active application frontier is
- Why PHASE8-IMPL-025 remains inactive
- How Project Memory relates to the application roadmap
- How evidence and source links support each claim

Technical details belong in `technical-annex.md`.
Generated story prose must not appear on any page.

### Page Record Presentation

Every rendered record must display or make available:

- Stable record ID
- Title
- Record type
- Authority class
- Lifecycle status
- Implementation status where relevant
- Validation status where relevant
- Source locators (with link targets)
- Provenance (creator, acceptor)
- Supersession (if any)
- Owner-decision state (if any)
- Missing/unavailable source state
- Freshness

Planned must never be presented as implemented.
Implemented must never be presented as validated unless evidence supports validation.
Candidate, review-pending, approved, promoted, and canon states must remain distinct.

### Linking Rules

Links must:

- Be repository-relative where possible
- Point to exact source files
- Include line ranges or JSON Pointers when available
- Distinguish available links from unavailable source references
- Never use local absolute paths
- Never link to ignored mutable evidence as if tracked authority
- Never silently drop broken links

## Build Manifest

The `build-manifest.json` must include:

- `renderer_name` and `version`
- `schema_version` and `architecture_version`
- Exact command used
- `task_id` and `run_id`
- Generated timestamp (ISO 8601 with timezone)
- `branch` and `bound_commit` (full 40-char SHA)
- Source snapshot path or identifier
- Snapshot hashes (all from SHA256SUMS)
- Registry hashes (SHA-256 of each registry file)
- Page list with per-page SHA-256 hashes
- Navigation order
- Convergence result
- Finding counts by code and severity
- Exclusions and known limitations
- `authority_class` fixed to `generated_evidence`
- `publication_eligibility`

## Determinism

Given identical:

- Renderer version
- Registries
- Snapshot package
- Run ID
- Generated timestamp

the semantic Markdown, manifest, inventory, and ordering must be identical.
Use UTF-8, sorted keys, stable record sorting, stable navigation ordering,
newline at end of every text file, no local absolute paths, no random IDs,
and no locale-dependent formatting.

## MkDocs Boundary

MkDocs remains the intended human-auditable site layer, but:

- T004A does not install MkDocs, add package dependencies, add `mkdocs.yml`,
  create a virtual environment, download a theme, use a plugin, run a server,
  or build a site.
- T004C performs the approved offline documentation-site integration after
  provenance, dependency, and reproducibility requirements are verified.
- The deterministic Markdown renderer must remain independently usable without
  MkDocs.

## Unavailable Source Display

When a source locator references a file that does not exist in the current
checkout, the rendered page must display "unavailable in this checkout" rather
than silently omitting the record. The missing-source classification must be
visible on the evidence and convergence-findings pages.

## Non-Authoritative Classification

Every generated page carries a prominent banner:

```text
Generated Evidence — Not Project Authority
Bound to commit <sha> on branch <branch>.
Snapshot: .codex-context/project-memory/<TASK_ID>/<RUN_ID>/
Generated: <ISO 8601 timestamp>
```

Pages never claim `authoritative` status and never become an additional tier
in the authority hierarchy.

## T004 Decomposition

T004 is decomposed into three bounded children:

- **T004A** — Convergence remediation and human-readable Project Memory architecture (complete/PASS-WITH-FINDINGS)
- **T004B** — Deterministic Markdown renderer implementation and focused tests (complete/PASS)
- **T004C** — Clean-HEAD documentation generation, offline site quality gate, and T004 closeout (complete/PASS-WITH-FINDINGS)

## First Publication Render (T004C)

T004C generated the first publication-mode human-readable Project Memory
documentation from a clean-HEAD snapshot bound to the T004B commit
`3f094205253652a14a90a66a7294841af68ff630` on branch `docs/project-memory-foundation`.

- **Render path:** `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T033724Z/`
- **Snapshot path:** `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T033724Z/`
- **Convergence result:** PASS_WITH_FINDINGS (4 nonblocking source_missing)
- **Quality-gate result:** PASS_WITH_FINDINGS
- **Freshness limitation:** The generated pages are current only for the T004B
  commit. The future T004C closeout commit will make them historical. A
  post-closeout clean-HEAD refresh is required.

No change to the committed renderer architecture occurred in T004C. The
publication render used only the committed T004B renderer as-is.
