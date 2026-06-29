# PHASE8-UX-001 - Master Plan UX / Navigation Proposal

## Status

Planned.

## Purpose

Create a UX master proposal for the Dramatica-Informed Writing Assistant that explains:

- Current UI/UX.
- Implemented UI/UX.
- Planned but not implemented UI/UX.
- Recommended navigation model.
- Recommended user workflows.
- Analysis, OMI, review queue, apply-promotion, and approved memory/canon UX.
- Aider UX recommendations.
- UI/UX reference search targets for future design improvement.

## Scope

This is a docs-only UX planning parent.

## Product Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Owner-authored prose storage/editing is allowed.
- AI-generated prose is permanently forbidden.
- No rewrite, continuation, imitation, polish, improvement, expansion, outline, draft, revise, or story-prose-production controls.
- Queue presence is not approval.
- Confidence is not truth.
- Candidate persistence is not canon.
- Raw artifacts are support data, not canon.
- Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.

## Expected Deliverables

- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/ux/PHASE8-UX-001-impeccable-ui-ux-qa-workflow.md`
- Current UI/UX inventory.
- Planned UI/UX from the master plan.
- Implemented / partially implemented / missing / unclear gap analysis.
- Primary user workflows.
- ASCII wireframes.
- UX safety rules.
- Aider recommendations.
- UI/UX reference search targets.
- Implementation task breakdown.

## Context Pack

.codex-context/PHASE8-UX-001/

## Validation

Run:

python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
git diff --check
git status --short --branch

## Explicit Non-Goals

- No frontend implementation.
- No backend implementation.
- No route/API changes.
- No model calls.
- No generated prose features.
- No OMI promotion behavior changes.
- No apply-promotion behavior changes.
- No roadmap status closeout until owner review accepts the UX proposal.
