# PHASE8-IMPL-015 Frontend Read-Only Surface Implementation Decision

## 1. Decision Summary

`PHASE8-IMPL-015-T005` follows the planning path.

The existing frontend metadata does not provide a usable frontend/component test harness without package changes at T005 start. `frontend/package.json` has a `test` script that exits with `Error: no test specified`, and no root `package.json` is present. T005 therefore creates this implementation decision instead of frontend contract tests, does not add production frontend files, and does not change package or dependency files.

The future frontend read-only queue work, if separately authorized, should use:

- API helper candidate: `frontend/src/api/reviewQueue.js`
- Surface candidate: `frontend/src/components/ReviewQueueSurface.jsx`

This decision is a plan only. It does not implement the helper, component, tests, owner action controls, apply-promotion controls, memory/canon write controls, runtime extraction controls, model calls, raw artifact persistence, or generated prose controls.

## 2. Frontend API Helper Candidate

The future helper candidate is `frontend/src/api/reviewQueue.js`.

It may expose read-only functions only:

- list review queue entries;
- get one review queue entry;
- get review queue index;
- get review queue summary.

The helper must use GET-only calls to the `PHASE8-IMPL-015-T004` route surface:

- `GET /api/projects/{project_id}/review-queue`
- `GET /api/projects/{project_id}/review-queue/{queue_entry_id}`
- `GET /api/projects/{project_id}/review-queue/index`
- `GET /api/projects/{project_id}/review-queue/summary`

The helper must not expose POST, PUT, PATCH, DELETE, WebSocket, background task, extraction trigger, owner action command, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model call, or generated prose call behavior.

Forbidden helper behavior:

- no owner action command calls;
- no apply-promotion calls;
- no memory/canon mutation calls;
- no raw artifact persistence calls;
- no runtime extraction calls;
- no model calls;
- no generated prose calls;
- no rewrite, continue, polish, improve, expand, outline, draft, revise, write, or prose-production calls.

## 3. Frontend Surface Candidate

The future surface candidate is `frontend/src/components/ReviewQueueSurface.jsx`.

It must be read-only display only. It may render review queue entries, a selected queue entry, index information, summary information, warnings, errors, empty states, and loading/error states from the read-only helper responses.

It must not implement:

- owner action controls;
- apply-promotion controls;
- canon/memory write controls;
- extraction controls;
- raw artifact persistence controls;
- model-call controls;
- generated-prose controls;
- rewrite, continue, polish, improve, expand, outline, draft, revise, write, or prose-production controls.

No UI copy may suggest approval, canonization, promotion, or truth. The surface is a review support display only, not an owner decision surface and not a promotion workflow.

## 4. Allowed Display Fields

The future surface may display only read-only review support fields from route/helper responses:

- queue entry ID;
- candidate record ID / candidate linkage;
- candidate type/kind if present;
- status / review state if present;
- target category if present;
- lifecycle state if present;
- evidence;
- provenance;
- source document;
- source locator;
- raw refs as support-only metadata;
- confidence as uncertainty/support strength;
- uncertainty flags if present;
- normalization status;
- `human_review_required`;
- warnings/errors from read-only helper responses;
- schema/version metadata;
- pagination/filter/index/summary metadata when read-only;
- read-only/no-promotion/no-canon metadata.

Pending candidates are not canon, and raw refs are support-only metadata. Confidence is uncertainty/support strength, not truth.

## 5. Required Warnings and Labels

The future helper/surface contract must preserve or display these warnings/labels:

- Pending candidates are not canon.
- Queue presence is not approval.
- Valid API response is not owner approval.
- Confidence is uncertainty/support strength, not truth.
- Frontend display is not promotion.
- Owner action execution is not available in this parent.
- owner action execution is not available in this parent.
- Apply-promotion is not available in this parent.
- Memory/canon mutation is not available in this parent.
- Runtime extraction/model calls/generated prose are not available in this parent.

Equivalent copy may be used, but it must keep the same meaning and must not imply approval, canon truth, promotion, apply-promotion, mutation, extraction, model execution, or prose production.

## 6. Accessibility and UX Expectations

Evidence/provenance must be visible or reachable for each rendered queue entry. `human_review_required` must be explicit.

Empty and missing queue states must be clear and non-mutating. Error states must be clear and non-mutating. Loading states must not create project files, queue entries, candidate records, raw artifacts, memory/canon records, or model/extraction work.

The UI must distinguish pending candidates, rejected/error states, malformed or missing support, and read-only metadata without implying owner approval. It must not hide the candidate-first and evidence/provenance-backed nature of the data.

## 7. Future Implementation Sequencing

T005 planning path does not implement frontend files and does not add frontend tests.

`PHASE8-IMPL-015-T006` will validate route/frontend read-only safety and may include conditional hardening only inside approved files. Because T005 did not add production frontend files, T006 frontend checks should remain source/status validation unless a later authorized change adds the approved surface.

`PHASE8-IMPL-016` remains the future owner-action execution workflow parent. Owner action execution is not available in this parent.

`PHASE8-IMPL-017` remains the future apply-promotion plus approved memory/canon mutation parent. Apply-promotion is not available in this parent, and memory/canon mutation is not available in this parent.

Raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy install/run/import, and analysis-only NCP/Subtxt/dramatica-flow runtime integration remain future MVP-required parents. Generated prose, rewrite, continuation, imitation, polish, improvement, expansion, outline generation, chapter generation, write/revise flows, and prose-production paths remain permanently forbidden.

## 8. Boundary Confirmation

This T005 decision adds no backend route changes, no production frontend implementation, no package/dependency changes, no owner action execution, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no model calls, no generated prose, no training data, no JSONL, no datasets, no model artifacts, and no source-cache changes.

Generated context artifacts remain evidence only, not roadmap truth or task completion.
