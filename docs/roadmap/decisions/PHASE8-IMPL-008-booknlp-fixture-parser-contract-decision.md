# PHASE8-IMPL-008 BookNLP Fixture Parser Contract Decision

## 1. Decision Summary

T005 accepts a mocked BookNLP-like fixture parser contract before any parser tests, parser implementation, raw artifact writes, real BookNLP install/run/import, or real spaCy install/run/import.

- T005 accepts a future pure mocked BookNLP-like fixture parser module before any test or implementation is created.
- The future parser must consume in-memory TSV/JSON fixture text only.
- The future parser must not read files from disk.
- The future parser must not write files to disk.
- The future parser must not run BookNLP.
- The future parser must not import BookNLP.
- The future parser must not import spaCy.
- The future parser must not install BookNLP or spaCy.
- The future parser must not call any model, Ollama, or extraction runtime.
- The future parser must not execute external repository code from `.external_sources/`.
- The future parser must not vendor external repository code into `backend/`.
- The future parser must not open `Path`, must not call `open(`, must not call `Path(`, must not call `.write_text`, must not call `.mkdir`, and must not call `subprocess` if its source is literally scanned.
- The future parser must not create OMI candidate records.
- The future parser must not create candidate JSON.
- The future parser must not persist raw artifacts.
- The future parser must not write to `writer_assistant/extractions/` on disk.
- The future parser must not write to `writer_assistant/candidates/`, `writer_assistant/index.json`, `writer_assistant/memory/`, `writer_assistant/canon/`, `bible.json`, `storyform.json`, `project.json`, `owner_memory.json`, `scenes/`, `notes/`, `materials/`, `omi/`, `training/`, dataset files, JSONL files, or `.external_sources/`.
- The future parser must not mutate memory/canon.
- The future parser must not apply promotion.
- The future parser must not generate, rewrite, continue, imitate, polish, improve, or expand owner-authored story prose.
- The future parser output must be an in-memory raw artifact bundle compatible with `validate_booknlp_raw_artifact_bundle` from `backend/story_knowledge/booknlp_adapter_contract.py`.
- The future parser output remains raw support data only and is non-canon, non-candidate, non-promotable, and non-memory/canon.
- T006 is tests-first only and expected-red.
- T006 must not implement the parser module.
- Parser implementation is recommended for `PHASE8-IMPL-009` unless T006 closeout changes the recommendation.
- T006 expected-red contract tests should import the future module path `backend.story_knowledge.booknlp_fixture_parser` even though the module does not exist yet.

## 2. Evidence Basis

This decision is based on the verified prior roadmap and source evidence, with no new external fetch, install, clone, or runtime:

- `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md` - read-only local BookNLP, dramatica-flow, NCP, and Subtxt docs source inventory; commit SHAs `3d900fc2224e55960c3363826ae28539b77b4204`, `890f099bfcb64adbf407fd83ab708c48e92b0766`, `b1222748376aae3d309176b3bb5afb884eb281ea`, `ec66121364c039693314dcce4cde464e497bece4`.
- `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md` - source inventory refresh and read-only re-inventory policy.
- `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md` - BookNLP-like raw-shape vs adapter-normalized shape separation, `booknlp_events` as app-owned derived support from `.tokens.event`, byte offsets as raw support, app-owned source locators/evidence as required for candidate drafts, `.book` `g` as raw aggregate metadata only, source-level forbidden runtime/tool/prose/mutation terms policy.
- `docs/roadmap/decisions/PHASE8-IMPL-008-raw-extraction-artifact-storage-contract-decision.md` - T002 storage contract: `project_dir / "writer_assistant" / "extractions"`, `writer_assistant/extractions/{tool_name}/{run_id}/`, first tool folder `booknlp`, strict tool/run ID safety, manifest shape, raw/derived artifact kinds, `booknlp_events_derived` as app-owned derived support.
- `backend/story_knowledge/booknlp_adapter_contract.py` - mocked BookNLP adapter contract module with `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, `build_booknlp_candidate_drafts`; bundle fields `bundle_id`, `project_id`, `run_manifest`, `source_map`, `tokens`, `entities`, `quotes`, `book_json`, `supersense`, `events`, `raw_output_references`, `created_at`; row field sets, raw-shape fields, normalized-shape fields, blocked field and forbidden-key policy.
- `backend/story_knowledge/raw_extraction_storage.py` - T004 pure storage path and manifest validation helpers; storage root `project_dir / "writer_assistant" / "extractions"`, run folder `writer_assistant/extractions/{tool_name}/{run_id}/`, raw artifact names `tokens.tsv`, `entities.tsv`, `quotes.tsv`, `supersense.tsv`, `book.json`, optional `book.html`; raw kinds `booknlp_tokens`, `booknlp_entities`, `booknlp_quotes`, `booknlp_supersense`, `booknlp_book_json`, `booknlp_book_html`; derived kind `booknlp_events_derived`; safe ID and hint policy.
- `backend/story_knowledge/source_map.py` - source document, source segment, source map, and source locator validation helpers used by the future parser bundle.
- `backend/story_knowledge/evidence.py` - evidence record, extraction run provenance, and raw output reference validation helpers used by the future parser bundle.
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py` - existing BookNLP adapter contract coverage that future parser bundles must remain compatible with.
- `tests/test_writer_assistant_core_raw_extraction_storage_contract.py` - existing raw extraction storage contract coverage that the future parser must not bypass.

Verified BookNLP-like raw output facts from T002 source inventory:

- BookNLP real output kinds: `.tokens`, `.entities`, `.quotes`, `.supersense`, `.book`, `.book.html`.
- No separate `.events` file in the real BookNLP output set.
- Events are app-derived support from the `.tokens.event` column.
- `.book.html` is renderable visual output, not parser input for normalization, but may be referenced as a raw output reference.
- Real `.tokens` header columns: `paragraph_ID`, `sentence_ID`, `token_ID_within_sentence`, `token_ID_within_document`, `word`, `lemma`, `byte_onset`, `byte_offset`, `POS_tag`, `fine_POS_tag`, `dependency_relation`, `syntactic_head_ID`, `event`.
- Real `.entities` header columns: `COREF`, `start_token`, `end_token`, `prop`, `cat`, `text`.
- Real `.quotes` header columns: `quote_start`, `quote_end`, `mention_start`, `mention_end`, `mention_phrase`, `char_id`, `quote`.
- Real `.supersense` header columns: `start_token`, `end_token`, `supersense_category`, `text`.
- Real `.book` top-level key: `characters`. Each character has `agent`, `patient`, `mod`, `poss`, `id`, `g`, `count`, `mentions`. `mentions` has `proper`, `common`, `pronoun` buckets with `c` and `n` entries.
- `.book` `g` is referential pronoun distribution, not identity.

## 3. Parser Module Decision

Future module path:

`backend/story_knowledge/booknlp_fixture_parser.py`

The future module is recommended to be:

- pure
- standard-library only
- in-memory only
- side-effect free
- no filesystem I/O
- no package or runtime imports beyond the Python standard library
- no model calls
- no Ollama calls
- no BookNLP import, install, or run
- no spaCy import, install, or run
- no external code execution, import, or vendoring
- no candidate persistence
- no raw artifact persistence
- no apply-promotion
- no memory/canon mutation
- no candidate JSON creation
- no prose generation, rewrite, continuation, imitation, polish, improvement, or expansion

Recommended future public APIs:

- `parse_booknlp_tokens_tsv(text: str) -> list[dict]`
- `parse_booknlp_entities_tsv(text: str) -> list[dict]`
- `parse_booknlp_quotes_tsv(text: str) -> list[dict]`
- `parse_booknlp_supersense_tsv(text: str) -> list[dict]`
- `parse_booknlp_book_json(text: str) -> dict`
- `build_booknlp_raw_artifact_bundle_from_fixture_texts(fixture_texts: dict, *, run_manifest: dict, source_map: dict, raw_output_references: list[dict]) -> dict`

Optional future API only if T006 needs it:

- `derive_booknlp_events_from_tokens(tokens: list[dict]) -> list[dict]`

Decision:

- T006 should test the APIs listed above.
- T006 must not implement the module.
- T006 expected-red failure must be limited to `ImportError` or `ModuleNotFoundError` for the missing future module or symbol.
- PHASE8-IMPL-009 should likely implement the module and integrate parsed fixture bundles with the existing `validate_booknlp_raw_artifact_bundle` API.
- Real BookNLP install/run remains deferred beyond `PHASE8-IMPL-009` unless owner explicitly authorizes it.

## 4. Fixture Input Shape Decision

The future parser builder should accept an in-memory dictionary of fixture strings, not file paths:

```python
{
    "tokens_tsv": "...",
    "entities_tsv": "...",
    "quotes_tsv": "...",
    "supersense_tsv": "...",
    "book_json": "..."
}
```

Optional metadata-only input that does not require parser handling:

```python
{
    "book_html": "..."
}
```

Decision:

- `book_html` is optional and is not required for candidate support.
- `book_html` must not be parsed into story claims.
- `book_html` may be accepted only as a display metadata string when included in `raw_output_references` through the storage helper.
- No file paths are accepted as parser inputs.
- No path hints are trusted as filesystem paths.
- No parser API accepts a `pathlib.Path` or string path argument.
- No parser API opens files.
- No parser API uses `os`, `os.path`, `pathlib`, `tempfile`, `shutil`, `subprocess`, `socket`, `urllib`, `httpx`, `requests`, or third-party filesystem/IO libraries.
- The future parser must not import `os`, `sys`, `pathlib`, `io`, `tempfile`, `shutil`, `subprocess`, `socket`, `urllib`, `http`, `ftplib`, `smtplib`, `multiprocessing`, `threading`, `asyncio` (beyond default standard library imports) if the source-level boundary scan is literal.

## 5. TSV Header Decision

The future parser should require exact header validation for synthetic fixture text:

Accepted `.tokens` header columns:

- `paragraph_ID`
- `sentence_ID`
- `token_ID_within_sentence`
- `token_ID_within_document`
- `word`
- `lemma`
- `byte_onset`
- `byte_offset`
- `POS_tag`
- `fine_POS_tag`
- `dependency_relation`
- `syntactic_head_ID`
- `event`

Accepted `.entities` header columns:

- `COREF`
- `start_token`
- `end_token`
- `prop`
- `cat`
- `text`

Accepted `.quotes` header columns:

- `quote_start`
- `quote_end`
- `mention_start`
- `mention_end`
- `mention_phrase`
- `char_id`
- `quote`

Accepted `.supersense` header columns:

- `start_token`
- `end_token`
- `supersense_category`
- `text`

Rules:

- missing required header columns raise `ValueError`.
- unknown header columns raise `ValueError` unless T006 explicitly allows strict ignore of extras, which is not recommended.
- malformed TSV rows raise `ValueError`.
- empty required cells raise `ValueError` unless the official BookNLP shape permits optional blanks and the test documents the reason.
- TSV must use tab separators, with optional trailing newline.
- header parsing must be case-sensitive and order-tolerant within the accepted column set.
- header count must match row column count; mismatched rows raise `ValueError`.
- returned rows must be normalized into dict shape compatible with the existing `validate_booknlp_raw_artifact_bundle` row field sets.
- returned rows must not mutate input structures or caller state.
- empty inputs (no rows after the header) are allowed and produce an empty list.

## 6. Numeric Field Decision

The future parser should require numeric coercion for known numeric columns. The following fields must parse as non-negative integers:

Token numeric fields:

- `paragraph_ID`
- `sentence_ID`
- `token_ID_within_sentence`
- `token_ID_within_document`
- `byte_onset`
- `byte_offset`
- `syntactic_head_ID`

Entity numeric fields:

- `COREF`
- `start_token`
- `end_token`

Quote numeric fields:

- `quote_start`
- `quote_end`
- `mention_start`
- `mention_end`
- `char_id`

Supersense numeric fields:

- `start_token`
- `end_token`

Rules:

- numeric values must parse as non-negative integers.
- `bool` is invalid because `True` and `False` are integer subclasses in Python; explicit `bool` values must raise `ValueError`.
- negative values raise `ValueError`.
- non-integer strings raise `ValueError`.
- empty strings in numeric columns raise `ValueError`.
- token/quote/entity/supersense spans must be half-open where applicable.
- `end` values must be greater than or equal to `start` values for any given span; `end < start` raises `ValueError`.
- numeric coercion must use safe integer parsing without falling back to floats, even for whole-number floats.

## 7. Event Derivation Decision

Recording again:

- no `.events` TSV/JSON raw input is accepted as a BookNLP raw artifact.
- future event fixture support is derived from `.tokens.event`.
- `derive_booknlp_events_from_tokens` may return app-owned derived rows.
- derived event rows must be marked as derived support, not raw external output.
- event rows do not imply timeline canon.
- event rows do not imply causal truth.
- event rows do not imply plot canon.
- missing/empty/non-event markers produce no event rows.
- unsupported event markers fail closed or are ignored based on T006 tests, and the chosen behavior must be explicit in tests.
- derived event output must be compatible with `booknlp_adapter_contract.normalize_booknlp_events` and must carry raw output reference `booknlp_tokens` plus a derived support marker, not `booknlp_events`.
- event records must never be returned as raw external BookNLP output even when derived from `.tokens.event`.
- event records do not pass through `booknlp_events_derived` storage kind in this parent; storage helpers are documented for later use only.

## 8. Book JSON Decision

The future parser should require JSON parsing for `.book` fixture text:

Rules:

- input must be JSON object text.
- malformed JSON raises `ValueError`.
- root must be a dict.
- required top-level field: `characters`.
- `characters` must be a list.
- each character entry may include: `agent`, `patient`, `mod`, `poss`, `id`, `g`, `count`, `mentions`.
- `mentions` may include `proper`, `common`, `pronoun` buckets.
- mention entries may include `c` and `n` fields.
- `g` must remain raw aggregate metadata only and must not become identity or demographic claim.
- `g` must not be stored or returned as `gender`, `identity`, `demographic`, or any human-attribute field.
- parser must not create OMI candidates, candidate drafts, or character/location/relationship records from `.book` fixture text.
- parser must not synthesize `g` if it is missing.
- parser must not coerce `g` into a normalized identity field.
- unknown top-level fields raise `ValueError` unless the future test allows strict ignore, which is not recommended.
- character entries with unknown fields raise `ValueError` unless the future test allows strict ignore, which is not recommended.
- mention buckets with unknown keys raise `ValueError` unless the future test allows strict ignore, which is not recommended.

## 9. Raw Artifact Bundle Builder Decision

The future builder API:

`build_booknlp_raw_artifact_bundle_from_fixture_texts(fixture_texts, *, run_manifest, source_map, raw_output_references)`

must:

- parse all provided fixture strings in memory.
- validate `run_manifest` using `raw_extraction_storage.validate_extraction_run_manifest`.
- validate `source_map` using `source_map.validate_source_map`.
- validate `raw_output_references` using `evidence.validate_raw_output_reference`.
- reject `Path` and string path arguments in any position.
- reject file system operations of any kind.
- return a dict compatible with `validate_booknlp_raw_artifact_bundle` (bundle_id, project_id, run_manifest, source_map, tokens, entities, quotes, book_json, supersense, events, raw_output_references, created_at).
- include parsed lists: `tokens`, `entities`, `quotes`, `supersense`, `events`.
- include parsed dict: `book_json`.
- include raw output references that match the manifest's `raw_artifacts`.
- preserve source/evidence/provenance linkage from the provided `source_map` and `run_manifest`.
- not write to disk.
- not persist raw artifacts.
- not create candidates.
- not invoke `build_booknlp_candidate_drafts` or any adapter normalizer that produces candidate drafts.
- not apply promotion.
- not mutate memory/canon.
- not modify input structures in place.
- raise `ValueError` for any forbidden argument, missing required fixture, malformed fixture, invalid manifest, invalid source map, or invalid raw output reference.

Decision:

- The future builder produces raw artifact bundle only.
- Candidate draft creation remains the responsibility of `booknlp_adapter_contract.build_booknlp_candidate_drafts`.
- The future parser must not call `build_booknlp_candidate_drafts`.
- The future parser must not call `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, or `normalize_booknlp_events`.
- The future parser is intentionally narrower than the adapter contract: it parses fixture text and produces a raw artifact bundle; it does not normalize, draft, or persist anything.

## 10. Relationship to Storage Helpers

Recording the boundary between parser and storage:

- `raw_extraction_storage.py` owns path derivation, ID validation, manifest validation, raw output reference validation, and derived artifact directory computation.
- The future parser accepts in-memory fixture text, not storage paths.
- The future parser accepts a `run_manifest` dict validated by the storage helper and a `source_map` dict validated by the source-map helper.
- The future parser may validate `raw_output_references` through `evidence.validate_raw_output_reference` because storage helpers already require that for valid manifest refs.
- The future parser must not read from `writer_assistant/extractions/` on disk.
- The future parser must not write to `writer_assistant/extractions/` on disk.
- The future parser must not list artifacts.
- The future parser implementation remains separate from storage write/read/list helpers.
- The future parser must not call `raw_artifact_path`, `derived_artifact_path`, `extraction_run_dir`, `extraction_manifest_path`, `raw_artifact_dir`, or `derived_artifact_dir` because these return filesystem paths the parser must not touch.
- The future parser must not create files or directories.
- The future parser must not pass `Path` arguments to storage helpers.

## 11. Relationship to Adapter Contract

Recording the boundary between parser and adapter contract:

- `booknlp_adapter_contract.py` validates in-memory raw artifact bundles, normalizes entity/quote/event records, and builds candidate drafts.
- The future fixture parser output must be compatible with `validate_booknlp_raw_artifact_bundle` so the existing adapter contract tests remain green for parsed fixture inputs.
- The future fixture parser must not duplicate candidate draft builder behavior.
- The future fixture parser must not create candidate JSON.
- The future fixture parser must not create canon/memory records.
- The future fixture parser must not call `build_booknlp_candidate_drafts`.
- The future fixture parser must not call `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, or `normalize_booknlp_events`.
- The future fixture parser must not write to candidate storage paths.
- The future fixture parser must not call `candidate_storage`, `candidate_persistence`, `candidate_index`, `candidate_record`, or `candidate_schema`.
- The future fixture parser remains pure parsing only.

## 12. Error Behavior Decision

The future parser should raise `ValueError` for:

- non-string fixture text.
- missing required fixture input.
- malformed TSV (mismatched column count, bad encoding characters, control characters).
- missing TSV headers.
- unknown TSV headers.
- malformed row length.
- invalid numeric field (non-integer, negative, bool, empty).
- invalid offset or span (`end < start`, out-of-range relative to total token count if the fixture provides a count).
- malformed JSON.
- non-dict `.book` JSON root.
- missing required `.book` top-level field `characters`.
- non-list `.book` `characters`.
- invalid `.book` character shape.
- invalid `g` field type (must be a string or numeric aggregate metric, never a boolean identity claim).
- invalid source map.
- invalid manifest.
- invalid raw output reference.
- unsupported fixture key.
- attempts to supply file paths.
- attempts to supply `pathlib.Path` arguments.
- attempts to supply candidate, canon, or memory shortcut fields in any parser argument.
- attempts to call parser with external library or system mutation.
- attempts to read or write files.

The future parser should not silently repair malformed fixture text.

The future parser should not coerce invalid inputs to defaults.

The future parser should not return `None` for failure; it raises `ValueError`.

The future parser should return deep-copied dicts and lists so caller mutation cannot affect internal state.

## 13. Source-Level Boundary Decision

The future production module must avoid forbidden runtime/tool/prose/mutation terms in production source if raw source scans are used by T006 tests.

Forbidden substrings include but are not limited to:

- `booknlp import`
- `from booknlp`
- `import booknlp`
- `spacy.load`
- `import spacy`
- `from spacy`
- `ollama`
- `openai`
- `requests`
- `httpx`
- `fastapi`
- `uvicorn`
- `subprocess`
- `pathlib.Path`
- `open(`
- `.write_text`
- `.mkdir`
- `training`
- `dataset_manifest`
- `jsonl`
- `generated_prose`
- `rewrite`
- `continuation`
- `write_to_canon`
- `mutate_memory`
- `apply_promotion`
- `world_state`
- `storyform_truth`

The future module may build forbidden strings from parts only if the test requires exact substring presence, which is not the case for the future module.

Decision:

- Tests may contain forbidden strings.
- The future production parser module must not.
- The future parser API surface should not accept `Path` or string file paths.
- The future parser source should avoid comments, docstrings, error messages, constants, and helper names containing forbidden strings if source-level tests scan raw module source.
- The future parser does not need filesystem APIs and should not import `os`, `sys`, `pathlib`, `io`, `tempfile`, `shutil`, `subprocess`, `socket`, `urllib`, `http`, `ftplib`, `smtplib`, `multiprocessing`, `threading`, or `asyncio` (beyond default standard library imports).
- The future parser must not import any third-party library.
- The future parser must not include `import` statements beyond the Python standard library.
- The future parser must not include runtime calls to `Path()` for filesystem targets.

## 14. T006 Handoff

T006 is `PHASE8-IMPL-008-T006 — BookNLP fixture parser contract tests`.

T006 should be tests-first only.

Expected future test file:

`tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`

Expected future module:

`backend.story_knowledge.booknlp_fixture_parser`

Expected-red result:

- missing future module import error
- failure limited to missing module or symbol
- no parser implementation in T006

T006 test coverage should include:

- parser module import expected-red.
- token TSV header parsing and required-column validation.
- entity TSV header parsing and required-column validation.
- quote TSV header parsing and required-column validation.
- supersense TSV header parsing and required-column validation.
- numeric coercion and non-negative integer rules for token, entity, quote, and supersense numeric fields.
- bool rejection in numeric fields.
- malformed TSV failures (column count, missing required cell).
- malformed JSON failures.
- `.book` character shape and `mentions` shape.
- `.book` `g` field identity guardrail (no gender, identity, or demographic claim).
- event derivation from token `event` column.
- no `.events` raw input accepted.
- raw artifact bundle builder compatibility with storage manifest and source map.
- raw output refs remain non-canon and non-candidate.
- parser does not persist raw artifacts.
- parser does not create candidates.
- parser does not mutate memory or canon.
- source-level boundary scan for future module.
- existing adapter, storage, source, evidence, and candidate regressions remain green.

T006 test file should not contain forbidden runtime/tool/prose/mutation substrings in production-quality test names; tests may contain such substrings only in test cases that explicitly verify boundary behavior.

T006 must not:

- implement the parser module.
- run pytest against the parser module.
- create raw extraction artifact files under real `projects/`.
- create runtime project files.
- install BookNLP or spaCy.
- import BookNLP or spaCy.
- run BookNLP or spaCy.
- clone, fetch, or pull from any external remote.
- vendor external repository code into `backend/`.
- stage, commit, or push.

## 15. T007 / Next Parent Handoff

Recording:

- `PHASE8-IMPL-008-T007` is closeout only.
- Since T006 is tests-first expected-red, recommend the next parent as:
  - `PHASE8-IMPL-009 — BookNLP fixture parser helper implementation and raw artifact bundle integration`.
- `PHASE8-IMPL-009` should implement the future parser module and make T006 tests pass.
- `PHASE8-IMPL-009` should integrate parsed fixture output into `validate_booknlp_raw_artifact_bundle` without changing the existing mocked adapter contract.
- Real BookNLP install/run should still remain deferred unless owner explicitly changes direction.
- Real spaCy install/run should still remain deferred unless owner explicitly changes direction.
- Raw file write/read/list helpers remain deferred to a later parent.

## 16. Deferred Work

List:

- parser implementation in `backend/story_knowledge/booknlp_fixture_parser.py`.
- real BookNLP install/run/import.
- real BookNLP output file parsing from disk.
- spaCy install/run/import.
- raw artifact write/read/list helpers.
- raw artifact persistence from real project runs.
- byte-to-character source matching implementation.
- extraction orchestrator.
- backend extraction routes.
- frontend parser/review UI.
- candidate JSON persistence from parser outputs.
- apply-promotion.
- memory/canon mutation.
- NCP/Subtxt/dramatica-flow implementation.
- model-assisted extraction.
- training/JSONL/dataset work.
- cloning, fetching, pulling, installing, importing, executing, or vendoring external repository code from `.external_sources/`.
- vendoring external code into `backend/`.
- staging, committing, or pushing.

## 17. Accepted Decision

- ACCEPT in-memory fixture parser contract.
- ACCEPT future module path `backend/story_knowledge/booknlp_fixture_parser.py`.
- ACCEPT future public APIs:
  - `parse_booknlp_tokens_tsv`
  - `parse_booknlp_entities_tsv`
  - `parse_booknlp_quotes_tsv`
  - `parse_booknlp_supersense_tsv`
  - `parse_booknlp_book_json`
  - `build_booknlp_raw_artifact_bundle_from_fixture_texts`
- ACCEPT optional future API:
  - `derive_booknlp_events_from_tokens`
- ACCEPT exact TSV header validation.
- ACCEPT numeric coercion with fail-closed behavior.
- ACCEPT `.book` JSON parser contract with `g` as raw aggregate metadata.
- ACCEPT event derivation from `.tokens.event` only.
- ACCEPT no `.events` raw input.
- ACCEPT raw bundle builder compatibility with `validate_booknlp_raw_artifact_bundle`.
- ACCEPT T006 as tests-first expected-red.
- ACCEPT parser implementation deferred to `PHASE8-IMPL-009`.
- REJECT file path parser inputs.
- REJECT filesystem reads or writes.
- REJECT real BookNLP/spaCy install, import, or execution.
- REJECT candidate, canon, or memory mutation.
- REJECT prose generation, rewrite, continuation, imitation, polish, improvement, or expansion.
- REJECT external code execution, import, or vendoring.
- REJECT `.external_sources/` modification, commit, or staging.
- REJECT context tools, MCP tools, LeanCTX, Graphify, Repomix, CCE, or AI Context execution in T005.
- REJECT staging, commit, or push in T005.
- REJECT training data, JSONL records, dataset files, or manifest updates in T005.
- REJECT package or dependency file changes in T005.
- REJECT backend routes or frontend UI changes in T005.
- REJECT project runtime file creation in T005.
- REJECT model calls, Ollama calls, or external tool execution in T005.
- REJECT source/web retrieval in T005.
