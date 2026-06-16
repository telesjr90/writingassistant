# PHASE8-IMPL-001 First Runtime Slice Decision

## 1. Decision Identity

- Parent: `PHASE8-IMPL-001`
- Child: `PHASE8-IMPL-001-T004`
- Decision: first Writer Assistant Core runtime slice
- Status: accepted / active decision
- Date: 2026-06-16
- Source evidence: `docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md`

## 2. Options Considered

### Schema/source-level tests only

- Summary: Add tests that lock the expected Writer Assistant Core candidate types, required fields, source locator, evidence/provenance, owner decision, destination, target category, and no-promotion boundaries without production changes.
- Benefits: Lowest blast radius; creates a contract before runtime behavior; keeps extraction, storage writes, routes, UI, and model calls out of scope.
- Risks: Tests can over-specify implementation shape if they assume module placement too early.
- Decision: Accepted as the first half of the selected slice for T005.
- Boundary concerns: Tests must assert contract and forbidden behavior without creating runtime modules, routes, UI, model paths, or project files.

### Backend candidate schema constants only

- Summary: Add a small backend constants/schema metadata surface for Writer Assistant Core candidate types and required field contracts.
- Benefits: Gives later storage, validation, route, and UI work a shared vocabulary; aligns runtime code with approved specs before extraction.
- Risks: Constants without tests can drift; adding constants directly to current OMI allowlists could accidentally imply runtime candidate acceptance.
- Decision: Accepted as the second half of the selected slice for T006, after T005 locks tests first.
- Boundary concerns: Constants must not enable extraction, storage writes, routes, UI, apply-promotion, or memory/canon mutation.

### Project-local candidate storage helper skeleton

- Summary: Add candidate-only storage helper contracts under project-local paths.
- Benefits: Could reuse existing path-safety and atomic JSON write patterns; prepares later OMI handoff.
- Risks: Higher mutation risk; could duplicate OMI storage or imply durable memory/canon writes before schema contracts are stable.
- Decision: Deferred.
- Boundary concerns: Storage helpers must not create `memory/` files, canon records, promotion application, or project truth mutation.

### Route contract tests before route implementation

- Summary: Specify future route expectations before adding backend routes.
- Benefits: Can prevent extraction/model/apply-promotion API drift.
- Risks: Route shape may be premature before schema constants and storage boundaries are selected.
- Decision: Deferred until after schema constants and candidate storage contracts are settled.
- Boundary concerns: No backend extraction routes, model calls, candidate creation from text, or apply-promotion endpoints should be added in the first slice.

### Frontend read-only candidate backlog placeholder

- Summary: Add a read-only UI placeholder for future candidate backlog/review.
- Benefits: Could keep candidate/canon separation visible in the workspace.
- Risks: UI would precede backend schema contract; current OMI panel is MVP-era and could drift from the selected runtime model.
- Decision: Deferred.
- Boundary concerns: UI must not imply extraction, approved canon, promotion application, generated prose, or memory/canon mutation.

### Evidence/provenance validation helper

- Summary: Add validation helpers for evidence, provenance, and source locator shapes.
- Benefits: Strengthens future promotion prerequisites and candidate trust before model or extraction work.
- Risks: May duplicate existing OMI normalization or expand into storage/extraction validation before constants are stable.
- Decision: Deferred as a follow-on candidate after constants exist.
- Boundary concerns: Validation helpers must not create candidates, evidence records, memory files, routes, UI, or model paths.

## 3. Selected First Runtime Slice

Selected first runtime slice: **Writer Assistant Core candidate schema constants plus source-level/contract tests**.

The next implementation sequence should start with tests that lock the expected schema/constants contract, then a small constants-only implementation later. T005 should be tests-first. T006 should implement only enough constants/schema metadata to satisfy the selected T005 contract, if the T006 prompt authorizes production changes.

## 4. Why This Slice Is Safest

- It aligns approved Writer Assistant Core specs with code contracts before runtime extraction exists.
- It avoids backend routes, frontend UI, model/Ollama calls, extraction orchestration, storage writes, and project runtime files.
- It preserves OMI as candidate-first, owner-controlled review infrastructure.
- It keeps no-prose, no-silent-promotion, no apply-promotion, and no memory/canon mutation boundaries testable before behavior expands.
- It creates a stable vocabulary for later storage, validation, route, and UI tasks.
- It is smaller and safer than storage, route, UI, or evidence-helper implementation because it changes only contract surfaces first.

## 5. What This Slice Does Not Implement

- Extraction.
- Model/Ollama calls.
- Candidate creation from text.
- Candidate storage writes.
- Backend extraction routes.
- Frontend extraction UI.
- Apply-promotion.
- Memory/canon mutation.
- OMI candidate promotion.
- Summaries as canon/truth.
- Training data, JSONL records, dataset manifests, or model artifacts.

## 6. Proposed T005 Scope

Recommended T005:

`PHASE8-IMPL-001-T005` - Writer Assistant Core candidate schema contract tests.

T005 should add source-level/contract tests only, likely focused on:

- Candidate type constants expected by Writer Assistant Core.
- Required field names.
- Source locator contract.
- Evidence/provenance contract.
- Owner decision, status, and destination contract.
- Target category contract.
- No apply-promotion and no canon/memory mutation boundary.
- No model/Ollama/extraction runtime.
- No generated prose behavior.
- No frontend UI requirement yet.

Preferred scope: tests only. T005 should not implement production constants unless the roadmap explicitly changes the task into a test-plus-implementation micro-slice.

## 7. Proposed T006 Scope

Recommended T006:

`PHASE8-IMPL-001-T006` - Writer Assistant Core candidate schema constants.

T006 should implement only enough constants/schema metadata to satisfy T005. It must not add routes, storage writes, extraction, model calls, UI, apply-promotion, OMI candidate promotion, or memory/canon mutation.

## 8. Acceptance Criteria for the Selected First Slice

- Candidate type list matches the approved Writer Assistant Core minimum set.
- Required candidate fields are contractually locked.
- Evidence/provenance fields are contractually locked.
- Owner decision, status, and destination fields are contractually locked.
- Target category mapping is explicit.
- No extraction runtime exists.
- No model/Ollama path exists.
- No route/UI expansion exists.
- No apply-promotion or memory/canon mutation exists.
- Validators pass.
- Relevant source-level tests pass when implemented.

## 9. Risks and Mitigations

- Risk: schema drift from docs to constants.
- Mitigation: tests first, then constants-only implementation.
- Risk: overbuilding runtime too early.
- Mitigation: constants before storage, routes, UI, extraction, or model work.
- Risk: treating candidates as canon.
- Mitigation: candidate-only naming and explicit no-promotion/no-canon tests.
- Risk: evidence/provenance too weak.
- Mitigation: contractually lock required evidence/provenance/source locator fields before storage or extraction.
- Risk: future route/UI work bypasses guardrails.
- Mitigation: defer route/UI work and require explicit no-prose/no-silent-promotion tests before route expansion.
- Risk: model/extraction work starts before contracts exist.
- Mitigation: defer extraction, model/Ollama calls, Story Check auto-runs, and apply-promotion until separate owner-authorized tasks.

## 10. Handoff to T005

- Add contract/source tests only.
- Inspect `docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md` and this decision record before writing tests.
- Do not add runtime implementation unless the T005 prompt explicitly scopes a test-plus-implementation micro-slice.
- Choose target test files conservatively.
- Likely file: `tests/test_frontend_project_workspace_source.py` only if source-level docs/frontend constants are involved.
- Likely new backend source test file only if a backend constants module is planned.
- Avoid creating a production module in T005 unless explicitly authorized.

## 11. Boundary Confirmation

- T004 is docs/decision only.
- No runtime code changed.
- No tests changed.
- No context tools run.
- No extraction/model/prose behavior added.
- No apply-promotion.
- No OMI candidate promotion.
- No memory/canon mutation.
- No training/JSONL/dataset work.
