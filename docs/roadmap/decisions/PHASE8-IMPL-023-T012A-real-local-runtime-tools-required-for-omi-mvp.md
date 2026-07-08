# PHASE8-IMPL-023-T012A Real Local/Runtime Tools Required for OMI MVP

## Result

PASS for docs-only roadmap correction. No product code, tests, package, or runtime changes.

## Decision

`PHASE8-IMPL-023` cannot close as MVP-complete until OMI and analysis run real local/runtime analysis through all selected tools, or any unavailable tool is explicitly documented as BLOCKED by owner decision.

Fixture/mock adapter contracts prove safety/schema compatibility only. They do not prove live analysis and do not count as MVP completion.

## Context

- `PHASE8-IMPL-023-T004` remains historically complete/PASS as deterministic marker extraction, but is fallback/safety baseline only.
- `PHASE8-IMPL-023-T005` through `PHASE8-IMPL-023-T011` are complete/PASS as orchestrator contract, fixture-only adapter contracts, backend fusion metadata, and candidate-only persistence scaffolding.
- The prior child sequence after T011 selected `PHASE8-IMPL-023-T012 - Frontend OMI analysis results UI/UX` as the next step. That sequence assumed fixture-backed backend work could proceed to UI before live runtime integration.
- Corrected MVP truth: live local/runtime tool integration is required before MVP closeout. UI work on fixture-only outputs does not satisfy MVP completion.
- T012 UI work may be mistaken for MVP completion if real runtime outputs are not connected.
- Each selected tool must be live-connected and validated or explicitly owner-blocked.

## Corrected Child Sequence After T011

1. `PHASE8-IMPL-023-T012A` — Real local/runtime tools required for OMI MVP roadmap reset (this decision; docs/status only).
2. `PHASE8-IMPL-023-T013` — Runtime configuration, preflight, health checks, and feature flags.
3. `PHASE8-IMPL-023-T014` — Live spaCy integration in OMI and analysis.
4. `PHASE8-IMPL-023-T015` — Live Ollama/local model integration in OMI and analysis.
5. `PHASE8-IMPL-023-T016` — Live Story Check integration in OMI and analysis.
6. `PHASE8-IMPL-023-T017` — Live BookNLP integration in OMI and analysis.
7. `PHASE8-IMPL-023-T018` — Live NCP integration in OMI and analysis.
8. `PHASE8-IMPL-023-T019` — Live Subtxt integration in OMI and analysis.
9. `PHASE8-IMPL-023-T020` — Live dramatica-flow integration in OMI and analysis.
10. `PHASE8-IMPL-023-T021` — Cross-tool fusion validation using real runtime outputs.
11. `PHASE8-IMPL-023-T022` — Candidate-only persistence validation using real runtime outputs.
12. `PHASE8-IMPL-023-T023` — Grouped owner-review UI for real runtime findings.
13. `PHASE8-IMPL-023-T024` — Automated end-to-end live OMI test.
14. `PHASE8-IMPL-023-T025` — Manual Cyber Detective Story live OMI test.
15. `PHASE8-IMPL-023-T026` — `PHASE8-IMPL-023` closeout only after live runtime tools are connected/tested or explicitly owner-blocked.

## Superseded Planning

The prior post-T011 sequence (`T012` frontend UI on fixture outputs, `T013` safety validation, `T014` browser/manual closeout) is superseded by `T012A` through `T026`. Prior `T012` UI intent is preserved in `T023`, but only after live runtime integration and validation.

## MVP Closeout Rule

MVP closeout for `PHASE8-IMPL-023` is blocked until:

- each selected tool adapter runs live local/runtime analysis in OMI and analysis paths, or
- the owner explicitly documents a tool as BLOCKED with rationale, and
- cross-tool fusion, candidate-only persistence, grouped owner-review UI, automated live OMI test, and manual Cyber Detective Story live OMI test pass against real runtime outputs where tools are not owner-blocked.

Fixture-only adapter contract tests remain required safety scaffolding but are not sufficient for MVP completion.

## Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Owner-authored prose storage/editing is allowed.
- No generated story prose.
- No rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, revision, or writing suggestion.
- Confidence/support is not truth.
- Candidate presence is not canon.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Tool/model output is not canon.
- No automatic Memory/Canon mutation.
- No promotion records.
- No apply-promotion.

## Safety Confirmations

- Docs-only correction; no backend/frontend runtime code changed.
- No tests changed.
- No package/dependency changes.
- No live tool/model calls in this task.
- No staging, commit, or push.
