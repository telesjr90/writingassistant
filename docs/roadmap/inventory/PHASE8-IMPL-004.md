# PHASE8-IMPL-004 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-004`
- Title: Writer Assistant Core candidate index contract and derived index helpers
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-003` - Writer Assistant Core candidate storage read/write contract and candidate-only persistence

## 2. Why This Parent Exists

`PHASE8-IMPL-003` delivered candidate JSON persistence and listing through `write_candidate_record`, `read_candidate_record`, and `list_candidate_records`, but intentionally deferred `writer_assistant/index.json`, index read/write helpers, and derived index contract work.

The next safe step is to define and test a derived index layer before any routes, UI, extraction, or model behavior exists. The index must remain a convenience artifact derived from candidate JSON records, not a source of truth or canon store.

## 3. Scope

This parent prepares a derived candidate index slice for typed Writer Assistant Core candidate records. It focuses on:

- Derived index contract under `projects/{project_id}/writer_assistant/index.json`.
- Candidate source of truth under `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json`.
- Index record shape decision.
- Source-of-truth boundary: candidate JSON files remain authoritative; index is derived only.
- Rebuild-from-candidates behavior.
- Stale/corrupt index handling decisions.
- Validation-before-indexing using existing candidate record validation.
- Path safety using existing `candidate_storage` helpers.
- Tests-first index helper implementation after contract decision and tests.
- Candidate-only separation from OMI MVP generic candidates, approved memory/canon, bible, storyform, scenes, notes, and materials.

## 4. Non-Scope

This parent, and specifically `PHASE8-IMPL-004-T001`, excludes:

- Production runtime code in T001.
- Tests in T001.
- Index read helpers in T001.
- Index write helpers in T001.
- Derived index helpers in T001.
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

- Index being mistaken for source of truth.
- Stale index hiding actual candidate JSON records.
- Corrupt index affecting candidate persistence.
- Index writes accidentally touching memory/canon, bible, storyform, scenes, notes, or materials.
- Route/UI/extraction work starting before index contract is stable.
- Index content accidentally including generated prose or unsafe excerpts.
- Duplicate confusion between generic OMI MVP candidates and typed Writer Assistant Core candidates.

## 6. Current T001 Inventory Result

`PHASE8-IMPL-004-T001` is docs/status/planning only. It publishes the candidate index parent, child-task plan, inventory, enrichment JSON, and roadmap/status updates. It does not run context tools and does not change runtime code, tests, backend/frontend/package files, project runtime files, training data, JSONL records, or dataset manifests.
