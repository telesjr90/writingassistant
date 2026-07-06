# PHASE8 Owner Override: Block Full MVP Closeout Until OMI Extraction Exists

## Decision

Owner decision: BLOCK full MVP completion closeout.

`PHASE8-MVP-COMPLETE-CLOSEOUT-001` must not proceed as the next roadmap step.

The next active implementation parent is:

`PHASE8-IMPL-023 - OMI Raw Idea Extraction Candidate Review MVP`

The next child task is:

`PHASE8-IMPL-023-T001 - Gap Audit and Architecture Decision`

This is implementation work, not just UX evidence, and `PHASE8-IMPL-023` follows the validator-compatible parent ID convention.

## Rationale

The prior PHASE8 final owner gate remains historically ACCEPTED by explicit owner decision, but owner-gate acceptance is distinct from full MVP completion.

The owner has clarified that OMI is still not working for MVP purposes because the current manual OMI workflow creates empty/manual candidate shells. That repair was useful because it made the limitation visible, but it did not deliver the required MVP behavior: raw idea input must produce identified review candidates for owner review.

## Supersession

`docs/roadmap/decisions/PHASE8-post-accepted-owner-gate-next-readiness-step-decision.md` is superseded by this owner override.

The post-accepted closeout plan is blocked by owner clarification. Full MVP completion closeout remains blocked until `PHASE8-IMPL-023` or an equivalent MVP-required OMI extraction path is complete and validated.

## Required MVP Behavior

- User enters or saves a raw idea in OMI.
- The system analyzes the raw idea.
- The system identifies review candidates from that raw idea.
- The UI lists those candidates for owner review.
- Candidate types include, where evidence exists: characters, locations, timeline/events, relationships, organizations/groups, objects/items, plot threads or story facts, open questions/ambiguities, and storyform/context candidates only when supportable.
- Every candidate is candidate-first, evidence/provenance-backed, and owner-controlled.
- Candidate presence is not canon.
- Candidate confidence is not truth.
- Candidate approval must not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- No story prose may be generated.

## Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- No generated prose.
- Confidence is not truth.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Apply-promotion is explicit, audited, owner-confirmed, and separate.
- No Memory/Canon mutation is authorized by this decision.
- No extraction run, model/Ollama call, candidate creation, apply-promotion run, product code change, product UI change, test edit, context tool run, staging, commit, or push occurred for this decision.
