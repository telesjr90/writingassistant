# PHASE8-IMPL-003 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-003`
- Title: Writer Assistant Core candidate storage read/write contract and candidate-only persistence
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-002` - Writer Assistant Core candidate storage contract and evidence/provenance validation

## 2. Why This Parent Exists

`PHASE8-IMPL-002` established candidate record contracts, evidence/provenance validation, pure validation helpers in `backend/story_knowledge/candidate_record.py`, and pure storage path helpers in `backend/story_knowledge/candidate_storage.py`. It intentionally stopped before candidate JSON persistence, JSON read/write/list helpers, backend routes, frontend review/backlog UI, extraction from owner text, model/Ollama calls, apply-promotion, OMI candidate promotion, memory/canon mutation, package changes, training data, JSONL records, dataset artifacts, or project runtime files.

The next safe step is to define and test candidate-only JSON persistence before routes, UI, extraction, or model behavior exists. Persistence must remain candidate-only and must not be mistaken for approved project truth.

## 3. Scope

This parent prepares a candidate-only persistence slice for typed Writer Assistant Core candidate records. It focuses on:

- Candidate JSON persistence contract under `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json`.
- Optional index contract under `projects/{project_id}/writer_assistant/index.json`, if authorized by decision and tests.
- Validation-before-write using `candidate_record.validate_candidate_record`.
- Storage path safety using `candidate_storage` pure path helpers.
- Safe write/read/list behavior boundaries and side-effect expectations.
- Read/list/write helper boundary definitions before implementation.
- Index behavior decision and tests-first implementation.
- Tests-first persistence implementation.
- Candidate-only separation from OMI MVP generic candidates, approved memory/canon, bible, storyform, scenes, notes, and materials.

## 4. Non-Scope

This parent, and specifically `PHASE8-IMPL-003-T001`, excludes:

- Production runtime code in T001.
- Tests in T001.
- JSON read helpers in T001.
- JSON write helpers in T001.
- JSON list helpers in T001.
- Candidate persistence in T001.
- Backend routes.
- API helpers.
- Frontend UI.
- Extraction behavior and candidate extraction from owner text.
- Model/Ollama calls and HTTP calls.
- Generated prose, rewriting, continuation, style imitation, or prose improvement.
- Semantic search and Story Check auto-runs.
- Dramatica analysis.
- Apply-promotion behavior and OMI candidate promotion.
- Memory/canon mutation and approved-memory helpers.
- Package/dependency changes.
- Training data, JSONL records, dataset artifacts, and project runtime files.
- Context-tool execution in T001.

## 5. Risks

- Persistence being mistaken for approved truth.
- Candidate records being treated as canon.
- Writes accidentally touching memory/canon, bible, storyform, scenes, notes, or materials.
- Storage helpers bypassing validation-before-write.
- Unsafe candidate or project IDs enabling path traversal or host filesystem escape.
- Incomplete or unsafe index updates corrupting list behavior.
- Route/UI work starting before the persistence contract is stable.
- Extraction/model work starting before persistence is safe.
- Duplicate confusion between generic OMI MVP candidates and typed Writer Assistant Core candidates.

## 6. Current T001 Inventory Result

`PHASE8-IMPL-003-T001` is docs/status/planning only. It publishes the candidate persistence parent, child-task plan, inventory, enrichment JSON, and roadmap/status updates. It does not run context tools and does not change runtime code, tests, backend/frontend/package files, project runtime files, training data, JSONL records, or dataset manifests.
