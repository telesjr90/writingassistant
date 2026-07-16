# PHASE8-IMPL-024 - Application UI/UX Audit Integrity and Acceptance Repair

## Status

Published and active as the release-blocker repair parent.

T001 OMI-guided creation integrity is complete/PASS through T001A-T001D.

T002 Story Check grounding integrity is complete/PASS through T002A-T002E. Live validation evidence: `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z` (PASS, 22 diagnostics: 17 unverified + 5 quarantined, exact source identity/hash matched, fail-closed on unsupported claims, non-mutating).

Latest completed child: `PHASE8-IMPL-024-T003A - Context-availability/readiness contract for Bible, storyform, and storyform-context` (`complete/PASS`).

Next implementation task: `PHASE8-IMPL-024-T003B - Conditional frontend loading with distinct absent, invalid, and request-failure states`. T003 remains active/in progress; T003C remains planned.

The application is not ready for broad owner acceptance or MVP readiness. T001 has repaired the guided-creation P0 defect; T002 has repaired the Story Check grounding P0 defect; T003A has implemented the backend readiness contract. T003B conditional frontend loading and T003C console/network validation remain incomplete.

## Controlling Evidence

- Audit synthesis: `.codex-context/application-uiux-audit/Pasted text(159).txt`
- Successful reconciliation summary: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/evidence-summary.md`
- Collector report: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/collector-report.json`
- Project manifest diff: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/project-manifest-diff.json`
- Phase evidence: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/phases/`

The failed `playwright-advanced` runs are excluded from product evidence. They are failed collector-development attempts and cannot classify any workflow as PASS or FAIL.

T001 final PASS evidence: `.codex-context/PHASE8-IMPL-024/manual-validation/T001C-guided-creation/20260712T205343Z`. The prior BLOCKED locator-ambiguity run at `.codex-context/PHASE8-IMPL-024/manual-validation/T001C-guided-creation/20260712T203726Z` remains preserved as superseded validation history. Closeout decision: `docs/roadmap/decisions/PHASE8-IMPL-024-T001-omi-guided-creation-integrity-closeout.md`.

T002 final PASS evidence: `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z`. The prior BLOCKED missing-storyform run at `20260712T235515Z` and the validation-script-failure run at `20260713T021350Z` remain preserved as superseded validation history. Closeout decision: `docs/roadmap/decisions/PHASE8-IMPL-024-T002-story-check-grounding-integrity-closeout.md`.

## Release Blockers

### P0-A - OMI-guided creation integrity (repaired/closed by T001 PASS)

T001A/T001B implemented the dedicated bounded guided-creation contract and frontend path. Exact owner-authored idea and note text is stored through existing OMI idea/Notes storage with owner provenance, linked IDs, `model_generated: false`, non-canon state, `creation_method: omi_guided`, atomic rollback, `failed_rolled_back`, and exceptional `recovery_required`; blank creation is unchanged. T001C validated deterministic and disposable API/browser behavior with no prohibited side effects.

### P0-B - Story Check accepts contradictory ungrounded findings (repaired/closed by T002 PASS)

The selected source now carries exact source ID and content hash; every diagnostic carries a deterministic verification state (`verified`/`unverified`/`quarantined`); unsupported factual warnings are quarantined rather than presented as verified; source mismatch fails closed. Story Check remains non-mutating and model output remains non-canon. Live validation returned 22 diagnostics (17 unverified + 5 quarantined, zero falsely verified) with exact source identity matched. Future architecture ungrounded-model-output risk is carried into PHASE8-IMPL-025-T007.

<!-- PHASE8-IMPL-024-UI-ORDER:START -->
## Owner-approved UI execution order

The UI/UX roadmap follows this sequence:

1. Fix P0/P1 functional and integrity issues.
2. Use Impeccable for evidence-based UI review.
3. Decide between shadcn/ui, React Aria, Radix Primitives, or retaining native/custom components.
4. Standardize the design system according to that recorded decision.
5. Complete responsive and accessibility work against the standardized component foundation.

Task identifiers remain stable. Dependencies and the documented workstream
order establish execution sequence:

- Functional and integrity work: `T001`, `T002`, `T003`, then `T006`.
- Impeccable evidence review: `T007A`.
- Component-library decision: `T007B`.
- Design-system and shared-component standardization: `T007C`.
- Responsive containment and validation: `T004`.
- Accessibility semantics, target sizing, and keyboard validation: `T005`.
- Remaining validation suites: `T008`.

The controlling indexed order is therefore `T003 -> T006 -> T007 -> T004 ->
T005 -> T008`. T003B and T003C close T003 before T006 begins. T007 follows
T006, and T007C must complete before either T004 or T005 begins. This order is
already owner-approved and does not require another decision gate.

This ordering prevents premature visual polish, avoids selecting a component
library without evidence, and avoids repeating responsive and accessibility
work after shared components are replaced.

<!-- PHASE8-IMPL-024-UI-ORDER:END -->

## Child Task Hierarchy

Lettered children are bounded execution slices under the indexed workstream child.

### `PHASE8-IMPL-024-T001` - OMI-guided creation integrity

- `PHASE8-IMPL-024-T001A` - Backend guided-creation contract and storage (`complete/PASS`; commit `77d9968d1b8eb893a76bdd4f485c0415fb75f907`).
- `PHASE8-IMPL-024-T001B` - Frontend request and confirmation wiring (`complete/PASS`; commit `5bcaed06e429a8d6e1d5f65974c5a08fe7185656`).
- `PHASE8-IMPL-024-T001C` - Focused deterministic tests and disposable-project Playwright validation (`complete/PASS`; final evidence `20260712T205343Z`; prior BLOCKED run preserved as superseded history).
- `PHASE8-IMPL-024-T001D` - Documentation and status closeout (`complete/PASS`).

### `PHASE8-IMPL-024-T002` - Story Check grounding integrity

- `PHASE8-IMPL-024-T002A` - Source identity/hash and diagnostic contract (`complete/PASS`; commit `1ee250b9c1432651436149c3f377ce69790d7add`).
- `PHASE8-IMPL-024-T002B` - Deterministic grounding validator (`complete/PASS`; commit `cde5f8855925c1a8245d3c9b5c939de8b93316eb`).
- `PHASE8-IMPL-024-T002C` - Engine, normalizer, route, and UI integration (`complete/PASS`; commit `02e9e5e40ff63aaa2e092a98ca6f9a1a7dc38ad2`).
- `PHASE8-IMPL-024-T002D` - Fixture regressions and live manual validation (`complete/PASS`; commit `467b7b747c7544054685053f5a44154e4e5eefe1`; final evidence `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z`; earlier BLOCKED run at `20260712T235515Z` preserved as superseded history).
- `PHASE8-IMPL-024-T002E` - Documentation and status closeout (`complete/PASS`).

The grounding validator must avoid over-filtering potentially useful diagnostics: unsupported factual warnings are quarantined or explicitly unverified, while supported non-factual diagnostics may remain visible under their correct evidence status.

Architecture coordination: T002 owns the immediate P0 exact-selected-source ID/hash, direct factual evidence, deterministic grounding, unsupported-output quarantine, and source-mismatch failure repair. The planned `PHASE8-IMPL-025-T007` must consume and extend this result into the shared `AnalysisRunManifest`/evidence-ledger architecture and the separate Ollama roles; it must not create a duplicate or conflicting Story Check grounding contract. PHASE8-IMPL-025 remains planned until T001/T002 complete.

### `PHASE8-IMPL-024-T003` - Optional-resource handling

- `PHASE8-IMPL-024-T003A` - Context-availability/readiness contract for Bible, storyform, and storyform-context (`complete/PASS`; depends on T002E). Decision: `docs/roadmap/decisions/PHASE8-IMPL-024-T003A-context-availability-readiness-contract.md`.
- `PHASE8-IMPL-024-T003B` - Conditional frontend loading with distinct absent, invalid, and request-failure states (`next`; depends on T003A).
- `PHASE8-IMPL-024-T003C` - Console/network regression validation (`planned`; depends on T003B).

T003A provides the deterministic `project_context_readiness.v1` backend contract at `GET /api/projects/{project_name}/context-readiness`. Normal optional-resource absence returns an explicit successful readiness result; invalid resources remain distinct; unsafe IDs/locators, missing projects, permission failures, and unexpected failures retain transport-error semantics. Existing direct resource endpoints retain their prior behavior. T003B owns conditional frontend use of this contract, and T003C owns console/network regression validation.

### `PHASE8-IMPL-024-T006` - Truthful OMI navigation

- `PHASE8-IMPL-024-T006A` - Resettable OMI Dashboard navigation and `App.jsx`/`OMIShell.jsx` state-owner decision (`planned`; depends on T003C).
- `PHASE8-IMPL-024-T006B` - Repeated inner-view navigation and enabled actions only for implemented destinations (`planned`; depends on T006A).
- `PHASE8-IMPL-024-T006C` - Navigation regression validation and closeout (`planned`; depends on T006B).

Unavailable workflows must render as honest status rows, not enabled no-op buttons. Duplicate resolution, audit mutation, and apply-promotion must not be implemented merely to make a dashboard button work.

### `PHASE8-IMPL-024-T007` - Evidence-based UI review, component-library decision, and design-system standardization

- `PHASE8-IMPL-024-T007A` - Run an evidence-based Impeccable UI review after the P0/P1 functional work, consolidate findings with the existing Playwright evidence, and define the prioritized information-architecture and shared-component requirements (`planned`; depends on T006C).
- `PHASE8-IMPL-024-T007B` - Record the owner-approved component-foundation decision between shadcn/ui, React Aria, Radix Primitives, or retaining native/custom components; evaluate accessibility, styling, migration cost, dependency impact, local-first compatibility, and fit with the existing React/Vite application before adoption (`planned`; depends on T007A).
- `PHASE8-IMPL-024-T007C` - Standardize the design system and shared boundary, metadata, status, empty, loading, error, action, disclosure, and owner-attention components according to the T007B decision; retain complete provenance and safety details and validate the standardized information architecture (`planned`; depends on T007B).

Impeccable is an evidence-based design and critique tool, not a runtime component dependency. T007A findings inform T007B but do not select a component library automatically.

T007B is a decision task. It must not install shadcn/ui, React Aria, Radix Primitives, Tailwind, or another component dependency until the decision is documented and its migration scope is explicitly authorized.

T007C implements the approved component strategy before responsive and accessibility repair, preventing those later workstreams from being performed against components that will immediately be replaced.

### `PHASE8-IMPL-024-T004` - Responsive containment

- `PHASE8-IMPL-024-T004A` - Document-level overflow repair and native-control containment (`planned`; depends on T007C).
- `PHASE8-IMPL-024-T004B` - OMI status/metric wrapping, local wide-table containment, and wider contextual OMI workspace (`planned`; depends on T004A).
- `PHASE8-IMPL-024-T004C` - Responsive validation at 1440, 1280, 834, 640, 390, and 320 pixels (`planned`; depends on T004B).

### `PHASE8-IMPL-024-T005` - Accessibility semantics and target sizing

- `PHASE8-IMPL-024-T005A` - Heading hierarchy and minimum operable-target policy (`planned`; depends on T004C).
- `PHASE8-IMPL-024-T005B` - Mobile/coarse-pointer sizing, checkbox label hit areas, and focus visibility (`planned`; depends on T005A).
- `PHASE8-IMPL-024-T005C` - Manual keyboard validation (`planned`; depends on T005B).

The policy must distinguish the WCAG 2.2 24 CSS-pixel minimum target requirement and its exceptions from the preferred 44 CSS-pixel touch target. A sub-44-pixel control is not automatically a WCAG failure.

### `PHASE8-IMPL-024-T008` - Remaining validation suites

- `PHASE8-IMPL-024-T008A` - Guided-creation persistence suite (`planned`; after T001C).
- `PHASE8-IMPL-024-T008B` - Candidate lifecycle and grouped-review owner-decision suite (`planned`; separate from apply-promotion).
- `PHASE8-IMPL-024-T008C` - Promotion creation and handoff suite (`planned`; separate disposable project).
- `PHASE8-IMPL-024-T008D` - Apply-promotion suite (`planned`; isolated from read-only and candidate-decision suites).
- `PHASE8-IMPL-024-T008E` - Review-queue command suite (`planned`; separate disposable project).
- `PHASE8-IMPL-024-T008F` - Non-mutating resilience and accessibility suite (`planned`; loading, degraded, failure, retry, recovery, evidence-drawer focus restoration, complete keyboard navigation, browser zoom, and screen-reader behavior).

Every future mutation suite must use its own disposable `uiux-audit-*` project; capture API and filesystem manifests before and after; reject writes outside that project; preserve all existing projects; package evidence before cleanup; and remove only the exact disposable project. Apply-promotion validation must never be combined with read-only or candidate-decision validation.

T008 is the reusable UI/readiness regression baseline for later layered work.
PHASE8-IMPL-025-T012 adds only layered-runtime and integration deltas. Candidate
lifecycle, promotion, apply-promotion, review-queue, and owner-decision
assertions must be reused from these suites rather than independently
reimplemented. T008 closeout must validate and close the PHASE8-IMPL-024 parent;
the accepted post-closeout Project Memory refresh must be `FRESH` before
PHASE8-IMPL-025 may activate.

## Evidence Classifications

Verified working behavior is limited to the successful reconciliation collector's actual coverage: read-only existing-project navigation, correct selected Story Check source transport, regular disposable project creation and owner-authored scene/note/material writes, unsaved-switch confirmation, staged guided-creation UI progression, and preservation of existing projects during that run.

Verified defects are P0-A, P0-B, document-level horizontal overflow in captured responsive/OMI views, OMI heading skip in captured states, and repeated normally absent-resource 404s. T003A supplies the backend contract needed to repair the 404 behavior; the frontend behavior remains open under T003B/T003C.

Likely defects requiring focused manual review are OMI workspace density, weak next-task prioritization, undersized-control standards triage, misleading enabled actions, and OMI internal reset ambiguity.

The following remain `NOT_YET_TESTED`: grouped-review owner-decision mutation; candidate lifecycle mutations beyond existing evidence; promotion creation/audit persistence; apply-promotion; approved Memory/Canon mutation; review-queue commands; evidence-drawer focus restoration; complete keyboard navigation; browser zoom and screen-reader behavior; and controlled loading, degraded, failure, retry, and recovery states.

## Product Boundaries

- Analysis-only, candidate-first, evidence/provenance-backed, and owner-controlled.
- Owner-authored prose may be stored and edited; no generated prose is introduced.
- Model and tool output remain non-canon.
- No automatic promotion, apply-promotion, or Memory/Canon mutation.
- No training, JSONL, dataset, or model-artifact work.

## Validation

Roadmap publication validation only:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-024.enrichment.json >/dev/null
python3 -m json.tool docs/roadmap/roadmap_index.yaml >/dev/null
git diff --check
git status --short --branch
```
