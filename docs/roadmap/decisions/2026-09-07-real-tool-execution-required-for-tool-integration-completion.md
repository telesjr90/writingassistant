# Real Tool Execution Required for Tool Integration Completion

Date: 2026-09-07

## Decision

Every MVP-required external-tool integration is complete only after all three
stages are demonstrated:

```text
implemented contract
-> real application adapter
-> successful bounded real tool execution through the applicable application path
```

For an artifact or schema gateway such as NCP, the third stage is successful
interoperability through a supported interface/schema, including the required
import, export, validation, and round trip.

Mocks and fixtures remain required deterministic regression evidence. They do
not prove that an external runtime, product, service, model, or supported
gateway interface executed and therefore cannot satisfy the third stage.

## Evidence interpretation

Historical real execution remains valid evidence for the exact code path and
scope it exercised. It does not automatically prove that a newer layered path
now reaches the same edge. Current-layer completion must prove the chain from
the current source identity and run control plane through the real edge, native
output, artifact/manifest/evidence ledger, normalization, guardrails, fusion, candidate persistence, and owner review where applicable.

Accepted contract, adapter, mock-validation, and implementation commits remain
accepted milestones. A stricter overall completion gate does not erase those
commits or convert them into failures. `RUNTIME_UNAVAILABLE`,
`NOT_EXECUTED_RUNTIME_UNAVAILABLE`, mock PASS, and fixture PASS are truthful
intermediate states, not real-execution PASS.

App-owned deterministic rubrics and fallbacks must remain explicitly labeled
as app-owned/internal implementations. Their execution is never evidence that
an external product with a related name executed.

## Roadmap consequences

- T004 keeps its accepted expanded BookNLP implementation milestone, but its
  overall real-tool completion remains pending until real expanded BookNLP
  output is proven through the T002/T003 layered artifact and ledger path.
- T005 remains complete/PASS as the official Subtxt contract milestone.
- T006 keeps its accepted adapter and mocked-validation milestone, but remains
  open until a verified official runtime is connected and successfully
  executed through the current layered path.
- T007E must prove bounded real current-layer execution for Ollama/qwen3:8b
  and Story Check; PHASE8-IMPL-023 runs are foundation evidence only.
- T008 must validate actual current-layer real contributor outputs for every
  applicable MVP-required external contributor alongside deterministic mock
  regressions. Fixture-only cross-adapter validation is insufficient.
- T010 must prove real supported-schema NCP gateway interoperability and round
  trip, not only fixture compatibility or the historical import-only path.
- T012 must prove the complete real source-to-owner-review chain for every
  enabled MVP-required external contributor. Mock-only end-to-end coverage is
  insufficient.

External `dramatica_flow` remains subject to its existing owner-blocked,
reference-only authority until the owner explicitly reconciles whether it
remains an MVP-required external integration. The app-owned
`dramatica_flow_informed_rubric` does not resolve that question.

## Safety

This decision does not authorize runtime execution, installation, external
access, adapter implementation, generated prose, automatic truth selection,
automatic approval or promotion, apply-promotion, or direct Memory/Canon
mutation.
