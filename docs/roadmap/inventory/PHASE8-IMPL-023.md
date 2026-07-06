# PHASE8-IMPL-023 Inventory

## Parent

- ID: `PHASE8-IMPL-023`
- Title: OMI Raw Idea Extraction Candidate Review MVP
- Status: published/active
- Next child: `PHASE8-IMPL-023-T001`

## Owner Override Source

- `docs/roadmap/decisions/PHASE8-owner-override-block-full-mvp-closeout-omi-extraction-required.md`
- `docs/roadmap/decisions/PHASE8-final-owner-accepted-gate-decision.md`
- `docs/roadmap/decisions/PHASE8-post-accepted-owner-gate-next-readiness-step-decision.md` is superseded by the owner override.
- `docs/roadmap/decisions/PHASE8-UX-004-omi-manual-workflow-repair-decision.md`
- `docs/roadmap/decisions/PHASE8-UX-004-owner-manual-test-approval.md`

## Current Known Limitation

- The OMI manual screen currently creates manual/empty candidate shells.
- It does not automatically extract or identify characters, locations, timeline items, plot/story facts, relationships, organizations, objects, or other review candidates from raw idea text.
- PHASE8-UX-004 made that limitation visible but did not implement extraction.

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

## Required Candidate Fields

Each extracted review candidate must carry:

- candidate type
- label/name
- extracted claim
- evidence/source excerpt or locator
- provenance
- status
- owner decision state

## Safety Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Candidate presence is not canon.
- Candidate confidence is not truth.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Approval does not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- No generated story prose.

## Child Task Inventory

- `PHASE8-IMPL-023-T001`: Gap Audit and Architecture Decision.
- `PHASE8-IMPL-023-T002`: expected-red raw idea to candidate listing tests.
- `PHASE8-IMPL-023-T003`: backend extraction contract/schema.
- `PHASE8-IMPL-023-T004`: Deterministic/rule-based MVP extractor.
- `PHASE8-IMPL-023-T005`: candidate persistence with evidence/provenance/source spans.
- `PHASE8-IMPL-023-T006`: frontend OMI extracted-candidate review UI/UX.
- `PHASE8-IMPL-023-T007`: no-canon/no-apply-promotion safety validation.
- `PHASE8-IMPL-023-T008`: browser/manual evidence and closeout.

## UI/UX Inventory

- Raw idea intake state.
- Extraction status/progress/result.
- Candidate grouping by type.
- Empty/fail-closed states.
- Review queue clarity.
- Error messages.
- Clear next action after candidate extraction.

## Validation Commands

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```
