# PHASE8-IMPL-023 Owner Override: AI Tool-Assisted OMI Analysis Required

## Result

PASS for roadmap correction and architecture reset only.

This decision records the owner override that deterministic-marker-only OMI extraction is not the MVP OMI target. `PHASE8-IMPL-023` remains the active parent, but its MVP scope is corrected to an AI/tool-assisted OMI analysis orchestrator that turns raw idea text into evidence-backed review candidates.

No backend product code, frontend product code, tests, models, tools, Memory/Canon state, apply-promotion behavior, training artifacts, staging, commit, push, or story prose changed or ran for this decision.

## Owner Override

The owner clarified that OMI must use AI and analysis tools to analyze raw idea text and show the user what was found for review.

The corrected MVP path may use:

- Ollama / local AI model.
- Story Check.
- BookNLP.
- spaCy.
- NCP.
- Subtxt.
- dramatica-flow.

All tool output must become candidate-first review material only. Model or tool output is not canon, confidence is not truth, candidate presence is not canon, queue presence is not approval, and approval does not automatically mutate Memory/Canon.

## Supersession Of T004 Direction

`PHASE8-IMPL-023-T004` remains historically complete/PASS as backend deterministic marker extraction.

It is superseded and re-scoped by this owner override as a fallback/safety baseline only. It is not sufficient for MVP OMI completion by itself and must not be treated as the final MVP extractor direction.

The prior T001 architecture decision is also superseded only where it selected deterministic/rule-based extraction as the first MVP target. Its safety boundaries remain valid.

## Corrected Product Definition

OMI receives raw idea text, runs tool-assisted analysis, groups findings by candidate type, shows evidence and provenance for each finding, and asks the owner to confirm, reject, or revise candidate findings.

OMI must not generate prose. OMI must not rewrite the idea, continue it, outline it, draft it, polish it, improve it, expand it, imitate a style, revise it, suggest a better way to write it, or produce story text.

Core output fields:

- `candidate_type`.
- `label` or `name`.
- `extracted_claim`.
- `evidence` or source excerpt.
- `source_locator`.
- `provenance` / tool source.
- `support` or `confidence` as support only, not truth.
- `owner_decision` defaulting to pending.
- Candidate/review status.
- Diagnostics or questions where appropriate.

## Corrected Architecture

The corrected MVP architecture is:

1. OMI analysis orchestrator receives raw idea text.
2. Tool adapters analyze the raw idea and return candidate findings, diagnostics, evidence, provenance, and support labels.
3. A normalization layer converts every adapter output to a common OMI candidate schema.
4. A fusion/dedupe layer groups equivalent findings, keeps conflicting claims visible, and preserves uncertainty.
5. Persistence stores fused evidence-backed candidates as candidate/review material only.
6. The UI lists what was found, grouped by type/tool/evidence.
7. The owner confirms, rejects, or revises candidates.

Full MVP completion remains blocked until AI/tool-assisted OMI analysis candidates are visible and owner-reviewable.

## Tool Boundaries

- Ollama/model: structured extraction only, schema-bound JSON only, no prose, no rewriting, no continuation, no outline, no drafting, no improvement suggestions.
- Story Check: diagnostic-only structural observations and questions, no prose suggestions.
- BookNLP/spaCy: local entities, entity-like mentions, sentence segmentation, events, relationships, mentions, and coreference-style support where applicable.
- NCP: structural context candidate mapping and import/export candidate representation, not truth export.
- Subtxt: rubric/reference guidance for diagnostic structural interpretation, not automatic Dramatica truth.
- dramatica-flow: analysis-pattern reference/integration for narrative-state patterns, promises, mysteries, causal chains, thread activity, and relationship shifts; generation/revision/continuation behavior remains disabled.
- All tools fail closed and may not silently fall back to unsupported claims.

## Safety Invariants

- Candidate persistence is not canon.
- Candidate presence is not canon.
- Queue presence is not approval.
- Confidence/support is not truth.
- Tool/model output is not canon.
- Owner approval in OMI review does not automatically mutate Memory/Canon.
- Apply-promotion remains separate, guarded, audited, owner-confirmed, and explicit.
- Generated prose remains forbidden.
- No automatic apply-promotion is authorized.
- No automatic Memory/Canon mutation is authorized.

## Revised Child Sequence

- `PHASE8-IMPL-023-T001` - Historical gap audit and architecture decision. Superseded only where it selected deterministic-only MVP extraction.
- `PHASE8-IMPL-023-T002` - Historical expected-red extraction tests. Complete/PASS as tests-first coverage under the previous path.
- `PHASE8-IMPL-023-T003` - Historical backend extraction contract/schema. Complete/PASS as contract/schema under the previous path.
- `PHASE8-IMPL-023-T004` - Historical deterministic/rule-based backend extractor. Complete/PASS, now fallback/safety baseline only.
- `PHASE8-IMPL-023-T004A` - Owner override and AI/tool-assisted OMI architecture reset. Complete/PASS as this decision record.
- `PHASE8-IMPL-023-T005` - Tool-assisted extraction orchestrator contract and adapter boundaries.
- `PHASE8-IMPL-023-T006` - Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests.
- `PHASE8-IMPL-023-T007` - spaCy/BookNLP local NLP candidate extraction adapters.
- `PHASE8-IMPL-023-T008` - Story Check diagnostic-only OMI handoff.
- `PHASE8-IMPL-023-T009` - NCP/Subtxt/dramatica-flow analysis-only candidate mapping.
- `PHASE8-IMPL-023-T010` - Candidate fusion, dedupe, conflict handling, and evidence/provenance normalization.
- `PHASE8-IMPL-023-T011` - Persistence of fused evidence-backed candidates.
- `PHASE8-IMPL-023-T012` - Frontend OMI analysis results UI/UX.
- `PHASE8-IMPL-023-T013` - Safety validation: no prose, no Memory/Canon mutation, no apply-promotion, and no tool output as truth.
- `PHASE8-IMPL-023-T014` - Browser/manual evidence closeout.

`PHASE8-IMPL-023-T005` is the next child for the corrected orchestrator path.

## Deferred Work

Implementation is deferred. This decision does not run Ollama, Story Check, BookNLP, spaCy, NCP, Subtxt, or dramatica-flow. It does not create candidates, mutate Memory/Canon, run or enable apply-promotion, or generate story prose.
