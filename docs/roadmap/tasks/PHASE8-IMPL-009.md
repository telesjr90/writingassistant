# PHASE8-IMPL-009

## ID

`PHASE8-IMPL-009`

## Title

Writer Assistant Core BookNLP fixture parser helper implementation and raw artifact bundle integration

## Status

active after `PHASE8-IMPL-009-T003` implementation. `PHASE8-IMPL-009-T001`, `PHASE8-IMPL-009-T002`, and `PHASE8-IMPL-009-T003` are complete; `PHASE8-IMPL-009-T004` is ready/active.

## Goal

Implement the pure in-memory BookNLP fixture parser helper layer that satisfies the expected-red contract tests from `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`.

The future implementation target is `backend/story_knowledge/booknlp_fixture_parser.py`. The parser helper must consume synthetic in-memory TSV/JSON fixture strings, return in-memory dictionaries/lists, and build raw artifact bundles compatible with `validate_booknlp_raw_artifact_bundle` from `backend/story_knowledge/booknlp_adapter_contract.py`.

This parent must remain fixture-only and in-memory-only. It must not run real BookNLP, install BookNLP, import BookNLP, parse real runtime files from disk, persist raw artifacts, create OMI candidates, or mutate memory/canon.

## Why Now

`PHASE8-IMPL-008` delivered the raw extraction artifact storage contract, pure storage path/manifest helpers, and expected-red BookNLP fixture parser contract tests. The parser contract is now the next narrow implementation gap: `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py` fails only because `backend.story_knowledge.booknlp_fixture_parser` is missing.

`PHASE8-IMPL-009` exists to satisfy that expected-red parser contract without widening into extractor runtime work. It bridges synthetic BookNLP-like TSV/JSON fixture text into the already implemented mocked raw artifact bundle validator while preserving the raw-support, non-canon, non-candidate, no-runtime-extraction, no-package-change, no-model-call, no-generated-prose, and no-memory/canon-mutation boundaries.

## Dependencies

- Completed parent: `PHASE8-IMPL-008` - Writer Assistant Core raw extraction artifact storage and BookNLP fixture parser contract.
- Completed child: `PHASE8-IMPL-008-T007` - Roadmap/status closeout.
- Contract tests and helper foundation:
  - `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`
  - `backend/story_knowledge/raw_extraction_storage.py`
  - `tests/test_writer_assistant_core_raw_extraction_storage_contract.py`
  - `backend/story_knowledge/booknlp_adapter_contract.py`
  - `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
- Decisions and inventory:
  - `docs/roadmap/decisions/PHASE8-IMPL-008-booknlp-fixture-parser-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-008-raw-extraction-artifact-storage-contract-decision.md`
  - `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`

## Scope

Include:

- a docs/decision reconciliation child before implementation;
- a pure standard-library parser module at `backend/story_knowledge/booknlp_fixture_parser.py` in a later implementation child;
- in-memory TSV parsing helpers for `.tokens`, `.entities`, `.quotes`, and `.supersense` fixture strings;
- in-memory `.book` JSON parsing with `g` preserved only as raw aggregate metadata;
- app-owned derived event support from `.tokens.event` only;
- an in-memory raw artifact bundle builder compatible with `validate_booknlp_raw_artifact_bundle`;
- validation through existing source-map, evidence, adapter-contract, and raw storage helper boundaries where the tests require it;
- fail-closed handling for missing headers, unknown headers, malformed rows, numeric coercion failures, unsafe fixture keys, path-like input, forbidden fields, unsupported raw `.events` input, and source/evidence/raw-ref validation failures;
- source-level boundary compliance for no filesystem I/O, no runtime tool imports, no model calls, no generated prose, no apply-promotion, and no memory/canon mutation.

## Exclusions

Explicitly excluded:

- parser implementation in `PHASE8-IMPL-009-T001`;
- real BookNLP install, import, run, or execution;
- real spaCy install, import, run, or execution;
- real BookNLP output file parsing from disk;
- filesystem reads or writes in the parser module;
- raw artifact write/read/list helpers;
- raw extraction artifact files under real `projects/`;
- runtime extraction orchestration;
- backend extraction routes or API endpoints;
- frontend extraction, review, or parse-preview UI;
- package or dependency file changes;
- external repository clone, fetch, pull, execution, import, copy, or vendoring;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- OMI candidate creation or candidate JSON persistence from parsed fixture output;
- apply-promotion;
- memory/canon mutation;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion of owner-authored prose;
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs.

## Child-Task Plan

1. `PHASE8-IMPL-009-T001` - Publish BookNLP fixture parser implementation parent. Status: complete on successful publication.
2. `PHASE8-IMPL-009-T002` - Parser implementation contract reconciliation decision. Status: complete as of 2026-06-21.
3. `PHASE8-IMPL-009-T003` - Minimal BookNLP TSV fixture parser implementation. Status: complete as of 2026-06-21.
4. `PHASE8-IMPL-009-T004` - Book JSON parsing and token-event derivation implementation. Status: ready/active.
5. `PHASE8-IMPL-009-T005` - Raw artifact bundle builder integration with adapter/storage/source/evidence contracts. Status: planned/draft.
6. `PHASE8-IMPL-009-T006` - Targeted parser contract validation and boundary hardening. Status: planned/draft.
7. `PHASE8-IMPL-009-T007` - Roadmap/status closeout. Status: planned/draft.

## Child Task Details

### `PHASE8-IMPL-009-T001` - Publish BookNLP fixture parser implementation parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-009` active in roadmap/status docs.
- Mark `PHASE8-IMPL-009-T001` complete on success.
- Mark `PHASE8-IMPL-009-T002` ready/active.
- Confirm `PHASE8-IMPL-008` and `PHASE8-IMPL-008-T007` are complete in local roadmap files.
- Confirm `backend/story_knowledge/booknlp_fixture_parser.py` does not exist before this parent implementation starts.
- Confirm the parser contract test remains expected-red because the future parser module is missing.
- No parser implementation, no backend/test edits, no raw artifact writes, no BookNLP/spaCy install/run/import, no context tools, no web research, no staging, no commit, no push.

### `PHASE8-IMPL-009-T002` - Parser implementation contract reconciliation decision

- Docs/decision only.
- Status: complete as of 2026-06-21.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-009-parser-implementation-contract-reconciliation-decision.md`.
- Reconcile the T006 parser contract tests with the T005 decision, T002 storage decision, raw storage helper behavior, adapter-contract bundle validator, source/evidence helper expectations, and source-level forbidden-term scan.
- Decide exact implementation split for T003 through T006.
- Decide whether all parser APIs should be implemented in one child or staged by fixture type while keeping imports collectible.
- Decide strict behavior for empty TSV cells, row count mismatches, numeric coercion, token/event marker handling, raw bundle builder missing optional fixture keys, and path-like string rejection.
- Confirm source-level implementation constraints for `backend/story_knowledge/booknlp_fixture_parser.py`.
- No runtime code, no tests, no parser implementation, no package changes, no external tool/runtime work.

T002 accepted:

- public parser APIs:
  - `parse_booknlp_tokens_tsv`
  - `parse_booknlp_entities_tsv`
  - `parse_booknlp_quotes_tsv`
  - `parse_booknlp_supersense_tsv`
  - `parse_booknlp_book_json`
  - `derive_booknlp_events_from_tokens`
  - `build_booknlp_raw_artifact_bundle_from_fixture_texts`
- implementation split:
  - T003: minimal TSV parser implementation and import/symbol collection support.
  - T004: `.book` JSON parser and `.tokens.event` event derivation.
  - T005: in-memory raw artifact bundle builder integration with storage/source/evidence/adapter validators.
  - T006: full parser contract validation and boundary hardening.
- T003 as the first runtime parser implementation child.
- standard-library-only, in-memory-only parser helpers.
- no filesystem I/O in parser helpers.
- no raw artifact persistence.
- no parser implementation in T002.
- no test changes in T002.
- no runtime extraction, routes, UI, package changes, real BookNLP/spaCy install/run/import, candidate persistence, generated prose, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-009-T003` - Minimal BookNLP TSV fixture parser implementation

- Create `backend/story_knowledge/booknlp_fixture_parser.py` only if T002 authorizes the implementation split.
- Implement public API symbols required for test collection.
- Implement in-memory parsing for `.tokens`, `.entities`, `.quotes`, and `.supersense` TSV fixture strings as authorized by T002.
- Keep implementation pure, standard-library-only, and side-effect free.
- Do not implement filesystem I/O, raw artifact persistence, candidate persistence, runtime extraction, external tool imports, package changes, routes, UI, model calls, generated prose, apply-promotion, or memory/canon mutation.
- Status: complete as of 2026-06-21.
- Created parser module: `backend/story_knowledge/booknlp_fixture_parser.py`.
- Implemented TSV APIs:
  - `parse_booknlp_tokens_tsv`
  - `parse_booknlp_entities_tsv`
  - `parse_booknlp_quotes_tsv`
  - `parse_booknlp_supersense_tsv`
- Added fail-closed deferred public symbols for:
  - `parse_booknlp_book_json`
  - `derive_booknlp_events_from_tokens`
  - `build_booknlp_raw_artifact_bundle_from_fixture_texts`
- Parser contract status: collection passes; full contract remains partially red only on deferred `.book` JSON, token-event derivation, and raw artifact bundle builder behavior; TSV parser portions passed in the full run.
- No parser filesystem I/O, no real BookNLP/spaCy install or execution, no runtime extraction, no raw artifact persistence, and no candidate/canon/memory mutation were added.

### `PHASE8-IMPL-009-T004` - Book JSON parsing and token-event derivation implementation

- Implement `parse_booknlp_book_json` and `derive_booknlp_events_from_tokens` as authorized by T002/T003 outcomes.
- Preserve `.book` `g` as raw aggregate metadata only.
- Derive app-owned event support from token `event` markers only.
- Reject `.events` raw input and do not claim real external BookNLP event files exist.
- No raw artifact persistence, no candidate creation, no canon/memory mutation, no runtime extraction.

### `PHASE8-IMPL-009-T005` - Raw artifact bundle builder integration with adapter/storage/source/evidence contracts

- Implement `build_booknlp_raw_artifact_bundle_from_fixture_texts` as an in-memory bundle builder.
- Validate run manifest, source map, and raw output references through existing helpers where required by the contract tests.
- Ensure the built bundle is compatible with `booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle`.
- Keep parser output as raw support data only, not candidates, canon, memory, or promotion records.
- No raw artifact file write/read/list behavior and no runtime project files.

### `PHASE8-IMPL-009-T006` - Targeted parser contract validation and boundary hardening

- Run the targeted parser contract tests and focused existing regressions authorized by the task prompt.
- Repair only parser-helper contract gaps in `backend/story_knowledge/booknlp_fixture_parser.py` if authorized.
- Preserve source-level forbidden-term boundaries.
- Do not widen into raw artifact persistence, runtime extraction, routes, UI, package/dependency changes, model calls, generated prose, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-009-T007` - Roadmap/status closeout

- Docs/status closeout only after implementation and validation children complete.
- Mark `PHASE8-IMPL-009` complete only if the parser contract is satisfied and all boundaries remain intact.
- Recommend the next parent without activating it unless separately authorized.
- No runtime feature expansion.

## T001 Publication Result

`PHASE8-IMPL-009-T001` publishes this parent as the next active Writer Assistant Core parent. It does not implement parser helpers and does not create `backend/story_knowledge/booknlp_fixture_parser.py`.

## T002 Decision Result

`PHASE8-IMPL-009-T002` accepts the parser implementation split and public API contract for T003 through T006. It creates only the decision artifact and roadmap/status updates. It does not implement parser helpers, does not create `backend/story_knowledge/booknlp_fixture_parser.py`, does not modify tests, does not add raw artifact write/read/list helpers, does not create runtime project files, and does not install/import/run BookNLP or spaCy.

## T003 Implementation Result

`PHASE8-IMPL-009-T003` created `backend/story_knowledge/booknlp_fixture_parser.py` and implemented the minimal pure in-memory TSV parser helpers for tokens, entities, quotes, and supersense fixture text.

Implemented TSV behavior includes exact header validation, duplicate/unknown/missing header rejection, malformed row rejection, empty required cell rejection except token `event`, non-negative integer coercion for known numeric fields, bool-like/negative/non-integer numeric rejection, and byte/span ordering checks. The output remains raw support dictionaries only.

Deferred APIs remain fail-closed placeholders for `PHASE8-IMPL-009-T004` and `PHASE8-IMPL-009-T005`: `.book` JSON parsing, token-event derivation, and raw artifact bundle building. The parser contract collection now passes. The full parser contract remains partially red only for these deferred APIs, while the TSV parser portions pass.

No filesystem I/O, real BookNLP/spaCy install or execution, runtime extraction, raw artifact persistence, raw write/read/list helpers, candidate/canon/memory mutation, generated prose behavior, package changes, routes, UI, project runtime files, training, JSONL, dataset work, staging, commit, or push were added.
