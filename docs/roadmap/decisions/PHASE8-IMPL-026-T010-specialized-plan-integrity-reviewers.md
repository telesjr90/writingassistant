# PHASE8-IMPL-026-T010 — Specialized Plan Integrity Reviewers

## Result

T010: **complete/PASS**.

T010 implements a repository-native, strictly read-only specialized-reviewer
contract for six bounded domains: backend contracts, frontend UI, test coverage,
roadmap consistency, enrichment accuracy, and decision coherence. No reviewer,
model, network service, external context tool, or application runtime was
invoked during implementation or testing.

## Delivered architecture

- `docs/project-memory/reviewer-protocol.md` defines the six domains, explicit
  request fields, source order, finding fields, fail-closed behavior, product
  boundaries, and relationship to deterministic Plan Integrity.
- `.agents/skills/project-memory-plan-integrity-review/SKILL.md` provides one
  shared bounded read-only review procedure without copying current truth.
- Six `.opencode/agents/project-memory-*-reviewer.md` definitions bind exactly
  one domain each to the shared protocol and skill.
- `scripts/project_memory/validate_reviewer_guidance.py` deterministically
  checks the guidance set, permissions, domains, and exact shell allowlist.
- `scripts/project_memory/reviewer_findings.py` validates supplied structured
  findings and normalizes evidence locators, authority, freshness, commit
  bindings, hashes, line ranges, stable IDs, and ordering. It performs no model
  call and writes no output file.
- The schema bundle defines reviewer domain, request, evidence-locator, finding,
  and normalized findings-package shapes.
- `tests/project_memory/test_plan_integrity_reviewers.py` uses temporary
  fixtures only and invokes no agent, model, network, retrieval tool, or
  external command.

## Request and finding controls

Every request supplies repository root, expected branch/full commit, reviewer
domain, bounded scope, maximum file scope, allowed source classes, protected
paths, accepted Plan Integrity report path, freshness rule, historical-evidence
permission, and owner-decision requirement. Current review requires matching
clean repository state and a current accepted T009 report with nonblocking
readiness.

Each proposed finding has a deterministic ID, domain, concern ID, title,
bounded claim, result/status, severity, blocking recommendation, affected IDs,
exact evidence locators, authority/freshness/commit metadata for every source,
separate facts and inferences, uncertainty/conflict reporting, owner-decision
status, deterministic follow-up, and an exact `generated_evidence` declaration.

Malformed, unsafe, external, missing, protected, out-of-scope, hash-mismatched,
stale, unbound, conflicting, unapproved, or owner-pending-required input fails
closed. Confidence-as-truth, authoritative/accepted/approved/canon claims, task
closure or activation, automatic roadmap/registry/Memory/Canon/promotion or
apply-promotion actions, semantic truth selection, and story-prose content are
rejected.

## Permissions and execution boundary

Every reviewer denies write, edit, patch, web/network fetch, external-directory
access, package installation, server startup, application/model execution,
nested agents, retrieval tools, Git mutation, roadmap/registry mutation,
Memory/Canon mutation, candidate promotion/apply-promotion, and story-prose
generation or modification. Shell is denied by default and allows only the six
read-only Git identity/state command patterns already accepted for T008 Ask.

Reviewers are definitions for a future explicit operator invocation. T010 does
not schedule, run, or operationalize them and does not select a synchronization
cadence.

## Relationship to T009

T009 remains the sole deterministic readiness authority. Reviewer output is
supporting `generated_evidence` only. It cannot override T009 comparisons,
change `READY`, `READY_WITH_ADVISORIES`, or `BLOCKED`, mutate an accepted report,
resolve conflicts, activate/reorder/complete/close tasks, infer semantic
duplication from similarity, or turn a recommendation into authoritative truth
or an owner decision.

## Validation

- Focused reviewer contracts: 48 passed.
- Related guidance, Plan Integrity, current-state, renderer, and semantic group:
  258 passed.
- Complete Project Memory suite: 428 passed.
- Python compilation, registry validation, Ask and reviewer guidance validation,
  JSON parsing, enrichment validation, roadmap validation, and diff checks: PASS.

## Preserved state

- T006/T007 remain owner-deferred, contingent, planned, inactive, and
  unimplemented.
- T008/T009 remain complete/PASS.
- T011 is the sole next Project Memory task, planned/inactive and unimplemented;
  Q154 remains open and no synchronization cadence is selected.
- Q152/Q153 remain open; Q151 remains resolved.
- The application frontier remains `PHASE8-IMPL-024-T003A`.
- PHASE8-IMPL-025 remains published/planned and inactive.
- Project Memory remains analysis-only, evidence-backed, and owner-controlled.
