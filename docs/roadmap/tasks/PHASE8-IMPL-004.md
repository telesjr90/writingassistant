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
6. `PHASE8-IMPL-004-T006` - Index safety repair or hardening. Status: ready/active (conditional docs/status validation only; no repair gap found).
7. `PHASE8-IMPL-004-T007` - Roadmap/status closeout. Status: planned.

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

- Conditional repair only if T005 finds a gap.
- T005 found no repair gap; T006 is docs/status validation update only unless a later review finds otherwise.
- No route/UI/extraction/model behavior.

### `PHASE8-IMPL-004-T007` - Roadmap/status closeout

- Close parent.
- Summarize derived index behavior and deferred work.
- Identify next roadmap-authorized parent or decision point.

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

`PHASE8-IMPL-004` is active. Last completed child: `PHASE8-IMPL-004-T005` - Index safety and stale/corrupt regression tests. Next child: `PHASE8-IMPL-004-T006` - Index safety repair or hardening (conditional docs/status validation only; no repair gap found). Prior completed child: `PHASE8-IMPL-004-T004` - Minimal candidate index helpers. Prior completed child: `PHASE8-IMPL-004-T003` - Candidate index contract tests. Prior completed child: `PHASE8-IMPL-004-T002` - Candidate index contract decision. Prior completed child: `PHASE8-IMPL-004-T001` - Publish candidate index parent and child-task plan. Last completed parent: `PHASE8-IMPL-003`. Last completed child under prior parent: `PHASE8-IMPL-003-T007`. T005 added `tests/test_writer_assistant_core_candidate_index_safety_regression.py`; targeted regression pytest passes with no repair gap. T004 created `backend/story_knowledge/candidate_index.py` with derived index helpers; T003 index contract tests pass. T002 accepted the derived index contract at `docs/roadmap/decisions/PHASE8-IMPL-004-candidate-index-contract-decision.md`. No routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation exist yet.
