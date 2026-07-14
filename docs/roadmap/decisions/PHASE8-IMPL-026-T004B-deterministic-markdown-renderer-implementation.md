# PHASE8-IMPL-026-T004B — Deterministic Markdown Renderer Implementation

**Task ID:** PHASE8-IMPL-026-T004B
**Parent task:** PHASE8-IMPL-026-T004 (Human-readable Project Memory)
**Decision type:** Implementation
**Status:** Accepted / Complete
**Date:** 2026-07-13
**Authority class:** authoritative

## Result

**PASS** — Implementation complete. 71 focused tests pass. Historical smoke against T003B snapshot succeeds. No findings block T004C.

## Starting Repository State

- **Repository:** `/home/tjrpirateking/projects/WritingAssistantApplication-project-memory`
- **Branch:** `docs/project-memory-foundation`
- **Full HEAD:** `4918051f0b3a6f65ebc13ae9b3648c8f12428cb1`
- **Subject:** `docs(pm): repair source locators and define rendering architecture (T004A)`
- **Staging empty:** Yes
- **Worktree clean:** Yes
- **T003B snapshot:** Present and checksums pass

## Renderer Module

- **Module:** `scripts/project_memory/render_docs.py`
- **Tests:** `tests/project_memory/test_render_docs.py`
- **Renderer name:** `project_memory_markdown_renderer`
- **Renderer version:** `project_memory_markdown_renderer.v1`

## CLI Contract

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

## Canonical Inputs

1. Tracked registry manifest and all 11 non-manifest registries
2. Project Memory schema and architecture version (1.0.0)
3. One explicitly selected generated snapshot package
4. Snapshot convergence findings
5. Snapshot source inventory and source hashes
6. Explicit invocation metadata (task ID, run ID, generated timestamp, mode)

## Snapshot Package Validation

- Validates all 11 required files exist
- Rejects unexpected files or subdirectories
- Parses and validates all JSON
- Verifies FILE-INVENTORY.txt completeness and sorting
- Verifies SHA256SUMS coverage and correctness
- Rejects traversal/absolute paths
- Validates authority_class is generated_evidence
- Rejects authoritative claims
- Validates 40-char lowercase Git SHA bound_commit
- Validates branch, task_id, run_id, generated_at presence
- Validates convergence result (PASS, PASS_WITH_FINDINGS, BLOCKED)
- Validates finding severity and code values

## Publication Mode Rules

- Clean tracked worktree required
- Empty staging area required
- Selected snapshot must be publication eligible
- Convergence must be PASS or PASS_WITH_FINDINGS
- No critical or publication-blocking finding
- Snapshot bound_commit must equal current HEAD
- Snapshot branch must equal current branch
- Output must be under .codex-context/project-memory/rendered/
- Refuses to overwrite existing run directory
- Stale snapshots rejected

## Historical-Preview Mode Rules

- Accepts valid stale snapshots
- Output marked `publication_eligible: false` (in build manifest)
- Freshness marked `historical`
- Historical preview banner on every page
- Explicit bound commit and target commit displayed
- Output must not be under publication root
- Refuses publication root output

## Exact Output Package

```text
<OUTPUT_ROOT>/
  <TASK_ID>/
    <RUN_ID>/
      build-manifest.json
      source-snapshot.json
      docs/
        index.md
        application-overview.md
        product-boundaries.md
        features.md
        capabilities.md
        current-roadmap.md
        remaining-work.md
        dependencies.md
        decisions.md
        assets.md
        evidence.md
        risks-and-open-questions.md
        convergence-findings.md
        technical-annex.md
      FILE-INVENTORY.txt
      SHA256SUMS
```

## Page Banner Contract

Every page begins with an HTML comment block and a rendered banner containing:
- `Generated evidence — not project authority`
- Renderer version
- Mode
- Source snapshot identity (task ID, run ID, branch, bound commit)
- Target identity (branch, commit)
- Generated timestamp
- Convergence result
- Freshness state
- Publication eligibility
- Unavailable source count
- Links to convergence-findings.md and technical-annex.md

Stale pages include: `Historical preview — this snapshot does not represent the current repository commit.`

## Status Fidelity Rules

- `planned` never presented as `implemented`
- `implemented` never presented as `validated` without evidence
- `validated` never implies `approved` or `canon`
- `candidate` presence never implies `approved`
- `owner_pending` never implies `accepted`
- `generated_evidence` never implies `authoritative`
- Unavailable sources never imply absent implementation
- Missing evidence never silently omitted
- Confidence never presented as truth

## Source Availability Behavior

- Repository-relative path safety validated
- Line ranges and JSON Pointers preserved
- Exact path displayed
- Availability checked against current checkout
- Authority context shown
- Unavailable sources prominently labeled

## Markdown Safety

- HTML-escaping of all raw text
- JavaScript link neutralization (`javascript:` prefix replaced)
- Control character removal
- Table separator escaping (`|` → `\|`)
- Backtick escaping in inline code
- Renderer-owned fixed headings and banner templates
- Line ending normalization (LF only)

## Build Manifest

`build-manifest.json` contains:
- Schema and architecture version
- Renderer name and version
- Authority class fixed to `generated_evidence`
- Mode, task ID, run ID, generated timestamp
- Exact command
- Repository and target identity
- Source snapshot identity and hashes
- Convergence result
- Finding counts by code and severity
- Unavailable source count
- Freshness state
- Publication eligibility
- Page count and navigation order
- Page hashes
- Registry hashes
- Exclusions, warnings, limitations
- `no_network`, `no_model`, `no_external_tool` declarations

## Source Snapshot Record

`source-snapshot.json` contains:
- Source snapshot identity and bound commit
- Branch, task ID, run ID, generated timestamp
- Authority class
- Publication eligibility and convergence result
- Freshness classification
- Registry file hashes
- Source hashes
- Findings summary
- Unavailable source count
- Limitations and target identity

## Deterministic and Atomic Output

- Identical inputs produce byte-identical output
- UTF-8 encoding with LF line endings
- Sorted JSON keys with stable indentation
- Stable record sorting (by type, then ID)
- Fixed 14-page navigation order
- No random identifiers or locale-dependent formatting
- Explicit timestamps only
- Temporary sibling build directory
- Atomic rename into final run directory
- Complete cleanup after failure
- No input mutation

## Test Results

- **Focused renderer tests:** 71 passed
- **Existing Project Memory tests:** 77 passed (unchanged)
- **Total Project Memory tests:** 148 passed
- **Test categories:** Input loading, snapshot package validation, freshness/mode, 14-page rendering, Markdown safety, manifest/package/checksums, CLI

## Historical Smoke Result

- **Path:** `/tmp/phase8-impl-026-t004b-render-smoke/PHASE8-IMPL-026-T004B/smoke-20260713T230207Z/`
- **Snapshot:** T003B (`a04b65cc42ba37fe1357272416828e49479cbce1`)
- **Target:** T004A HEAD (`4918051f0b3a6f65ebc13ae9b3648c8f12428cb1`)
- **Mode:** historical_preview
- **Freshness:** historical
- **Pages:** 14 generated
- **Checksums:** All pass
- **Missing sources:** 4 visible
- **Historical banner:** Present
- **Banner:** `Historical preview — this snapshot does not represent the current repository commit.`

## What Was Not Done

- No publication render created
- No MkDocs installation or site build
- No dependency changes
- No external tool use
- No registry, schema, scanner, or snapshot modification
- No generated output under `.codex-context/project-memory/rendered/`
- No commit, stage, or push

## T004 Status

- **T004:** In progress
- **T004A:** Complete/PASS-WITH-FINDINGS
- **T004B:** Complete/PASS
- **T004C:** Planned next

## Correction Note — T003B Finding Count (Documentation-Only)

The structured T003B convergence-findings.json (immutable snapshot) is the source of truth
for finding counts: **14 findings: 10 source_locator_invalid and 4 source_missing**.

Some older prose records (T003B decision log entry, Q151) incorrectly stated 11 invalid + 3
missing. The older 11/3 narrative grouping was inaccurate. The immutable T003B snapshot was
not changed. T004A repaired all 10 invalid locators. The four source_missing findings remain
expected cross-branch absences. Current tracked summaries now consistently state 10 + 4.

## Open Questions

- **Q151** — Full Plan Integrity classification model: Open
- **Q152** — Serena adoption criteria: Open
- **Q153** — Embedding-model selection: Open
- **Q154** — Operational synchronization cadence: Open (T004B's explicit freshness and render-mode rules do not resolve synchronization cadence)

## Unchanged State

- Application frontier: `PHASE8-IMPL-024-T003A`
- PHASE8-IMPL-025: `published/planned` and inactive

## Remaining Risks

- Competing renderer authority: Mitigated by fixed `generated_evidence` classification
- Hidden missing evidence: Mitigated by mandatory unavailable-source presentation
- Stale rendering: Mitigated by strict publication rejection and historical-preview labeling
- Markdown injection: Mitigated by escaping and renderer-owned templates
- Nondeterministic documentation: Mitigated by fixed inputs and hash validation
- Partial output: Mitigated by atomic build
- Stale memory: Remains active
- Branch synchronization inconsistency: Remains active
- Prompt injection in future retrieval: Remains active
- External-tool provenance: Unchanged
- Duplicate context systems: Unchanged
- Model-generated amendments: Unchanged
