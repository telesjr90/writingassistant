# PHASE8 Post-Accepted Owner Gate Next Readiness Step Decision

## Decision

Result: SUPERSEDED by owner override.

Superseding decision: `docs/roadmap/decisions/PHASE8-owner-override-block-full-mvp-closeout-omi-extraction-required.md`.

The owner clarified that OMI is still not working for MVP purposes because the current manual OMI workflow only creates empty/manual candidate shells. Full MVP completion closeout is therefore BLOCKED.

This decision no longer selects `PHASE8-MVP-COMPLETE-CLOSEOUT-001` as the next roadmap step.

The active next implementation parent is:

`PHASE8-IMPL-023 - OMI Raw Idea Extraction Candidate Review MVP`.

The next child task is:

`PHASE8-IMPL-023-T001 - Gap Audit and Architecture Decision`.

## Historical Selection

The superseded historical selection was:

`PHASE8-MVP-COMPLETE-CLOSEOUT-001 - Full MVP completion closeout and post-MVP readiness publication`.

That closeout is blocked until `PHASE8-IMPL-023` or an equivalent MVP-required OMI extraction path is complete and validated.

## Superseded Historical Rationale

The final owner gate is accepted by explicit owner decision in `docs/roadmap/decisions/PHASE8-final-owner-accepted-gate-decision.md`.

Owner acceptance is PASS by explicit owner decision, and the MVP owner gate is accepted for the next manual-test/readiness step according to roadmap conventions.

The current roadmap still preserves a distinction between:

- MVP owner gate accepted.
- Full MVP completion closeout.

The historical reasoning selected a full MVP completion closeout before any new implementation parent. That selection is now superseded and blocked by the owner clarification that OMI raw idea extraction is still MVP-required.

## Superseded Historical Selected Next Task

The superseded historical task was `PHASE8-MVP-COMPLETE-CLOSEOUT-001`. It should not proceed as the next step under the current owner override.

The superseded closeout would have:

- Record the accepted owner gate as owner acceptance PASS by explicit owner decision.
- Decide and record whether the full MVP completion closeout is PASS, PARTIAL, or BLOCKED.
- Preserve the historical `PHASE8-UX-003` complete/PARTIAL state and the accepted owner decision separately.
- Preserve `PHASE8-UX-004` as complete/PASS for OMI manual workflow repair only.
- Keep all accepted manual risks and limitations visible.
- Publish the post-MVP readiness/frontier handoff only after the closeout decision is recorded.

## Implementation Parent Decision Superseded

The original decision selected no new implementation parent or runtime task.

That is no longer current. The owner override now selects `PHASE8-IMPL-023` as the active implementation parent.

This implementation parent is now separately published and scoped as `PHASE8-IMPL-023`.

## Accepted Limitations Preserved

- `PHASE8-UX-003-C-CYBER` remains `MANUAL_REVIEW_REQUIRED` because selected-source Story Check diagnostic output was unavailable/fail-closed on missing `storyform.json`.
- A-category blockers were manual owner review only.
- `PHASE8-UX-003` remains complete/PARTIAL historically, even though its owner gate is accepted by explicit owner decision.
- `PHASE8-UX-004` remains complete/PASS for OMI manual workflow repair only.
- OMI manual screen still does not automatically extract characters, locations, timeline, or story facts.
- OMI approval remains lifecycle/status metadata only.
- Approval does not mutate Memory/Canon.
- Promotion remains separate/guarded.
- No automatic extraction, runtime extraction, model/Ollama generation, Story Check call from OMI decision routes, apply-promotion, Memory/Canon mutation, candidate creation, or story prose generation is authorized.

## Non-Authorization Boundary

This decision is documentation/status only. It does not implement or authorize frontend code, backend code, tests, browser harness scripts, product UI changes, Memory/Canon mutation, apply-promotion, extraction, candidates, model/Ollama calls, Story Check route work, context tool generation, or story prose.
