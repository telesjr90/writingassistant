# PHASE8-IMPL-026-T011 — Synchronization, CI, Rebuild, and Operational Rollout

## Result

T011: **complete/PASS**. PHASE8-IMPL-026 closes as
**complete/PASS-WITH-FINDINGS**. The only accepted findings are the four known
nonblocking `source_missing` advisories, or fewer if their sources later become
available.

## Q154 decision: event-driven, commit-bound cadence

Q154 is resolved. Project Memory refresh is event-driven and commit-bound, not
time-based. Run a full deterministic refresh after every accepted application
commit synchronization; after every completed Project Memory task or tracked
Project Memory authority, registry, or tooling change; before parent or phase
closeout publication; and whenever stale detection reports commit, source-hash,
registry-hash, binding, semantic, authority, inventory, checksum, or quality
drift. Parent and phase checkpoints are additional publication gates, not
substitutes for per-sync refresh. No cron schedule is required. Time passage
alone does not make a commit-bound publication stale; repository divergence
does.

## Synchronization contract

Synchronize only complete accepted commits from clean worktrees. Prefer a
reviewed full merge from the application branch. A complete-commit cherry-pick
is permitted only when the owner selects the precise accepted commit.
Path-filtered cherry-picking, roadmap-only copying, reset, restore, clean,
stash, rebase, amend, force, and automatic push workflows remain forbidden.

Synchronization remains an explicit owner/operator-controlled Git action.
T011 tooling validates and rebuilds but does not merge, cherry-pick, commit,
push, mutate another worktree, or access the original application worktree.

## Operational system

- `docs/project-memory/operations.json` is the dependency-free machine-readable
  policy for triggers, clean-state gates, accepted readiness, stale reasons,
  checks, output roots, CI behavior, and mutation boundaries.
- `docs/project-memory/operator-manual.md` separates synchronization, refresh,
  CI verification, publication acceptance, evidence retention, and diagnosis.
- `scripts/project_memory/operational_rollout.py` exposes read-only
  `status`/`check`, clean-HEAD `refresh`, and detached-capable ephemeral
  `ci-check`.
- `scripts/project_memory/build_quality_package.py` encodes the accepted
  T004C2/T009/T010 four-file inventory/checksum quality-package structure.
- `scripts/project_memory/validate_operational_rollout.py` validates policy,
  manual, CLI, workflow, and safety contracts without dependencies.
- `.github/workflows/project-memory.yml` runs relevant pull-request, Project
  Memory branch push, and manual checks with no schedule.

`status` validates repository identity/state, selected or deterministically
discovered packages, inventories, checksums, bindings, source/registry hashes,
readiness, snapshot eligibility/currentness, semantic/authority results, and
quality. Stale output is diagnostic and grants no mutation permission.

`refresh` orchestrates the existing deterministic Plan Integrity, snapshot,
rendering, and semantic validators in order, then builds and verifies the
quality package. Every package is atomic and overwrite-refusing; historical
evidence is retained. `READY_WITH_ADVISORIES` is accepted only for nonblocking,
evidence-backed allowlisted advisories.

`ci-check` copies the exact clean tracked checkout into an explicit temporary
root, performs an ephemeral rebuild there, requires no pre-existing ignored
evidence, and verifies both source and ephemeral checkouts remain clean. CI
output stays generated evidence and is not uploaded, committed, or accepted as
publication authority.

The completed-parent “no next Project Memory implementation task” state uses
explicit JSON `null` in the enrichment record, not an empty string. Plan
Integrity treats the null declaration as evidence-backed only when the parent
is complete/closed, all required children are complete, T006/T007 retain their
owner-deferred contingent state, T011 closeout evidence and the Q154 owner
decision are current, tracked roadmap records converge on operational
maintenance, and `PHASE8-IMPL-024-T003A` remains the application frontier. Any
active/incomplete parent, eligible child, missing evidence, or roadmap conflict
keeps readiness blocked.

## Authority and safety

Generated packages remain `generated_evidence`. They cannot update roadmap,
registries, Memory/Canon, candidates, promotions, apply-promotion state, or
story prose and cannot become truth through confidence, reviewer, model, or CI
output. No reviewer, model, retrieval system, context tool, network call,
application runtime, synchronization action, or application-worktree access
was performed during T011 implementation.

## Closeout truth

- T006/T007 remain owner-deferred, contingent, planned, inactive, and
  unimplemented; T011 does not activate them.
- Q152/Q153 remain open. Q154 is resolved only by this operational decision.
- T008/T009/T010 remain complete/PASS.
- PHASE8-IMPL-026 is complete and closed as complete/PASS-WITH-FINDINGS.
- There is no next Project Memory implementation task. Ongoing maintenance is
  the operational procedure defined here, not a new roadmap child.
- The sole next implementation focus is `PHASE8-IMPL-024-T003A`.
- PHASE8-IMPL-025 remains published/planned and inactive.
