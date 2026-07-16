# Project Memory Operator Manual

## Purpose

This manual governs owner-controlled synchronization, deterministic refresh,
CI verification, publication acceptance, historical evidence retention, and
stale-state diagnosis. Project Memory remains analysis-only. Its packages are
generated evidence, never project authority.

## Owner-controlled synchronization

Synchronization is an explicit operator-controlled Git action outside the
T011 tooling. Synchronize only complete accepted commits from clean worktrees.
Prefer a reviewed full merge from the application branch. A complete-commit
cherry-pick is permitted only when the owner selects the precise accepted
commit. Path-filtered cherry-picking, roadmap-only copying, reset, restore,
clean, stash, rebase, amend, force, and automatic push workflows are forbidden.

The operational CLI never merges, cherry-picks, commits, pushes, or changes
another worktree. It does not access the original application worktree.

## Event-driven cadence

Run a full deterministic refresh:

- after every accepted application-commit synchronization;
- after every completed Project Memory task;
- after any tracked Project Memory authority, registry, or tooling change;
- before a parent or phase closeout publication; and
- whenever stale-state diagnosis reports commit, source-hash, registry-hash,
  binding, semantic, authority, inventory, checksum, or quality drift.

Parent and phase checkpoints are additional publication gates, not substitutes
for per-sync refresh. There is no cron or time-based schedule. Time passage
alone does not stale a commit-bound publication; repository divergence does.

## Deterministic refresh

From a clean, non-detached `docs/project-memory-foundation` checkout at the
exact intended full commit, run:

```bash
python3 scripts/project_memory/operational_rollout.py refresh \
  --repo-root . \
  --output-root .codex-context/project-memory \
  --task-id PHASE8-IMPL-026-T011 \
  --expected-branch docs/project-memory-foundation \
  --expected-commit "$(git rev-parse HEAD)" \
  --json
```

The command builds, in order, the Plan Integrity report, snapshot, publication
render, semantic and authority validation, and quality package. Existing
builders remain responsible for their deterministic package contracts and
atomic finalization. Existing run directories are never overwritten or
deleted. A failed run is diagnostic evidence only and does not authorize
deletion or mutation of historical evidence.

`READY_WITH_ADVISORIES` is accepted only when every advisory is nonblocking,
evidence-backed, and on the configured allowlist. The only accepted advisory
code at T011 closeout is `source_missing`.

## Stale-state diagnosis

`status` and its `check` alias are read-only:

```bash
python3 scripts/project_memory/operational_rollout.py status \
  --repo-root . \
  --output-root .codex-context/project-memory \
  --task-id PHASE8-IMPL-026-T011 \
  --expected-branch docs/project-memory-foundation \
  --expected-commit "$(git rev-parse HEAD)" \
  --json
```

Explicit `--report-dir`, `--snapshot-dir`, `--render-dir`, and `--quality-dir`
select an accepted set. Without them, discovery is deterministic: the
lexicographically latest run directory containing the package's identifying
metadata file is selected. Exit code 0 means fresh, 2 means stale/rebuild
required, and 3 means malformed or blocked operational input.

A stale result is a diagnosis, not permission to overwrite evidence, mutate
roadmap or registries, or run destructive Git commands.

When the Project Memory parent is complete and closed, the authoritative
enrichment represents “no next Project Memory implementation task” with JSON
`null`, never an empty string. Plan Integrity accepts that state only when all
non-contingent children are complete; T006/T007 remain explicitly
owner-deferred, contingent, inactive, and unimplemented; T011 accepted evidence
and the Q154 owner decision exist; the roadmap closeout records converge;
ongoing work is explicitly the T011 operational procedure; and the application
frontier is validated independently. The current application frontier is
`PHASE8-IMPL-024-T003B`; advancing a valid application frontier does not reopen
Project Memory work. A missing or null next task while the Project Memory parent
is active, an eligible Project Memory child remains, or required evidence
conflicts is blocking.

## CI verification

`ci-check` requires an explicit temporary output root plus the expected branch
and full commit (arguments or trusted GitHub Actions environment variables).
It copies the exact clean tracked checkout into that temporary root, runs the
same deterministic refresh there, verifies inventories/checksums/bindings, and
confirms both the source and ephemeral checkouts remain clean. It does not
require local ignored evidence and does not write publication evidence into the
tracked checkout.

CI runs on relevant pull requests, relevant pushes to the Project Memory
branch, and manual dispatch. CI output is generated evidence only. It is not
uploaded, committed, accepted automatically, or treated as publication
authority.

## Publication acceptance

Deterministic PASS is necessary but not itself owner acceptance. Before
acceptance, verify exact branch/full-commit binding; Plan Integrity readiness;
current and publication-eligible snapshot state; page inventory; semantic and
authority PASS; quality PASS or accepted nonblocking findings; and complete
inventory/checksum coverage. The owner retains publication control.

## Historical evidence retention

Never overwrite or delete historical Project Memory packages during normal
refresh. Generated packages remain ignored and uncommitted. A later commit
makes an older package historical; it does not make that package authoritative
or disposable.

## Safety boundaries

Operational tooling performs no automatic Git, roadmap, registry,
Memory/Canon, candidate, promotion, apply-promotion, or story-prose mutation.
It invokes no reviewer, model, retrieval system, external context tool,
application runtime, or network service. Candidate, confidence, reviewer,
model, CI, and generated output never become truth through this workflow.
