# PHASE8-IMPL-004 Candidate Index Contract Decision

## 1. Decision Identity

- Parent: `PHASE8-IMPL-004`
- Child: `PHASE8-IMPL-004-T002`
- Title: Candidate index contract decision
- Track: Writer Assistant Core
- Status: accepted
- Date: 2026-06-17
- Dependencies:
  - completed `PHASE8-IMPL-004-T001`
  - completed `PHASE8-IMPL-003`

## 2. Decision Summary

The accepted `PHASE8-IMPL-004` sequence is:

- **T003**: tests-only derived index contract
- **T004**: minimal index helpers (`build_candidate_index`, `write_candidate_index`, `read_candidate_index`)
- **T005**: index safety and stale/corrupt regression tests
- **T006**: conditional repair/hardening only if T005 finds a gap; otherwise docs/status validation only
- **T007**: closeout

Important boundaries:

- T002 does not implement index helpers.
- T003 must be tests-only.
- T004 may implement the three index helpers only.
- T004 must not implement incremental sync/update/delete index APIs, routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation.
- Candidate JSON files under `writer_assistant/candidates/{candidate_id}.json` remain the source of truth.
- `writer_assistant/index.json` is a derived convenience artifact only.

## 3. Source-of-Truth Rule

Accepted:

- Candidate JSON records under `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json` remain the source of truth.
- `projects/{project_id}/writer_assistant/index.json` is derived.
- If the index conflicts with candidate JSON records, candidate JSON records win.
- The index is never canon.
- The index is never an apply-promotion mechanism.
- The index never mutates memory/canon, bible, storyform, scenes, notes, materials, or generic OMI MVP storage.
- Index existence does not prove story truth.

## 4. Index Path Decision

Accepted path:

- `projects/{project_id}/writer_assistant/index.json`

Rules:

- Future helpers operate from a `project_dir: Path`.
- Future helpers must use `candidate_storage.candidate_index_path(project_dir)` for the index path.
- Future helpers must not accept arbitrary output paths.
- Future helpers must not write outside `project_dir / "writer_assistant" / "index.json"`.
- Future helpers must not write to `memory/`, `bible.json`, `storyform.json`, `scenes/`, `notes/`, `materials/`, `writer_assistant/candidates/`, or generic OMI MVP storage.

## 5. Candidate Source Path Decision

Accepted candidate source path:

- `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json`

Rules:

- Future index helpers must derive from `candidate_persistence.list_candidate_records(project_dir)`.
- Future index helpers must not scan unrelated folders.
- Future index helpers must not read candidate records through ad hoc directory walks outside the list helper.

## 6. Future Module Location Decision

Accepted future module:

- `backend/story_knowledge/candidate_index.py`

Alternative considered:

- Add index helpers to `backend/story_knowledge/candidate_persistence.py`

Selected: separate `candidate_index.py`.

Rationale:

- `candidate_persistence.py` already owns candidate JSON write/read/list against source-of-truth files.
- Derived index build/write/read is a separate concern with different failure modes (stale index, corrupt index, summary derivation).
- `PHASE8-IMPL-003` deferred index helpers to this parent specifically to keep persistence and derived index behavior separate.
- No strong local style conflict requires combining them.

## 7. Future Helper API Decision

### T004 exports (authorized)

- `build_candidate_index(project_dir: Path) -> dict`
- `write_candidate_index(project_dir: Path) -> dict`
- `read_candidate_index(project_dir: Path) -> dict`

### Meaning

- `build_candidate_index` is side-effect free. It derives an index dict from validated candidate JSON records via `list_candidate_records`. It does not read or write `index.json`.
- `write_candidate_index` builds from candidate JSON records, validates the derived index, writes `writer_assistant/index.json`, and returns the written index dict.
- `read_candidate_index` reads and validates `writer_assistant/index.json` only. It does not rebuild or repair automatically.

### Deferred APIs

- `sync_candidate_index`
- `update_candidate_index_for_record`
- `delete_candidate_index_entry`
- route-level index endpoints
- UI-triggered index refresh
- extraction-triggered index refresh

## 8. Index Schema Decision

### Top-level index shape

```json
{
  "schema_version": 1,
  "kind": "writer_assistant_candidate_index",
  "source": "writer_assistant_candidates",
  "candidate_count": 0,
  "candidate_ids": [],
  "candidates": [],
  "generated_from": {
    "source_of_truth": "writer_assistant/candidates",
    "index_is_derived": true
  }
}
```

### Required top-level fields

| Field | Type | Purpose |
| --- | --- | --- |
| `schema_version` | integer | Index schema version; accepted value is `1`. |
| `kind` | string | Stable index kind label; accepted value is `writer_assistant_candidate_index`. |
| `source` | string | Stable source label; accepted value is `writer_assistant_candidates`. |
| `candidate_count` | integer | Count of indexed candidates; must equal `len(candidate_ids)` and `len(candidates)`. |
| `candidate_ids` | array of strings | Sorted candidate IDs present in the index. |
| `candidates` | array of objects | Per-candidate summary objects; sorted by `candidate_id`. |
| `generated_from` | object | Derived-index metadata. |

### Required `generated_from` fields

| Field | Type | Purpose |
| --- | --- | --- |
| `source_of_truth` | string | Accepted value: `writer_assistant/candidates`. |
| `index_is_derived` | boolean | Accepted value: `true`. |

### Per-candidate summary shape

Each item in `candidates` is a summary object, not the full candidate record.

```json
{
  "candidate_id": "core_candidate_character_001",
  "candidate_type": "character_candidate",
  "status": "candidate",
  "destination": "omi_candidate_only",
  "confidence": 0.8,
  "source_document_ids": ["scene_001"],
  "evidence_count": 1,
  "provenance_kind": "manual",
  "created_at": "2026-06-17T00:00:00Z",
  "updated_at": "2026-06-17T00:00:00Z"
}
```

### Per-candidate summary required fields

| Field | Type | Derivation |
| --- | --- | --- |
| `candidate_id` | string | `record["candidate_id"]` |
| `candidate_type` | string | `record["candidate_type"]`; must be a `CORE_CANDIDATE_TYPES` value |
| `status` | string | `record["status"]` |
| `destination` | string | `record["destination"]`; must be a `CORE_DESTINATION_VALUES` value |
| `confidence` | number | `record["confidence"]` |
| `source_document_ids` | array of strings | Unique sorted document IDs from top-level `source_locator.source_document_id` and each evidence item's `source_locator.source_document_id` |
| `evidence_count` | integer | `len(record["evidence"])` |
| `provenance_kind` | string | `record["provenance"]["origin"]` |
| `created_at` | string | `record["created_at"]` |
| `updated_at` | string | `record["updated_at"]` |

Notes:

- `created_at` and `updated_at` are required on validated candidate records per `candidate_record.validate_candidate_record`; index summaries include them.
- `candidate_type` uses full typed values such as `character_candidate`, not shortened labels.
- `destination` uses stored destination values such as `omi_candidate_only`, not target-category labels.
- `provenance_kind` maps to provenance `origin`, which is required on validated candidate records.

### Forbidden index content

Do not include in the index:

- full evidence text excerpts
- owner-authored prose bodies
- scene bodies
- notes/material bodies
- generated prose
- canon facts
- approved-memory records
- OMI generic candidate payloads
- analysis output
- model output
- full candidate records

## 9. Ordering Decision

Accepted:

- `candidate_ids` sorted ascending by `candidate_id`
- `candidates` sorted ascending by `candidate_id`
- `source_document_ids` within each summary sorted ascending

## 10. Build Behavior Decision

`build_candidate_index(project_dir: Path) -> dict`

### Required behavior

- Calls `candidate_persistence.list_candidate_records(project_dir)`.
- Missing `writer_assistant/candidates/` directory produces a valid empty index.
- Empty `writer_assistant/candidates/` directory produces a valid empty index.
- Invalid candidate JSON behavior follows `list_candidate_records`: fail-fast `ValueError`.
- Derives one summary object per validated candidate record.
- Sets `candidate_count`, `candidate_ids`, and `candidates` consistently.
- Does not read existing `index.json`.
- Does not create files or directories.
- Is side-effect free.

## 11. Write Behavior Decision

`write_candidate_index(project_dir: Path) -> dict`

### Required behavior

- Calls `build_candidate_index(project_dir)`.
- Validates the derived index shape before writing.
- Creates only `writer_assistant/` as needed for `index.json`.
- Writes stable UTF-8 JSON with `indent=2`, `sort_keys=True`, and a trailing newline.
- Uses `candidate_storage.candidate_index_path(project_dir)` as the write target.
- Overwrites existing `index.json`.
- Does not mutate candidate records.
- Does not repair invalid candidate files.
- Returns the written index dict.

### Atomic write decision

- Simple overwrite is accepted for `PHASE8-IMPL-004`.
- Atomic write hardening is deferred unless T003/T005 tests reveal a necessary local pattern.

## 12. Read Behavior Decision

`read_candidate_index(project_dir: Path) -> dict`

### Required behavior

- Reads only `writer_assistant/index.json` via `candidate_storage.candidate_index_path(project_dir)`.
- Missing index file raises `FileNotFoundError`.
- Malformed JSON raises `ValueError`.
- Non-dict root raises `ValueError`.
- Invalid index shape raises `ValueError`.
- Does not rebuild or repair the index automatically.
- Does not compare against candidate JSON records automatically.
- Is side-effect free.

Reason:

- Rebuild behavior belongs to `build_candidate_index` / `write_candidate_index`.
- Read should remain a pure read/validate operation.

## 13. Stale Index Behavior Decision

Accepted:

- A stale index is allowed to exist as a derived artifact.
- `read_candidate_index` validates shape only; it does not decide staleness against candidate JSON files.
- `build_candidate_index` always derives fresh state from candidate JSON files.
- `write_candidate_index` is the explicit refresh operation.
- Staleness detection against candidate JSON files may be future work after routes/UI need it.

## 14. Corrupt Index Behavior Decision

Accepted:

- `read_candidate_index` fails fast with `ValueError` on malformed JSON or invalid shape.
- `build_candidate_index` ignores any existing corrupt index because it derives from candidate JSON files and reads no index.
- `write_candidate_index` may overwrite a corrupt index with a fresh derived index if candidate JSON records are valid.

## 15. Validation Behavior Decision

Future helpers should validate:

- top-level index fields
- `schema_version`
- `kind`
- `source`
- `candidate_count`
- `candidate_ids`
- `candidates`
- `generated_from`
- per-candidate summary fields
- sorted ordering
- consistency between `candidate_count`, `candidate_ids`, and `candidates`
- consistency between each summary `candidate_id` and `candidate_ids`

Validation helper visibility:

- T003 tests may require private validation through public helper behavior only.
- No public validation helper is required unless T003 tests demonstrate need.
- A private `_validate_candidate_index(index: dict) -> dict` helper in `candidate_index.py` is acceptable.

## 16. Error Behavior Decision

| Condition | Exception |
| --- | --- |
| Invalid candidate record during build/write | `ValueError` via `list_candidate_records` validation |
| Missing index on read | `FileNotFoundError` |
| Malformed index JSON on read | `ValueError` |
| Invalid index shape on read | `ValueError` |
| Unsafe candidate ID during list/build | `ValueError` via existing path/list validation |

Path safety:

- Helpers receive `project_dir: Path` and use known helper paths only.
- No arbitrary path input is accepted.
- Path traversal risk is constrained by `candidate_storage.candidate_index_path` and `candidate_persistence.list_candidate_records`.

## 17. Non-Scope / Deferred

Explicitly deferred:

- backend routes
- frontend review/backlog UI
- automatic refresh
- watcher-based refresh
- extraction-triggered refresh
- model/Ollama behavior
- semantic search
- Story Check integration
- apply-promotion
- OMI promotion
- memory/canon mutation
- approved-memory helpers/routes
- graph/vector/embedding index
- search index
- training/JSONL/dataset work
- incremental index update APIs

## 18. T003 Handoff Decision

`PHASE8-IMPL-004-T003` — Candidate index contract tests.

T003 should be:

- tests-only
- create `tests/test_writer_assistant_core_candidate_index_contract.py`
- normal import: `from backend.story_knowledge import candidate_index`
- expected red until T004 because `backend.story_knowledge.candidate_index` does not exist yet
- use `tmp_path`
- test build empty index for missing/empty candidates
- test build valid index from candidate JSON records
- test deterministic ordering
- test summary field derivation
- test write index path and JSON serialization
- test read valid index
- test missing index read error
- test malformed index read error
- test invalid index shape error
- test corrupt existing index ignored by build
- test corrupt existing index overwritten by write if candidates are valid
- test index never overrides candidate JSON
- test no memory/canon/bible/storyform/scenes/notes/materials/OMI mutation
- test no routes/UI/extraction/model behavior

## 19. T004 Handoff Decision

`PHASE8-IMPL-004-T004` — Minimal candidate index helpers.

Allowed T004 implementation:

- create `backend/story_knowledge/candidate_index.py`
- implement `build_candidate_index`
- implement `write_candidate_index`
- implement `read_candidate_index`
- use `candidate_persistence.list_candidate_records`
- use `candidate_storage.candidate_index_path`
- no routes/UI/extraction/model/apply-promotion/memory mutation

## 20. T005/T006/T007 Handoff Decision

### T005

`PHASE8-IMPL-004-T005` — Index safety and stale/corrupt regression tests.

- Tests-first or regression-only after T004
- Verify index never overrides candidate JSON
- Verify stale/corrupt index behavior follows this decision
- Verify no memory/canon/bible/storyform/scenes/notes/materials mutation

### T006

`PHASE8-IMPL-004-T006` — Index safety repair or hardening.

- Conditional repair only if T005 finds a gap
- Otherwise docs/status validation update only
- Atomic write hardening is optional only if T005 demonstrates need

### T007

`PHASE8-IMPL-004-T007` — Roadmap/status closeout.

- Close parent
- Summarize derived index behavior and deferred work
- Identify next roadmap-authorized parent or decision point

## 21. Acceptance Criteria

T002 is complete when:

- This decision file exists.
- Source-of-truth rule is explicit.
- Index path, candidate source path, module location, helper API, and index schema are decided.
- Build/write/read/stale/corrupt/validation/error behavior is explicit enough for T003 tests.
- T003/T004 handoff is clear.
- Roadmap/status files mark T002 complete and T003 active/ready.
- Validators pass.
- No code, tests, or runtime files changed in T002.
