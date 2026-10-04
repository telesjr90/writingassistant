# PHASE8-IMPL-025 Inventory

## Parent

- ID: `PHASE8-IMPL-025`
- Title: Layered Analysis Architecture and Tool Integration Expansion
- Status: published/active
- Immediate implementation frontier: `PHASE8-IMPL-025-T012A` dependency/
  eligibility preflight. T009, T010, accepted T010H at
  `9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`, and T011 through T011H have local
  acceptance evidence. T012A implementation has not begun, and T012
  eligibility remains unasserted until the separate preflight verifies every
  recorded prerequisite.
- Activation dependency: satisfied by PHASE8-IMPL-024 fully complete/closed
  with application closeout validation PASS; Project Memory is
  paused/nonblocking and is not an activation gate
- Controlling decisions:
  `docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`
  and
  `docs/roadmap/decisions/PHASE8-IMPL-025-T001-tool-role-and-layered-orchestration-contract.md`
  and
  `docs/roadmap/decisions/2026-09-07-subtxt-optional-paid-integration-free-local-mvp-path.md`
  and
  `docs/roadmap/decisions/2026-09-08-dramatica-flow-analysis-only-reference-and-app-owned-rubric-mvp-boundary.md`
- Completed child: `PHASE8-IMPL-025-T001` (`complete/PASS`)
- Completed child: `PHASE8-IMPL-025-T002` (`complete/PASS`)
- Completed child: `PHASE8-IMPL-025-T003` (`complete/PASS`), implementation
  commit `95a406e3f97899d83c00ff1cdeb229ced1400cef`
- Completed child: `PHASE8-IMPL-025-T004` (`complete/PASS`), preserving
  implementation commit `ca2f99f35a7dc029a217954872ca7a5ab479ed2f`
  separately from accepted T004G real-runtime validation/fix commit
  `bc2a65e6350fdd65720606253b120d7fbcfa2b78`
- Completed child: `PHASE8-IMPL-025-T005` (`complete/PASS`), implementation
  commit `7e58e4859f828b3ca0edb886c999f5f376f151ac`
- Accepted/closed T006 optional paid-integration foundation: commit
  `23d4825da9a257180cdc0d1d1239ce13b4e01f78`; T006G remains
  `NOT_EXECUTED_RUNTIME_UNAVAILABLE`, and paid production-runner/current-layer
  real execution is deferred optional debt
- Completed child: `PHASE8-IMPL-025-T007` (`complete/PASS`), implementation
  commit `f843b615762192ca8f6865e76b2c4e4c9bcc2170`; deterministic and bounded
  real Ollama/qwen3:8b plus Story Check current-layer execution accepted
- Completed child: `PHASE8-IMPL-025-T008` (`complete/PASS`), implementation
  commit `2465722cedfe9f8dcb4135d8de124f36a999593f`; deterministic validation and
  BookNLP, Ollama/qwen3:8b, and Story Check current-layer evidence accepted
- T008 closeout:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T008-cross-adapter-semantic-guardrails-closeout.md`
- T002 closeout:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T002-source-identity-and-analysis-run-manifest.md`
- T005 contract/closeout:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T005-full-subtxt-runtime-inventory-and-contracts.md`
- T006 accepted-foundation/deferred-runtime record:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T006-full-subtxt-adapter-integration-and-validation.md`
- T001 supporting context pack:
  `.codex-context/PHASE8-IMPL-025/T001-tool-role-layered-orchestration/20260830T175126Z/`
  (generated/read-only supporting evidence, not authority or a tracked
  deliverable)

## Owner authorization

- Full Subtxt runtime implementation is authorized as optional paid work.
- Subtxt licensing and owner-authorization concerns are resolved.
- Historical owner-blocked/reference-only/licensing limitations are
  superseded only on that point.
- The app-owned `subtxt_informed_rubric` remains valid, complete/PASS,
  supplemental, deterministic, and distinct from official/full Subtxt.
- The required MVP path is free/local; no paid subscription, token, or
  official Subtxt API execution is required for MVP.
- The app-owned `dramatica_flow_informed_rubric` is the approved MVP boundary
  for wanted dramatica-flow-derived analysis concepts.
- External `dramatica_flow` is reference/provenance-only for MVP, is not
  MVP-required, requires no runtime proof, and is not authorized for
  implementation or execution.
- All analysis-only, no-prose, candidate-only, provenance, owner-review,
  promotion, apply-promotion, and Memory/Canon boundaries remain in force.

## Implemented foundation preserved

1. Real local spaCy extraction.
2. Real Ollama/qwen3:8b structured candidate extraction.
3. Real Story Check through the existing analysis engine/Ollama, with P0
   grounding repair complete/PASS.
4. Real BookNLP character/location findings and compatibility repair.
5. Explicit owner-selected NCP JSON candidate import validation.
6. App-owned Subtxt-informed and dramatica-flow-informed rubrics; the latter is
   the approved MVP boundary for wanted dramatica-flow-derived analysis and is
   not evidence of external runtime execution.
7. Deterministic fusion IDs/fingerprints, duplicate/conflict/uncertainty.
8. Candidate-only persistence.
9. Grouped owner review; T023A/T023B complete/PASS.
10. T003 immutable raw-artifact/evidence-ledger persistence, live-run control
    plane, and persisted-data compatibility.
11. T004 expanded BookNLP extraction and evidence mappings, with accepted
    T004G real-runtime retry validation.
12. T005 official/full Subtxt runtime inventory and fail-closed contracts.
13. T006 official/full Subtxt adapter, integration, mocked validation, and
    zero-available-runtime current-machine matrix.

These results establish accepted historical and implementation foundation;
T004G also establishes accepted current-layer BookNLP real-runtime validation.
A genuinely available official/full
Subtxt runtime and T006G live execution remain unavailable; T006 is nevertheless
accepted/closed as an optional paid-integration foundation without making the
adapter implementation a failure or claiming a runtime PASS.

## Layer inventory

| Layer | Target | Current classification |
| --- | --- | --- |
| 0 | Owner source identity, snapshot, hashes, offsets/maps | complete shared T002 contract |
| 1 | Raw spaCy, BookNLP, explicit NCP parsing, deterministic extraction | partial foundation |
| 2 | Immutable raw artifact/evidence ledger and run manifest | complete shared T002/T003 contracts and persistence |
| 3 | Ollama, Story Check, optional full Subtxt, app-owned rubrics, diagnostics | partial; T006 optional paid-integration foundation accepted/closed, paid official runtime deferred, project diagnostics missing |
| 4 | Exact grounding and semantic guardrails | complete shared T008 six-classification guardrail contract and exactly-once pre-fusion assessment |
| 5 | Fusion/conflict/uncertainty/provenance | implemented foundation; layered inputs not fully validated |
| 6 | Candidate persistence and expanded owner review | implemented foundation; correction lifecycle incomplete |
| 7 | Explicit promotion and approved context | existing isolated boundary; layered handoff validation incomplete |
| 8 | NCP import/export gateway and round-trip provenance | narrow import foundation only |

## Indexed workstreams

1. `PHASE8-IMPL-025-T001` — Tool-role and layered-orchestration contract
   (`complete/PASS`).
2. `PHASE8-IMPL-025-T002` — Source identity and AnalysisRunManifest
   (`complete/PASS`).
3. `PHASE8-IMPL-025-T003` — Immutable raw artifact and evidence ledger
   (`complete/PASS`).
4. `PHASE8-IMPL-025-T004` — BookNLP extraction expansion (`complete/PASS`;
   implementation commit `ca2f99f35a7dc029a217954872ca7a5ab479ed2f`;
   accepted T004G real-runtime validation/fix commit
   `bc2a65e6350fdd65720606253b120d7fbcfa2b78`).
5. `PHASE8-IMPL-025-T005` — Full Subtxt runtime inventory and contracts
   (`complete/PASS`).
6. `PHASE8-IMPL-025-T006` — Full Subtxt adapter, integration, and validation
   (accepted/closed optional paid-integration foundation; T006G
   `NOT_EXECUTED_RUNTIME_UNAVAILABLE`; T006K zero currently available official
   runtime surfaces; real paid execution deferred).
7. `PHASE8-IMPL-025-T007` — Evidence-bounded Ollama and Story Check
   (`complete/PASS`; implementation commit
   `f843b615762192ca8f6865e76b2c4e4c9bcc2170`; deterministic and bounded real
   current-layer Ollama/qwen3:8b and Story Check execution accepted).
8. `PHASE8-IMPL-025-T008` — Cross-adapter semantic guardrails
   (`complete/PASS`; implementation commit
   `2465722cedfe9f8dcb4135d8de124f36a999593f`; T008A-T008E satisfied;
   deterministic validation `458 passed, 7 warnings`; BookNLP,
   Ollama/qwen3:8b, and Story Check current-layer evidence accepted; optional
   Subtxt absence nonblocking; external `dramatica_flow` not executed and not
   required runtime proof).
9. `PHASE8-IMPL-025-T009` — Read-only project-level narrative diagnostics
   (`complete/PASS`; closeout commit
   `2b7515cfc17ba4194e4ab98af38f85b01473cb55`).
10. `PHASE8-IMPL-025-T010` — Full NCP gateway (`implemented`; commit
    `0622a21779c38cdea4738f8f30e63b71376a7ecb`; T010H owner UI complete/PASS
    at accepted implementation commit
    `9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`).
11. `PHASE8-IMPL-025-T011` — Candidate review lifecycle expansion
    (`complete/PASS` through accepted T011H implementation commit
    `66d3c587655161415e9508c2dfb1aa2e09f3d231`).
12. `PHASE8-IMPL-025-T012` — Layered end-to-end validation (`planned`; not
    begun; next lifecycle is T012A dependency/eligibility preflight).

Accepted bounded additions: T003F live-run API/control plane; T003G persisted-
data compatibility; T005H/T006K provisioning and current-machine runtime
compatibility; T010H NCP/diagnostics owner UI; T011H owner live-run workflow;
T012K layered integration deltas. PHASE8-IMPL-027 is the terminal gate.

T001-T005 and T007-T011 are locally accepted within their recorded scopes. T004 completion preserves its
implementation commit and the later accepted T004G real-runtime validation/fix
commit as distinct identities. T006 is accepted/closed as the optional
paid-integration foundation, with paid real execution deferred. T008 is
complete/PASS at
`2465722cedfe9f8dcb4135d8de124f36a999593f`. T011H is accepted at
`66d3c587655161415e9508c2dfb1aa2e09f3d231`. T010H is accepted/closed at
`9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`; T012 remains open. T012A is the
next dependency/eligibility preflight; its implementation has not begun and
must verify T003F, T003G, T009, T010, T010H at its accepted commit, T011, and
T011H from live repository evidence before T012 eligibility may be asserted.
Lettered bounded slices are defined in the parent task record.

## Dependencies

```text
PHASE8-IMPL-024 closeout + application validation PASS
  -> PHASE8-IMPL-025 -> T001 -> T002 -> T003
  -> required branches [T004] + [T007] -> T008
  -> optional branch [T005 -> T006] may feed T008 when available
  -> [T009] + [T010] + [T011]
  -> T012 -> PHASE8-IMPL-027
```

T007 consumed PHASE8-IMPL-024-T002's completed Story Check grounding work
without duplicating it; T007E accepted current-layer real Ollama/qwen3:8b and
Story Check execution through the T002/T003 layered path. T010H is
accepted/closed at `9376ddd379e8cb9addac00b3aa691c7c82fe1bf2` after accepted
T009 and T010 backend work; T011H is accepted. T012 reuses
PHASE8-IMPL-024-T008 and adds only layered deltas after its dependency gate.
T012I apply-promotion
validation remains isolated. T007 is complete/PASS. The T004/T004G
contributor branch was satisfied before T008 at accepted T004G closeout HEAD
`bc2a65e6350fdd65720606253b120d7fbcfa2b78`. T008 is complete/PASS; its
completion satisfied the dependency of T009/T010/T011; those workstreams now
have local acceptance evidence. Optional
official Subtxt output may participate in future applicable work when
configured and available, but its absence did not block T008 or MVP acceptance.
The app-owned `dramatica_flow_informed_rubric` participates
within its accepted internal scope; external `dramatica_flow` is not part of
the T007/T008/T012/PHASE8-IMPL-027 execution or proof path.

## Open technical questions

- Optional provisioning of a genuinely available verified official/full
  Subtxt callable interface and its evidenced source granularity.
- Optional Subtxt runtime/interface/version/provider/model provenance where a
  future available runtime reports it.
- NCP schema/mapping versions and trusted round-trip rules.
- Project-level diagnostic context contract.
- Owner correction and merge/split lifecycle.

Subtxt authorization/licensing and external `dramatica_flow` MVP classification
are not open questions. Historical T020B remains unchanged; the 2026-09-08
owner decision resolves the later classification question.
Cross-adapter guardrail ordering is resolved by accepted T008: one pre-fusion
guardrail assessment followed by one deterministic fusion pass.

## Safety inventory

- Analysis-only and candidate-first.
- Evidence/provenance-backed and owner-controlled.
- No generated prose or prose transformation.
- No automatic truth, approval, promotion, or apply-promotion.
- No direct model/tool mutation of Memory/Canon.
- Raw artifacts are immutable support data, not canon/candidates/training data.
- External NCP status is source metadata, not local approval.
- Project-level diagnostics are read-only candidates, not settled state.
