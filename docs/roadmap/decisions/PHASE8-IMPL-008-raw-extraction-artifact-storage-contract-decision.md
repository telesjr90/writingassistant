# PHASE8-IMPL-008 Raw Extraction Artifact Storage Contract Decision

## 1. Decision Summary

T002 accepts a project-local raw extraction artifact storage contract before any storage helpers or parser helpers exist.

- Raw extraction artifacts will be stored under a project-local `writer_assistant/extractions/` tree in future implementation children.
- Raw artifacts are support data only.
- Raw artifacts are not canon.
- Raw artifacts are not OMI candidates.
- Raw artifacts do not become candidate JSON automatically.
- Raw artifacts do not trigger apply-promotion.
- Real BookNLP install/run remains deferred.
- Real BookNLP output parsing remains deferred.
- T003 will be tests-only.
- T004 may implement pure path helpers and manifest shape validators only if authorized by T003 tests.
- Parser contract remains deferred to T005/T006.

## 2. Storage Root Decision

Accepted future storage root:

`project_dir / "writer_assistant" / "extractions"`

Accepted tool/run storage shape:

`project_dir / "writer_assistant" / "extractions" / tool_name / run_id`

Accepted first tool-specific root:

`project_dir / "writer_assistant" / "extractions" / "booknlp" / run_id`

Rules:

- helper APIs take `project_dir: Path`
- callers never pass arbitrary artifact output directories
- helpers construct paths from validated `tool_name`, `run_id`, and artifact kind/name
- storage stays inside `writer_assistant/extractions/`
- source path hints are display/debug only, never trusted as filesystem targets

## 3. Tool Name and Run ID Safety Decision

Safe tool names:

- lower-case alphanumeric plus underscore/hyphen
- first supported value: `booknlp`

Safe run IDs:

- lower-case alphanumeric plus underscore/hyphen
- no empty/whitespace-only values
- no `.`
- no `..`
- no `/`
- no `\`
- no `..` substring
- no leading slash
- no Windows drive patterns such as `C:\`
- no path suffix like `.json`, `.tsv`, `.html`, or `.txt` for IDs
- run IDs are identifiers, not filenames

Recommended future helper:

`validate_extraction_storage_id(value: str, *, field_name: str) -> str`

## 4. Future Storage Helper API Decision

Future module:

`backend/story_knowledge/raw_extraction_storage.py`

Recommended future public APIs for T004:

- `extraction_storage_dir(project_dir: Path) -> Path`
- `tool_extraction_dir(project_dir: Path, tool_name: str) -> Path`
- `extraction_run_dir(project_dir: Path, tool_name: str, run_id: str) -> Path`
- `extraction_manifest_path(project_dir: Path, tool_name: str, run_id: str) -> Path`
- `raw_artifact_dir(project_dir: Path, tool_name: str, run_id: str) -> Path`
- `raw_artifact_path(project_dir: Path, tool_name: str, run_id: str, artifact_name: str) -> Path`
- `derived_artifact_dir(project_dir: Path, tool_name: str, run_id: str) -> Path`
- `validate_extraction_storage_path(project_dir: Path, tool_name: str, run_id: str, artifact_name: str | None = None) -> Path`

T004 decision:

- T004 should implement pure path helpers and manifest shape validators only.
- T004 should not write raw artifact files.
- T004 should not read raw artifact files.
- T004 should not list raw artifact files unless T003 explicitly authorizes path-only listing tests.
- T004 should not parse BookNLP fixture text.
- T004 should not create project runtime folders except in tests using `tmp_path` if later helpers require mkdir behavior.
- Prefer pure path helpers first.

## 5. Future Manifest Shape Decision

Future `manifest.json` required fields:

- `run_id`
- `project_id`
- `tool_name`
- `tool_version`
- `adapter_name`
- `adapter_version`
- `run_type`
- `status`
- `source_documents`
- `source_snapshot_hashes`
- `storage_root`
- `run_dir`
- `raw_artifacts`
- `derived_artifacts`
- `artifact_hashes`
- `created_at`
- `updated_at`
- `parameters`
- `environment`
- `warnings`
- `errors`
- `human_review_required`
- `candidate_generation_allowed`
- `canon_write_allowed`
- `prose_generation_allowed`

Allowed `run_type` values:

- `booknlp_fixture_parse`
- `booknlp_raw_import`
- `manual_fixture_import`

Allowed `status` values:

- `planned`
- `running`
- `complete`
- `partial`
- `failed`
- `rejected`

Required policy values:

- `human_review_required` must be `true`
- `candidate_generation_allowed` must be `false`
- `canon_write_allowed` must be `false`
- `prose_generation_allowed` must be `false`

Manifest rules:

- manifest is raw-support metadata only
- manifest is not a candidate record
- manifest is not canon
- manifest cannot include model prompts or generated story prose
- manifest cannot include memory/canon mutation fields
- manifest source documents must validate through the existing source-map helper
- raw artifact refs should validate through the existing evidence helper where compatible
- storage paths inside manifest are display/debug only unless validated by storage helper from project root

## 6. Raw Artifact Layout Decision

Recommended future run folder layout:

`writer_assistant/extractions/booknlp/{run_id}/manifest.json`

`writer_assistant/extractions/booknlp/{run_id}/raw/tokens.tsv`

`writer_assistant/extractions/booknlp/{run_id}/raw/entities.tsv`

`writer_assistant/extractions/booknlp/{run_id}/raw/quotes.tsv`

`writer_assistant/extractions/booknlp/{run_id}/raw/supersense.tsv`

`writer_assistant/extractions/booknlp/{run_id}/raw/book.json`

Optional raw reference only:

`writer_assistant/extractions/booknlp/{run_id}/raw/book.html`

Derived support, only if a future child authorizes:

`writer_assistant/extractions/booknlp/{run_id}/derived/events.json`

`events.json` is derived app support data, not a real BookNLP raw output file. BookNLP event support originates from the `.tokens` `event` column. T002 records this distinction so T003 tests do not require or bless a raw external `events.tsv` or `.events` file.

## 7. Raw Artifact Kind Decision

Accepted future raw artifact kinds:

- `booknlp_tokens`
- `booknlp_entities`
- `booknlp_quotes`
- `booknlp_supersense`
- `booknlp_book_json`
- `booknlp_book_html`

Accepted future derived artifact kind:

- `booknlp_events_derived`

Rules:

- `booknlp_events_derived` must not be represented as a real external raw BookNLP file.
- raw artifact kinds are support data only
- raw artifact refs must remain `is_canon = false` and `is_candidate = false`
- raw artifacts cannot directly create candidates
- parser output can feed `validate_booknlp_raw_artifact_bundle` only in a future parser parent/child

## 8. Side-Effect Boundary Decision

T003:

- tests only
- use `tmp_path`
- no project runtime artifact writes

T004:

- pure path helpers: no filesystem side effects
- if manifest validation helpers are included: no filesystem side effects
- do not create directories
- do not write files
- do not read raw files
- do not list files unless explicitly authorized by T003 and still side-effect free

Deferred later parent:

- raw artifact write/read/list helpers
- atomic write behavior
- cleanup/rebuild behavior
- raw artifact hash computation from files
- real parser reading from disk

## 9. Forbidden Locations Decision

Future helpers must never place extraction artifacts under:

- `writer_assistant/candidates/`
- `writer_assistant/index.json`
- `writer_assistant/memory/`
- `writer_assistant/canon/`
- `memory/`
- `canon/`
- `bible.json`
- `storyform.json`
- `project.json`
- `scenes/`
- `notes/`
- `materials/`
- `omi/`
- `training/`
- `.external_sources/`
- package/dependency files
- dataset/JSONL paths

Raw extraction artifacts must stay inside:

`writer_assistant/extractions/{tool_name}/{run_id}/`

## 10. Relationship to Existing Helpers

- `booknlp_adapter_contract.py` validates in-memory raw artifact bundles and draft normalization.
- `raw_extraction_storage.py` will only provide storage path/manifest support.
- Storage helpers must not call adapter normalizers.
- Storage helpers must not call parser helpers.
- Storage helpers must not create candidate records.
- Storage helpers may construct raw output references compatible with `evidence.validate_raw_output_reference` only if T003/T004 authorize it.
- Existing candidate persistence/index helpers remain separate.

## 11. T003 Handoff

T003:

`PHASE8-IMPL-008-T003 — Extraction artifact storage path and manifest contract tests`

T003 should be tests-first only.

Expected future test file:

`tests/test_writer_assistant_core_raw_extraction_storage_contract.py`

Expected future module:

`backend.story_knowledge.raw_extraction_storage`

Expected future API names:

- `extraction_storage_dir`
- `tool_extraction_dir`
- `extraction_run_dir`
- `extraction_manifest_path`
- `raw_artifact_dir`
- `raw_artifact_path`
- `derived_artifact_dir`
- `validate_extraction_storage_path`
- optional: `validate_extraction_run_manifest`

T003 test coverage should include:

- storage root path under `writer_assistant/extractions`
- tool/run path helpers
- manifest path helper
- raw artifact path helper
- derived artifact path helper
- path safety for `project_dir`/`tool_name`/`run_id`/`artifact_name`
- reject path traversal
- reject suffixes in IDs
- reject forbidden target folders
- no memory/canon/candidate path writes
- no `.external_sources/` path use
- no filesystem side effects from path helpers
- manifest shape validation
- manifest policy flags
- raw artifact kind validation
- raw artifact refs non-canon/non-candidate
- expected-red import error if future module does not exist
- existing regression tests remain green

## 12. T004 Handoff

T004:

`PHASE8-IMPL-008-T004 — Minimal extraction artifact storage helpers`

T004 should:

- create `backend/story_knowledge/raw_extraction_storage.py`
- implement pure path helpers
- implement optional manifest validation only if T003 tests authorize it
- keep helpers standard-library only
- avoid filesystem I/O unless T003 explicitly requires validation around path existence; prefer no filesystem side effects
- no raw artifact write/read/list helpers
- no BookNLP fixture parser
- no real BookNLP install/run/import
- no real spaCy install/run/import
- no backend routes
- no frontend UI
- no package/dependency changes
- no project runtime artifact creation
- no candidate JSON persistence from raw artifacts
- no memory/canon mutation
- no apply-promotion

## Accepted Decision

- ACCEPT `writer_assistant/extractions/{tool_name}/{run_id}/` as the future project-local raw extraction artifact storage boundary.
- ACCEPT `booknlp` as the first supported `tool_name`.
- ACCEPT strict single-component ID validation for tool/run identifiers and artifact names.
- ACCEPT `manifest.json`, `raw/`, and future-authorized `derived/` as the run folder structure.
- ACCEPT `booknlp_events_derived` as app-owned derived support from `.tokens.event`, not as a real external raw BookNLP file.
- ACCEPT T003 as tests-only.
- ACCEPT T004 as pure path helpers plus manifest shape validators only if T003 authorizes them.
- REJECT raw artifacts as canon, candidates, promotion input, or durable truth.
- REJECT project runtime raw artifact writes in T002/T003.
- REJECT real BookNLP/spaCy install, run, import, or parser implementation in this decision.
