# PHASE8-IMPL-024 - Application UI/UX Audit Integrity and Acceptance Repair

## Status

Published and active as the release-blocker repair parent.

T001 OMI-guided creation integrity is complete/PASS through T001A-T001D.

Next implementation task: `PHASE8-IMPL-024-T002A - Source identity/hash and diagnostic contract` (first bounded child of pending T002).

The application is not ready for broad owner acceptance or MVP readiness. T001 has repaired the guided-creation P0 defect, but T002 Story Check grounding remains pending and blocks readiness before visual polish or the remaining `PHASE8-IMPL-023-T023C` through `T026` closeout path can establish readiness.

## Controlling Evidence

- Audit synthesis: `.codex-context/application-uiux-audit/Pasted text(159).txt`
- Successful reconciliation summary: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/evidence-summary.md`
- Collector report: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/collector-report.json`
- Project manifest diff: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/project-manifest-diff.json`
- Phase evidence: `.codex-context/application-uiux-audit/playwright-reconciliation/20260712T030010Z/phases/`

The failed `playwright-advanced` runs are excluded from product evidence. They are failed collector-development attempts and cannot classify any workflow as PASS or FAIL.

T001 final PASS evidence: `.codex-context/PHASE8-IMPL-024/manual-validation/T001C-guided-creation/20260712T205343Z`. The prior BLOCKED locator-ambiguity run at `.codex-context/PHASE8-IMPL-024/manual-validation/T001C-guided-creation/20260712T203726Z` remains preserved as superseded validation history. Closeout decision: `docs/roadmap/decisions/PHASE8-IMPL-024-T001-omi-guided-creation-integrity-closeout.md`.

## Release Blockers

### P0-A - OMI-guided creation integrity (repaired/closed by T001 PASS)

T001A/T001B implemented the dedicated bounded guided-creation contract and frontend path. Exact owner-authored idea and note text is stored through existing OMI idea/Notes storage with owner provenance, linked IDs, `model_generated: false`, non-canon state, `creation_method: omi_guided`, atomic rollback, `failed_rolled_back`, and exceptional `recovery_required`; blank creation is unchanged. T001C validated deterministic and disposable API/browser behavior with no prohibited side effects.

### P0-B - Story Check accepts contradictory ungrounded findings

The selected source and POST transport were correct, but the result claimed selected-scene details were absent when those details were visibly present. The repair must carry selected source ID and source-content hash, require direct source evidence for factual warnings, validate grounding deterministically against the exact selected scene, quarantine or mark unsupported warnings unverified, and fail closed on source mismatch. Story Check remains non-mutating and model output remains non-canon.

## Child Task Hierarchy

Lettered children are bounded execution slices under the indexed workstream child.

### `PHASE8-IMPL-024-T001` - OMI-guided creation integrity

- `PHASE8-IMPL-024-T001A` - Backend guided-creation contract and storage (`complete/PASS`; commit `77d9968d1b8eb893a76bdd4f485c0415fb75f907`).
- `PHASE8-IMPL-024-T001B` - Frontend request and confirmation wiring (`complete/PASS`; commit `5bcaed06e429a8d6e1d5f65974c5a08fe7185656`).
- `PHASE8-IMPL-024-T001C` - Focused deterministic tests and disposable-project Playwright validation (`complete/PASS`; final evidence `20260712T205343Z`; prior BLOCKED run preserved as superseded history).
- `PHASE8-IMPL-024-T001D` - Documentation and status closeout (`complete/PASS`).

### `PHASE8-IMPL-024-T002` - Story Check grounding integrity

- `PHASE8-IMPL-024-T002A` - Source identity/hash and diagnostic contract (`planned`; depends on T001D).
- `PHASE8-IMPL-024-T002B` - Deterministic grounding validator (`planned`; depends on T002A).
- `PHASE8-IMPL-024-T002C` - Engine, normalizer, route, and UI integration (`planned`; depends on T002B).
- `PHASE8-IMPL-024-T002D` - Fixture regressions and live manual validation (`planned`; depends on T002C).
- `PHASE8-IMPL-024-T002E` - Documentation and status closeout (`planned`; depends on T002D).

The grounding validator must avoid over-filtering potentially useful diagnostics: unsupported factual warnings are quarantined or explicitly unverified, while supported non-factual diagnostics may remain visible under their correct evidence status.

Architecture coordination: T002 owns the immediate P0 exact-selected-source ID/hash, direct factual evidence, deterministic grounding, unsupported-output quarantine, and source-mismatch failure repair. The planned `PHASE8-IMPL-025-T007` must consume and extend this result into the shared `AnalysisRunManifest`/evidence-ledger architecture and the separate Ollama roles; it must not create a duplicate or conflicting Story Check grounding contract. PHASE8-IMPL-025 remains planned until T001/T002 complete.

### `PHASE8-IMPL-024-T003` - Optional-resource handling

- `PHASE8-IMPL-024-T003A` - Context-availability/readiness contract for Bible, storyform, and storyform-context (`planned`; depends on T002E).
- `PHASE8-IMPL-024-T003B` - Conditional frontend loading with distinct absent, invalid, and request-failure states (`planned`; depends on T003A).
- `PHASE8-IMPL-024-T003C` - Console/network regression validation (`planned`; depends on T003B).

Normal absence must not generate repeated noisy 404s or obscure genuine invalid-resource and request-failure errors.

### `PHASE8-IMPL-024-T004` - Responsive containment

- `PHASE8-IMPL-024-T004A` - Document-level overflow repair and native-control containment (`planned`; depends on T003C).
- `PHASE8-IMPL-024-T004B` - OMI status/metric wrapping, local wide-table containment, and wider contextual OMI workspace (`planned`; depends on T004A).
- `PHASE8-IMPL-024-T004C` - Responsive validation at 1440, 1280, 834, 640, 390, and 320 pixels (`planned`; depends on T004B).

### `PHASE8-IMPL-024-T005` - Accessibility semantics and target sizing

- `PHASE8-IMPL-024-T005A` - Heading hierarchy and minimum operable-target policy (`planned`; depends on T004C).
- `PHASE8-IMPL-024-T005B` - Mobile/coarse-pointer sizing, checkbox label hit areas, and focus visibility (`planned`; depends on T005A).
- `PHASE8-IMPL-024-T005C` - Manual keyboard validation (`planned`; depends on T005B).

The policy must distinguish the WCAG 2.2 24 CSS-pixel minimum target requirement and its exceptions from the preferred 44 CSS-pixel touch target. A sub-44-pixel control is not automatically a WCAG failure.

### `PHASE8-IMPL-024-T006` - Truthful OMI navigation

- `PHASE8-IMPL-024-T006A` - Resettable OMI Dashboard navigation and `App.jsx`/`OMIShell.jsx` state-owner decision (`planned`; depends on T005C).
- `PHASE8-IMPL-024-T006B` - Repeated inner-view navigation and enabled actions only for implemented destinations (`planned`; depends on T006A).
- `PHASE8-IMPL-024-T006C` - Navigation regression validation and closeout (`planned`; depends on T006B).

Unavailable workflows must render as honest status rows, not enabled no-op buttons. Duplicate resolution, audit mutation, and apply-promotion must not be implemented merely to make a dashboard button work.

### `PHASE8-IMPL-024-T007` - OMI information architecture and component standardization

- `PHASE8-IMPL-024-T007A` - "Needs owner attention" summary with pending and blocked work prioritization (`planned`; depends on T006C).
- `PHASE8-IMPL-024-T007B` - Progressive disclosure for hashes/raw audit metadata plus shared boundary, metadata, status, empty, loading, error, and action components (`planned`; depends on T007A).
- `PHASE8-IMPL-024-T007C` - Information-architecture validation and closeout (`planned`; depends on T007B).

This workstream follows the integrity, optional-resource, responsive, accessibility, and navigation repairs. Complete provenance and safety details must remain available.

### `PHASE8-IMPL-024-T008` - Remaining validation suites

- `PHASE8-IMPL-024-T008A` - Guided-creation persistence suite (`planned`; after T001C).
- `PHASE8-IMPL-024-T008B` - Candidate lifecycle and grouped-review owner-decision suite (`planned`; separate from apply-promotion).
- `PHASE8-IMPL-024-T008C` - Promotion creation and handoff suite (`planned`; separate disposable project).
- `PHASE8-IMPL-024-T008D` - Apply-promotion suite (`planned`; isolated from read-only and candidate-decision suites).
- `PHASE8-IMPL-024-T008E` - Review-queue command suite (`planned`; separate disposable project).
- `PHASE8-IMPL-024-T008F` - Non-mutating resilience and accessibility suite (`planned`; loading, degraded, failure, retry, recovery, evidence-drawer focus restoration, complete keyboard navigation, browser zoom, and screen-reader behavior).

Every future mutation suite must use its own disposable `uiux-audit-*` project; capture API and filesystem manifests before and after; reject writes outside that project; preserve all existing projects; package evidence before cleanup; and remove only the exact disposable project. Apply-promotion validation must never be combined with read-only or candidate-decision validation.

## Evidence Classifications

Verified working behavior is limited to the successful reconciliation collector's actual coverage: read-only existing-project navigation, correct selected Story Check source transport, regular disposable project creation and owner-authored scene/note/material writes, unsaved-switch confirmation, staged guided-creation UI progression, and preservation of existing projects during that run.

Verified defects are P0-A, P0-B, document-level horizontal overflow in captured responsive/OMI views, OMI heading skip in captured states, and repeated normally absent-resource 404s.

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
