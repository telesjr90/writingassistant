# PHASE8-IMPL-023 - OMI AI Tool-Assisted Analysis Candidate Review MVP

## Status

Published and active.

Latest completed child: `PHASE8-IMPL-023-T013 - Runtime configuration, preflight, health checks, and feature flags`.

Next child task: `PHASE8-IMPL-023-T014 - Live spaCy integration in OMI and analysis`.

Full MVP completion closeout is blocked until OMI and analysis run real local/runtime analysis through all selected tools, or any unavailable tool is explicitly documented as BLOCKED by owner decision, and the resulting real runtime outputs are fused, persisted as candidates only, visible for grouped owner review, and validated end to end.

## Goal

Build the real MVP OMI path where raw idea input is analyzed by an AI/tool-assisted analysis orchestrator and converted into structured, evidence-backed review candidates for owner review.

## Owner Override

Deterministic-marker-only extraction is not the MVP OMI target.

MVP OMI requires tool-assisted analysis that can use Ollama/local AI models, Story Check, BookNLP, spaCy, NCP, Subtxt, and dramatica-flow. Tool output must become evidence-backed candidates only.

`PHASE8-IMPL-023-T004` remains historically complete/PASS as backend deterministic marker extraction, but it is superseded and re-scoped as a fallback/safety baseline only. It is not sufficient for MVP completion by itself.

## Current Gap

The current OMI path has a backend deterministic marker extractor for explicit owner-authored markers, but the corrected MVP requires analysis of raw idea text through AI/tool-assisted adapters.

The orchestrator can now normalize fixture-only adapter outputs, annotate deterministic fusion/dedupe/conflict/uncertainty metadata, and persist fused findings as candidate-only OMI review records when explicitly requested and source context is safe. That work is useful scaffolding only. Fixture/mock adapter contracts prove safety/schema compatibility; they do not prove live analysis and do not count as MVP completion.

Remaining MVP behavior requires live local/runtime OMI and analysis integration for each selected tool, explicit owner-blocked status for unavailable tools, cross-tool validation using real runtime outputs, candidate-only persistence validation using real runtime outputs, grouped owner-review UI for real runtime findings, automated live OMI validation, manual Cyber Detective Story live OMI validation, and parent closeout only after those gates pass or are explicitly owner-blocked.

## MVP Behavior

- User enters or saves raw idea text in OMI.
- OMI runs tool-assisted analysis through the orchestrator.
- Adapters return candidate findings, diagnostics, evidence, provenance, source locators, and support labels.
- The normalization layer converts all outputs to the common OMI candidate schema.
- The fusion/dedupe layer groups equivalent findings and keeps conflicts or uncertainty visible.
- The UI lists findings grouped by type, tool/provenance, and evidence.
- The owner confirms, rejects, or revises findings.
- Candidate presence is not canon, confidence is not truth, queue presence is not approval, and tool/model output is not canon.

## Candidate Types

Candidate types include, where evidence exists:

- characters
- locations
- timeline/events
- relationships
- organizations/groups
- objects/items
- plot threads or story facts
- open questions / ambiguities
- storyform/context candidates only when supportable
- diagnostics/questions where appropriate

## Required Candidate Fields

Each finding must carry:

- candidate type
- label/name
- extracted claim
- evidence/source excerpt
- source locator
- provenance/tool source
- support/confidence as support only, not truth
- owner decision state, default pending
- candidate/review status
- diagnostics/questions where appropriate

## Architecture

- OMI analysis orchestrator receives raw idea text.
- Tool adapters perform bounded analysis and return candidate findings only.
- Normalization converts every adapter output to the common OMI candidate schema.
- Fusion/dedupe groups equivalent findings, preserves conflicts, and shows uncertainty.
- Persistence stores fused evidence-backed candidates as candidate/review material only.
- UI lists what was found and lets the owner confirm, reject, or revise.

## Tool Boundaries

- Ollama/model: structured extraction only, schema-bound JSON only, no prose, no rewriting, no continuation, no outline, no drafting, no improvement suggestions.
- Story Check: fixture-only diagnostic observations/questions in T008, no live runtime calls, no prose suggestions, no candidate persistence.
- BookNLP/spaCy: entities, entity-like mentions, sentence segmentation, events, relationships, mentions, and coreference-style support where applicable.
- NCP: structural context candidate mapping and import/export candidate representation, not truth export.
- Subtxt: rubric/reference guidance for diagnostic structural interpretation, not automatic Dramatica truth.
- dramatica-flow: analysis-pattern reference/integration for narrative-state patterns, promises, mysteries, causal chains, thread activity, and relationship shifts; generation/revision/continuation disabled.
- All tools fail closed.

## Acceptance Criteria

- Given raw idea text, OMI can produce non-empty tool-assisted candidate findings where evidence exists.
- Candidate list is visible in the UI and grouped by type.
- Each candidate has candidate type, label/name, extracted claim, evidence/source excerpt, source locator, provenance/tool source, support label, status, and owner decision state.
- Diagnostics/questions are shown where appropriate without writing or suggesting story prose.
- Empty or unsupported analysis fails closed with a clear explanation and does not create misleading empty shells.
- UI clearly separates extracted candidates from approved Memory/Canon.
- No automatic Memory/Canon mutation occurs.
- No automatic apply-promotion occurs.
- No generated story prose is produced.
- Tool/model output is never treated as canon or truth.

## UI/UX Improvement Scope

- Better raw idea intake state.
- Clear analysis status, progress, and result.
- Clear candidate grouping by type.
- Empty and fail-closed states.
- Review queue clarity.
- Evidence/provenance/source locator display.
- Conflict/uncertainty display.
- Better error messages.
- Clear next action after candidate analysis.

## Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- No generated prose.
- No rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, revision, or writing suggestion.
- Confidence/support is not truth.
- Candidate presence is not canon.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Tool/model output is not canon.
- Candidate approval does not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- Raw idea analysis must not write, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, suggest, or produce story prose.

## Child Task Sequence

- `PHASE8-IMPL-023-T001` - Historical gap audit and architecture decision. Scope: docs/decision and narrow source audit only; superseded only where it selected deterministic-only MVP extraction.
- `PHASE8-IMPL-023-T002` - Historical expected-red raw idea to candidate listing tests. Scope: tests-first expected-red only under the previous path.
- `PHASE8-IMPL-023-T003` - Historical backend extraction contract/schema. Scope: contract/schema implementation under the previous path.
- `PHASE8-IMPL-023-T004` - Historical deterministic/rule-based backend extractor. Scope: fallback/safety baseline only; not sufficient for MVP completion.
- `PHASE8-IMPL-023-T004A` - Owner override and AI/tool-assisted OMI architecture reset. Scope: docs/status/architecture correction only; complete/PASS.
- `PHASE8-IMPL-023-T005` - Tool-assisted extraction orchestrator contract and adapter boundaries. Scope: corrected orchestrator contract and adapter boundaries.
- `PHASE8-IMPL-023-T006` - Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T007` - BookNLP/spaCy local NLP candidate extraction adapters. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T008` - Story Check diagnostic-only OMI handoff. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T009` - NCP/Subtxt/dramatica-flow diagnostic and context adapter contracts. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T010` - Candidate fusion, dedupe, conflict handling, and evidence/provenance normalization. Scope: backend-only contract; complete/PASS.
- `PHASE8-IMPL-023-T011` - Candidate-only persistence for fused AI/tool-assisted findings. Scope: backend-only; complete/PASS.
- `PHASE8-IMPL-023-T012A` - Real local/runtime tools required for OMI MVP roadmap reset. Scope: complete/PASS; docs/status reset only.
- `PHASE8-IMPL-023-T013` - Runtime configuration, preflight, health checks, and feature flags. Scope: complete/PASS; read-only backend/runtime preflight foundation only; no live tool/model analysis.
- `PHASE8-IMPL-023-T014` - Live spaCy integration in OMI and analysis. Scope: ready/active next.
- `PHASE8-IMPL-023-T015` - Live Ollama/local model integration in OMI and analysis.
- `PHASE8-IMPL-023-T016` - Live Story Check integration in OMI and analysis.
- `PHASE8-IMPL-023-T017` - Live BookNLP integration in OMI and analysis.
- `PHASE8-IMPL-023-T018` - Live NCP integration in OMI and analysis.
- `PHASE8-IMPL-023-T019` - Live Subtxt integration in OMI and analysis.
- `PHASE8-IMPL-023-T020` - Live dramatica-flow integration in OMI and analysis.
- `PHASE8-IMPL-023-T021` - Cross-tool fusion validation using real runtime outputs.
- `PHASE8-IMPL-023-T022` - Candidate-only persistence validation using real runtime outputs.
- `PHASE8-IMPL-023-T023` - Grouped owner-review UI for real runtime findings.
- `PHASE8-IMPL-023-T024` - Automated end-to-end live OMI test.
- `PHASE8-IMPL-023-T025` - Manual Cyber Detective Story live OMI test.
- `PHASE8-IMPL-023-T026` - PHASE8-IMPL-023 closeout only after live runtime tools are connected/tested or explicitly owner-blocked.

## Non-Goals

- Do not mark full MVP complete in this parent reset.
- Do not run extraction in this parent reset.
- Do not create candidates in this parent reset.
- Do not mutate Memory/Canon.
- Do not create promotion records.
- Do not run apply-promotion.
- Do not run Ollama/models, Story Check, BookNLP, spaCy, NCP, Subtxt, or dramatica-flow in this parent reset.
- Do not generate, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, suggest, or produce story prose.
- Do not create training data, JSONL records, datasets, model artifacts, or fine-tuning configs.
- Do not stage, commit, or push unless explicitly requested.

## Validation Commands

Parent reset validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```
