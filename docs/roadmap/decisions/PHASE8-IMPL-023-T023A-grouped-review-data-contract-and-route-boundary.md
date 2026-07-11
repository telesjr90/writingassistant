# PHASE8-IMPL-023-T023A — Grouped Review Data Contract And Route Boundary

## Result

`PHASE8-IMPL-023-T023A = complete/PASS`.

The persisted T022 candidates are read authoritatively through
`GET /api/projects/{project_name}/omi`. The response already includes the
source ideas, complete candidate records, evidence, provenance, conflict and
uncertainty metadata needed by grouped review. No grouped-display backend
route is required.

`PATCH /api/projects/{project_name}/omi/candidates/{candidate_id}/decision`
is the authoritative owner-decision path. T023B must wait for its
server-confirmed response and then refresh OMI; optimistic approval state is
not authorized.

## Data Contract

`frontend/src/omiGroupedReview.js` is a pure, dependency-free data module. It
selects only the safe, explicit source idea's linked candidate IDs, includes
only `omi_tool_assisted_fused_analysis` records, preserves the complete
original record, and fails closed for malformed input. It groups by
`candidate_content.source_adapter`, counts secondary
`candidate_content.candidate_type` values, and sorts adapters, types, finding
IDs, and candidate IDs deterministically.

The normalized review candidate preserves candidate/source IDs, source
adapter/tool source, original finding and storage types, label/name/claim,
evidence/locator/provenance, support/confidence/uncertainty/conflict,
duplicate and related-finding metadata, raw/normalized finding IDs,
fingerprints, owner decision, review status, promotion status, and the
complete original record. It exposes static boundary metadata: queue presence
is not approval; support is not truth; candidate persistence and tool output
are not canon; and approval does not apply promotion.

## Route Boundary

Review-queue routes and `ReviewQueuePanel` are a separate review-queue
workflow. They must not be treated as the source of the 113 T022 OMI
candidates, and T023A creates no queue entries. Grouped review has no
promotion or apply-promotion action; those remain separate, explicit,
owner-confirmed, audited workflows.

## Child Sequence

```text
T023A — grouped-review data contract and route-boundary decision
T023B — grouped-review React UI and owner-decision integration
T023C — automated frontend/backend integration tests
T023D — manual browser and accessibility validation
T023  — closeout after T023A-T023D pass
```

## Validation

- `node --check frontend/src/omiGroupedReview.js` passed.
- `node --test frontend/tests/omiGroupedReview.test.mjs` passed.
- `npm --prefix frontend run build` passed (existing Vite chunk-size warning
  only).
- Focused backend/source regressions passed: `48 passed`.
- Read-only real-data validation derived 113 linked candidates across six
  adapters: spaCy 17, Ollama 6, Story Check 10, NCP 64, Subtxt-informed rubric
  7, dramatica-flow-informed rubric 9; 22 uncertain candidates, two conflict
  groups containing eight candidates, and 113 pending/unapproved candidates.

No backend route or code changed; no React UI, queue entry, owner-decision,
candidate/project, Memory/Canon, promotion/apply-promotion, live analysis,
browser, persistence, generated prose, dependency, stage, commit, or push
occurred.

## Frontier

```text
PHASE8-IMPL-023-T023A = complete/PASS
PHASE8-IMPL-023-T023  = in_progress
PHASE8-IMPL-023       = published/active
full MVP completion   = blocked
```

Next:

```text
PHASE8-IMPL-023-T023B
Grouped-review React UI and owner-decision integration
planned
```
