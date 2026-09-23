# PHASE8-IMPL-025-T007 — Evidence-bounded Ollama and Story Check closeout

## Decision

`PHASE8-IMPL-025-T007` is complete/PASS through T007E.

Accepted implementation commit:

`f843b615762192ca8f6865e76b2c4e4c9bcc2170`

This closeout does not activate T008. T007's dependency contribution is
satisfied, but `PHASE8-IMPL-025-T004/T004G` remains the outstanding required
free/local contributor gate before T008.

T006 remains accepted/closed as optional paid Subtxt/Dramatica integration.
Its unavailable paid runtime is deferred optional debt and is not reopened by
this closeout.

## Deterministic validation

The final accepted T007E deterministic gate passed 379 tests.

Accepted regression coverage includes:

- exact-source byte preservation;
- Ollama immutable original-output retention;
- truthful Ollama execution provenance and model-call state;
- Story Check live execution provenance;
- source-mismatch fail-closed behavior;
- unverified/quarantined diagnostic output lineage;
- evidence isolation;
- T003 model-call truthfulness;
- zero automatic candidate/canon/promotion mutation.

## Bounded real Ollama validation

A real current-layer `analyze-ollama-model` run reached Ollama/qwen3:8b through
the application control path.

Accepted run:

`analysis-run-9427bef28f41d7d4f6afae578f3f5b28`

Accepted observations:

- exact source: 180 UTF-8 bytes;
- SHA-256:
  `63a7a3e4df3e156f23f6ee5cf93031a40dc055d9b6a25e39eefff5cc6e1c2886`;
- real Ollama/qwen3:8b execution recorded truthfully;
- immutable original model output retained;
- unsupported `candidate_type="person"` failed closed without coercion;
- zero accepted/persisted candidates;
- rejected output remained attributable;
- T003 recorded confirmed authorized model execution.

## Bounded real Story Check validation

A separate real current-layer `analyze-story-check` run reached the
application-owned Story Check runtime and Ollama/qwen3:8b exactly once.

Accepted run:

`analysis-run-56a426348d61221e97f5185dea663e0f`

Accepted observations:

- exact source remained 180 bytes with SHA-256
  `63a7a3e4df3e156f23f6ee5cf93031a40dc055d9b6a25e39eefff5cc6e1c2886`;
- provenance recorded Story Check runtime, Ollama provider, and qwen3:8b;
- 16 diagnostics total;
- 0 verified;
- 15 unverified;
- 1 quarantined;
- 16 manifest output-lineage records;
- 16 corresponding `output_recorded` ledger events;
- zero evidence references on nonvalidated outputs;
- zero candidate transformations;
- zero persisted candidates;
- confirmed-model-execution T003 flags present.

Execution is not factual verification. The absence of verified diagnostics is
not a failure. The operation remained fail-closed/empty while preserving
nonvalidated diagnostic attribution.

## Safety

Accepted evidence confirms:

- analysis-only behavior;
- candidate-first behavior;
- no automatic truth selection;
- no automatic approval;
- no promotion or apply-promotion;
- no Memory/Canon mutation;
- no training/dataset/model mutation;
- no generated story prose.

Model/tool output remains non-canon and owner-controlled.

## Next required application frontier

`PHASE8-IMPL-025-T004` retains its accepted implementation milestone.

Its `T004G — Expanded real-runtime fusion and candidate-only persistence
validation` remains the next required contributor gate.

T008 remains planned/not begun until T004/T004G is accepted.
