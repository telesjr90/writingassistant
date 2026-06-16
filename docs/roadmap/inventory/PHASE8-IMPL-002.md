# PHASE8-IMPL-002 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-002`
- Title: Writer Assistant Core candidate storage contract and evidence/provenance validation
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-001` - Writer Assistant Core implementation readiness and first runtime slice plan

## 2. Why This Parent Exists

`PHASE8-IMPL-001` established Writer Assistant Core as the post-Phase-7 frontier, collected targeted context through direct inspection only, selected the first runtime slice, added candidate schema contract tests, and implemented minimal constants-only schema metadata in `backend.story_knowledge.candidate_schema`.

The completed parent did not add runtime extraction, candidate creation from text, candidate storage writes, backend routes, frontend extraction UI, model/Ollama calls, apply-promotion, OMI candidate promotion, memory/canon mutation, package changes, training data, JSONL records, dataset artifacts, or project runtime files.

The next safe step is to define and test candidate storage, evidence, and provenance contracts before any extraction, route, UI, or model behavior exists.

## 3. Scope

This parent prepares a storage/evidence validation slice for Writer Assistant Core candidate records. It focuses on:

- Project-local candidate record shape.
- Storage path contract, without writes at first.
- Source locator contract.
- Evidence span/support contract.
- Provenance/origin contract.
- Confidence and uncertainty fields.
- Owner decision, status, and destination fields.
- Target category alignment with `backend/story_knowledge/candidate_schema.py`.
- Validation helpers before storage writes.
- Tests-first implementation.

## 4. Non-Scope

This parent, and specifically `PHASE8-IMPL-002-T001`, excludes:

- Runtime extraction.
- Candidate extraction from owner text.
- Model/Ollama calls.
- Backend extraction routes.
- Frontend extraction UI.
- Storage writes in T001.
- Apply-promotion.
- Memory/canon mutation.
- Candidate-to-canon promotion.
- Package/dependency changes.
- Training, JSONL, dataset, or model artifact work.
- Project runtime artifacts.
- Context-tool execution in T001.

## 5. Risks

- Candidate records being treated as canon.
- Storage helpers accidentally mutating approved memory.
- Evidence/provenance being optional or too weak.
- Source locator format drifting from specs.
- Overbuilding routes/UI before validation contracts exist.
- Extraction/model work starting before storage contracts are stable.
- Confusion between OMI MVP generic candidates and typed Writer Assistant Core candidates.
- Path traversal or unsafe project-local storage assumptions.

## 6. Current T001 Inventory Result

`PHASE8-IMPL-002-T001` is docs/status/planning only. It publishes the candidate storage/evidence validation parent, child-task plan, inventory, enrichment JSON, and roadmap/status updates. It does not run context tools and does not change runtime code, tests, backend/frontend/package files, project runtime files, training data, JSONL records, or dataset manifests.
