# PHASE8-IMPL-024-T008C Promotion Creation and Handoff Suite Closeout

## Decision

`PHASE8-IMPL-024-T008C - Promotion creation and handoff suite` is
**complete/PASS** under parent `PHASE8-IMPL-024-T008`. Its dependency on
complete/PASS `PHASE8-IMPL-024-T008B` was satisfied before execution.

The task was validation-led, exposed a bounded frontend product defect, received
explicit correction authorization, and closed after independent correction
validation and commit review. The accepted implementation commit is:

- Commit: `f8b8be5d37a28e182f18cacd719667db5884a969`
- Subject: `fix(ui): reconcile promotion audit presentation (T008C)`

## Accepted implementation and validation evidence

### Controlling final acceptance evidence

| Evidence | Path | SHA-256 |
|---|---|---|
| Final validation archive | `/tmp/PHASE8-IMPL-024-T008C-opencode-validation-20260731T013447Z.tar.gz` | `0cd09a08358c522f49e6eeb2f852db2b74316e7c92d24ebe23edbc5f9e341d41` |
| Pre-cleanup archive | `/tmp/PHASE8-IMPL-024-T008C-opencode-validation-20260731T013447Z-pre-cleanup.tar.gz` | `b02ad57f32a6d0ffa9dd7ac1c3a9af726ef5fbd9a92622628b523a1ca742a827` |
| Commit evidence archive | `/tmp/PHASE8-IMPL-024-T008C-commit-20260731T023409Z.tar.gz` | `c24c35b2bda11b0fa1c05cc0527e3818ddaf17af679dd43f25afbf5d71939c3c` |
| Implementation commit | `f8b8be5d37a28e182f18cacd719667db5884a969` | `fix(ui): reconcile promotion audit presentation (T008C)` |

Internal final manifest: 520 entries verified. Internal commit manifest: 71
entries verified.

### Historical validation and correction evidence (supporting, not controlling)

| Evidence | Path | SHA-256 |
|---|---|---|
| Initial runtime archive | `/tmp/PHASE8-IMPL-024-T008C-promotion-runtime-20260730T034020Z.tar.gz` | `5a696b9e2f82ba2ca53a44990a21fbf2631ec9f0da47de1c77e6592c89e5ad9c` |
| Initial pre-cleanup archive | `/tmp/PHASE8-IMPL-024-T008C-promotion-runtime-20260730T034020Z-pre-cleanup.tar.gz` | `9ff0a358ce8a936c0fbb20b4e6c82125a325275a711d937ea1cec005662cb89c` |
| Codex correction archive | `/tmp/PHASE8-IMPL-024-T008C-correction-20260731T010226Z.tar.gz` | `eb97cc475c19f60177614f916905a1b95ab0e8d853458eea69f64802da2bd88f` |
| Codex pre-cleanup archive | `/tmp/PHASE8-IMPL-024-T008C-correction-20260731T010226Z-pre-cleanup.tar.gz` | `459a3a15fc22497b6e60718ae13472e074a80104f8031b8cf475e4fa75469040` |

The initial runtime validation correctly returned `PRODUCT_DEFECT` — promotion
creation and persistence worked, but the frontend presented canonical evidence,
provenance, and promotion-audit association falsely. The Codex correction run
produced useful supporting evidence, but its execution environment had LeanCTX
active and was therefore not used as the controlling acceptance run. The
independent OpenCode validation above is the controlling final acceptance
evidence.

### Accepted deterministic validation

| Suite | Result |
|---|---|
| Focused promotion-audit presentation source tests | 11 passed |
| Existing grouped-review/navigation source contracts | 23 passed |
| Workspace boundary selection | 3 passed, 380 deselected |
| Backend promotion contracts | 27 passed, 83 deselected |
| Frontend production build | PASS, 200 modules transformed, existing chunk-size advisory only |
| `git diff --check` | PASS |

## Accepted behavior

The real route-backed workflow verified:

- explicit owner-controlled promotion creation;
- required candidate approval and final confirmation;
- fail-closed invalid requests;
- successful promotion record persistence;
- evidence and provenance preservation;
- owner-decision audit metadata;
- timestamps;
- candidate-to-promotion lineage;
- complete source snapshot;
- promotion status `ready_for_manual_application`;
- no optimistic promotion presentation;
- successful POST followed by authoritative OMI refresh;
- editor promotion audit presentation;
- dashboard promotion audit presentation;
- Candidate Detail association by exact `promotion.candidate_id`;
- zero, one, or multiple associated records supported;
- unrelated candidates do not display another candidate's promotion record;
- structured canonical evidence and provenance remain reviewable.

The independently validated dashboard fixture:

```text
Candidates: 2
Evidence Linked: 1 / 2
Provenance Linked: 2 / 2
Promotion Audit Records: 1
Promotion Handoff Readiness: 0
Status: Not Ready
```

The unrelated candidate truthfully received normalized owner-input provenance
from the backend, so `2 / 2` was correct.

## Frontend correction

### Original defect

Canonical candidate evidence and provenance were persisted on the backend but
presented as missing in the frontend. The separate authoritative promotion
collection was not associated with Candidate Detail. Dashboard and Candidate
Detail could therefore present false audit readiness information.

### Accepted correction

- canonical `candidate.evidence` and `candidate.provenance` are first-class
  presentation inputs;
- legacy fields remain fallbacks;
- empty arrays and objects fail closed;
- structured values are rendered deterministically;
- dashboard evidence and provenance counts are independent;
- `omiData.promotions` is passed to Candidate Detail;
- records are associated using exact candidate lineage;
- the audit presentation remains candidate-side and not applied to
  Memory/Canon.

Backend persistence was not changed. Handoff-ready semantics were not changed.

Commited paths:

```text
frontend/src/components/OMICandidateDetail.jsx
frontend/src/components/OMIDashboard.jsx
frontend/src/components/OMIPromotionReadinessChecklist.jsx
frontend/src/components/OMIShell.jsx
tests/test_frontend_omi_promotion_audit_presentation_source.py
```

## Mutation isolation

- disposable project prefix `uiux-audit-t008c-`;
- final accepted disposable project `uiux-audit-t008c-20260731t015400z`;
- candidate remained byte-identical through promotion creation;
- successful promotion creation changed only:
  - `omi/index.json`;
  - the new `omi/promotions/{promotion_id}.json`;
- zero unexpected project mutations;
- pre-existing projects remained byte-identical;
- bounded cleanup restored API and filesystem baselines;
- task-owned processes stopped;
- ports 8000 and 5173 were released.

## Product boundaries

Zero:

- `apply-promotion` requests;
- `review-queue` mutation commands;
- model/runtime calls;
- Memory/Canon mutations.

Promotion creation is audit/candidate-side state. It does not apply promotion.
It does not mutate approved Memory or Canon. It does not make a candidate or
promotion record canon. It does not generate story prose. It does not invoke
live analysis runtimes.

## Historical blockers and superseded evidence

1. The initial runtime validation returned `PRODUCT_DEFECT` because dashboard
   and Candidate Detail presentation did not consume canonical
   evidence/provenance or the separate promotion collection truthfully.
2. The bounded frontend correction fixed that defect.
3. The Codex correction run produced useful supporting evidence, but its
   execution environment had LeanCTX active and therefore was not used as the
   controlling acceptance run.
4. The independent OpenCode validation ran without prohibited context processes
   and is the controlling final acceptance evidence.
5. Temporary browser-runner selector or navigation retries were
   validation-runner issues, did not alter repository files, and did not conceal
   a product defect.

LeanCTX did not change application behavior or repository content.

## Known nonblocking finding

No explicit idempotency key or same-candidate duplicate-promotion guard was
found in the current promotion-creation boundary.

No duplicate behavior was silently invented. No change was authorized under
T008C. The finding is preserved for a future owner decision. It does not alter
T008C's accepted promotion-creation and handoff scope.

No new roadmap task or open question is created by this finding.

## Remaining scope

T008C did not implement or validate:

- apply-promotion execution;
- approved Memory/Canon mutation;
- review-queue owner commands;
- T008F resilience and full accessibility scope;
- broad MVP acceptance.

```text
T008D:
apply-promotion suite

T008E:
review-queue command suite

T008F:
non-mutating resilience and accessibility suite
```

## Frontier transition

```text
PHASE8-IMPL-024-T008:
remains active/in_progress

PHASE8-IMPL-024-T008C:
complete/PASS

PHASE8-IMPL-024-T008D:
planned
dependency on complete/PASS T008C satisfied
eligible
immediate application frontier
not begun

PHASE8-IMPL-024-T008E:
planned
depends on T008D
not begun

PHASE8-IMPL-024-T008F:
planned
depends on T008E
not begun

PHASE8-IMPL-025:
remains inactive until PHASE8-IMPL-024 fully closes and application closeout
validation passes

Project Memory:
preserved, paused, nonblocking
```

T008D is not marked active or begun.
