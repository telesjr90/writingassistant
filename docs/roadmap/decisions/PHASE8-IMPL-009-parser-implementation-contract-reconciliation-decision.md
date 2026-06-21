# PHASE8-IMPL-009 Parser Implementation Contract Reconciliation Decision

## 1. Decision Summary

- T002 accepts the implementation split for `PHASE8-IMPL-009`.
- T003 will create `backend/story_knowledge/booknlp_fixture_parser.py` and implement minimal in-memory TSV parser helpers.
- T004 will add `.book` JSON parsing and event derivation from `.tokens.event`.
- T005 will add raw artifact bundle builder integration with storage/source/evidence/adapter validators.
- T006 will validate and harden the full parser contract.
- No real BookNLP/spaCy runtime is authorized.
- No filesystem I/O is authorized in parser helpers.
- No raw artifact persistence is authorized.
- No candidate persistence, apply-promotion, memory/canon mutation, generated prose, rewrite, or continuation is authorized.

## 2. Evidence Reviewed

T002 reviewed:

- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`
- `docs/roadmap/decisions/PHASE8-IMPL-008-booknlp-fixture-parser-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-008-raw-extraction-artifact-storage-contract-decision.md`
- `backend/story_knowledge/raw_extraction_storage.py`
- `backend/story_knowledge/booknlp_adapter_contract.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`
- `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`

No new external retrieval was performed.

## 3. Expected-Red Contract Status

- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py` is expected-red.
- Failure is expected to be limited to missing `backend.story_knowledge.booknlp_fixture_parser`.
- T002 does not change the test file.
- T003 begins implementation by satisfying the module import and TSV parser symbols.

The target test was not run in T002 because this is a docs/decision-only task and the parser module is still absent.

## 4. Public API Decision

T002 accepts these future public APIs:

- `parse_booknlp_tokens_tsv(text: str) -> list[dict]`
- `parse_booknlp_entities_tsv(text: str) -> list[dict]`
- `parse_booknlp_quotes_tsv(text: str) -> list[dict]`
- `parse_booknlp_supersense_tsv(text: str) -> list[dict]`
- `parse_booknlp_book_json(text: str) -> dict`
- `derive_booknlp_events_from_tokens(tokens: list[dict]) -> list[dict]`
- `build_booknlp_raw_artifact_bundle_from_fixture_texts(fixture_texts: dict, *, run_manifest: dict, source_map: dict, raw_output_references: list[dict]) -> dict`

Although the T005 decision marked `derive_booknlp_events_from_tokens` optional, the existing expected-red contract includes it in the public API tuple and references it in bundle behavior. T002 accepts it as part of the implementation parent to reduce ambiguity.

## 5. T003 Implementation Decision - Minimal TSV Parsers

T003 should:

- create `backend/story_knowledge/booknlp_fixture_parser.py`;
- implement only the four TSV parser APIs if practical:
  - `parse_booknlp_tokens_tsv`
  - `parse_booknlp_entities_tsv`
  - `parse_booknlp_quotes_tsv`
  - `parse_booknlp_supersense_tsv`
- expose placeholder public symbols for later APIs only if required to allow targeted TSV tests to run, but placeholders must fail closed with `NotImplementedError` or `ValueError` rather than silently returning incomplete data;
- keep the module pure standard-library only;
- avoid filesystem APIs;
- avoid imports from BookNLP/spaCy;
- avoid candidate/canon/memory behavior;
- make TSV parser portions of the contract pass if possible;
- accept that the full parser contract may remain partially red until T004/T005.

TSV parser behavior to implement in T003:

- exact header validation;
- no unknown columns unless a later accepted decision explicitly allows them, which T002 does not;
- malformed row length raises `ValueError`;
- required cell validation;
- numeric coercion to non-negative integers;
- bool-like string rejection for numeric fields;
- negative/non-integer rejection;
- offset/span ordering checks;
- return list of dictionaries;
- do not mutate caller input.

## 6. T004 Implementation Decision - Book JSON and Event Derivation

T004 should:

- implement `parse_booknlp_book_json`;
- implement `derive_booknlp_events_from_tokens`;
- preserve `.book` `g` field as raw aggregate metadata only;
- validate `.book` root as dict;
- require `characters` list;
- validate character and mention shape as required by tests;
- derive events only from token rows with event markers;
- reject any `.events` raw input conceptually through builder behavior later;
- keep derived events as app-owned support only;
- avoid timeline/canon/causal truth claims;
- keep no filesystem I/O and no external imports.

## 7. T005 Implementation Decision - Raw Artifact Bundle Builder

T005 should implement:

`build_booknlp_raw_artifact_bundle_from_fixture_texts(...)`

The builder should:

- accept in-memory fixture strings only;
- reject `Path` or path-like inputs;
- reject unsupported fixture keys;
- parse provided TSV/JSON fixture text;
- validate `run_manifest` via `raw_extraction_storage.validate_extraction_run_manifest`;
- validate `source_map` via `source_map.validate_source_map`;
- validate raw output references via `evidence.validate_raw_output_reference`;
- build an in-memory raw artifact bundle compatible with `booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle`;
- include tokens, entities, quotes, supersense, book_json, events, raw refs, manifest/source map linkage, and required bundle metadata according to tests;
- not call candidate draft builders or normalizers;
- not write files;
- not read files;
- not persist raw artifacts;
- not create candidates.

T005 should preserve the storage decision that derived event support is `booknlp_events_derived` and should stop with a narrow PARTIAL report if the parser contract and existing adapter/evidence raw reference shape conflict in a way that cannot be reconciled without weakening safety.

## 8. T006 Validation and Hardening Decision

T006 should:

- run the full parser contract test;
- run raw extraction storage contract tests;
- run BookNLP adapter contract tests;
- run source/evidence tests;
- run candidate regressions;
- run focused OMI/project regressions if local style requires;
- repair only parser-helper gaps;
- ensure source-level boundary scan passes;
- update roadmap/status as validation/hardening only unless small parser repairs are required;
- not expand scope.

## 9. Test Contract Correction Policy

- T002 does not modify tests.
- Future implementation children should not weaken safety tests.
- If T003/T004/T005 discovers a contradiction between tests and decisions, stop and report PARTIAL unless the correction is purely narrow and preserves safety.

Allowed narrow corrections, if ever required:

- aligning exact helper names with accepted public API;
- clarifying event derivation as app-owned support;
- correcting a fixture typo that contradicts the official T005 decision.

Forbidden corrections:

- allowing filesystem I/O;
- allowing real BookNLP/spaCy imports;
- allowing candidate/canon/memory mutation;
- allowing generated prose/rewrite/continuation;
- weakening path/input rejection;
- bypassing storage/source/evidence/adapter validation.

## 10. Source-Level Boundary Decision

Future production parser module must avoid forbidden runtime/tool/prose/mutation/filesystem terms used by the parser contract source scan.

Implementation children should avoid these substrings in production source comments/docstrings/error strings when source scans are literal:

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
- `Path(`
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

Tests may contain these strings; production source must not.

## 11. Dependency and Import Policy

Accept:

- standard library only;
- likely `csv`;
- likely `io.StringIO`;
- likely `json`;
- likely `copy`;
- existing local modules only:
  - `backend.story_knowledge.raw_extraction_storage`
  - `backend.story_knowledge.source_map`
  - `backend.story_knowledge.evidence`
  - `backend.story_knowledge.booknlp_adapter_contract`

Reject:

- BookNLP import;
- spaCy import;
- any external package;
- package/dependency file changes;
- filesystem/pathlib parser APIs;
- subprocess or network libraries;
- model/runtime calls.

## 12. In-Memory Input Policy

Accept:

- TSV fixture text strings;
- JSON fixture text strings;
- dict/list metadata inputs for manifest/source map/raw refs;
- optional `book_html` as metadata-only string if tests already include it.

Reject:

- file paths;
- `Path` objects;
- file-like objects;
- bytes unless tests explicitly require bytes rejection;
- any API that opens files;
- any API that writes files;
- any API that lists directories;
- any API that reads `.external_sources/` or `projects/`.

## 13. Parser Output Policy

Output remains raw support data only.

Parser output must not include:

- candidate JSON persistence;
- owner decisions;
- promotion decisions;
- canon flags;
- memory write permissions;
- generated prose fields;
- rewrite/continuation fields;
- storyform truth;
- timeline truth;
- character identity truth from `.book.g`.

Parser output may include only raw-support fields needed by tests and adapter validation.

## 14. Risk Decisions

Active risks and mitigations:

- fixture parser mistaken for real BookNLP runtime - mitigated by naming, docs, no imports, and no filesystem I/O;
- parser output mistaken for candidates/canon - mitigated by raw support output and adapter boundary;
- event derivation mistaken for timeline truth - mitigated by app-owned derived support status;
- `.book.g` mistaken for identity/demographic truth - mitigated by raw aggregate metadata rule;
- quote/coreference attribution mistaken for approved truth - mitigated by candidate-only downstream boundary;
- source-level scans forcing awkward source wording - mitigated by minimal production comments/docstrings;
- T003 partial green/full red sequencing - mitigated by explicit split and T006 full hardening.

## 15. Accepted Decision

- ACCEPT PHASE8-IMPL-009 implementation split T003-T006.
- ACCEPT T003 as minimal TSV parser implementation.
- ACCEPT T004 as `.book` JSON parser and event derivation implementation.
- ACCEPT T005 as raw artifact bundle builder integration.
- ACCEPT T006 as validation/hardening.
- ACCEPT all parser APIs listed in section 4.
- ACCEPT standard-library-only, in-memory-only implementation.
- ACCEPT no filesystem I/O.
- ACCEPT no BookNLP/spaCy import/run/install.
- ACCEPT raw support output only.
- ACCEPT no candidate/canon/memory mutation.
- REJECT implementation in T002.
- REJECT test weakening in T002.
- REJECT runtime extraction, routes, UI, package changes, raw persistence, generated prose, rewrite, continuation, apply-promotion, memory/canon mutation.
