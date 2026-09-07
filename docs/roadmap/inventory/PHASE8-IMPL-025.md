# PHASE8-IMPL-025 Inventory

## Parent

- ID: `PHASE8-IMPL-025`
- Title: Layered Analysis Architecture and Tool Integration Expansion
- Status: published/active
- Immediate implementation frontier: `PHASE8-IMPL-025-T006`
  (`active/open`; adapter milestone accepted; real official-runtime connection
  and current-layer execution pending)
- Activation dependency: satisfied by PHASE8-IMPL-024 fully complete/closed
  with application closeout validation PASS; Project Memory is
  paused/nonblocking and is not an activation gate
- Controlling decisions:
  `docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`
  and
  `docs/roadmap/decisions/PHASE8-IMPL-025-T001-tool-role-and-layered-orchestration-contract.md`
- Completed child: `PHASE8-IMPL-025-T001` (`complete/PASS`)
- Completed child: `PHASE8-IMPL-025-T002` (`complete/PASS`)
- Completed child: `PHASE8-IMPL-025-T003` (`complete/PASS`), implementation
  commit `95a406e3f97899d83c00ff1cdeb229ced1400cef`
- Accepted T004 implementation milestone: commit
  `ca2f99f35a7dc029a217954872ca7a5ab479ed2f`; overall real-tool completion
  remains open pending expanded BookNLP execution through T002/T003 artifacts,
  ledger, fusion, and candidates
- Completed child: `PHASE8-IMPL-025-T005` (`complete/PASS`), implementation
  commit `7e58e4859f828b3ca0edb886c999f5f376f151ac`
- Accepted T006 implementation milestone: commit
  `23d4825da9a257180cdc0d1d1239ce13b4e01f78`; overall T006 remains active/open
  pending a verified production official runner and current-layer real
  execution
- T002 closeout:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T002-source-identity-and-analysis-run-manifest.md`
- T005 contract/closeout:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T005-full-subtxt-runtime-inventory-and-contracts.md`
- T006 milestone/pending-runtime record:
  `docs/roadmap/decisions/PHASE8-IMPL-025-T006-full-subtxt-adapter-integration-and-validation.md`
- T001 supporting context pack:
  `.codex-context/PHASE8-IMPL-025/T001-tool-role-layered-orchestration/20260830T175126Z/`
  (generated/read-only supporting evidence, not authority or a tracked
  deliverable)

## Owner authorization

- Full Subtxt runtime implementation is authorized.
- Subtxt licensing and owner-authorization concerns are resolved.
- Historical owner-blocked/reference-only/licensing limitations are
  superseded only on that point.
- The app-owned `subtxt_informed_rubric` remains valid, complete/PASS,
  supplemental, deterministic, and distinct from official/full Subtxt.
- All analysis-only, no-prose, candidate-only, provenance, owner-review,
  promotion, apply-promotion, and Memory/Canon boundaries remain in force.

## Implemented foundation preserved

1. Real local spaCy extraction.
2. Real Ollama/qwen3:8b structured candidate extraction.
3. Real Story Check through the existing analysis engine/Ollama, with P0
   grounding repair complete/PASS.
4. Real BookNLP character/location findings and compatibility repair.
5. Explicit owner-selected NCP JSON candidate import validation.
6. App-owned Subtxt-informed and dramatica-flow-informed rubrics.
7. Deterministic fusion IDs/fingerprints, duplicate/conflict/uncertainty.
8. Candidate-only persistence.
9. Grouped owner review; T023A/T023B complete/PASS.
10. T003 immutable raw-artifact/evidence-ledger persistence, live-run control
    plane, and persisted-data compatibility.
11. T004 expanded BookNLP extraction and evidence mappings.
12. T005 official/full Subtxt runtime inventory and fail-closed contracts.
13. T006 official/full Subtxt adapter, integration, mocked validation, and
    zero-available-runtime current-machine matrix.

These results establish accepted historical and implementation foundation, not
current-layer real-execution completion. A genuinely available official/full
Subtxt runtime and T006G live execution remain unavailable; this keeps overall
T006 open without making the accepted adapter implementation a failure. T004's
expanded implementation likewise remains accepted while real layered
validation is pending.

## Layer inventory

| Layer | Target | Current classification |
| --- | --- | --- |
| 0 | Owner source identity, snapshot, hashes, offsets/maps | complete shared T002 contract |
| 1 | Raw spaCy, BookNLP, explicit NCP parsing, deterministic extraction | partial foundation |
| 2 | Immutable raw artifact/evidence ledger and run manifest | complete shared T002/T003 contracts and persistence |
| 3 | Ollama, Story Check, full Subtxt, app-owned rubrics, diagnostics | partial; T006 adapter milestone accepted, real official runtime/current-layer execution pending, project diagnostics missing |
| 4 | Exact grounding and semantic guardrails | P0 Story Check grounding and bounded T006 seam complete; shared T008 guardrail missing |
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
4. `PHASE8-IMPL-025-T004` — BookNLP extraction expansion (implementation
   milestone accepted; real expanded current-layer validation pending).
5. `PHASE8-IMPL-025-T005` — Full Subtxt runtime inventory and contracts
   (`complete/PASS`).
6. `PHASE8-IMPL-025-T006` — Full Subtxt adapter, integration, and validation
   (`active/open`; implementation milestone accepted; T006G
   `NOT_EXECUTED_RUNTIME_UNAVAILABLE`; T006K zero currently available official
   runtime surfaces; real execution pending).
7. `PHASE8-IMPL-025-T007` — Evidence-bounded Ollama and Story Check
   (`planned`; dependency-satisfied/eligible; not begun).
8. `PHASE8-IMPL-025-T008` — Cross-adapter semantic guardrails (`planned`; not
   begun; awaits T004/T006 real-execution gates and T007).
9. `PHASE8-IMPL-025-T009` — Read-only project-level narrative diagnostics.
10. `PHASE8-IMPL-025-T010` — Full NCP gateway.
11. `PHASE8-IMPL-025-T011` — Candidate review lifecycle expansion.
12. `PHASE8-IMPL-025-T012` — Layered end-to-end validation.

Accepted bounded additions: T003F live-run API/control plane; T003G persisted-
data compatibility; T005H/T006K provisioning and current-machine runtime
compatibility; T010H NCP/diagnostics owner UI; T011H owner live-run workflow;
T012K layered integration deltas. PHASE8-IMPL-027 is the terminal gate.

T001-T003 and T005 are complete/PASS. T004 and T006 have accepted implementation
milestones with open real-execution gates. T006 remains the immediate active
frontier. T007 through T012 remain planned and not begun. Lettered bounded
slices are defined in the parent task record.

## Dependencies

```text
PHASE8-IMPL-024 closeout + application validation PASS
  -> PHASE8-IMPL-025 -> T001 -> T002 -> T003
  -> [T004] + [T005 -> T006] + [T007]
  -> T008
  -> [T009] + [T010] + [T011]
  -> T012 -> PHASE8-IMPL-027
```

T007 consumes PHASE8-IMPL-024-T002's completed Story Check grounding work and
must not duplicate it; T007E must add current-layer real Ollama and Story Check
execution. T010H waits for T009 and T010 backend contracts; T011H
waits for T003F and the completed PHASE8-IMPL-024 component foundation. T012
reuses PHASE8-IMPL-024-T008 and adds only layered deltas. T012I apply-promotion
validation remains isolated. T006 is the immediate active frontier. T007
remains planned/not begun. T008 remains not begun and waits for T004/T006
real-execution completion plus T007.

## Open technical questions

- Provisioning of a genuinely available verified official/full Subtxt callable
  interface and its evidenced source granularity.
- Subtxt runtime/interface/version/provider/model provenance where a future
  available runtime reports it.
- Cross-adapter guardrail ordering.
- NCP schema/mapping versions and trusted round-trip rules.
- Project-level diagnostic context contract.
- Owner correction and merge/split lifecycle.
- Whether external `dramatica_flow` remains an MVP-required external
  integration despite T020B's owner-blocked/reference-only runtime authority;
  `OWNER_DECISION_REQUIRED_BEFORE_EXTERNAL_DRAMATICA_FLOW_IMPLEMENTATION`.

Authorization and licensing are not open questions.

## Safety inventory

- Analysis-only and candidate-first.
- Evidence/provenance-backed and owner-controlled.
- No generated prose or prose transformation.
- No automatic truth, approval, promotion, or apply-promotion.
- No direct model/tool mutation of Memory/Canon.
- Raw artifacts are immutable support data, not canon/candidates/training data.
- External NCP status is source metadata, not local approval.
- Project-level diagnostics are read-only candidates, not settled state.
