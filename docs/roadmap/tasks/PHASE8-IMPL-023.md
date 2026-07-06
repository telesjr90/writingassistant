# PHASE8-IMPL-023 - OMI Raw Idea Extraction Candidate Review MVP

## Status

Published and active.

Next child task: `PHASE8-IMPL-023-T001 - Gap Audit and Architecture Decision`.

Full MVP completion closeout is blocked until this parent, or an equivalent MVP-required OMI extraction path, is complete and validated.

## Goal

Build the real MVP OMI path where raw idea input produces structured, evidence-backed review candidates for owner review.

## Current Gap

The current manual OMI workflow can create empty/manual candidate shells and can make that limitation visible. It does not identify candidates from raw idea text for owner review. That means OMI is not yet MVP-complete.

## MVP Behavior

- User enters or saves a raw idea in OMI.
- The system analyzes the raw idea.
- The system identifies review candidates from that raw idea.
- The UI lists those candidates for owner review.
- Candidate types include, where evidence exists:
  - characters
  - locations
  - timeline/events
  - relationships
  - organizations/groups
  - objects/items
  - plot threads or story facts
  - open questions / ambiguities
  - storyform/context candidates only when supportable

## Acceptance Criteria

- Given raw idea text, OMI produces non-empty candidate records where evidence exists.
- Candidate list is visible in the UI.
- Each candidate has type, label/name, extracted claim, evidence/source excerpt or locator, provenance, status, and owner decision state.
- Empty extraction fails closed with a clear explanation and does not create misleading empty shells.
- UI clearly separates extracted candidates from approved Memory/Canon.
- No automatic Memory/Canon mutation occurs.
- No automatic apply-promotion occurs.
- No generated story prose is produced.

## UI/UX Improvement Scope

- Better raw idea intake state.
- Clear extraction status, progress, and result.
- Clear candidate grouping by type.
- Empty and fail-closed states.
- Review queue clarity.
- Better error messages.
- Clear next action after candidate extraction.

## Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- No generated prose.
- Confidence is not truth.
- Candidate presence is not canon.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Candidate approval does not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- Raw idea extraction must not write, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, or produce story prose.

## Child Task Sequence

- `PHASE8-IMPL-023-T001` - Gap Audit and Architecture Decision. Scope: docs/decision and narrow source audit only; no implementation.
- `PHASE8-IMPL-023-T002` - Expected-red raw idea to candidate listing tests. Scope: tests-first expected-red only.
- `PHASE8-IMPL-023-T003` - Backend extraction contract/schema. Scope: contract/schema implementation only.
- `PHASE8-IMPL-023-T004` - Deterministic/rule-based MVP extractor. Scope: implementation only after tests/contract.
- `PHASE8-IMPL-023-T005` - Candidate persistence with evidence/provenance/source spans. Scope: candidate-first persistence only; no Memory/Canon mutation.
- `PHASE8-IMPL-023-T006` - Frontend OMI extracted-candidate review UI/UX. Scope: owner review UI for extracted candidates.
- `PHASE8-IMPL-023-T007` - No-canon/no-apply-promotion safety validation. Scope: safety validation/hardening only.
- `PHASE8-IMPL-023-T008` - Browser/manual evidence and closeout. Scope: evidence, validation, and closeout.

## Non-Goals

- Do not mark full MVP complete in this parent publication.
- Do not run extraction in this parent publication.
- Do not create candidates in this parent publication.
- Do not mutate Memory/Canon.
- Do not run apply-promotion.
- Do not call models/Ollama.
- Do not generate, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, or produce story prose.
- Do not create training data, JSONL records, datasets, model artifacts, or fine-tuning configs.
- Do not stage, commit, or push unless explicitly requested.

## Validation Commands

Parent publication validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```
