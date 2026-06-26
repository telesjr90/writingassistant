# PHASE8-IMPL-004

## ID

`PHASE8-IMPL-004`

## Title

Writer Assistant Core candidate index contract and derived index helpers

## Goal

Prepare and implement a derived candidate index layer for typed Writer Assistant Core candidate records after `PHASE8-IMPL-003` established candidate-only JSON write/read/list persistence, defining tests-first derived index contracts before routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation exists.

## Why Now

`PHASE8-IMPL-003` is complete through `PHASE8-IMPL-003-T007`. It accepted the candidate persistence contract decision, added tests-first write/read and list contract coverage, implemented candidate-only JSON write/read/list persistence helpers, and closed with final validation.

That parent intentionally deferred `writer_assistant/index.json`, index read/write helpers, derived index contract, and route/UI/extraction/model/apply-promotion/memory-canon work. The next safe step is to define and test a derived index layer before routes, UI, extraction, or model behavior expands.

## Dependencies

- Completed parent: `PHASE8-IMPL-003` - Writer Assistant Core candidate storage read/write contract and candidate-only persistence.
- Completed child: `PHASE8-IMPL-003-T007` - Roadmap/status closeout.
- Source evidence:
  - `docs/roadmap/decisions/PHASE8-IMPL-003-candidate-persistence-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-002-candidate-storage-evidence-contract-decision.md`
  - `docs/roadmap/writer_assistant_core_candidate_schemas.md`
  - `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
  - `docs/roadmap/omi_mvp_schema_lifecycle.md`
  - `docs/roadmap/omi_storage_model.md`
  - `docs/roadmap/project_memory_canon_storage_model.md`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `tests/test_writer_assistant_core_candidate_schema_contract.py`
  - `tests/test_writer_assistant_core_candidate_record_contract.py`
  - `tests/test_writer_assistant_core_candidate_storage_contract.py`
  - `tests/test_writer_assistant_core_candidate_persistence_contract.py`
  - `tests/test_writer_assistant_core_candidate_list_contract.py`

## Scope

Include:

- Derived index contract for typed Writer Assistant Core candidates.
- Index file path: `projects/{project_id}/writer_assistant/index.json`.
- Index record shape decision.
- Source-of-truth boundary: candidate JSON files remain authoritative.
- Rebuild-from-candidates behavior.
- Stale/corrupt index handling decisions.
- Validation-before-indexing.
- Path safety.
- Tests-first index helper implementation.
- Candidate-only separation from memory/canon and OMI MVP storage.
- No mutation of approved memory/canon, bible, storyform, scenes, notes, or materials.

Important rule:

- `writer_assistant/index.json` is a derived convenience artifact. It must not be authoritative over candidate JSON records under `writer_assistant/candidates/{candidate_id}.json`.

## Exclusions

- Production runtime code in T001.
- Tests in T001.
- Index read helpers in T001.
- Index write helpers in T001.
- Derived index helpers in T001.
- Backend routes and API helpers.
- Frontend UI.
- Extraction from owner text.
- Model/Ollama calls and HTTP calls.
- Generated prose, rewriting, continuation, style imitation, or prose improvement.
- Semantic search and Story Check auto-runs.
- Dramatica analysis.
- Apply-promotion and OMI candidate promotion.
- Memory/canon mutation and approved-memory routes/helpers.
- Package/dependency changes.
- Training data, JSONL records, dataset artifacts, and project runtime files.
- Context-tool execution in T001.

## Child-Task Plan

1. `PHASE8-IMPL-004-T001` - Publish candidate index parent and child-task plan. Status: complete.
2. `PHASE8-IMPL-004-T002` - Candidate index contract decision. Status: complete.
3. `PHASE8-IMPL-004-T003` - Candidate index contract tests. Status: complete.
4. `PHASE8-IMPL-004-T004` - Minimal candidate index helpers. Status: complete.
5. `PHASE8-IMPL-004-T005` - Index safety and stale/corrupt regression tests. Status: complete.
6. `PHASE8-IMPL-004-T006` - Index safety repair or hardening. Status: complete (validation-only; no repair or hardening patch required).
7. `PHASE8-IMPL-004-T007` - Roadmap/status closeout. Status: complete.

## Child Task Details

### `PHASE8-IMPL-004-T001` - Publish candidate index parent and child-task plan

- Docs/status/planning only.
- Publish parent, inventory, enrichment JSON, and roadmap/status updates.
- No code, tests, index helpers, context tools, routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-004-T002` - Candidate index contract decision

- Docs/decision only.
- Accepted derived index contract at `docs/roadmap/decisions/PHASE8-IMPL-004-candidate-index-contract-decision.md`.
- Accepted helper API: `build_candidate_index`, `write_candidate_index`, `read_candidate_index` in future `backend/story_knowledge/candidate_index.py`.
- Accepted index schema: `schema_version`, `kind`, `source`, `candidate_count`, `candidate_ids`, `candidates`, `generated_from`; per-candidate summaries derive from validated candidate records only.
- Accepted build/write/read, stale/corrupt, validation, and error behavior for T003/T004.
- No runtime implementation in T002.

### `PHASE8-IMPL-004-T003` - Candidate index contract tests

- Tests-first. Status: complete.
- Created `tests/test_writer_assistant_core_candidate_index_contract.py`.
- Normal import: `from backend.story_knowledge import candidate_index`.
- Expected red until T004 because `candidate_index` module/helpers do not exist yet.
- Covers build empty index, valid index from candidate JSON, ordering, summary derivation, write path/serialization, read/validation errors, corrupt index ignored by build and overwritten by write, no candidate JSON override, and no memory/canon mutation.
- No runtime/index helper implementation in T003.
- No routes/UI/extraction/model behavior.

### `PHASE8-IMPL-004-T004` - Minimal candidate index helpers

- Status: complete.
- Created `backend/story_knowledge/candidate_index.py` with `build_candidate_index`, `write_candidate_index`, and `read_candidate_index`.
- Derived index helpers use `list_candidate_records` as source of truth; `writer_assistant/index.json` is derived convenience metadata only.
- T003 index contract tests now pass.
- No routes/UI/extraction/model/apply-promotion/memory-canon behavior added.

### `PHASE8-IMPL-004-T005` - Index safety and stale/corrupt regression tests

- Status: complete.
- Created `tests/test_writer_assistant_core_candidate_index_safety_regression.py`.
- Focused regression test slice for source-of-truth safety, stale/corrupt index behavior, validation-before-index-write, candidate file mutation safety, non-candidate path mutation safety, missing/empty path side effects, summary-field leakage boundaries, source document ID derivation, and source-level/API boundary checks.
- Targeted regression pytest passes (15 tests).
- Combined Writer Assistant Core candidate contract pytest passes (307 tests).
- No runtime/index helper implementation changes in T005.
- No repair gap found; T006 is conditional docs/status validation only.

### `PHASE8-IMPL-004-T006` - Index safety repair or hardening

- Status: complete (validation-only).
- T005 found no repair or hardening gap; targeted safety regression, index contract, combined candidate contract, and focused OMI/project manager regressions all passed.
- No runtime repair required; no hardening patch required.
- T004 implementation (`build_candidate_index`, `write_candidate_index`, `read_candidate_index`) already satisfies T005 safety/stale/corrupt regression coverage.
- Preserved behavior: `writer_assistant/index.json` is derived only; candidate JSON files remain source of truth; build is side-effect free; write refreshes index from candidate JSON; read validates only and does not rebuild/repair.
- Docs/status validation only; no runtime code, tests, index helpers, routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-004-T007` - Roadmap/status closeout

- Close parent.
- Summarize derived index behavior and deferred work.
- Identify next roadmap-authorized parent or decision point.
- Completed: closed parent with final roadmap/status updates and validation.
- Recorded final artifacts, runtime behavior, deferred work, and boundary confirmations.
- Recorded that no next Writer Assistant Core parent is published; next parent/child requires owner/roadmap confirmation.

## Acceptance Criteria

- `PHASE8-IMPL-004` is published as the active Writer Assistant Core parent after completed `PHASE8-IMPL-003`.
- `PHASE8-IMPL-004-T001` publishes the parent, inventory, enrichment JSON, and roadmap/status updates.
- `PHASE8-IMPL-004-T002` accepts the derived index contract decision and identifies T003 as the next child task.
- Child tasks T001-T007 are documented with tests-first sequencing.
- Scope explicitly prioritizes derived candidate index contract before extraction/runtime expansion.
- Non-scope explicitly blocks extraction, routes, UI, model calls, index helpers in T001, apply-promotion, and memory/canon mutation.
- Candidate JSON files remain source of truth; index is derived convenience metadata only.
- The context tools policy records that T001 does not run context tools and that PHASE8-IMPL-001 through PHASE8-IMPL-003 provide sufficient evidence unless a later child authorizes a narrow collect task.

## Validation Expectations

For `PHASE8-IMPL-004-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Non-LeanCTX whitespace check on changed docs

Do not run pytest unless runtime code or tests were accidentally changed. Do not run context tools, CCE, Graphify, Repomix, AI Context generation, MCP tools, LeanCTX, app servers, browser/manual validation, frontend build, model calls, Ollama, or broad discovery.

## Safety / Product Boundaries

- The app is analysis-only.
- The app must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Owner-authored prose storage and editing remain allowed only when text is authored by the owner.
- Candidates are not canon.
- Schema validity, storage validity, persistence existence, or index existence does not prove story truth.
- Candidate records must remain separate from approved memory/canon.
- Index helpers must not mutate approved memory, canon, bible, storyform, scenes, notes, materials, project metadata, training data, JSONL records, or dataset manifests.
- Index must not become authoritative over candidate JSON source of truth.
- OMI remains the central review and future promotion layer.
- Promotion records remain audit-only until future apply-promotion exists.
- Context outputs are evidence, not roadmap truth.

## Current Status

`PHASE8-IMPL-004` is complete. Last completed child: `PHASE8-IMPL-004-T007` - Roadmap/status closeout. Prior completed child: `PHASE8-IMPL-004-T006` - Index safety repair or hardening (validation-only; no repair or hardening patch required). Prior completed child: `PHASE8-IMPL-004-T005` - Index safety and stale/corrupt regression tests. Prior completed child: `PHASE8-IMPL-004-T004` - Minimal candidate index helpers. Prior completed child: `PHASE8-IMPL-004-T003` - Candidate index contract tests. Prior completed child: `PHASE8-IMPL-004-T002` - Candidate index contract decision. Prior completed child: `PHASE8-IMPL-004-T001` - Publish candidate index parent and child-task plan. Last completed parent: `PHASE8-IMPL-004`. Prior completed parent: `PHASE8-IMPL-003`. Prior completed child under prior parent: `PHASE8-IMPL-003-T007`.

## Final Result

`PHASE8-IMPL-004` is complete. It accepted the derived candidate index contract decision, added tests-first index contract coverage, implemented minimal derived index build/write/read helpers, added focused index safety regression tests, completed validation-only T006 because T005 found no repair gaps, and completed final roadmap/status validation. Candidate JSON files under `writer_assistant/candidates/{candidate_id}.json` remain source of truth. `writer_assistant/index.json` is derived convenience metadata only. `build_candidate_index` derives from `list_candidate_records` and is side-effect free. `write_candidate_index` builds and writes stable UTF-8 JSON to `candidate_index_path`. `read_candidate_index` validates existing index shape only and does not rebuild, repair, or compare staleness. Stale-but-valid index can be read as-is. Corrupt index raises `ValueError` on read. Corrupt index is ignored by build. Corrupt index may be overwritten by write if candidate JSON records validate. No routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation exists.

## Final Artifacts

Decision artifact:

- `docs/roadmap/decisions/PHASE8-IMPL-004-candidate-index-contract-decision.md`

Implemented runtime file:

- `backend/story_knowledge/candidate_index.py`

Final test files:

- `tests/test_writer_assistant_core_candidate_index_contract.py`
- `tests/test_writer_assistant_core_candidate_index_safety_regression.py`

## Final Runtime Behavior

- `build_candidate_index(project_dir: Path) -> dict`
- `write_candidate_index(project_dir: Path) -> dict`
- `read_candidate_index(project_dir: Path) -> dict`
- Candidate JSON files under `writer_assistant/candidates/{candidate_id}.json` remain source of truth.
- `writer_assistant/index.json` is derived convenience metadata only.
- Build derives from candidate JSON through `list_candidate_records`.
- Build is side-effect free.
- Write builds and writes stable UTF-8 JSON to `candidate_index_path`.
- Read validates existing index only.
- Read does not rebuild, repair, or compare staleness.
- Stale-but-valid index can be read as-is.
- Corrupt index raises `ValueError` on read.
- Corrupt index is ignored by build.
- Corrupt index may be overwritten by write if candidate JSON records validate.

## Final Validation Results

- `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_candidate_index_safety_regression.py tests/test_writer_assistant_core_candidate_index_contract.py tests/test_writer_assistant_core_candidate_list_contract.py tests/test_writer_assistant_core_candidate_persistence_contract.py tests/test_writer_assistant_core_candidate_storage_contract.py tests/test_writer_assistant_core_candidate_record_contract.py tests/test_writer_assistant_core_candidate_schema_contract.py -q`: PASS (307 passed).
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py tests/test_omi_routes.py tests/test_project_manager.py -q`: PASS (109 passed).
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- Non-LeanCTX whitespace check on changed docs: PASS.

## Final Boundaries

- Derived candidate index helpers exist; candidates are not canon.
- Index existence does not prove story truth.
- Index is derived convenience metadata only; candidate JSON remains authoritative.
- No runtime extraction or candidate extraction from owner text.
- No backend routes or frontend candidate review/backlog UI.
- No model/Ollama calls, semantic search, or Story Check auto-runs.
- No apply-promotion or OMI candidate promotion.
- No memory/canon mutation or approved-memory routes/helpers.
- No automatic, watcher, route, UI, or extraction-triggered index refresh.
- No graph/vector/search index behavior.
- No package/dependency changes.
- No training data, JSONL records, dataset artifacts, or project runtime files.
- No staging, commit, or push.

## Deferred Work

- Backend routes.
- Frontend candidate review/backlog UI.
- Extraction from owner text.
- Model/Ollama calls.
- Semantic search.
- Story Check auto-runs.
- Apply-promotion.
- OMI candidate promotion.
- Memory/canon mutation.
- Approved-memory routes/helpers.
- Automatic/watcher/extraction-triggered index refresh.
- Graph/vector/search indexes.
- Training/JSONL/dataset work.

## Next Frontier

No next Writer Assistant Core parent is currently published in `docs/roadmap/roadmap_index.yaml`. The next parent/child requires owner/roadmap confirmation. A proposed future direction (not active truth) is `PHASE8-IMPL-005` — Writer Assistant Core candidate review/read API contract and route planning — but it is not authorized until published in roadmap docs. An alternative proposed frontier (not active) is `PHASE8-IMPL-005` — Writer Assistant Core candidate review UI planning and API boundary decision.
