# PHASE8-IMPL-025-T006 — Accepted Optional Paid-Integration Foundation

## Result

`ACCEPTED_OPTIONAL_PAID_INTEGRATION_FOUNDATION_REAL_PAID_RUNTIME_DEFERRED`.

The T006 application-side adapter implementation and deterministic mocked
validation are accepted. Under the later 2026-09-07 owner decision that makes
official Subtxt/Dramatica an optional paid integration, T006 is accepted/closed
as an optional-integration foundation. Paid real-runtime execution is deferred
and does not block the free/local MVP path.

This is not an adapter failure and is not a real-runtime PASS. It is a truthful
accepted foundation with optional external-runtime debt. Controlling
reconciliation:
`docs/roadmap/decisions/2026-09-07-subtxt-optional-paid-integration-free-local-mvp-path.md`.

## Accepted milestones

Accepted implementation commit:
`23d4825da9a257180cdc0d1d1239ce13b4e01f78`
(`feat(analysis): integrate official Subtxt adapter (T006)`).

- T005 contract milestone remains `complete/PASS` at
  `7e58e4859f828b3ca0edb886c999f5f376f151ac`.
- T006A-T006F and T006H-T006I provide the injected official-runtime adapter
  seam, normalized evidence-backed candidate conversion, T002/T003 lineage
  integration, a bounded future T008 guardrail input seam, deterministic and
  mocked validation, fail-closed runtime/output handling, candidate-only
  persistence validation, and grouped-review validation.
- T006K provides a truthful current-machine runtime matrix.
- T006J is this accepted-foundation and deferred optional-runtime status
  record.

## Deferred optional paid-runtime gate

- T006G: `NOT_EXECUTED_RUNTIME_UNAVAILABLE`.
- T006K records zero currently available verified official/full runtime
  surfaces on this machine.
- No verified callable official/full runtime was available. No real Subtxt,
  runtime, API, model, or external-service call occurred.
- `run_official_subtxt_adapter` invokes an injected `runner(...)` seam;
  production code does not supply a concrete official runtime runner.
- The T003 control plane does not currently supply the required normalized
  evidence to, or invoke, the T006 official adapter.
- Runtime/interface/version/provider/model fields remain unknown where current
  evidence does not establish them.
- Runtime absence was not converted into a fake success and is not a T006
  application-adapter failure.
- Future provisioning and live validation require separate authorization and
  current evidence as applicable. They are not MVP prerequisites.

Any future claim that the optional official integration is fully operational
requires a verified concrete official runner, a T003-to-official-Subtxt
connection, and successful bounded real execution producing native output and
provenance through manifest/artifact/evidence-ledger,
normalization/guardrails/fusion, candidate persistence, and owner review where
applicable. No such claim is made here.

## Identity and safety

`subtxt` is the official/full adapter with implementation kind
`official_external`. `subtxt_informed_rubric` is the separate app-owned OMI
adapter, and `app_owned_subtxt_informed_rubric` remains its separate internal
identity. The sole positive official operation is `analyze-subtxt`; there is
no silent app-owned fallback.

Outputs remain evidence-backed, candidate-only, pending, non-canon, and
owner-review-required. The adapter performs no prose generation or
transformation and no automatic truth selection, approval, promotion,
apply-promotion, or Memory/Canon mutation.

## Accepted T002/T003 integration code

The mocked application-side adapter path reuses T002/T003 source identity,
exact source snapshot and hash,
`AnalysisRunManifest`, canonical evidence-locator grounding, immutable raw
artifact storage, evidence ledger, and output/transformation/contributor
lineage. Exact native runtime output is retained as opaque bytes, separate from
the app-owned mapped output. Deterministic/idempotent persistence is validated.
The app-owned mapped output is not claimed to be the native official runtime
format. This accepted code does not prove that T003 currently invokes the
official adapter or that a real official runtime produced the persisted bytes.

## Validation

Accepted pre-commit validation:

- T006 adapter correction suite: 49 passed;
- T005 runtime/preflight: 193 passed;
- T002/T003/raw artifact: 211 passed;
- integration/orchestrator/persistence/grouped-review source: 312 passed;
- grouped-review Node test: 1 passed;
- final consolidated focused suite: 765 passed, with 7 existing Pydantic
  deprecation warnings; and
- `git diff --check`: PASS.

These results remain accepted regression and implementation-milestone
evidence. They are not official-runtime execution evidence.

## Current status and frontier

T006 is accepted/closed as the optional paid-integration foundation. T006G
remains `NOT_EXECUTED_RUNTIME_UNAVAILABLE`; paid runtime connection and
current-layer execution remain optional deferred work.

T007 remains planned/not begun, depends on completed/PASS T003, and is the next
dependency-eligible application frontier. T008 remains planned/not begun, and
T006D supplies its bounded optional-input seam when official Subtxt is
configured and available; absence of that optional output does not block T008.
T004 separately retains an accepted implementation milestone with a required
real expanded BookNLP layered-validation debt before downstream acceptance may
rely on it.
