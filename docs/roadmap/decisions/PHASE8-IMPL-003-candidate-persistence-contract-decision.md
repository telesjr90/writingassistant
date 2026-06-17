# PHASE8-IMPL-003 Candidate Persistence Contract Decision

## 1. Decision Identity

- Parent: `PHASE8-IMPL-003`
- Child: `PHASE8-IMPL-003-T002`
- Title: Candidate persistence contract decision
- Track: Writer Assistant Core
- Status: accepted
- Date: 2026-06-17
- Dependencies:
  - completed `PHASE8-IMPL-003-T001`
  - completed `PHASE8-IMPL-002`

## 2. Decision Summary

The accepted `PHASE8-IMPL-003` sequence is:

- **T003**: tests-only write/read persistence contract
- **T004**: minimal candidate-only JSON write/read helpers
- **T005**: tests-only list contract (index deferred)
- **T006**: minimal list helper only if T005 authorizes
- **T007**: closeout

Important boundaries:

- T002 does not implement persistence.
- T003 must be tests-only.
- T004 may implement minimal write/read helpers only.
- T004 must not implement list/index unless T003 explicitly tests and T002 authorizes it. T002 does not authorize list/index in T003/T004.
- T005/T006 handle list separately; index read/write is deferred to a later parent (`PHASE8-IMPL-004` or equivalent).
- No routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation are authorized by this decision.

## 3. Persistence Scope Decision

### In scope for PHASE8-IMPL-003

- Candidate-only JSON write/read helpers
- Validation-before-write using `candidate_record.validate_candidate_record`
- Project-local storage path enforcement using `candidate_storage.candidate_record_path`
- Safe JSON serialization/deserialization for candidate records
- Side-effect bounded writes only to candidate JSON files under `writer_assistant/candidates/`, after T003 tests authorize
- List behavior only after separate T005 tests
- Index path remains documented but index mutation is deferred

### Out of scope for PHASE8-IMPL-003

- Backend routes
- Frontend UI
- Extraction from owner text
- Model/Ollama calls
- Apply-promotion
- Memory/canon mutation
- Writes to `bible.json`, `storyform.json`, `scenes/`, `notes/`, `materials/`, or `memory/`
- Generic OMI MVP mutation
- Approved-memory routes/helpers
- Package/training/dataset work
- Index read/write helpers (deferred to later parent)

## 4. Storage Location Contract

Use the existing `PHASE8-IMPL-002` path contract:

- Candidate records: `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json`
- Optional future index: `projects/{project_id}/writer_assistant/index.json` (deferred)

Rules:

- Persistence helpers operate from a `project_dir: Path`.
- Helpers must use `candidate_storage.candidate_record_path` for record paths.
- Helpers must not accept arbitrary output paths.
- Helpers must not write outside the project-local `writer_assistant/candidates/` directory.
- Helpers must not write to `memory/`, `bible.json`, `storyform.json`, `scenes/`, `notes/`, `materials/`, or generic OMI MVP storage.

## 5. Future Helper API Decision

Recommended future module:

- `backend/story_knowledge/candidate_persistence.py`

### T004 exports (authorized)

- `write_candidate_record(project_dir: Path, record: dict) -> dict`
- `read_candidate_record(project_dir: Path, candidate_id: str) -> dict`

### T006 exports (conditional on T005)

- `list_candidate_records(project_dir: Path) -> list[dict]`

### Deferred to later parent

- `write_candidate_index(project_dir: Path, records: list[dict]) -> dict`
- `read_candidate_index(project_dir: Path) -> dict`

Rationale: index mutation adds derived-state risk and corruption surface. Candidate JSON files remain the source of truth. List-only is sufficient for the first persistence slice; index helpers belong in a separate parent after list behavior is stable.

## 6. Write Contract

`write_candidate_record(project_dir: Path, record: dict) -> dict`

### Required behavior

- Input `record` must be a `dict`.
- Record must validate with `candidate_record.validate_candidate_record`.
- `candidate_id` must come from the validated record.
- Path must be built with `candidate_storage.candidate_record_path`.
- Write target: `project_dir / "writer_assistant" / "candidates" / f"{candidate_id}.json"`.
- Helper may create `writer_assistant/` and `writer_assistant/candidates/` only after validation succeeds.
- Helper may write exactly one candidate JSON file.
- Helper must not write index files in T004.
- Helper must not write any other files.
- Helper must serialize stable JSON:
  - UTF-8
  - `indent=2`
  - `sort_keys=True`
  - trailing newline recommended
- Helper returns the validated record, or a shallow/deep normalized copy.
- Helper must not mutate the caller's input record.
- Helper must reject invalid records before creating directories/files.
- If validation fails, no files or directories should be created.

### Overwrite behavior

- T004 may overwrite the same candidate file only when the candidate ID in the record matches the existing file name.
- Overwrite remains candidate-only.
- No append mode.
- No merge behavior.
- No index update in T004.

## 7. Read Contract

`read_candidate_record(project_dir: Path, candidate_id: str) -> dict`

### Required behavior

- Candidate ID must be path-safe via `candidate_storage.candidate_record_path`.
- Read target is the project-local candidate JSON path.
- If file does not exist, raise `FileNotFoundError`.
- If JSON is malformed, raise `ValueError`.
- If loaded JSON is not a `dict`, raise `ValueError`.
- Loaded record must validate with `candidate_record.validate_candidate_record`.
- If loaded record `candidate_id` does not match requested `candidate_id`, raise `ValueError`.
- Return validated record.
- Read must be side-effect free.
- Read must not create directories/files.
- Read must not repair invalid JSON.
- Read must not update index.

## 8. List/Index Contract Decision

### Scope decision

- List/index is in-scope only after T005 tests.
- T004 does not implement list/index.
- T005 defines exact list behavior only.
- T006 implements list only if T005 authorizes.
- Index read/write is deferred to `PHASE8-IMPL-004` or equivalent later parent.

### Selected option: Option A (list-only)

- T005 tests list-only first.
- T006 implements `list_candidate_records` only.
- Index read/write deferred to `PHASE8-IMPL-004`.

Rationale: index is derived state with corruption risk; candidate JSON files are the source of truth; list-only satisfies review/backlog needs without index mutation in this parent.

### Recommended future list behavior

`list_candidate_records(project_dir: Path) -> list[dict]`

- Reads all `*.json` records in `writer_assistant/candidates/`
- Rejects or skips non-JSON files per T005 decision (T005 should prefer reject-on-invalid-file for safety)
- Validates each record before returning
- Sorts deterministically by `candidate_id`
- Side-effect free
- Does not create directories/files
- Missing `candidates/` directory returns empty list

### Deferred index behavior

- `writer_assistant/index.json` is a derived index, not source of truth.
- Candidate JSON files are source of truth.
- Index may later contain candidate IDs, types, statuses, target categories, timestamps, and source locator summary.
- Index must not contain generated prose.
- Index must not apply promotion or mutate memory/canon.
- Index write must be tested separately in a later parent.
- Index corruption must not corrupt candidate records.

## 9. Validation-Before-Write Decision

- `candidate_record.validate_candidate_record` is mandatory before write.
- `candidate_storage.candidate_record_path` is mandatory for path creation.
- Invalid records must not be persisted.
- Unknown fields remain rejected according to `PHASE8-IMPL-002` record validation.
- Persistence helpers must not bypass validation for convenience.

## 10. Side-Effect and Failure Behavior

- No files/directories created on validation failure.
- Read is side-effect free.
- Write is limited to the one target JSON file, plus directory creation for candidate storage only.
- No memory/canon/bible/storyform/scenes/notes/materials files touched.
- No generic OMI MVP files touched.
- No package/training/dataset/project fixture files touched by tests.
- Tests should use `tmp_path`.

### Atomicity decision

- Do not require robust atomic replace in T004.
- T004 may use a simple write after validation.
- Atomic writes can be a future hardening task if needed.

## 11. Error Behavior

Expected exceptions:

| Condition | Exception |
| --- | --- |
| Invalid record | `ValueError` |
| Unsafe candidate ID | `ValueError` |
| Candidate file missing | `FileNotFoundError` |
| Malformed JSON | `ValueError` |
| JSON root not object | `ValueError` |
| Candidate ID mismatch between path and record | `ValueError` |

## 12. T003 Handoff Decision

`PHASE8-IMPL-003-T003` — Candidate persistence write/read contract tests.

T003 should be:

- tests-only
- create `tests/test_writer_assistant_core_candidate_persistence_contract.py`
- normal import of future module; no `pytest.importorskip`
- expected red until T004 because `backend.story_knowledge.candidate_persistence` does not exist yet
- use `tmp_path`
- test write/read behavior only
- test validation-before-write
- test no files on validation failure
- test read missing/malformed/wrong-ID behavior
- test no index creation in T004 scope
- test no writes outside candidate directory
- test no memory/canon/bible/storyform/scenes/notes/materials mutation
- do not test list/index in T003

## 13. T004 Handoff Decision

`PHASE8-IMPL-003-T004` — Minimal candidate persistence helpers.

Allowed T004 implementation:

- create `backend/story_knowledge/candidate_persistence.py`
- implement `write_candidate_record`
- implement `read_candidate_record`
- use `candidate_record.validate_candidate_record`
- use `candidate_storage.candidate_record_path`
- create candidate storage directories only after validation
- write/read JSON only for candidate records
- no list/index
- no routes/UI/extraction/model/apply-promotion/memory mutation

## 14. T005/T006 Handoff Decision

### T005

`PHASE8-IMPL-003-T005` — Candidate list contract tests.

- Tests-first list-only contract
- Define `list_candidate_records` behavior
- Do not test index read/write
- Document index deferral to later parent

### T006

`PHASE8-IMPL-003-T006` — Candidate list helper implementation.

- Implement `list_candidate_records` only if T005 authorizes
- No index helpers
- No routes/UI/extraction/model/apply-promotion/memory mutation

### Option selected: Option A

- T005 tests list-only first.
- T006 implements list-only.
- Index read/write deferred to `PHASE8-IMPL-004`.

Why: index mutation adds derived-state corruption risk without being required for the first persistence slice; list-only keeps T005/T006 bounded while candidate JSON remains source of truth.

## 15. Source-Level Boundary Tests Decision

T003 should include source-level tests for future `candidate_persistence.py`.

Recommended forbidden terms in source scan:

- model/Ollama/HTTP client names (`ollama`, `openai`, `requests`, `httpx`)
- extraction package names
- route/UI terms (`FastAPI`, `router`, `React`, `jsx`)
- apply-promotion/canon/memory mutation terms (`apply_promotion`, `mutate_memory`, `write_to_canon`)
- training/dataset terms (`jsonl`, `dataset_manifest`)

Do not forbid normal persistence words:

- `json`
- `read_text`
- `write_text`
- `mkdir`

Bound write behavior through functional tests instead.

## 16. Deferred Work

- Backend routes
- Frontend review/backlog UI
- Extraction from owner text
- Model/Ollama calls
- Semantic search
- Story Check auto-runs
- Apply-promotion
- Memory/canon mutation
- Generic OMI MVP mutation
- Approved-memory helpers/routes
- Training/JSONL/dataset work
- Browser/manual validation
- Index read/write helpers (deferred to `PHASE8-IMPL-004` or equivalent)
- Atomic write hardening unless explicitly chosen later
- Conflict detection unless explicitly chosen later
- Migrations

## 17. Acceptance Criteria

T002 is complete when:

- This decision file exists.
- Write/read contract is explicit enough for T003 tests.
- List/index scope is decided (list-only in T005/T006; index deferred).
- T003 tests-only handoff is clear.
- T004 helper scope is clear.
- T005/T006 handoff is clear.
- Roadmap/status files mark T002 complete and T003 active/ready.
- Validators pass.
- No code, tests, or runtime files changed in T002.
