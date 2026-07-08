# PHASE8-IMPL-023 Inventory

## Parent

- ID: `PHASE8-IMPL-023`
- Title: OMI AI Tool-Assisted Analysis Candidate Review MVP
- Status: published/active
- Latest completed child: `PHASE8-IMPL-023-T007`
- Next child: `PHASE8-IMPL-023-T008`

## Owner Override Sources

- `docs/roadmap/decisions/PHASE8-IMPL-023-owner-override-ai-tool-assisted-omi-analysis-required.md`
- `docs/roadmap/decisions/PHASE8-owner-override-block-full-mvp-closeout-omi-extraction-required.md`
- `docs/roadmap/decisions/PHASE8-final-owner-accepted-gate-decision.md`
- `docs/roadmap/decisions/PHASE8-post-accepted-owner-gate-next-readiness-step-decision.md` is superseded by the owner override.
- `docs/roadmap/decisions/PHASE8-UX-004-omi-manual-workflow-repair-decision.md`
- `docs/roadmap/decisions/PHASE8-UX-004-owner-manual-test-approval.md`

## Corrected MVP Scope

OMI must analyze raw idea text through an AI/tool-assisted analysis orchestrator and present evidence-backed findings for owner review.

The MVP target is not deterministic-marker-only extraction. `PHASE8-IMPL-023-T004` remains historically complete/PASS as backend deterministic marker extraction, but it is fallback/safety baseline only and is not sufficient for MVP completion.

## Current Known Limitation

- The current OMI path can store owner-authored raw ideas and candidate records.
- A deterministic marker extractor exists for explicit owner-authored markers.
- That deterministic extractor does not satisfy the corrected MVP target by itself.
- The corrected path requires orchestrated analysis using AI/tool adapters, output normalization, fusion/dedupe, evidence/provenance preservation, conflict/uncertainty display, and owner-reviewable UI.
- Full MVP completion remains blocked until AI/tool-assisted OMI analysis candidates are visible and owner-reviewable.

## Required Tool-Assisted Sources

The corrected OMI path can use:

- Ollama / local AI model for structured candidate extraction and validation.
- Story Check for diagnostic-only structural observations.
- BookNLP for narrative/entity/event/coreference-style extraction where applicable.
- spaCy for local entity/entity-like extraction, sentence segmentation, and rule-assisted NLP.
- NCP for structural context mapping/import-export candidate representation.
- Subtxt rubric/reference guidance for diagnostic structural interpretation.
- dramatica-flow as analysis-pattern reference/integration for narrative-state patterns, promises, mysteries, causal chains, thread activity, and relationship shifts.

## Required Candidate Types

Candidate identification must include these types where evidence exists:

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

Each extracted review candidate or diagnostic finding must carry:

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

## Architecture Inventory

- OMI analysis orchestrator receives raw idea text.
- Each adapter returns candidate findings, diagnostics, evidence, provenance, and support labels.
- Normalization converts all outputs to a common OMI candidate schema.
- Fusion/dedupe groups equivalent findings, preserves conflicts, and keeps uncertainty visible.
- Persistence stores fused evidence-backed candidates as candidate/review material only.
- UI lists what was found, grouped by type/tool/evidence.
- Owner confirms, rejects, or revises findings.

## Tool Boundary Inventory

- Ollama/model: structured extraction only, schema-bound JSON, no prose, no rewriting.
- Story Check: diagnostic-only observations, no prose suggestions.
- BookNLP/spaCy: entities/events/relationships/mentions as evidence-backed candidate sources.
- NCP: structural context candidate mapping, not truth export.
- Subtxt: rubric/diagnostic interpretation, not automatic Dramatica truth.
- dramatica-flow: analysis-pattern reference only; generation/revision/continuation disabled.
- All tools must fail closed.

## Safety Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Candidate presence is not canon.
- Candidate confidence/support is not truth.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Tool/model output is not canon.
- Approval does not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- No generated story prose.
- No rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, revision, or writing suggestion.

## Child Task Inventory

- `PHASE8-IMPL-023-T001`: historical gap audit and architecture decision; superseded only where it selected deterministic-only MVP extraction.
- `PHASE8-IMPL-023-T002`: historical expected-red raw idea to candidate listing tests.
- `PHASE8-IMPL-023-T003`: historical backend extraction contract/schema.
- `PHASE8-IMPL-023-T004`: historical deterministic/rule-based backend extractor; fallback/safety baseline only.
- `PHASE8-IMPL-023-T004A`: owner override and AI/tool-assisted OMI architecture reset.
- `PHASE8-IMPL-023-T005`: tool-assisted extraction orchestrator contract and adapter boundaries.
- `PHASE8-IMPL-023-T006`: Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests.
- `PHASE8-IMPL-023-T007`: BookNLP/spaCy local NLP candidate extraction adapters; complete/PASS as fixture-only local NLP normalization.
- `PHASE8-IMPL-023-T008`: Story Check diagnostic-only OMI handoff.
- `PHASE8-IMPL-023-T009`: NCP/Subtxt/dramatica-flow analysis-only candidate mapping.
- `PHASE8-IMPL-023-T010`: candidate fusion, dedupe, conflict handling, and evidence/provenance normalization.
- `PHASE8-IMPL-023-T011`: persistence of fused evidence-backed candidates.
- `PHASE8-IMPL-023-T012`: frontend OMI analysis results UI/UX.
- `PHASE8-IMPL-023-T013`: safety validation: no prose, no Memory/Canon mutation, no apply-promotion, no tool output as truth.
- `PHASE8-IMPL-023-T014`: browser/manual evidence closeout.

## UI/UX Inventory

- Raw idea intake state.
- Analysis status/progress/result.
- Candidate grouping by type.
- Tool/provenance grouping and display.
- Evidence/source locator display.
- Conflict and uncertainty display.
- Empty/fail-closed states.
- Review queue clarity.
- Error messages.
- Confirm/reject/revise owner decision actions.
- Clear next action after analysis.

## Validation Commands

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```
