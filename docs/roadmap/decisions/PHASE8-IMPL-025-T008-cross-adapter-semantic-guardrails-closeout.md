# PHASE8-IMPL-025-T008 — Cross-adapter semantic guardrails closeout

## Identity and decision

- Task: `PHASE8-IMPL-025-T008 — Cross-adapter semantic guardrails`
- Final status: `complete/PASS`
- Parent: `PHASE8-IMPL-025 — Layered Analysis Architecture and Tool Integration Expansion`
- Decision: accept the already implemented T008 semantic-guardrail scope and
  its deterministic and real-output validation evidence. This record closes
  T008 only; it does not close the parent or activate a downstream task.

## Commit binding

- Implementation commit:
  `2465722cedfe9f8dcb4135d8de124f36a999593f`
- Implementation parent:
  `bc2a65e6350fdd65720606253b120d7fbcfa2b78`
- Subject: `feat(analysis): add cross-adapter semantic guardrails (T008)`

The implementation parent is also the accepted T004G closeout HEAD, with
subject `fix(analysis): validate BookNLP real-runtime retry`. It follows the
distinct T004 implementation commit
`ca2f99f35a7dc029a217954872ca7a5ab479ed2f`. Accepted T004G completed the
T004 BookNLP prerequisite before T008 began.

This documentation reconciliation does not modify application code and does
not claim a documentation commit.

## Accepted implementation scope

T008A-T008E are satisfied. The accepted implementation provides:

- a shared semantic-guardrail input/result contract;
- post-normalization, pre-fusion guardrail ordering;
- the six classifications `supported`, `unsupported`, `ambiguous`,
  `subject_matter_only`, `author_intent_dependent`, and
  `insufficient_evidence`;
- normalized-evidence dependency enforcement and source-lineage checks;
- a prohibition on interpretive findings self-supporting their own claims;
- an explicit distinction between ordinary owner interpretation and explicit
  author intent;
- perspective-ambiguity checks and unsupported Storypoint/Throughline
  overclaim checks;
- immutable preservation of original findings and outputs with separate
  guardrail annotations;
- no finding rewriting and no truth/canon selection;
- exactly one guardrail assessment followed by exactly one deterministic
  fusion pass in the authoritative run-control path; and
- retained Story Check diagnostics represented only by separate
  non-candidate, non-fusion guardrail annotations.

## Accepted deterministic validation

- Combined deterministic result: `458 passed, 7 warnings`.
- The seven warnings were existing Pydantic deprecation warnings, not product
  failures.
- `py_compile`: PASS.
- `git diff --check`: PASS.

## T008E real-output evidence

### BookNLP

- 49 findings and 49 separate guardrail annotations.
- 45 annotations classified `supported`.
- 4 annotations classified `ambiguous`.
- Original findings remained unchanged.

### Ollama/qwen3:8b

- Actual current-layer live-model execution occurred.
- One assessable finding produced one annotation classified
  `insufficient_evidence`.
- The reason was `eligible_normalized_evidence_missing`, proving that the
  interpretive model finding could not satisfy its own normalized-evidence
  dependency.
- Original output remained unchanged and persistence remained zero.
- A separate real qwen3:8b output omitted required `source_locator` data,
  failed closed, and yielded zero valid findings and zero annotations.

### Story Check

- Real current-layer output remained preserved.
- Zero normalized candidate findings were created.
- 16 diagnostics were retained with 16 separate retained-diagnostic guardrail
  annotations.
- 15 annotations were `insufficient_evidence`; 1 was `unsupported`.
- There were zero candidate transformations and zero fusion-eligible retained
  annotations.
- Original output remained unchanged.

### Official Subtxt

- Official Subtxt remains optional paid integration.
- It was unavailable/unconfigured during T008 validation.
- No installation, provisioning, subscription, or runtime call occurred.
- Its absence was accepted and nonblocking for T008 and the free/local MVP.

### External dramatica_flow

- External `dramatica_flow` was not executed.
- It remains reference/provenance-only for MVP and outside required T008
  runtime proof.

## Safety result

T008 remained analysis-only, candidate-first, evidence/provenance-backed, and
owner-controlled. Validation performed no candidate persistence, automatic
approval, automatic truth/canon selection, promotion, apply-promotion,
Memory/Canon mutation, training/dataset/model mutation, or generated story
prose. Tool and model output remained non-canon and did not become durable
project truth automatically.

## Downstream status

The accepted dependency order is:

```text
T004/T004G complete/PASS + T007/T007E complete/PASS
-> T008 complete/PASS
-> T009 / T010 / T011 planned and dependency-satisfied
```

T008 completion satisfies the T008 dependency of T009, T010, and T011. Those
three workstreams remain separate bounded tasks with these unchanged states:

- `PHASE8-IMPL-025-T009`: `planned`; not activated or begun.
- `PHASE8-IMPL-025-T010`: `planned`; not activated or begun.
- `PHASE8-IMPL-025-T011`: `planned`; not activated or begun.

Current authority permits parallel downstream work but does not select a
singular owner implementation priority among T009/T010/T011. This closeout
therefore activates none of them. `PHASE8-IMPL-025` remains active, T012
remains a later layered end-to-end validation gate, and terminal
`PHASE8-IMPL-027` remains later. No MVP-complete claim is made.
