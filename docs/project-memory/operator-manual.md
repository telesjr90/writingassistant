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

An ordinary mid-task application commit is not task acceptance. While the same
eligible application task remains active and the frontier, implementation
supervision may classify exact ancestor-commit lag as
`project_memory_commit_lag_application_only` when every intervening path is
bounded application code or a directly related test and all live authority,
routing, dependency, frontier, safety, and Plan Integrity checks still pass.
That state is `READY_WITH_ADVISORIES`, never `FRESH`, and does not run a full
refresh. Full refresh remains mandatory at strict baseline, task closeout, and
governance boundaries.

## Supervision gate profiles

The repository-owned, standard-library entry point is:

```bash
python3 scripts/project_memory/supervise.py --mode implementation --repo-root . --task-id PHASE8-IMPL-024-T003B
python3 scripts/project_memory/supervise.py --mode closeout --repo-root . --task-id PHASE8-IMPL-024-T003B
python3 scripts/project_memory/supervise.py --mode governance --repo-root . --task-id PHASE8-IMPL-026-T011
```

Implementation mode is the fast application gate. It preserves normal task,
dependency, frontier, routing, product-safety, changed-path, and validation
checks but permits only the bounded commit-lag advisory above. A control-plane,
authority, task, dependency, frontier, workflow, Project Instructions, shared
skill/agent, schema, registry, routing, or Project Memory protocol change is
blocking.

Closeout mode requires explicitly synchronized complete task state, expected
frontier advancement, supplied passing task-test evidence, zero Plan Integrity
blockers, and exact-commit `FRESH` packages. Governance mode requires the same
strict freshness plus registry, current-truth, routing, agent, reviewer, and
operational-policy validation. Neither mode edits tracked state or claims
acceptance.

Every run writes an atomic checksum-verified generated-evidence package under
`.codex-context/project-memory/handoff/<task>/<sha>/<mode>/`. The core has no
network dependency. GitHub publication is a separate workflow layer.

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

CI runs on relevant pull requests, pushes, and manual dispatch. Implementation
is the default; manual dispatch may select implementation, closeout, or
governance. The checksum-verified handoff is uploaded as a workflow artifact
and its Markdown is appended to the step summary. Same-repository pull requests
receive one updated stable-marker comment. Comment-permission failure is
advisory; the gate result remains visible. CI output is generated evidence
only. It is never committed, pushed, accepted automatically, or treated as
publication authority.

The copy-ready ChatGPT/GitHub operating contract is maintained in
`docs/project-memory/chatgpt-github-supervision-policy.md`. Project Sources are
a fallback/bootstrap mechanism, not commit-by-commit replication.

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
