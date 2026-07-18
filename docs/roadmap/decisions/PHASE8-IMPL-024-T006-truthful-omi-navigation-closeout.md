# PHASE8-IMPL-024 T006 Truthful OMI Navigation Closeout

## Decision

`PHASE8-IMPL-024-T006` is complete/PASS through T006A, T006B, and T006C. This closes the functional and truthful OMI navigation workstream without beginning T007A. The parent `PHASE8-IMPL-024` remains active and incomplete.

## Accepted implementation

- T006A commit `64dd90c23a926465ec42718032d79c6181d138e4` establishes App ownership of coarse workspace selection and OMIShell ownership of inner OMI state. App issues a monotonic Dashboard-reset request; OMIShell consumes it through one centralized reset that clears inner view, selected candidate, evidence, and stale opener state without persistence or product mutation.
- T006B commit `14e8c8138621a87973fb469e8233c08180da8374` makes Candidate Detail, Grouped Owner Review, review-only Apply-Promotion Confirmation, and App-owned Approved Memory/Canon actionable. Owner Input, Duplicate Decisions, Promotion Audit Records, Deferred Categories, and Warnings / Health remain truthful unavailable status rows. Disabled Apply-to-Memory/Canon remains unchanged.
- Candidate navigation uses the current collection; grouped review clears candidate/evidence/opener state; promotion review retains a valid current candidate or selects the first current candidate; every exit converges through the T006A reset; Approved Memory/Canon resets inner OMI state before App changes workspace.

## T006C validation

Fresh PASS evidence: `.codex-context/PHASE8-IMPL-024/manual-validation/T006C-navigation-regression/20260718T202605Z`.

- The historical grouped-review source guard reproduced identically in the checkout and a clean archive of starting HEAD: 1 failed, 22 passed, with only `test_t023a_api_and_backend_contract_files_are_unchanged` failing for `frontend/src/api.js`; expected SHA-256 `be637430c152ebaa6d7866dd3c8f7782284dceac4d569adb4275457aae9ee52f`, actual SHA-256 `0d4d0e4046b28ebe144fd4d2ca94949803fa46a4315844737bfa64ce87848811`.
- The separately authorized diagnostic comparison at `.codex-context/PHASE8-IMPL-024/manual-validation/T006C-navigation-regression-diagnostic/20260718T194703Z` proved the focused source selection has the same exit code, 48 failed node IDs, assertion meanings/values, and 349 passing nodes in the checkout and clean starting-HEAD archive. The failures are historical lexical/exact-source guards; two legacy assertions directly reject the owner-accepted T006A workspace callback, while the T006 ownership/reset/delegation guards pass. No test was edited or weakened.
- `frontend/tests/omiGroupedReview.test.mjs` passed; the frontend production build passed with 144 modules transformed; the evidence-local component branch test passed all nine required branches.
- The dashboard, candidate-detail, evidence-drawer, and apply-promotion tracked browser harnesses each passed.
- The dedicated fixture-only browser collector passed 127/127 assertions: 61 desktop, 35 mobile, and 31 loading/empty/controlled-error/component/aggregate assertions. Candidate/evidence, grouped/evidence, promotion/cancel, Approved Memory/Canon, persistent OMI activation, and coarse-workspace cycles reset cleanly; the desktop cycle was repeated twice.
- Product console errors, page errors, request failures, unexpected HTTP 400+ responses, and unexpected fixture GETs were zero. Two intentional controlled 503 responses and their two browser console resource messages were classified separately. Vite/browser-environment output was classified separately.
- POST, PUT, PATCH, DELETE, apply-promotion, review-queue, candidate-decision, promotion creation, Bible/storyform write, scene/note/material write, Story Check/extraction, and model/runtime requests were zero.
- All protected fixture snapshots were identical before and after. The `projects/example` filesystem SHA-256 manifest was also identical before and after.

The installed Impeccable context detector returned NO_PRODUCT_MD. Under the project-owned UI execution wrapper and task-specific authority, product/design initialization was not applicable to this validation-only task and no Impeccable context files were created or modified.

T006C changed no application, test, browser-harness, package, backend, project-data, dependency, API, storage, or runtime file. It performed no product mutation and created no Project Memory requirement.

## Status and next task

- T006A: complete/PASS at commit `64dd90c23a926465ec42718032d79c6181d138e4`.
- T006B: complete/PASS at commit `14e8c8138621a87973fb469e8233c08180da8374`.
- T006C: complete/PASS; fresh evidence `20260718T202605Z`.
- T006 parent: complete/PASS.
- T007A is next/planned, dependency-satisfied, and eligible. It has not begun.

Responsive acceptance, accessibility acceptance, complete keyboard navigation, focus behavior beyond the existing focused harness, browser zoom, and screen-reader work remain deferred to their authorized later workstreams. This closeout is ready for implementation-supervisor review; it is not owner acceptance of T006C or broad application acceptance.
