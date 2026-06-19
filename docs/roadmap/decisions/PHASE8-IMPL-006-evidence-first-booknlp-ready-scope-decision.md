# PHASE8-IMPL-006 Evidence-First BookNLP-Ready Scope Decision

## 1. Decision Summary

`PHASE8-IMPL-006` will be an evidence-first, BookNLP-ready extraction foundation parent.

It replaces the narrow spaCy-first-only framing with an evidence/source/provenance foundation that can support BookNLP as the first serious literary extractor after source maps and provenance are stable. spaCy remains a possible lightweight local baseline for segmentation, simple NLP, and rule support, but it is not the sole strategic center of the parent.

BookNLP is not installed or run in `PHASE8-IMPL-006-T001`. No extraction implementation exists yet. All extraction outputs remain candidate-only, owner review remains mandatory, and no prose generation, rewrite, continuation, Storyform truth, memory/canon mutation, or NCP automatic truth is allowed.

## 2. Why This Decision Exists

`PHASE8-IMPL-005` closed with a spaCy-first local deterministic/rule-assisted candidate extraction recommendation. After that closeout, the owner ran targeted follow-up analysis and saved the results in five local files under `docs/`.

Those files show a better next-parent shape: evidence-first and BookNLP-ready before runtime extraction begins. The goal is to avoid generic entity extraction while still preserving safety, source locators, evidence spans, provenance, and owner approval. The goal is also to avoid unsafe direct integration of dramatica-flow, NCP, or Subtxt as automatic truth sources.

This decision shapes `PHASE8-IMPL-006` before runtime work starts.

## 3. Evidence Basis

Local evidence inputs:

- `docs/feasibility.md`: overall feasibility is YELLOW with GREEN subcomponents. The safe stack is BookNLP extracting literary evidence, conservative analysis rubrics, Subtxt/NCP rules preventing overclaiming, and NCP import/export only for approved structural context. RED conditions include automatic canon, definitive Storyform inference, rewrite/continue/prose generation, and truth/world-state mutation. The minimal safe architecture is manuscript text, BookNLP job, Evidence Ledger, candidate extraction layer, analysis-only rubric engine, semantic guardrails, review UI, owner approval, approved project context, and NCP import/export gateway.
- `docs/booknlp.md`: BookNLP is recommended as a second-stage extraction tool or the first serious automated extractor after stable app source maps exist. It is strong for evidence-backed candidate records and can connect `.tokens`, `.entities`, `.quotes`, `.book`, and related outputs to source locators, evidence spans, and provenance. BookNLP should not decide canon; coreference, quote, and event outputs require owner review; raw outputs should be stored separately from candidate records.
- `docs/dramaticaflow.md`: dramatica-flow can only be constrained through an allowlisted analysis adapter or reimplementation; the repo should not be used as-is. Safe concepts include causal links, continuity risks, information-boundary violations, relationship/emotional changes, hooks, timeline/thread events, and audit issues. Unsafe behavior includes writing pipelines, Writer/Reviser/Architect generation, write/revise APIs, outline/chapter generation, continuation, world_state/truth writes, final draft saving, export, and canon settlement.
- `docs/subtxt.md`: Subtxt/Dramatica concepts should become semantic rubric rules, not automatic classifiers. Subject matter is not conflict; source-of-conflict claims require a "why is this a problem?" mechanism; author-level interpretation is required; throughlines/storypoints remain candidates unless evidence and owner approval exist; insufficient evidence and diagnostic questions should be first-class outcomes.
- `docs/ncp.md`: NCP is useful as structural context interchange, not automatic canon. NCP files should be schema-validated, original imports stored unchanged, fields mapped to candidates first, owner review required before approved context, and exports limited to approved context by default. Imported NCP must not be treated as project truth.

Unknowns are deferred to later children: exact source locator priority, raw output storage location, mandatory run provenance fields, BookNLP-like fixture policy, object/item first-slice inclusion, and the timing of NCP/Subtxt/dramatica-flow rubric implementation.

## 4. Revised Parent Direction

Accepted direction:

```text
owner-authored text
-> stable source map / Evidence Ledger
-> simple local baseline extraction where useful
-> BookNLP-ready raw output and adapter contract
-> normalized Writer Assistant Core candidates
-> source locator + evidence + provenance
-> candidate persistence/index
-> owner review
-> later narrative rubrics / NCP export
```

Rejected direction:

```text
owner-authored text
-> BookNLP/dramatica-flow/NCP/Subtxt output
-> automatic canon/story truth
```

Rejected direction:

```text
owner-authored text
-> dramatica-flow writer/reviser/continuation pipeline
-> generated outline/prose/world_state/truth
```

## 5. Tool Roles Accepted for PHASE8-IMPL-006

### BookNLP

Accepted role:

- first serious literary extractor candidate after source maps/provenance exist
- evidence-producing tool candidate
- BookNLP-ready adapter contract target

Not accepted:

- canon authority
- Storyform interpreter
- automatic character/relationship truth
- immediate package install in T001

### spaCy

Accepted role:

- lightweight local baseline candidate
- segmentation/simple NLP/rule support
- fallback or supporting baseline

Not accepted:

- sole strategic center of `PHASE8-IMPL-006`
- advanced story intelligence by itself

### dramatica-flow

Accepted role:

- reference-only / future wrapped analysis-only rubric source
- causal links, hooks, information boundaries, timelines, relationship/emotion deltas, audit ideas

Not accepted:

- runtime dependency in `PHASE8-IMPL-006`
- writing pipeline
- generation/revision/continuation
- world_state/truth mutation

### Subtxt docs

Accepted role:

- semantic guardrails
- source-of-conflict rubric
- insufficient-evidence rules
- diagnostic questions
- author-level interpretation guidance

Not accepted:

- automatic Dramatica/Subtxt classifier
- Storyform proof
- generation prompt source

### NCP

Accepted role:

- future approved-context import/export mapping
- candidate import boundary reference

Not accepted:

- automatic truth
- direct memory/canon mutation
- raw candidate export as final approved structure

## 6. PHASE8-IMPL-006 Child Task Plan

1. `PHASE8-IMPL-006-T001` - Publish evidence-first extraction foundation parent and scope decision
   - docs/status/planning only
   - create parent, inventory, enrichment JSON, scope decision
   - no runtime code/tests

2. `PHASE8-IMPL-006-T002` - Evidence/source-map contract decision
   - docs/decision only
   - decide source document IDs, scene/chapter/note/material locator forms, byte/char/token offset policy, source hash policy, and Evidence Ledger shape
   - no runtime code/tests

3. `PHASE8-IMPL-006-T003` - Evidence/source-map contract tests
   - tests-first only
   - expected red if helpers do not exist
   - test source locator shape, evidence span shape, source hash, owner-authored source type, no-canon mutation

4. `PHASE8-IMPL-006-T004` - Minimal source-map/evidence helper implementation
   - implement pure helpers only if T003 authorizes
   - no external tools
   - no BookNLP install
   - no spaCy install
   - no extraction runtime
   - no routes/UI

5. `PHASE8-IMPL-006-T005` - BookNLP-ready raw output and adapter contract decision
   - docs/decision only
   - decide raw tool output storage policy, run provenance, `.tokens`/`.entities`/`.quotes`/`.book` mapping expectations, and candidate normalization boundaries
   - no BookNLP install or execution

6. `PHASE8-IMPL-006-T006` - BookNLP-ready adapter contract tests
   - tests-first only
   - validate mapping contracts using fixtures/mocked sample structures only
   - no BookNLP runtime execution unless a later parent authorizes
   - ensure candidate-only, evidence/provenance-backed behavior

7. `PHASE8-IMPL-006-T007` - Roadmap/status closeout
   - close parent
   - summarize source/evidence foundation and BookNLP-ready contract
   - recommend the next parent as either BookNLP adapter implementation spike or simple local baseline extraction implementation, depending on T005/T006 results

If local roadmap conventions require implementation only after T007, keep T004/T006 as contract/helper-only and defer adapter implementation to `PHASE8-IMPL-007`.

## 7. Acceptance Criteria

- `PHASE8-IMPL-006` is active/published in roadmap docs.
- Parent scope is evidence-first + BookNLP-ready, not spaCy-only.
- The five answer files are referenced as evidence inputs.
- `PHASE8-IMPL-005` remains complete.
- `PHASE8-IMPL-006-T001` is marked complete if successful.
- `PHASE8-IMPL-006-T002` is marked ready/active.
- No runtime extraction is claimed.
- No external tools are installed, cloned, or executed.
- No code/tests are changed.
- No generated prose/rewrite/continuation behavior is added.
- No memory/canon mutation is added.

## 8. Deferred Work

- BookNLP package approval/install
- BookNLP runtime adapter implementation
- spaCy package approval/install
- actual extraction runs
- raw output storage implementation
- frontend review UI
- backend extraction routes
- dramatica-flow analysis rubrics
- Subtxt semantic rubric implementation
- NCP import/export implementation
- apply-promotion
- memory/canon mutation
- model-assisted extraction
- training/JSONL/dataset work

## 9. Open Questions

- Should `PHASE8-IMPL-007` be BookNLP adapter implementation or simple local baseline extraction?
- What exact source locator priority should be used: char offsets, byte offsets, token offsets, line numbers, or mixed?
- Should raw tool outputs be stored under `writer_assistant/extractions/{tool}/{run_id}/`?
- What run provenance fields are mandatory before any extraction result becomes a candidate?
- What fixture policy should be used for BookNLP-like outputs without running BookNLP?
- Should object/item candidates be in the first implementation slice?
- When should NCP import/export be implemented?
- When should Subtxt-inspired rubric checks be implemented?
- When should dramatica-flow-inspired causal/information-boundary rubrics be implemented?
