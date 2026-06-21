# PHASE8-IMPL-009 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-009`
- Title: Writer Assistant Core BookNLP fixture parser helper implementation and raw artifact bundle integration
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active after T001 publication
- Depends on: completed `PHASE8-IMPL-008`
- Current child: `PHASE8-IMPL-009-T001` - Publish BookNLP fixture parser implementation parent
- Next child: `PHASE8-IMPL-009-T002` - Parser implementation contract reconciliation decision

## 2. Why This Parent Exists

`PHASE8-IMPL-008` closed the raw extraction artifact storage and BookNLP fixture parser contract parent. It produced:

- raw extraction artifact storage contract decision;
- pure storage path and manifest validation helpers in `backend/story_knowledge/raw_extraction_storage.py`;
- expected-red BookNLP fixture parser contract tests in `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`;
- a clear recommendation that parser implementation belongs in `PHASE8-IMPL-009`.

The remaining implementation gap is narrow: create the pure fixture parser helper module that turns in-memory BookNLP-like TSV/JSON fixture text into in-memory raw artifact bundles acceptable to `validate_booknlp_raw_artifact_bundle`.

This parent does not authorize real BookNLP runtime, real spaCy runtime, raw artifact persistence, runtime extraction, routes, UI, package changes, candidate creation, generated prose, apply-promotion, or memory/canon mutation.

## 3. Existing Inputs

Required implementation contract:

- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py` - expected-red parser contract tests for future `backend.story_knowledge.booknlp_fixture_parser`.
- `docs/roadmap/decisions/PHASE8-IMPL-008-booknlp-fixture-parser-contract-decision.md` - accepted parser contract.
- `docs/roadmap/decisions/PHASE8-IMPL-008-raw-extraction-artifact-storage-contract-decision.md` - storage/raw artifact boundary contract.
- `docs/roadmap/tasks/PHASE8-IMPL-008.md` - completed parent record and T006/T007 handoff.
- `docs/roadmap/inventory/PHASE8-IMPL-008.md` - completed parent inventory and future parent recommendation.
- `docs/roadmap/enrichment/PHASE8-IMPL-008.enrichment.json` - completed parent enrichment metadata.

Foundation modules and tests:

- `backend/story_knowledge/raw_extraction_storage.py` - pure storage path and manifest validation helpers; no raw artifact write/read/list helpers.
- `tests/test_writer_assistant_core_raw_extraction_storage_contract.py` - storage helper contract coverage.
- `backend/story_knowledge/booknlp_adapter_contract.py` - mocked adapter contract and raw bundle validator.
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py` - adapter contract coverage.
- `backend/story_knowledge/source_map.py` - source document, source map, and locator validation helpers.
- `backend/story_knowledge/evidence.py` - evidence/provenance/raw output reference validation helpers.
- `tests/test_writer_assistant_core_source_evidence_contract.py` - source/evidence regression coverage.

Prior source evidence and decisions:

- `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`
- `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`

## 4. Accepted BookNLP Fixture Facts

From the completed local source inventory and parser contract decision:

- BookNLP real output kinds recorded for fixture compatibility: `.tokens`, `.entities`, `.quotes`, `.supersense`, `.book`, and `.book.html`.
- No separate real `.events` file is accepted.
- Event support is app-owned derived support from `.tokens.event`.
- `.book.html` is optional display/reference output and is not parser input for story claims.
- `.book` `g` is raw aggregate pronoun distribution metadata, not identity.

Accepted TSV headers:

- tokens: `paragraph_ID`, `sentence_ID`, `token_ID_within_sentence`, `token_ID_within_document`, `word`, `lemma`, `byte_onset`, `byte_offset`, `POS_tag`, `fine_POS_tag`, `dependency_relation`, `syntactic_head_ID`, `event`
- entities: `COREF`, `start_token`, `end_token`, `prop`, `cat`, `text`
- quotes: `quote_start`, `quote_end`, `mention_start`, `mention_end`, `mention_phrase`, `char_id`, `quote`
- supersense: `start_token`, `end_token`, `supersense_category`, `text`

## 5. Scope

Implementation scope for later children:

- pure standard-library module `backend/story_knowledge/booknlp_fixture_parser.py`;
- parser APIs named by the T006 contract tests;
- exact header validation and fail-closed numeric coercion;
- in-memory TSV/JSON parsing only;
- derived event support from tokens only;
- raw artifact bundle builder compatibility with `validate_booknlp_raw_artifact_bundle`;
- input immutability;
- no filesystem I/O and no runtime side effects;
- no candidate/canon/memory/promotion writes.

## 6. Non-Scope

Explicitly out of scope:

- parser implementation in T001;
- raw artifact write/read/list helpers;
- real BookNLP install, import, run, execution, or disk-output parsing;
- real spaCy install, import, run, or execution;
- external repo clone, fetch, pull, import, execution, copying, or vendoring;
- runtime extraction orchestration;
- project runtime extraction files;
- backend routes or frontend UI;
- package/dependency changes;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- OMI candidate creation or candidate JSON persistence from parsed output;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion;
- apply-promotion;
- memory/canon mutation;
- training data, JSONL, dataset manifests, or model artifacts.

## 7. Risks

- Parser implementation widens into real BookNLP or spaCy runtime.
- Parser reads fixture files from disk instead of accepting in-memory strings.
- Parser output is mistaken for candidate, canon, memory, or approved truth.
- Raw artifact bundle integration calls candidate builders or persistence helpers.
- `.events` is accidentally treated as a real raw BookNLP artifact.
- `.book` `g` is accidentally treated as identity.
- Source/evidence/raw-ref validation is bypassed.
- Source-level forbidden runtime/tool/prose/mutation terms regress.
- Raw artifact write/read/list helpers are added before a separate authorization.
- Project runtime files are created under `projects/`.

## 8. T001 Precondition Findings

- Local roadmap files show `PHASE8-IMPL-008` complete.
- Local roadmap files show `PHASE8-IMPL-008-T007` complete.
- Local roadmap files show no active child after `PHASE8-IMPL-008-T007`.
- `PHASE8-IMPL-009` was recommended but not active before this publication.
- `backend/story_knowledge/raw_extraction_storage.py` exists.
- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py` exists.
- `backend/story_knowledge/booknlp_fixture_parser.py` does not exist at T001 publication.
- Target parser contract remains expected-red because the parser module is missing.
- No raw artifact write/read/list helpers are authorized by this parent.
- `.external_sources/` remains an ignored local source cache and must not be staged or committed.

## 9. Child Sequence

1. `PHASE8-IMPL-009-T001` - Publish BookNLP fixture parser implementation parent.
2. `PHASE8-IMPL-009-T002` - Parser implementation contract reconciliation decision.
3. `PHASE8-IMPL-009-T003` - Minimal BookNLP TSV fixture parser implementation.
4. `PHASE8-IMPL-009-T004` - Book JSON parsing and token-event derivation implementation.
5. `PHASE8-IMPL-009-T005` - Raw artifact bundle builder integration with adapter/storage/source/evidence contracts.
6. `PHASE8-IMPL-009-T006` - Targeted parser contract validation and boundary hardening.
7. `PHASE8-IMPL-009-T007` - Roadmap/status closeout.

