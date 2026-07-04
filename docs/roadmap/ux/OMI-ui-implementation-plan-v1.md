# OMI UI Implementation Plan v1

Status: planning-only frontend implementation sequence. No runtime code is implemented by this document.

## 1. Purpose

This plan converts the PASS OMI low-fidelity wireframes into a safe frontend implementation sequence for four OMI surfaces:

1. OMI Dashboard
2. Candidate Detail
3. Evidence Drawer
4. Apply-Promotion Confirmation

The plan preserves the project boundary that OMI stores review material only. Owner input, candidates, promotion audit records, readiness state, and evidence are not Memory/Canon. Ready means the handoff packet is complete; Memory/Canon has not changed.

## 2. Source artifacts

Primary UX sources:

- `docs/roadmap/ux/OMI-ui-screen-spec-v1.md`
- `docs/roadmap/ux/OMI-low-fi-wireframes-v1.md`
- `docs/roadmap/ux/PHASE8-UX-001-impeccable-ui-ux-qa-workflow.md`
- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/ux/PHASE8-UX-002-ui-acceptance-matrix.md`
- `docs/roadmap/decisions/PHASE8-UX-002-ui-acceptance-matrix-route-workflow-decision.md`

OMI and Memory/Canon model sources:

- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`

Existing frontend/test sources inspected for future implementation fit:

- `frontend/src/App.jsx`
- `frontend/src/api.js`
- `frontend/src/components/ProjectNav.jsx`
- `frontend/src/components/AnalysisSidebar.jsx`
- `frontend/src/components/ReviewQueuePanel.jsx`
- `frontend/src/components/ApplyPromotionConfirmation.jsx`
- `frontend/src/styles.css`
- `tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py`

## 3. Implementation boundaries

Frontend implementation must remain analysis-only, candidate-first, evidence/provenance-backed, owner-controlled, project-local, and no-prose.

Allowed future frontend behavior:

- Display stored OMI review metadata.
- Display stored owner-authored raw idea metadata as owner input.
- Display stored candidates as candidates only.
- Display promotion audit records as audit-only.
- Display approved Memory/Canon counts only from applied Memory/Canon records.
- Let the owner navigate review surfaces and make review metadata decisions when an authorized API already supports that behavior.
- Keep unavailable and disabled risky actions visible with programmatically associated reasons.

Forbidden future frontend behavior:

- Generated summaries.
- Assistant-composed text.
- Source-text transformation.
- Model/Ollama calls.
- Candidate creation unless a later task explicitly authorizes that track.
- Memory/Canon mutation except through a separately authorized apply-promotion implementation.
- Treating owner input, candidates, promotion audit records, evidence, confidence, queue presence, or readiness as truth.
- Controls for write, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, or story-prose production.

## 4. Existing frontend surfaces to inspect

Future coding tasks should inspect these surfaces before editing:

- `frontend/src/App.jsx`: current workspace view state, OMI load/refresh state, review panels, and project-scoped data loading.
- `frontend/src/components/ProjectNav.jsx`: current project navigation pattern and workspace entry points.
- `frontend/src/components/ReviewQueuePanel.jsx`: current candidate-only review wording, review queue fixture labels, and apply-promotion embedding.
- `frontend/src/components/ApplyPromotionConfirmation.jsx`: current confirmation gate, destination fields, blocker computation, and submit behavior.
- `frontend/src/components/AnalysisSidebar.jsx`: current no-prose, raw artifact, diagnostic-only, and NOT_EXPOSED status patterns.
- `frontend/src/styles.css`: current operational UI classes, metadata grids, review panels, forms, badges, and responsive constraints.

## 5. Existing API/helper surfaces to inspect

Future coding tasks should inspect these helpers before adding new ones:

- `getOMI(projectId)` for dashboard and candidate list data.
- `getOMIIdea(projectId, ideaId)` if a raw idea source link is shown.
- `getOMICandidate(projectId, candidateId)` for Candidate Detail once detail-level routing exists.
- `updateOMICandidateDecision(projectId, candidateId, payload)` for owner review metadata only.
- `getOMIPromotion(projectId, promotionId)` and `getOMIPromotions(projectId)` for audit-only summaries.
- `fetchReviewQueueEntries(projectId)` for current review queue entries and apply-promotion fixture state.
- `submitApplyPromotion(projectId, payload)` only inside Apply-Promotion Confirmation, and only when every blocker is absent and final owner confirmation is true.
- `isSafeReviewRouteId`, `APPLY_PROMOTION_DESTINATION_TYPES`, and review/apply helper validation.

Do not add API calls that create candidates, call models, run extraction, mutate Memory/Canon, or transform source text unless a later task explicitly authorizes that behavior.

## 6. Proposed component map

Recommended future components:

- `OMIShell`: route/workspace wrapper with active project label, OMI boundary banner, local OMI navigation, and candidate/canon status strip.
- `OMIBoundaryBanner`: static boundary copy and standard no-prose refusal reference.
- `OMICandidateCanonStatusStrip`: candidate count, blocker count, handoff-ready count, promotion audit count, and approved Memory/Canon unchanged snapshot.
- `OMIDashboard`: operational workflow table and mobile stacked rows.
- `OMIWorkflowStatusRow`: one safe navigation action per workflow area.
- `OMICandidateDetail`: candidate header, action bar, field review table, duplicate/dependency panel, readiness checklist, and read-only references.
- `OMICandidateFieldTable`: structured field rows with stored proposed values and field-level review state.
- `OMIPromotionReadinessChecklist`: gate list with checked/blocked states and blocker IDs.
- `OMIEvidenceDrawer`: contextual drawer or mobile sheet for stored evidence/provenance metadata.
- `OMIApplyPromotionRoute`: guarded route-backed confirmation wrapper.
- `OMIApplyPromotionBlockers`: visible blocker list semantically associated with the final action.

Existing components may be refactored only when needed by a coding task. The safest path is to add focused OMI components rather than expanding `App.jsx` into a large conditional renderer.

## 7. Proposed route/state map

The route/state model should be explicit enough for browser evidence but small enough for the current app:

- Dashboard: `workspace=omi` or route-equivalent state `omiView=dashboard`.
- Candidate Detail: `workspace=omi`, `omiView=candidate-detail`, `candidateId`.
- Evidence Drawer: state overlay keyed by `evidenceScope`, `candidateId`, optional `fieldKey`, `promotionId`, or approved-memory reference ID.
- Apply-Promotion Confirmation: route-backed state such as `omiView=apply-promotion`, `candidateId`, `queueEntryId` or `promotionId`.

State rules:

- Switching filters must not change owner decisions.
- Opening OMI must not create candidates.
- Opening Candidate Detail must not mutate candidate state.
- Opening Evidence Drawer must not edit candidates, promotion records, or approved Memory/Canon.
- Apply-Promotion final submit state must be disabled whenever any visible blocker exists.
- Any future URL or route state must remain active-project scoped.

## 8. OMI Dashboard implementation slice

Target user-visible behavior:

- The owner sees an operational overview of owner input, candidates, grouped review, duplicate decisions, promotion handoff readiness, promotion audit records, deferred categories, approved Memory/Canon snapshot, and warnings.
- The dashboard uses a table on desktop and stacked workflow rows on mobile.
- Each workflow row has exactly one safe navigation action.
- `Apply to Memory/Canon` is disabled with a visible reason.

Files likely touched:

- `frontend/src/App.jsx`
- `frontend/src/components/ProjectNav.jsx`
- Future `frontend/src/components/OMIShell.jsx`
- Future `frontend/src/components/OMIDashboard.jsx`
- `frontend/src/styles.css`
- Future focused source/browser tests

Components likely created or modified:

- Create `OMIShell`, `OMIBoundaryBanner`, `OMICandidateCanonStatusStrip`, `OMIDashboard`, and `OMIWorkflowStatusRow`.
- Modify `ProjectNav` to expose a dedicated OMI workspace entry only if the route/workspace model needs it.
- Modify `App.jsx` to select the OMI Dashboard without changing existing editor/review behavior.

API calls likely needed:

- Use existing `getOMI(activeProjectId)`.
- Optionally use existing promotion and approved-memory summary helpers only if already present; otherwise show approved Memory/Canon as zero/unchanged or unavailable without inference.

Mock/fixture data needed:

- Prefer loaded `omiData` from `getOMI`.
- If a source test needs deterministic browser markers, use UI-only zero states and labels, not generated candidates.
- Do not create runtime candidate fixtures in project data.

States to display:

- Loaded OMI counts.
- Zero owner input.
- Zero candidates.
- Evidence linked/missing.
- Provenance linked/missing.
- Blocked handoff items.
- Promotion audit records as `Promotion Audit Record` and `Not Applied to Memory/Canon`.
- Approved Memory/Canon snapshot as separate and unchanged.

Disabled states:

- Disabled `Apply to Memory/Canon` with: `Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.`
- Disabled extraction/model actions as unavailable if shown.

Empty/loading/error states:

- Loading: keep boundary banner visible and show `Loading OMI status`.
- Empty: show zero rows and safe navigation back to project workspace or owner input.
- Error: show degraded OMI warning, no inferred counts, and disable readiness/apply actions.

Accessibility requirements:

- Use a real table or accessible row group.
- Give each row action an accessible name that includes the workflow area.
- Associate disabled apply reason with the disabled control using `aria-describedby` or equivalent.
- Status badges must include text and not rely on color alone.

Test expectations:

- Source tests should verify data-testid markers for `omi-dashboard`, `omi-boundary-banner`, `omi-dashboard-candidate-count`, `omi-dashboard-approved-memory-snapshot`, disabled apply reason, and absence of generated-prose controls.
- Browser tests should prove opening the dashboard does not create candidates or change Memory/Canon counts.

Browser evidence expectations:

- Desktop screenshot: operational table, boundary banner, disabled apply reason, separated approved Memory/Canon snapshot.
- Mobile screenshot: stacked rows, banner above filters, full-width safe row actions.
- Browser assertions: candidate counts do not appear as approved Memory/Canon.

What must not happen:

- No inline candidate approval.
- No enabled apply-promotion.
- No model/Ollama controls.
- No candidate creation.
- No Memory/Canon mutation.
- No metric-card dashboard that implies canon success.

## 9. Candidate Detail implementation slice

Target user-visible behavior:

- The owner sees one candidate as a review packet with header/status, destination/source, candidate-level actions, field-level review rows, evidence/provenance, duplicate/dependency review, promotion readiness, and read-only approved Memory/Canon references.
- Candidate-level approval prepares a handoff only; it does not update Memory/Canon.

Files likely touched:

- `frontend/src/App.jsx`
- `frontend/src/api.js` only if existing detail helpers are insufficient.
- Future `frontend/src/components/OMICandidateDetail.jsx`
- Future `frontend/src/components/OMICandidateFieldTable.jsx`
- Future `frontend/src/components/OMIPromotionReadinessChecklist.jsx`
- `frontend/src/styles.css`
- Future focused source/browser tests

Components likely created or modified:

- Create candidate detail, field table, duplicate/dependency panel, readiness checklist, and read-only reference components.
- Reuse existing OMI metadata/grid styling where possible.

API calls likely needed:

- `getOMICandidate(activeProjectId, candidateId)` for selected detail.
- `getOMIIdea(activeProjectId, ideaId)` only for source metadata if needed.
- `updateOMICandidateDecision(activeProjectId, candidateId, payload)` only for owner review metadata when enabled by a future task.
- No apply-promotion call from Candidate Detail.

Mock/fixture data needed:

- Stored candidate record with structured fields, owner decision, destination, provenance, evidence, duplicate/dependency metadata, blockers, and optional linked promotion record.
- Use static empty state when no candidate exists; do not create candidates.

States to display:

- `Candidate: Pending Review`
- `Candidate: Owner Approved`
- `Destination`
- `Source`
- `Field`, `Proposed value`, `Decision`, `Evidence`, `Provenance`
- `Confidence indicates support strength, not truth.`
- Duplicate/dependency state.
- Promotion readiness checklist.
- `Approved Memory/Canon links` as read-only references.
- `Promotion Audit Record` and `Not Applied to Memory/Canon`.

Disabled states:

- Candidate approval disabled when field decisions, evidence/provenance, destination, duplicate decisions, dependency review, or schema support are incomplete.
- Field approval disabled when field evidence/provenance is missing or unsupported.
- Apply to Memory/Canon disabled or absent; if shown, reason must be associated with the disabled control.

Empty/loading/error states:

- Loading candidate.
- Candidate not found with return to dashboard/list.
- Unsupported schema blocks handoff.
- Missing evidence/provenance blocks readiness.
- No approved Memory/Canon links shows `No applied Memory/Canon links`.

Accessibility requirements:

- Field table supports keyboard traversal.
- Field-level buttons include field names in accessible labels.
- Readiness checklist exposes checked/unchecked state and blocker text.
- Disabled reasons are associated with controls via `aria-describedby` or equivalent.
- Read-only references must not look editable.

Test expectations:

- Source tests should verify candidate-only labels, readiness copy, no enabled apply-promotion, and no prose controls.
- Browser tests should verify field approval does not approve the candidate, and candidate approval does not change Memory/Canon.

Browser evidence expectations:

- Desktop screenshot: field table main workspace, right rail or lower evidence/readiness panel.
- Mobile screenshot: `Fields`, `Evidence`, and `Readiness` sections/tabs with candidate actions above field actions.
- Assertions: ready state copy says Memory/Canon has not changed.

What must not happen:

- No `Approve all fields and promote`.
- No generated replacement text.
- No editable approved Memory/Canon records.
- No duplicate merge that deletes or overwrites candidates.
- No confidence label that implies truth.

## 10. Evidence Drawer implementation slice

Target user-visible behavior:

- The owner opens contextual evidence from Dashboard, Candidate Detail, audit record, or approved-memory reference and sees stored source/evidence/provenance metadata.
- Desktop uses a right-side drawer; mobile uses a full-screen sheet.
- Evidence review actions update review metadata only where authorized.

Files likely touched:

- Future `frontend/src/components/OMIEvidenceDrawer.jsx`
- `frontend/src/App.jsx` or OMI route state owner.
- `frontend/src/styles.css`
- Future focused source/browser tests

Components likely created or modified:

- Create evidence drawer/sheet.
- Add drawer trigger buttons to Dashboard rows and Candidate Detail field rows.
- Add source-open/copy action controls with disabled reasons.

API calls likely needed:

- Prefer stored evidence/provenance already loaded with candidate, group, promotion, or approved-memory summary.
- Add read-only source-record fetch only in a later authorized task if existing APIs expose it safely.
- No generation, summarization, extraction, or apply-promotion calls.

Mock/fixture data needed:

- Stored evidence object with scope, source type, source location, quote exactness, confidence/support label, original wording excerpt, evidence summary, supports-claim note, limitations, provenance chain, related IDs, timestamps, source hash, and snapshot hash.
- Broken/missing source cases for disabled open/copy controls.

States to display:

- Scoped loaded evidence.
- No source location.
- No excerpt stored.
- Support uncertain.
- Source record loading/missing/corrupt/unsafe/out of range.
- Source belongs to another project.
- Hash not recorded.

Disabled states:

- Copy/open source disabled when source location is missing, unsafe, out of range, corrupt, cross-project, or unavailable.
- Apply to Memory/Canon unavailable from the drawer if a boundary marker is shown.
- Disabled source-opening reasons must be semantically associated with controls.

Empty/loading/error states:

- Loading drawer content.
- Missing source record with stored metadata still visible.
- Broken related ID with unsafe navigation disabled.
- Source open failed closed with no inferred replacement evidence.

Accessibility requirements:

- Focus trap on desktop drawer.
- Return focus to opener on close.
- Labelled close button at top and bottom on mobile.
- Drawer title includes scope.
- Footer action order is predictable.
- Original wording/excerpt has readable line length and wraps safely.

Test expectations:

- Source tests should verify stored-review-metadata labels and absence of summary generation controls.
- Browser tests should verify focus trap, close/return focus, disabled source-open reasons, and no mutation from opening evidence.

Browser evidence expectations:

- Desktop screenshot: right drawer over a candidate/detail context.
- Mobile screenshot: full-screen evidence sheet with close visible at top and bottom.
- Assertions: evidence summary, supports-claim note, excerpt, and provenance are displayed as stored metadata only.

What must not happen:

- No edit candidate content.
- No rewrite source.
- No generate summary from source.
- No promote candidate.
- No apply to Memory/Canon.
- No mark canon truth.

## 11. Apply-Promotion Confirmation implementation slice

Target user-visible behavior:

- The owner sees a guarded route-backed confirmation surface with candidate snapshot, destination, evidence/provenance, duplicate/dependency state, approved Memory/Canon before-state, audit preview, blockers, explicit owner confirmation, cancel/return, and final action.
- The final action is disabled whenever any blocker is visible.

Files likely touched:

- `frontend/src/components/ApplyPromotionConfirmation.jsx`
- Future `frontend/src/components/OMIApplyPromotionRoute.jsx`
- Future `frontend/src/components/OMIApplyPromotionBlockers.jsx`
- `frontend/src/App.jsx`
- `frontend/src/api.js` only if existing helper validation needs frontend-only guard expansion.
- `frontend/src/styles.css`
- Future focused source/browser tests

Components likely created or modified:

- Convert or wrap current apply-promotion confirmation into a route-backed OMI confirmation surface.
- Add blocker list above confirmation.
- Add before-state and audit preview sections.
- Add final action with associated disabled reason IDs.

API calls likely needed:

- `fetchReviewQueueEntries(activeProjectId)` or selected queue entry state for candidate/review context.
- `submitApplyPromotion(activeProjectId, payload)` only when all blockers are absent and owner confirmation is true.
- Existing promotion/audit read helpers for audit preview if available.

Mock/fixture data needed:

- Queue entry or handoff packet with candidate ID/type, destination, evidence refs, provenance refs, source locator refs, duplicate/dependency status, before-state count, and audit preview.
- Invalid packet cases for each blocker.

States to display:

- Valid handoff ready packet.
- Missing owner approval.
- Missing destination.
- Missing evidence/provenance/source locator.
- Duplicate unresolved.
- Dependency unresolved.
- Missing owner actor/final confirmation.
- Unsupported destination.
- Approved Memory/Canon before-state.
- Audit preview.
- Submit pending, success audit result, failure with unchanged Memory/Canon copy.

Disabled states:

- Final action disabled when any blocker is visible.
- Owner confirmation checkbox disabled when base handoff packet is invalid.
- Submit disabled while loading/submitting.
- All disabled reasons must be associated with controls using `aria-describedby` or equivalent.

Empty/loading/error states:

- No handoff packet selected.
- Candidate not found.
- Handoff packet loading.
- Audit preview unavailable.
- Apply-promotion request failed; show unchanged Memory/Canon copy.

Accessibility requirements:

- Confirmation heading identifies it as apply-promotion confirmation.
- Blockers appear before the checkbox/final action in reading order.
- Checkbox label explicitly says owner final confirmation.
- Final action accessible name includes destination and candidate where possible.
- Cancel/return remains reachable and lower risk than confirm.

Test expectations:

- Source tests should verify explicit owner confirmation, audit evidence, blocker markers, and final action disabled conditions.
- Browser tests should verify blocked confirmation cannot submit, invalid promotion fails closed, and rejected/failed promotion leaves approved Memory/Canon unchanged.

Browser evidence expectations:

- Desktop screenshot: route-backed confirmation with blockers above final action.
- Mobile screenshot: stacked sections with final action disabled and reason visible.
- Assertions: final action disabled whenever a blocker exists; no hidden apply path.

What must not happen:

- No apply-promotion from Dashboard, Candidate Detail, or Evidence Drawer.
- No final submit while any blocker is visible.
- No automatic promotion after candidate approval.
- No hidden Memory/Canon mutation.
- No generated prose.

## 12. Stored-review-metadata-only rendering rules

These UI regions display stored review metadata only:

- Evidence summary.
- Supports-claim note.
- Proposed value.
- Structured field summary.
- Original wording excerpt.
- Evidence/provenance summary.
- Source location summary.
- Promotion audit preview.
- Approved Memory/Canon before-state.

Implementation rules:

- Render strings and structured values already returned by project-local APIs or fixtures.
- Do not synthesize a summary from source text.
- Do not call a model or local runtime to explain evidence.
- Do not transform source wording into cleaner prose.
- Do not create assistant-authored replacement copy for candidate values.
- Missing values must render as missing, not inferred.

## 13. Accessibility implementation requirements

- Disabled reasons must be programmatically associated with disabled controls through `aria-describedby`, `aria-errormessage`, fieldsets/legends, or an equivalent semantic association.
- Status badges must include visible text and must not rely on color alone.
- Tables must use semantic table markup or an accessible row-group pattern.
- Drawer/sheet implementation must manage focus and restore focus to the opener.
- Long IDs, paths, source locators, and field values must wrap or truncate with accessible full-value access.
- Keyboard order must follow the visible workflow: boundary, filters, rows, detail, evidence, readiness, confirmation.
- Error states that block workflow actions should use `role="alert"` or equivalent when they appear after user action.

## 14. Mobile/responsive implementation requirements

- Dashboard table collapses to stacked workflow rows.
- Candidate Detail collapses to `Fields`, `Evidence`, and `Readiness` sections/tabs.
- Evidence Drawer becomes a full-screen sheet on mobile.
- Apply-Promotion Confirmation uses stacked sections with blockers before confirmation.
- Touch targets should be full-width or at least comfortably sized in stacked mobile rows.
- Critical IDs and paths must remain visible or copyable; they must not be available only in hover tooltips.
- Avoid horizontal scrolling for primary review flows.

## 15. Disabled-state implementation requirements

- Risky actions should be disabled with visible reasons, not silently hidden, when showing the boundary improves safety.
- Every disabled reason should start with `Disabled:` for present but unavailable actions, or `Unavailable:` for out-of-scope capabilities.
- The final Apply-Promotion action must be disabled whenever any blocker is visible.
- Disabled Dashboard apply reason must list owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.
- Disabled Candidate Detail approval must name the missing handoff gate.
- Disabled Evidence Drawer source actions must name the source issue.
- Disabled reasons must be connected to controls in the DOM, not only nearby visually.

## 16. Acceptance test strategy

Recommended layers:

- Source-contract tests for required markers, labels, disabled reasons, and absence of forbidden controls.
- Focused component/unit tests if the frontend test stack gains component testing.
- Browser/Playwright tests for visible workflow evidence, mobile/desktop layout, disabled controls, focus behavior, and no mutation proof.
- Existing roadmap validation for docs consistency.

Future source test targets:

- `omi-dashboard`
- `omi-boundary-banner`
- `omi-candidate-canon-status`
- `omi-dashboard-approved-memory-snapshot`
- `omi-candidate-detail`
- `omi-evidence-drawer`
- `omi-apply-promotion-confirmation`
- `omi-apply-promotion-final-action`
- `aria-describedby` or explicit reason IDs for disabled controls.

Negative test targets:

- No `rewrite`, `continue`, `outline`, `draft`, `polish`, `improve`, `expand`, `imitate`, or generated-prose control on OMI routes.
- No enabled apply-promotion outside Apply-Promotion Confirmation.
- No candidate count displayed as approved Memory/Canon.

## 17. Playwright/browser evidence strategy

Each implementation slice should produce browser-visible evidence:

- Desktop and mobile screenshots for the implemented OMI surface.
- Assertions for active project scoping.
- Assertions that boundary copy is visible.
- Assertions that risky actions are disabled with associated reasons.
- Assertions that opening the surface does not create candidates.
- Assertions that Memory/Canon counts remain unchanged unless a separately authorized apply-promotion test explicitly exercises the confirmation path.
- For Apply-Promotion Confirmation, assertions that blocked packets cannot submit and failure/rejection keeps approved Memory/Canon unchanged.

Do not run Playwright against external SaaS or external reference sites for this OMI implementation sequence.

## 18. Validation commands

For this docs-only plan:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
git diff --check
git status --short --branch
```

For future frontend coding tasks, add focused frontend validation such as:

```bash
npm --prefix frontend run build
```

Add focused pytest or Playwright commands only when the task authorizes those tests.

## 19. Implementation task sequence

Fixed implementation order:

1. OMI Dashboard
2. Candidate Detail
3. Evidence Drawer
4. Apply-Promotion Confirmation

Recommended first coding task: **A. OMI Dashboard only**.

Why this is safest:

- It establishes the route/workspace entry, persistent boundary banner, candidate/canon separation, disabled apply reason, loading/empty/error states, and responsive operational layout without introducing owner decision mutations.
- It can use existing `getOMI` data and safe zero states.
- It avoids early apply-promotion wiring and avoids creating candidates.
- It gives browser evidence for the most important boundary: OMI review counts are not approved Memory/Canon.

Do not choose these as the first coding task:

- B. Candidate Detail only: it requires candidate selection/routing and decision/readiness state before the OMI shell is proven.
- C. Shared OMI shell + Dashboard: acceptable only if the shell is strictly necessary, but it is broader than Dashboard only.
- D. Shared OMI shell + all four screens as static mock surfaces: too broad and risks normalizing nonfunctional confirmation surfaces before safety gates are implemented.

Detailed sequence:

1. Implement Dashboard only with boundary banner, dashboard rows, disabled apply reason, project-scoped labels, and zero/error states.
2. Add Candidate Detail route/state and stored field review display without apply-promotion.
3. Add Evidence Drawer as stored-metadata-only overlay/sheet with focus handling and disabled source action reasons.
4. Convert Apply-Promotion Confirmation into a route-backed guarded handoff surface with visible blockers, before-state, audit preview, final owner confirmation, and final action disabled while any blocker exists.

## 20. Explicit non-goals

- No frontend code in this docs task.
- No backend code.
- No test edits.
- No candidate creation.
- No Memory/Canon mutation.
- No apply-promotion execution.
- No model/Ollama calls.
- No extraction runtime.
- No Impeccable initialization.
- No `PRODUCT.md` or `DESIGN.md`.
- No training data, JSONL, dataset manifest, or model artifact changes.
- No staging, commit, or push.

## 21. Risks and mitigations

Risk: Dashboard counts look like success metrics or approved truth.

Mitigation: Use workflow rows, not metric cards; keep approved Memory/Canon snapshot separated and labeled unchanged.

Risk: Candidate approval is mistaken for canon mutation.

Mitigation: Label approval as `Approve Candidate for Handoff` and show `Ready means the handoff packet is complete. Memory/Canon has not changed.`

Risk: Evidence display implies canon truth.

Mitigation: Show `Evidence supports review; it is not canon truth until owner approval and apply-promotion are complete.`

Risk: Disabled reasons are visible but inaccessible.

Mitigation: Require `aria-describedby` or equivalent semantic association for every disabled control reason.

Risk: Apply-Promotion Confirmation submits with a visible blocker.

Mitigation: Derive final disabled state from the same blocker list rendered to the user; test each blocker.

Risk: UI developers accidentally add summarization or rewrite affordances.

Mitigation: Use stored-review-metadata-only rendering rules and source tests for forbidden control labels.

Risk: Existing review queue confirmation behavior conflicts with route-backed confirmation.

Mitigation: Wrap or migrate the existing component after Dashboard, Candidate Detail, and Evidence Drawer are stable; do not make apply-promotion available from earlier screens.

## 22. Open implementation questions

- Should the OMI Dashboard live as a new top-level workspace view or under the existing editor/review area?
- Should OMI use URL routes, internal workspace state, or both for browser evidence?
- Which existing backend OMI response fields are stable enough for dashboard counts without adding new API support?
- Should Candidate Detail load from `getOMICandidate` directly or from the already loaded `getOMI` payload until detail-specific APIs are verified?
- What is the exact shape of stored field-level evidence and duplicate/dependency metadata in current candidate records?
- Should Apply-Promotion Confirmation remain embedded in Review Queue until the route-backed OMI confirmation is implemented, or should future work first hide it behind the new route?
- What approved Memory/Canon summary API, if any, should Dashboard use before future memory folder implementation exists?
- Which Playwright harness should own the four-screen OMI browser evidence sequence?
