# PHASE8-IMPL-003

## ID

`PHASE8-IMPL-003`

## Title

Writer Assistant Core candidate storage read/write contract and candidate-only persistence

## Goal

Prepare and implement a candidate-only persistence layer for typed Writer Assistant Core candidate records after `PHASE8-IMPL-002` established pure validation and path helpers, defining tests-first JSON read/write/list contracts before extraction runtime, routes, UI, model calls, apply-promotion, or memory/canon mutation exists.

## Why Now

`PHASE8-IMPL-002` is complete through `PHASE8-IMPL-002-T007`. It accepted the candidate storage/evidence/provenance contract decision, added tests-first record and storage path contract coverage, implemented pure candidate record validation helpers in `backend/story_knowledge/candidate_record.py`, and implemented pure storage path helpers in `backend/story_knowledge/candidate_storage.py` with no file I/O or storage writes.

That parent intentionally stopped before candidate JSON persistence, JSON read/write/list helpers, backend routes, frontend review/backlog UI, extraction from owner text, model/Ollama calls, apply-promotion, OMI candidate promotion, memory/canon mutation, package changes, training data, JSONL records, dataset artifacts, or project runtime files. The next safe step is candidate-only persistence contracts and tests before runtime expansion.

## Dependencies

- Completed parent: `PHASE8-IMPL-002` - Writer Assistant Core candidate storage contract and evidence/provenance validation.
- Completed child: `PHASE8-IMPL-002-T007` - Roadmap/status closeout.
- Source evidence:
  - `docs/roadmap/decisions/PHASE8-IMPL-002-candidate-storage-evidence-contract-decision.md`
  - `docs/roadmap/writer_assistant_core_candidate_schemas.md`
  - `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
  - `docs/roadmap/omi_mvp_schema_lifecycle.md`
  - `docs/roadmap/omi_storage_model.md`
  - `docs/roadmap/project_memory_canon_storage_model.md`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `tests/test_writer_assistant_core_candidate_schema_contract.py`
  - `tests/test_writer_assistant_core_candidate_record_contract.py`
  - `tests/test_writer_assistant_core_candidate_storage_contract.py`

## Scope

Include:

- Candidate-only JSON persistence contract.
- Validation-before-write using `candidate_record.validate_candidate_record`.
- Project-local path safety using `candidate_storage`.
- Safe write/read/list behavior boundaries.
- Side-effect expectations for project-local candidate files only.
- Candidate index behavior decision and tests, if authorized.
- Tests-first persistence implementation.
- No mutation of approved memory/canon, bible, storyform, scenes, notes, or materials.
- No backend routes or UI in this parent unless a later child explicitly defers them to a future parent.

Future storage path remains:

- `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json`
- optional index: `projects/{project_id}/writer_assistant/index.json`

## Exclusions

- Production runtime code in T001.
- Tests in T001.
- JSON read/write/list helpers in T001.
- Candidate persistence in T001.
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

1. `PHASE8-IMPL-003-T001` - Publish candidate persistence parent and child-task plan. Status: complete.
2. `PHASE8-IMPL-003-T002` - Candidate persistence contract decision. Status: complete.
3. `PHASE8-IMPL-003-T003` - Candidate persistence write/read contract tests. Status: complete.
4. `PHASE8-IMPL-003-T004` - Minimal candidate persistence helpers. Status: complete.
5. `PHASE8-IMPL-003-T005` - Candidate list/index contract tests. Status: complete.
6. `PHASE8-IMPL-003-T006` - Candidate list/index helper implementation. Status: ready.
7. `PHASE8-IMPL-003-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-003-T001` - Publish candidate persistence parent and child-task plan

- Docs/status/planning only.
- Publish parent, inventory, enrichment JSON, and roadmap/status updates.
- No code, tests, persistence helpers, context tools, routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-003-T002` - Candidate persistence contract decision

- Docs/decision only.
- Decide exact JSON read/write/list/index contract.
- Decide whether index is in-scope for this parent.
- Decide whether T003 is tests-only or split tests by write/read/list.
- No runtime implementation.
- Completed decision: `docs/roadmap/decisions/PHASE8-IMPL-003-candidate-persistence-contract-decision.md`.
- Selected sequence: T003 tests-only write/read; T004 minimal write/read helpers; T005 tests-only list; T006 list helper only if T005 authorizes; index read/write deferred to later parent.
- T004 must not implement list/index. T003 must not test list/index.

### `PHASE8-IMPL-003-T003` - Candidate persistence write/read contract tests

- Tests-first.
- Define write/read behavior for candidate-only JSON records.
- Require validate-before-write and path safety.
- No routes/UI/extraction/model behavior.
- Expected red if helpers are missing.
- Test file: `tests/test_writer_assistant_core_candidate_persistence_contract.py`.
- Defines expected T004 helper API on `backend.story_knowledge.candidate_persistence`.
- Tests write/read only; no list/index tests in T003.
- Completed: added tests-only write/read persistence contract coverage.
- Expected red status until T004 creates `backend/story_knowledge/candidate_persistence.py`.
- List/index remains deferred to T005/T006; index read/write deferred to later parent per T002 decision.

### `PHASE8-IMPL-003-T004` - Minimal candidate persistence helpers

- Implement the smallest candidate-only JSON write/read helpers required by T003.
- Use existing validation and path helpers.
- Project-local only.
- No list/index unless already authorized by T002/T003.
- No routes/UI/extraction/model behavior.
- Completed: created `backend/story_knowledge/candidate_persistence.py`.
- Added `write_candidate_record(project_dir: Path, record: dict) -> dict`.
- Added `read_candidate_record(project_dir: Path, candidate_id: str) -> dict`.
- Validation runs before any directory or file creation.
- Write scope remains one candidate JSON file only; no list/index helper exists.
- Targeted persistence contract pytest now passes.

### `PHASE8-IMPL-003-T005` - Candidate list/index contract tests

- Tests-first.
- Decide and test list behavior only; index read/write deferred to later parent.
- Candidate-only.
- No memory/canon mutation.
- T005 tests `list_candidate_records` only per T002 decision.
- Completed: added tests-only list contract coverage in `tests/test_writer_assistant_core_candidate_list_contract.py`.
- Defines expected T006 helper API: `list_candidate_records(project_dir: Path) -> list[dict]`.
- Covers missing/empty directory behavior, valid listing with deterministic sort, file filtering, invalid JSON/record fail-fast, filename/record ID mismatch, side-effect boundaries, index deferral, and source-level boundary scan.
- Expected red status until T006 implements `list_candidate_records`.
- T005 is list-only despite the child label mentioning list/index; index read/write remains deferred to a later parent.

### `PHASE8-IMPL-003-T006` - Candidate list/index helper implementation

- Implement `list_candidate_records` only if T005 authorizes it.
- Index read/write deferred to later parent.
- No routes/UI/extraction/model behavior.
- No apply-promotion or memory/canon mutation.
- Ready after T005 list contract tests.

### `PHASE8-IMPL-003-T007` - Roadmap/status closeout

- Close parent.
- Summarize persistence behavior and deferred work.
- Identify next roadmap-authorized parent or decision point.

## Acceptance Criteria

- `PHASE8-IMPL-003` is published as the active Writer Assistant Core parent after completed `PHASE8-IMPL-002`.
- `PHASE8-IMPL-003-T001` publishes the parent, inventory, enrichment JSON, and roadmap/status updates.
- `PHASE8-IMPL-003-T002` is identified as the next child task.
- Child tasks T001-T007 are documented with tests-first sequencing.
- Scope explicitly prioritizes candidate-only JSON persistence before extraction/runtime expansion.
- Non-scope explicitly blocks extraction, routes, UI, model calls, persistence in T001, apply-promotion, and memory/canon mutation.
- The context tools policy records that T001 does not run context tools and that PHASE8-IMPL-001 targeted context plus PHASE8-IMPL-002 contracts are sufficient evidence unless a later child authorizes a narrow collect task.

## Validation Expectations

For `PHASE8-IMPL-003-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Non-LeanCTX whitespace check on changed docs

Do not run pytest unless runtime code or tests were accidentally changed. Do not run context tools, CCE, Graphify, Repomix, AI Context generation, MCP tools, LeanCTX, app servers, browser/manual validation, frontend build, model calls, Ollama, or broad discovery.

## Safety / Product Boundaries

- The app is analysis-only.
- The app must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Owner-authored prose storage and editing remain allowed only when text is authored by the owner.
- Candidates are not canon.
- Schema validity, storage validity, or persistence existence does not prove story truth.
- Candidate records must remain separate from approved memory/canon.
- Persistence helpers must not mutate approved memory, canon, bible, storyform, scenes, notes, materials, project metadata, training data, JSONL records, or dataset manifests.
- OMI remains the central review and future promotion layer.
- Promotion records remain audit-only until future apply-promotion exists.
- Context outputs are evidence, not roadmap truth.

## Current Status

`PHASE8-IMPL-003` is active. Last completed child: `PHASE8-IMPL-003-T005` - Candidate list/index contract tests. Active child: `PHASE8-IMPL-003-T006` - Candidate list/index helper implementation. Next child: `PHASE8-IMPL-003-T007` - Roadmap/status closeout. Last completed parent: `PHASE8-IMPL-002`. Prior completed child under prior parent: `PHASE8-IMPL-002-T007`. T002 accepted write/read persistence contract; list-only in T005/T006; index deferred. T003 added tests-only write/read persistence contract coverage in `tests/test_writer_assistant_core_candidate_persistence_contract.py`. T004 added minimal candidate-only JSON write/read helpers in `backend/story_knowledge/candidate_persistence.py`, and the targeted persistence contract pytest now passes. T005 added tests-only list contract coverage in `tests/test_writer_assistant_core_candidate_list_contract.py`; targeted list pytest is expected red until T006 implements `list_candidate_records`. T005 is list-only despite the child label mentioning list/index; index read/write remains deferred to a later parent. No list helper, index helpers, extraction, routes, UI, model calls, apply-promotion, or memory/canon mutation exists.
