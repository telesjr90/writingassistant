# PHASE8-IMPL-025 Inventory

## Parent

- ID: `PHASE8-IMPL-025`
- Title: Layered Analysis Architecture and Tool Integration Expansion
- Status: published/planned
- Immediate implementation frontier: `PHASE8-IMPL-024-T003B`
  (`planned/next/unimplemented`)
- Activation dependency: PHASE8-IMPL-024 fully complete/closed, closeout
  validation PASS, and accepted post-closeout Project Memory refresh `FRESH`
- Controlling decision:
  `docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`

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

These results are foundation-level and do not satisfy the missing architecture
layers or official/full Subtxt runtime path.

## Layer inventory

| Layer | Target | Current classification |
| --- | --- | --- |
| 0 | Owner source identity, snapshot, hashes, offsets/maps | partial/missing unified contract |
| 1 | Raw spaCy, BookNLP, explicit NCP parsing, deterministic extraction | partial foundation |
| 2 | Immutable raw artifact/evidence ledger and run manifest | partial/missing unified lineage |
| 3 | Ollama, Story Check, full Subtxt, app-owned rubrics, diagnostics | partial; full Subtxt and project diagnostics missing |
| 4 | Exact grounding and semantic guardrails | P0 Story Check work planned; shared guardrail missing |
| 5 | Fusion/conflict/uncertainty/provenance | implemented foundation; layered inputs not fully validated |
| 6 | Candidate persistence and expanded owner review | implemented foundation; correction lifecycle incomplete |
| 7 | Explicit promotion and approved context | existing isolated boundary; layered handoff validation incomplete |
| 8 | NCP import/export gateway and round-trip provenance | narrow import foundation only |

## Indexed workstreams

1. `PHASE8-IMPL-025-T001` — Tool-role and layered-orchestration contract.
2. `PHASE8-IMPL-025-T002` — Source identity and AnalysisRunManifest.
3. `PHASE8-IMPL-025-T003` — Immutable raw artifact and evidence ledger.
4. `PHASE8-IMPL-025-T004` — BookNLP extraction expansion.
5. `PHASE8-IMPL-025-T005` — Full Subtxt runtime inventory and contracts.
6. `PHASE8-IMPL-025-T006` — Full Subtxt adapter, integration, and validation.
7. `PHASE8-IMPL-025-T007` — Evidence-bounded Ollama and Story Check.
8. `PHASE8-IMPL-025-T008` — Cross-adapter semantic guardrails.
9. `PHASE8-IMPL-025-T009` — Read-only project-level narrative diagnostics.
10. `PHASE8-IMPL-025-T010` — Full NCP gateway.
11. `PHASE8-IMPL-025-T011` — Candidate review lifecycle expansion.
12. `PHASE8-IMPL-025-T012` — Layered end-to-end validation.

Accepted bounded additions: T003F live-run API/control plane; T003G persisted-
data compatibility; T005H/T006K provisioning and current-machine runtime
compatibility; T010H NCP/diagnostics owner UI; T011H owner live-run workflow;
T012K layered integration deltas. PHASE8-IMPL-027 is the terminal gate.

All are planned. Lettered bounded slices are defined in the parent task record.

## Dependencies

```text
PHASE8-IMPL-024 closeout + validation PASS + accepted FRESH refresh
  -> PHASE8-IMPL-025 -> T001 -> T002 -> T003
  -> [T004] + [T005 -> T006] + [T007]
  -> T008
  -> [T009] + [T010] + [T011]
  -> T012 -> PHASE8-IMPL-027
```

T007 consumes PHASE8-IMPL-024-T002's completed Story Check grounding work and
must not duplicate it. T010H waits for T009 and T010 backend contracts; T011H
waits for T003F and the completed PHASE8-IMPL-024 component foundation. T012
reuses PHASE8-IMPL-024-T008 and adds only layered deltas. T012I apply-promotion
validation remains isolated.

## Open technical questions

- Exact full Subtxt callable interface and source granularity.
- Official analysis-only Subtxt operation allowlist.
- Subtxt internal model/provider provenance availability.
- Raw artifact retention policy.
- Final AnalysisRunManifest schema.
- Cross-adapter guardrail ordering.
- Exact expanded BookNLP mappings.
- NCP schema/mapping versions and trusted round-trip rules.
- Project-level diagnostic context contract.
- Owner correction and merge/split lifecycle.

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
