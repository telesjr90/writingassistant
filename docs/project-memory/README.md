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

**Generated commit-bound snapshots** live under `.codex-context/project-memory/`. They:
- Bind tracked registries and discovered repository state to an exact commit.
- Carry `bound_commit`, source hashes, tool/version, generation time, scope, exclusions, and freshness.
- Are generated evidence (`generated_evidence`), not authoritative.
- Include accepted current publication packages only after clean-HEAD freshness,
  checksum, authority, convergence, and semantic validation.

## Project Memory Ask

T008 defines a deterministic, read-only consultation contract:

- `ask-protocol.md` defines request/response fields, precedence, citations,
  freshness, owner-decision reporting, and fail-closed results.
- `.agents/skills/project-memory-read/SKILL.md` defines bounded source
  consultation for Codex and compatible agents.
- `.opencode/agents/project-memory-ask.md` defines a strictly read-only OpenCode
  subagent with mutation/network access denied and shell limited to explicit
  read-only Git inspection.
- `scripts/project_memory/validate_agent_guidance.py` validates these contracts
  deterministically with the Python standard library.

Ask uses accepted repository sources first. Registries and current rendered
publications are navigation aids, not authority. Generated evidence and model
output never become truth. T006/T007 retrieval pilots are not required.

## Specialized Plan Integrity Reviewers

T010 defines six bounded read-only reviewer domains: backend contracts,
frontend UI, test coverage, roadmap consistency, enrichment accuracy, and
decision coherence. `reviewer-protocol.md` and
`.agents/skills/project-memory-plan-integrity-review/SKILL.md` provide the
shared request, evidence, finding, freshness, authority, and fail-closed
contract. Six OpenCode definitions bind one domain each without embedding
mutable project truth.

`scripts/project_memory/reviewer_findings.py` validates and normalizes supplied
structured findings without invoking a model. Output remains
`generated_evidence`; it cannot alter T009 readiness, select semantic truth,
create an owner decision, or mutate roadmap, registry, Memory/Canon, candidate,
promotion, apply-promotion, or story-prose state. Reviewers are not scheduled or
automatically active.

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

Validate shared guidance:

```bash
python3 scripts/project_memory/validate_agent_guidance.py
python3 scripts/project_memory/validate_agent_guidance.py --json
```

Validate specialized reviewer guidance:

```bash
python3 scripts/project_memory/validate_reviewer_guidance.py
python3 scripts/project_memory/validate_reviewer_guidance.py --json
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
- Read-only existing context-tool evidence import is implemented (T005); no live context-tool runner exists.
- No retrieval pilot is active. T006/T007 remain owner-deferred, contingent, and inactive; T008 read-only Ask guidance is implemented without retrieval integration.
- Deterministic Plan Integrity engine and clean-HEAD generated report package are implemented (T009); specialized reviewer agents (T010) are not implemented.
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
- **T005:** complete/PASS (read-only existing context-tool evidence import)

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

## Post-Closeout Clean-HEAD Refresh (20260714T042826Z)

A clean-HEAD refresh was attempted at `20260714T042826Z` bound to the T004C
closeout commit `a415270b18f978e601a9ffc6d7bcb4ab8a250c42`.

### Status

The refresh generated structurally valid packages:

- **Snapshot:** `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T042826Z/`
- **Render:** `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T042826Z/`
- **Quality:** `.codex-context/project-memory/PHASE8-IMPL-026-T004C-quality/20260714T042826Z/`

All packages pass SHA256SUMS. Bound commit is correct. Convergence is
PASS_WITH_FINDINGS (4 nonblocking source_missing). Publication eligibility is
true.

### Why not accepted

The rendered documentation incorrectly reported T004 as "in progress" and
T004C as "planned" because:

1. The task registry (`docs/project-memory/registries/tasks.json`) contained
   records only through T003 and lacked normalized records for T004, T004A,
   T004B, T004C, and T005.
2. The renderer (`scripts/project_memory/render_docs.py`) hardcodes the
   "Project Memory Workstream Status" table in `_render_index()` (lines
   718-726) rather than reading task lifecycle status from the registry.

The one-off quality checker returned PASS (false positive) because it did
not verify rendered task-status convergence with accepted roadmap truth.

### Classification

The `20260714T042826Z` packages are structurally valid generated evidence
but were not accepted as the current publication. No accepted current
publication exists for `a415270b18f978e601a9ffc6d7bcb4ab8a250c42`.

## T004C1 Registry Repair

T004C1 is a bounded post-closeout repair that:

- Added normalized task records for T004, T004A, T004B, T004C, and T005
  to `docs/project-memory/registries/tasks.json`.
- Updated T003 from "planned" to "complete".
- Added a T004-depends-on-T003 dependency edge to
  `docs/project-memory/registries/dependencies.json`.
- Removed hardcoded task-status strings from `_render_index()` and
  `_render_current_roadmap()` in `scripts/project_memory/render_docs.py`.
- Implemented deterministic task-status derivation from the validated
  normalized task registry.
- Created a semantic rendered-package validator
  (`scripts/project_memory/validate_rendered_docs.py`) with CLI.
- Added a fail-closed semantic publication gate in the renderer:
  publication rendering refuses atomic finalization when generated pages
  contradict normalized task truth.
- Added focused regression coverage across three test files.
- Updated documentation to record the failed refresh, the repair, and
  the required next operational step.

### Known renderer defect (RESOLVED)

The renderer no longer hardcodes the index page's "Project Memory
Workstream Status" table or the current-roadmap child indicator.
Task status is now derived from the validated task registry.

### Required next steps

1. **Post-repair clean-HEAD refresh** — Generate an accepted current
   publication snapshot and render bound to the T004C2 commit.

The post-repair clean-HEAD publication was accepted at `20260714T221454Z`,
bound to `8961b35`. T005 is complete/PASS.

## Next Task

T006/T007 remain owner-deferred, planned/contingent/inactive. T008 and T009 are
complete/PASS. The next sequenced Project Memory task is T010,
planned/inactive; T011 remains planned/inactive.

T004 is closed as complete/PASS-WITH-FINDINGS. T004C1 and T004C2 are complete/PASS.

## T004C2 Authority Semantics Repair

The current, task-state-convergent T004C1 refresh at `20260714T213628Z`
was rejected by the committed authority validator because it treated any
lowercase `authoritative` token as a possible claim that the generated page
itself was authoritative. The rendered pages instead displayed tracked-record
authority metadata, described the accepted authority hierarchy and trust
classes, or explicitly denied generated-evidence authority.

T004C2 replaces that page-wide keyword rule with deterministic line-level
checks that distinguish statement subjects. The validator now:

- requires the exact generated-evidence banner;
- classifies legitimate hierarchy, trust-class, tracked-source, disclaimer,
  historical, technical, inline-code, and Markdown-link references;
- detects explicit generated-page/render/snapshot/package/output claims of
  authority, truth control, roadmap override, owner-decision resolution,
  canon establishment, or automatic candidate approval;
- reports every forbidden claim with page, line, matched text, rule, class,
  and reason;
- returns no generic authority warning when no forbidden claim exists.

Renderer wording did not require modification. The accepted current T004C2
publication is the `20260714T221454Z` snapshot/render/quality set bound to
`8961b35`.

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

## Operational Maintenance

T005 and T008-T011 are complete/PASS. T006/T007 remain owner-deferred,
planned/contingent/inactive and unimplemented. PHASE8-IMPL-026 is closed as
complete/PASS-WITH-FINDINGS; there is no next Project Memory implementation
task. Ongoing maintenance follows the event-driven, commit-bound policy in
`operations.json` and `operator-manual.md`. The application implementation
frontier remains `PHASE8-IMPL-024-T003A`.

The standard-library-only operational CLI provides:

- `status`/`check`: read-only stale-state, binding, inventory, checksum, hash,
  readiness, semantic, authority, and quality diagnosis;
- `refresh`: one-command clean-HEAD Plan Integrity report, snapshot,
  publication render, semantic/authority validation, and quality package; and
- `ci-check`: an exact-commit ephemeral rebuild under an explicit temporary
  directory without repository publication output.

The cadence has no cron component. Refresh follows accepted synchronization,
Project Memory tracked changes/task completion, closeout gates, or detected
repository divergence. Synchronization itself remains owner-controlled and is
never performed by the operational CLI.

T004 is complete/PASS-WITH-FINDINGS. T004C is complete/PASS-WITH-FINDINGS.

T004 is decomposed into three bounded children:

- **T004A** — Convergence remediation and human-readable Project Memory
  architecture. Complete/PASS-WITH-FINDINGS.
- **T004B** — Deterministic Markdown renderer implementation. Complete/PASS.
- **T004C** — Clean-HEAD documentation generation, offline site quality gate,
  and T004 closeout. Complete/PASS-WITH-FINDINGS.

T004 is complete/PASS-WITH-FINDINGS. T005 is complete/PASS.

## T005 Existing Context-Tool Evidence Import

T005 implements deterministic, standard-library-only read adapters for
existing Repomix, Graphify, and CCE artifacts:

- public discovery, inspection, normalization, package-build, and package-validation APIs;
- deterministic tool attribution from manifests, recorded commands, metadata,
  or tracked conventions—never filenames alone;
- `current`, `stale`, `historical`, `unknown`, and `unusable` freshness states;
- bounded inventory, declared-checksum validation, safety exclusions, and
  explicit default eligibility or quarantine;
- fixed `generated_evidence` authority with no automatic registry or truth update;
- exact eight-file, atomic, overwrite-refusing ignored evidence packages.

Unknown and ambiguous origins are classified as
`unknown_generated_context`. Stale, historical, unknown, ambiguous, unsafe,
authority-claiming, and provenance-incomplete artifacts remain inventoried but
quarantined. Read-import approval does not approve installation, indexing,
search, or live execution.

At implementation time, `ai_context/` and `graphify-out/` were absent in this
checkout. `.codex-context/` contained only prior Project Memory evidence, which
is excluded from recursive ingestion. No context tool was installed or
executed, and no network or model call occurred.
