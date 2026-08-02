# PHASE8-IMPL-024-T008D Apply-promotion Suite Closeout

## Decision

`PHASE8-IMPL-024-T008D - Apply-promotion suite` is complete/PASS.

T008D is a child of the active `PHASE8-IMPL-024-T008` validation workstream
under `PHASE8-IMPL-024`. Its direct dependency,
`PHASE8-IMPL-024-T008C`, is complete/PASS. This closeout satisfies the direct
dependency for `PHASE8-IMPL-024-T008E` without beginning T008E.

This decision does not complete T008 or PHASE8-IMPL-024. T008E remains
planned, eligible, and not begun as the immediate application frontier. T008F
remains dependency-gated behind T008E. PHASE8-IMPL-025 remains inactive until
PHASE8-IMPL-024 is fully complete/closed and its required application closeout
validation passes. Broad owner acceptance and MVP readiness remain blocked.

## Implementation Binding

- Commit: `bc93fcedd6e4609ce3e695b2706be4cc7682a6b0`
- Subject: `feat(app): implement apply-promotion suite (T008D)`
- Parent: `65330c78282db1e43bcd7ef71c17e41d3fa60ec6`
- Reviewed implementation patch SHA-256: `08f96fe2c0dbe4469dd386a606b5c8e70ca02fa8ab47f8cbcf7d7dd22ee2f578`
- Committed path count: 22

The implementation commit contains exactly these paths:

1. `backend/main.py`
2. `backend/routes/apply_promotion.py`
3. `backend/story_knowledge/apply_contract.py`
4. `backend/story_knowledge/apply_promotion.py`
5. `backend/story_knowledge/approved_records.py`
6. `backend/story_knowledge/owner_identity.py`
7. `backend/story_knowledge/promotion_apply_events.py`
8. `backend/story_knowledge/promotion_apply_runtime.py`
9. `frontend/src/api.js`
10. `frontend/src/components/ApplyPromotionConfirmation.jsx`
11. `frontend/src/components/OMIApplyPromotionBlockers.jsx`
12. `frontend/src/components/OMIApplyPromotionRoute.jsx`
13. `frontend/src/components/OMIShell.jsx`
14. `frontend/src/styles.css`
15. `frontend/tests/omiApplyPromotion.test.mjs`
16. `scripts/t008d-apply-promotion-browser-smoke.mjs`
17. `tests/test_apply_promotion_memory_canon_safety_regression.py`
18. `tests/test_frontend_apply_promotion_workflow_source.py`
19. `tests/test_frontend_omi_grouped_review_ui_source.py`
20. `tests/test_omi_apply_contract_persistence.py`
21. `tests/test_omi_apply_event_storage.py`
22. `tests/test_omi_apply_promotion_routes.py`

No package manifest, lockfile, roadmap file, dataset, model, training artifact,
or project data was included in the implementation commit.

## Accepted Contract and Safety Boundaries

The accepted contract archive is
`/tmp/PHASE8-IMPL-024-T008D-contract-decision-event-recovery-revision-20260801T021854Z.tar.gz`
with SHA-256
`f1f982e021c10bba1825491a6c2071e79fa61dcae2a69242dc9125391cffc8cc`.

The completed implementation remains analysis-only, candidate-first,
evidence- and provenance-backed, and owner-controlled. It supports explicit
`create` and `update` operations only; operation type is never inferred and no
promotion or apply-promotion occurs automatically. It does not generate story
prose or automatically mutate approved Memory or Canon.

Successful final apply adds or replaces only the explicitly owner-approved
destination record and appends the accepted intent, completion, or recovery
audit events.
Final apply does not mutate candidates, promotions, the OMI index, owner
configuration, contracts, preparations, revisions, or unrelated approved
records. The owner identity is server-authoritative from the local owner
configuration, and the API exposes no owner-configuration mutation route.

## Backend Implementation

The backend now provides strict bounded canonical JSON handling, duplicate-key
and invalid-number rejection, invalid-surrogate rejection, deterministic
hashing, closed destination-specific `approved_record.v1` schemas, explicit
create/update version rules, and complete approved-record hash and size
binding. It persists immutable preparations and numbered revisions while
retaining exact canonical revision bytes.

Promotion audit storage uses deterministic contiguous v2 events with bounded
full-chain replay and corruption/collision blocking. Runtime controls provide
the required single-process/single-worker lease, project-scoped reader/writer
coordination, nonblocking kernel locking, zero-write GET behavior, and a
boot-scoped, single-use, 120-second final-challenge registry. Final apply uses
the closed reference-only request, authoritative reload and revalidation,
before-state validation, structured duplicate/dependency decisions, one atomic
approved-record replacement, deterministic completion/recovery handling, and
at most one completed apply per promotion lineage. Legacy audit reads remain
read-only.

## Frontend Implementation

The frontend now requires exact promotion selection with no first-item
fallback, displays authoritative owner identity, exposes explicit create/update
selection and typed destination fields, and collects structured duplicate and
dependency decisions. It retains owner-entered preparation values, supports
bounded dependency-entry add/remove controls, and blocks incomplete or
semantically inconsistent dependency records with visible, keyboard-accessible,
screen-reader-associated explanations.

The final flow explicitly requests the anti-replay challenge, presents expiry,
replacement, and restart states, requires the live final-confirmation control,
and submits the accepted reference-only final request. Success and recovery
states trigger authoritative refresh. The flow preserves candidate-only and
non-prose boundaries, keyboard semantics, and responsive containment.

## Test-only Correction

The final validation included a test-only correction in
`tests/test_apply_promotion_memory_canon_safety_regression.py`. Stale
`owner_confirmation` and obsolete React-symbol assertions were replaced with
assertions for the accepted eight-field reference-only final request, its
`final_confirmation` binding, and the live explicit-confirmation blocker.
Candidate-only positive-copy checks now compare normalized lowercase source
text while the forbidden-control assertions remain intact. No backend or
frontend product behavior changed in that correction.

## Accepted Validation

- Focused backend suite: 272 passed.
- Apply-promotion safety regression: 32 passed.
- Focused frontend Python suite: 47 passed.
- Frontend Node protocol/state suite: 1 passed.
- Frontend production build: PASS.
- `git diff --check`: PASS.

The accepted final validation command set was:

- `/home/tjrpirateking/projects/WritingAssistantApplication/.venv-unsloth-clean/bin/python -m pytest -q tests/test_apply_promotion_memory_canon_safety_regression.py`
- `python3 -m pytest -q tests/test_writer_assistant_core_apply_promotion_contract.py tests/test_omi_routes.py tests/test_omi_boundaries.py tests/test_project_manager.py tests/test_omi_apply_contract_persistence.py tests/test_omi_apply_event_storage.py tests/test_omi_apply_promotion_routes.py`
- `python3 -m pytest -q tests/test_frontend_apply_promotion_workflow_source.py tests/test_frontend_omi_grouped_review_ui_source.py tests/test_frontend_omi_promotion_audit_presentation_source.py`
- `node --test frontend/tests/omiApplyPromotion.test.mjs`
- `cd frontend && npm run build`
- `git diff --check`

The disposable browser/runtime validation passed create, update, structured
blocked dependency, completed replay, zero-write GET behavior, event-chain
integrity, mutation isolation, keyboard reachability, responsive containment,
browser error-state handling, cleanup, and clear-port checks. No application
test, build, server, browser, or runtime scenario was rerun for this
documentation closeout.

## Runtime, Event-chain, and Mutation-isolation Evidence

The accepted runtime archive is
`/tmp/PHASE8-IMPL-024-T008D-codex-conversation-loop/phases/phase-9/runtime-evidence-resume-6.tar.gz`
with SHA-256
`de4b660dcf0d11c952d35af535eda683ec789f630c7f369d045f7cbfab60a970`.

Runtime evidence records six-event create and update chains and a two-event
blocked-draft chain with no blocked final apply. Chain sequences, filenames,
event IDs, content hashes, previous-document hashes, replay, and lookup passed.
Mutation-isolation evidence shows only the explicitly approved destination
record added or replaced, surrounded by append-only intent/completion events;
protected candidates, promotions, OMI index, owner configuration, contracts,
preparations, revisions, and unrelated approved records remained unchanged.

## Review Evidence

- Supervisor diff-review archive:
  `/tmp/PHASE8-IMPL-024-T008D-supervisor-diff-review-20260802T190239Z.tar.gz`
- Supervisor diff-review archive SHA-256:
  `24a8368dab0419d74386c33aaf36930268af6c9405d1aea65e8492df81d4fd55`
- Commit-review archive:
  `/tmp/PHASE8-IMPL-024-T008D-commit-review-20260802T191634Z.tar.gz`
- Commit-review archive SHA-256:
  `2ef0afba383ab25f9f21cb4c1105ccec72d179c4207c1de82ac74a875359c23a`

The implementation commit ended with empty staging and a clean worktree. No
push occurred. No roadmap update was part of the implementation commit, and no
T008E, T008F, or PHASE8-IMPL-025 implementation began.

## Known Findings and Limitations

- The final challenge is anti-replay evidence, not authentication.
- The MVP runtime contract requires exactly one backend OS process and one ASGI
  worker.
- The commit evidence pack contains a nonblocking evidence-generation labeling
  issue. It does not affect implementation or commit hashes, validation, or
  product behavior and is not a product defect.

## Next Frontier

The exact next application frontier is
`PHASE8-IMPL-024-T008E - Review-queue command suite`. Its dependency on
complete/PASS T008D is satisfied; it is planned, eligible, and not begun. T008F
remains gated behind T008E. This decision does not authorize T008E execution.
