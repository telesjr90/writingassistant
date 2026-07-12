# PHASE8-IMPL-024 Inventory

## Parent

- ID: `PHASE8-IMPL-024`
- Title: Application UI/UX Audit Integrity and Acceptance Repair
- Status: published/active
- Immediate child: `PHASE8-IMPL-024-T001A` (`ready`)
- Controlling decision: `docs/roadmap/decisions/PHASE8-IMPL-024-application-uiux-audit-readiness-reconciliation.md`
- Evidence pack: `.codex-context/application-uiux-audit/`

## Workstreams

1. `T001` OMI-guided creation integrity: T001A-T001D.
2. `T002` Story Check grounding integrity: T002A-T002E.
3. `T003` optional-resource handling: T003A-T003C.
4. `T004` responsive containment: T004A-T004C.
5. `T005` accessibility semantics and target sizing: T005A-T005C.
6. `T006` truthful OMI navigation: T006A-T006C.
7. `T007` OMI information architecture and component standardization: T007A-T007C.
8. `T008` remaining validation suites: T008A-T008F.

## Sequencing

P0-A T001 precedes P0-B T002 as the immediate implementation frontier. Both integrity repairs precede optional-resource, responsive, accessibility, truthful-navigation, and information-architecture work. T007 visual/structural standardization is last among product repairs. T008 validation suites are independently isolated and may run only after their corresponding implementation dependencies are ready.

Existing `PHASE8-IMPL-023-T023A` and T023B completion remains historical and valid. T023 remains in progress. T023C/T023D and T024-T026 are not renumbered or marked complete; broad acceptance and closeout claims are blocked by PHASE8-IMPL-024.

The separate `PHASE8-IMPL-025` layered-architecture parent is published/planned and does not change this immediate sequence. T002 is the authoritative P0 Story Check grounding repair. PHASE8-IMPL-025-T007 later consumes that source-ID/hash/evidence/quarantine work within the shared run-manifest/evidence-ledger architecture instead of duplicating it. Full Subtxt runtime is authorized and planned in PHASE8-IMPL-025 T005/T006; the completed app-owned rubric remains distinct.

## Evidence Boundary

The `20260712T030010Z` collector run is successful evidence collection only. Failed `playwright-advanced` attempts are excluded. Advanced owner-mutation, promotion, apply-promotion, approved-data mutation, review-queue command, complete accessibility, and resilience workflows remain `NOT_YET_TESTED`.

## Safety Boundary

Owner-controlled, candidate-first, non-canon boundaries remain unchanged. No generated prose, automatic canon, automatic promotion, automatic apply-promotion, training data, or model artifacts are authorized.
