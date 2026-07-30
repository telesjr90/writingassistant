# PHASE8-IMPL-024-T008B Candidate Lifecycle and Grouped-Review Owner-Decision Suite Closeout

## Decision

`PHASE8-IMPL-024-T008B - Candidate lifecycle and grouped-review
owner-decision suite` is **complete/PASS** under parent
`PHASE8-IMPL-024-T008`. Its dependency on complete/PASS
`PHASE8-IMPL-024-T008A` was satisfied before execution.

This closeout is validation-led with one narrow stale-test correction. The
correction changed no application behavior and was committed as:

- Commit: `81f6d7c3a5566ab5b2a9ffb8e30c5ed4bc275593`
- Subject: `test(ui): narrow grouped-review checksum guard (T008B)`

The correction keeps checksum protection for the pure grouped-review helper and
its focused unit test while removing stale historical whole-file hashes for
shared API and backend files. Route, wiring, lifecycle, and backend behavior
remain validated semantically.

## Accepted validation evidence

| Evidence | Path | SHA-256 |
|---|---|---|
| Final runtime archive | `/tmp/PHASE8-IMPL-024-T008B-owner-runtime-20260729T224916Z.tar.gz` | `66f7a42ea64361f5a76f4ca56eef22ca24b90791f8d514ced1d18ab1732cfe2a` |
| Pre-cleanup archive | `/tmp/PHASE8-IMPL-024-T008B-owner-runtime-20260729T224916Z-pre-cleanup.tar.gz` | `72d824c54ff6a3f0bee3ceef0048e934f95286bc5e382ed7e433f49f8ab3ecad` |
| Disposable-project archive | Preserved inside the runtime evidence set | `21eec95193c78884ff644eaabb429f60f879081acf9c392bfe9076b0226c2317` |
| Correction verification archive | `/tmp/PHASE8-IMPL-024-T008B-stale-test-correction-verification-20260729T211817Z.tar.gz` | `0fd64afeeb8ee615836cab8a3f250087e0587021827757efa326408130c0f788` |

Accepted deterministic validation includes the Node syntax check, the focused
grouped-review Node test, the frontend production build, the corrected focused
source suite (`23 passed`), and the requested grouped-review/backend regression
suite (`133 passed`). The final runtime archive contains 111 internally
verified checksum entries.

## Accepted behavior

The real frontend derived grouped-review data from one explicitly selected
source idea and grouped four linked tool-assisted candidates deterministically
across two source adapters. The accepted run verified four pending candidates,
two uncertain candidates, one conflict group, deterministic adapter and
candidate ordering, and the search, adapter, review-state, uncertainty, and
conflict filter checks.

The grouped-review surface presented evidence, source locators, provenance,
confidence/support as support rather than truth, uncertainty, conflict
metadata, fingerprints, lifecycle state, owner-decision state, and stored
review state. It preserved the visible boundaries that queue presence is not
approval, candidate persistence and tool output are not canon, approval does
not apply promotion, and Memory/Canon remains unchanged.

Owner-decision mutation waited for the server-confirmed candidate PATCH and an
authoritative OMI refresh. The UI did not update lifecycle state optimistically.
Approval remained disabled until explicit owner confirmation. The accepted run
exercised and persisted all seven legal transitions:

1. `candidate -> owner_review`;
2. `owner_review -> approved`;
3. `approved -> owner_review`;
4. `owner_review -> rejected`;
5. `rejected -> owner_review`;
6. `owner_review -> candidate` through `needs_revision`; and
7. `candidate -> archived`.

Archived candidates exposed no enabled owner-decision action. Approval stored
`decision: approve`, `approval_confirmed: true`, `decided_by: owner`, and
`status: approved`, but promotion eligibility remained false. No promotion
record or apply-promotion request was created.

All six negative cases failed closed with HTTP 400 or 404 and byte-identical
candidate persistence: approval without confirmation, unsupported decision,
invalid lifecycle transition, reserved `promoted` status, blocked
`scene_prose` destination, and unknown candidate ID.

## Mutation isolation

The submitting run used only disposable project
`uiux-audit-t008b-validation-submit-1`. All writes were confined to that
project. The evidence recorded 19 authorized mutation requests and zero
forbidden mutation requests.

Every pre-existing project file and protected path remained byte- and
metadata-identical. Pre-cleanup evidence preserved the complete disposable OMI
state and project archive. Exact cleanup restored the initial API project list,
complete filesystem manifest, and protected-path manifest. All task-owned
backend, frontend, browser, and helper processes ended, and ports 8000 and 5173
were free.

## Product boundaries

T008B did not generate story prose; run a model, Ollama, Story Check,
extraction, BookNLP, spaCy, NCP, Subtxt, dramatica-flow, or another analysis
runtime; create a promotion record; apply promotion; invoke a review-queue
action; mutate Memory/Canon, Bible, storyform, scenes, chapters, notes,
materials, or other protected owner content; or modify datasets, training
files, model artifacts, or fine-tuning configuration.

Candidate persistence remains non-canon. Approval in this suite is a
review-lifecycle decision only and does not apply promotion or mutate approved
truth.

## Historical blockers

Initial focused validation exposed a stale historical whole-file checksum
assertion. It was classified as a stale test baseline rather than a product
defect. The accepted correction narrowed the checksum guard to the pure
grouped-review contract files without weakening semantic route, wiring,
lifecycle, or backend validation.

The first runtime attempt was blocked by a network-isolated Codex execution
sandbox. The accepted runtime validation ran in normal local WSL with loopback
socket permissions. Neither blocker changed application behavior or weakened
the expected validation contract.

## Remaining scope

T008B does not validate or implement promotion creation and handoff,
apply-promotion, approved Memory/Canon mutation, review-queue owner commands,
or the remaining resilience, accessibility, and final-acceptance coverage.
Those obligations remain with T008C through T008F. In particular, T008E owns
the review-queue command suite and T008F owns the non-mutating resilience and
accessibility suite.

## Frontier transition

`PHASE8-IMPL-024-T008` remains `active/in_progress`.

The next task is:

```text
PHASE8-IMPL-024-T008C
Promotion creation and handoff suite
planned; dependency on complete/PASS T008B satisfied; eligible; immediate application frontier; not begun
```

T008C is activated but not begun. T008D depends on T008C, T008E depends on
T008D, and T008F depends on T008E. `PHASE8-IMPL-025` remains inactive until
`PHASE8-IMPL-024` is fully complete/closed and application closeout validation
passes.

Project Memory remains preserved, paused, and nonblocking for application
implementation, validation, acceptance, and closeout.
