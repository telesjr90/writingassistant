# PHASE8-IMPL-025-T006 — Full Subtxt Adapter Implementation Milestone and Pending Real-Runtime Completion

## Result

`IMPLEMENTATION_MILESTONE_ACCEPTED_REAL_RUNTIME_EXECUTION_PENDING`.

The T006 application-side adapter implementation and deterministic mocked
validation are accepted. Overall `PHASE8-IMPL-025-T006` remains open under the
2026-09-07 owner completion rule because no verified official/full Subtxt
runtime was available, no concrete production runner was connected, and no
real execution occurred through the current T002/T003 layered path.

This is not an adapter failure. It is a truthful incomplete external-runtime
integration state.

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
- T006J is this implementation-milestone and pending-runtime status record.

## Missing completion gate

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
- Future provisioning and live validation require separate current evidence
  and authorization as applicable.

Completion requires a verified concrete official runner, a T003-to-official-
Subtxt connection, and successful bounded real execution producing native
output and provenance through manifest/artifact/evidence-ledger,
normalization/guardrails/fusion, candidate persistence, and owner review where
applicable.

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

Overall T006 is active/open: implementation milestone accepted; real official
runtime connection and current-layer execution validation pending. T006 is the
immediate execution frontier for this lifecycle.

T007 remains planned/not begun and is not activated by the T006 adapter commit.
T008 remains planned/not begun, and T006D supplies only its bounded future
input seam. T004 separately retains an accepted implementation milestone with
a required real expanded BookNLP layered-validation debt before downstream
acceptance may rely on it.
