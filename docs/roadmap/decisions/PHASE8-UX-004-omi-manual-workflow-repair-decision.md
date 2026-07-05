# PHASE8-UX-004 OMI Manual Workflow Repair Decision

## Decision

`PHASE8-UX-004` repairs owner-test confusion in the manual OMI workflow only.

The OMI manual screen now labels raw idea capture as owner-authored planning input and labels empty OMI candidates as manual candidate shells when `candidate_content.fields` is empty or missing, `candidate_content.summary` is empty or missing, and `evidence` is empty or missing.

Automatic extraction of characters, locations, timeline, and other story facts remains unavailable from this OMI manual screen unless a later separately authorized task implements and tests a safe extraction route.

## Boundaries

- Approval remains lifecycle metadata only.
- Approval does not extract fields.
- Approval does not mutate Memory/Canon.
- Promotion remains separate and guarded.
- Empty approved candidate shells must not be presented as captured story facts.
- Missing storyform or storyform context is Story Check/context readiness, not OMI raw idea extraction failure.
- Backend validation failures must remain visible to the owner and must not be presented as successful approval.

## Implementation Notes

- The UI maps decision choices to backend-valid statuses: approve -> approved, reject -> rejected, needs_revision -> candidate, pending -> owner_review.
- Approve requires explicit confirmation before submit.
- Empty/manual shell warnings remain visible after approval.
- Promotion readiness copy blocks confusion around empty approved shells and keeps Memory/Canon mutation out of this workflow.
- A source-level UI contract test records the manual workflow labeling and no-extraction/no-promotion boundaries.

## Non-Decisions

- No automatic extraction was added.
- No runtime extraction was executed.
- No model/Ollama generation call was added.
- No Story Check call was added to OMI decision routes.
- No Memory/Canon mutation was added or executed.
- Apply-promotion was not enabled or run.
- No story prose was generated.
- Owner acceptance is not PASS.
- MVP is not complete.
