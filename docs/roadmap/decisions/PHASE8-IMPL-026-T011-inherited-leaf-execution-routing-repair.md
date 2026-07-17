# PHASE8-IMPL-026-T011 Operational Maintenance Event — Inherited-Leaf Execution-Routing Repair

## Result

Accepted/complete as PASS. This is one owner-authorized, bounded post-closeout
operational-maintenance event under the existing `PHASE8-IMPL-026-T011`
event-driven procedure. It is not a new roadmap child, does not reopen
`PHASE8-IMPL-026-T012`, and does not create a Project Memory implementation
frontier. The T012 routing decision remains the controlling current routing
policy.

## Starting authority and repository gate

- Repository: `/home/tjrpirateking/projects/WritingAssistantApplication`.
- Branch: `docs/opencode-go-routing-small-task-execution`.
- Starting HEAD: `2f7f4cf1e08fce46fa7dd1589448ca8d15cfa6b9`.
- Starting subject: `docs(governance): close T012 after fresh memory validation`.
- Starting worktree and staging: clean and empty.
- Starting divergence: `0 behind / 8 ahead`.
- Starting Project Memory: exact-commit `FRESH`.
- Starting Plan Integrity: `READY_WITH_ADVISORIES`, zero blockers, and the
  same four accepted nonblocking `source_missing` advisories.
- Application frontier: `PHASE8-IMPL-024-T003B`, planned, dependency-eligible,
  and unimplemented.
- `PHASE8-IMPL-025`: planned/inactive.
- T012: complete/PASS.

## Authoritative maintenance identity

The maintenance identity is the T011 operational procedure plus this accepted
decision, normalized as decision ID
`pmf-t011-inherited-leaf-execution-routing-repair` and owner-decision ID
`inherited-leaf-execution-routing-repair`.

T011 already requires an exact-commit deterministic refresh after tracked
Project Memory authority, registry, or tooling changes. T012 explicitly returns
later maintenance to T011 and states that there is no next Project Memory
implementation task. Creating `PHASE8-IMPL-026-T013` would therefore add a new
child where existing accepted authority already provides a legal maintenance
mechanism. No T013 task, dependency, inventory, enrichment, or roadmap-index
record is created.

## Reproduced defect

The standard command, without `--allow-inactive`, was:

```bash
python3 scripts/project_memory/execution_routing.py resolve PHASE8-IMPL-024-T003B --repo-root .
```

It exited `1` with `result: BLOCKED`, rule `ROUTING-012`, classification
`aggregate_or_owner_task_not_delegable`, and `offending_value: false`.

The selected route was the exact allowlisted inheritance contract at
`execution-routing.json#symbol=PHASE8-IMPL-024-T003`. The leaf roadmap task was
planned, depended only on complete/PASS T003A, and was the current application
frontier. The failure arose before lifecycle, dependency, and frontier checks.

## Root cause

`_resolve_record()` shallow-copied the complete parent aggregate record and
changed only the child task ID, inherited-parent marker, and copied source
locator. That copied the parent aggregate's correct
`delegation_eligible: false` value into the resolved leaf. The later standard
eligibility gate then applied `ROUTING-012` to the copied aggregate value.

The same defect affected the exact allowlisted T003C and T004/T005/T006 child
families. It was not specific to T003B and could not be repaired coherently by
adding a one-off explicit child route.

## Accepted inherited-leaf contract

1. The canonical routing registry and T012 decision remain current and
   authoritative for executor selection.
2. Inheritance requires one current parent record, enabled inheritance, exact
   child allowlisting, direct roadmap parentage, a leaf child, no unsafe
   owner-only boundary, and no conflicting explicit child contract.
3. A conflicting explicit child contract requires the parent's accepted
   override permission plus explicit enabled override metadata and rationale.
4. The inherited leaf receives execution class, model category, reasoning,
   risk, rationale, escalation conditions, owner-only status, applicability,
   capability tags, required skills, and the parent routing-record source
   locator.
5. Only after those inheritance checks does the resolved leaf receive
   `delegation_eligible: true`.
6. The standard resolver separately evaluates the child's own lifecycle,
   dependencies, current frontier, and delegated executor.
7. Inheritance-providing aggregate records and owner-only records remain
   nondelegable. `PHASE8-IMPL-024-T007B` remains `owner_decision` and cannot be
   delegated.
8. Missing, non-allowlisted, conflicting, stale, inapplicable, inactive,
   dependency-ineligible, non-frontier, and owner-only resolution continues to
   fail closed.

## Registry and schema disposition

No execution-routing registry metadata changes. The T003/T004/T005/T006
records already encode the accepted allowlists and correctly keep their
aggregate records nondelegable. The shared registry schema already represents
the required booleans and inheritance contract; no schema or manifest change
is needed.

## Scope and preserved boundaries

The tracked repair is limited to the routing resolver, systemic Project Memory
routing tests, this decision and its normalized decision records, and concise
governance synchronization. No backend, frontend, application test, project
data, dependency, runtime/model configuration, candidate, promotion,
apply-promotion, approved Memory/Canon, dataset/training artifact, or story
prose is changed. T003B remains unimplemented and the application frontier.
