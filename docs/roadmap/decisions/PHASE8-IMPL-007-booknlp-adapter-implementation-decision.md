# PHASE8-IMPL-007 BookNLP Adapter Implementation Decision

## 1. Decision Summary

T003 accepts a staged implementation plan for `backend/story_knowledge/booknlp_adapter_contract.py`.

- T004 will implement manifest and raw artifact bundle validators first.
- T005 will implement mocked entity, quote, and event normalization helpers.
- T006 will implement or harden the candidate draft builder, fail-closed behavior, and boundary checks.
- The implementation remains standard-library only.
- The implementation must not import, install, or run BookNLP.
- The implementation must not import, install, or run spaCy.
- The implementation must use mocked BookNLP-like in-memory dictionaries only.
- Real BookNLP parsing remains deferred.
- Raw artifacts remain non-canon and non-candidate.
- Candidate drafts remain unpersisted.
- Owner review remains mandatory.
- No prose generation, rewrite, continuation, apply-promotion, or memory/canon mutation is allowed.

## 2. Evidence Basis

This decision is based on:

- `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`
- `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md`
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`

T002 confirmed real BookNLP artifacts: `.tokens`, `.entities`, `.quotes`, `.supersense`, `.book`, and `.book.html`. T002 found no separate `.events` file; events are derived from `.tokens.event`. T002 also confirmed real field names for `.tokens`, `.entities`, `.quotes`, `.supersense`, and `.book`.

Real BookNLP dependencies remain too heavy for this parent and are deferred. Existing source/evidence helpers provide the safe validation primitives for source documents, source maps, source locators, evidence records, run provenance, and raw output references.

## 3. Raw Shape vs Normalized Shape Decision

### Raw BookNLP-like shapes

Raw mocked fixture shapes should reflect real BookNLP source names where practical.

`.tokens` raw-like fields:

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

`.entities` raw-like fields:

- `COREF`
- `start_token`
- `end_token`
- `prop`
- `cat`
- `text`

`.quotes` raw-like fields:

- `quote_start`
- `quote_end`
- `mention_start`
- `mention_end`
- `mention_phrase`
- `char_id`
- `quote`

`.supersense` raw-like fields:

- `start_token`
- `end_token`
- `supersense_category`
- `text`

`.book` raw-like fields:

- `characters`
- character fields: `agent`, `patient`, `mod`, `poss`, `id`, `g`, `count`, `mentions`
- mention buckets: `proper`, `common`, `pronoun`
- mention bucket entries: `c`, `n`

### Adapter-normalized shapes

Adapter-normalized internal records may use app-owned field names for clarity, including:

- `source_locator`
- `confidence`
- `raw_output_refs`
- `normalization_status`
- `candidate_type`
- `target_category`
- `evidence`
- `provenance`

Current `tests/test_writer_assistant_core_booknlp_adapter_contract.py` mostly uses app-normalized mocked in-memory dictionaries rather than exact raw BookNLP output rows. That is acceptable for the implementation parent if the code and docs keep the boundary explicit: raw fixture builders should use or accept `raw_*`/BookNLP-like fields where needed, while normalized output drafts should use app-owned candidate/evidence fields.

T004 validators should accept the current T006 test shapes where they are clearly adapter-normalized mocked shapes. If a current test shape conflicts with T002-verified real BookNLP field names or falsely treats an app-derived abstraction as a raw BookNLP file, T004 is authorized to make minimal contract-test fixture corrections before implementation. T003 does not make those fixture corrections.

## 4. Fixture Correction Policy

Current T006 fixtures need limited policy refinement, not broad replacement.

Authorized future fixture corrections:

- Mark `booknlp_events` as app-derived from `.tokens.event`, not as a real raw `.events` or `events.tsv` BookNLP output file.
- Add or adjust raw-like fixture aliases only where tests need to exercise T002-verified BookNLP field names.
- Preserve the existing app-normalized fixture records where they are testing normalized adapter behavior rather than raw BookNLP shape.
- Record any fixture correction in the T004 or T006 status docs.

Deferred fixture changes:

- Exact real BookNLP file parser fixtures.
- Full `.book.html` parsing.
- Full byte-to-character source snapshot matching.
- Any fixture that requires installing or running BookNLP or spaCy.

T004 may edit `tests/test_writer_assistant_core_booknlp_adapter_contract.py` only if needed to align the contract with T002 verified source inventory. T004 must not delete safety tests, weaken boundaries, change the expected public API names, add real BookNLP dependencies, or widen into real parser implementation. Prefer a small compatibility layer in the future helper if it keeps tests stable and the boundary safe.

## 5. Event Derivation Decision

`booknlp_events` is not a raw BookNLP output file. In PHASE8-IMPL-007 it remains an app-owned derived abstraction.

Future event records are derived from `.tokens.event` where token rows contain event markers. Event derivation must use token source locators and source-map evidence. Event records remain candidate support only. Event records do not imply timeline canon, causal-chain truth, plot truth, or owner-approved story knowledge.

Missing or ambiguous event markers must fail closed.

T004 raw artifact bundle validators may allow `events` as an app-derived list, but must not require a raw `events.tsv` artifact. T005 normalizers may normalize event drafts from token rows or app-derived event fixture rows. T006 should harden fail-closed behavior.

## 6. Offset Mapping Decision

BookNLP raw token offsets are byte-oriented. The app's evidence/source-map foundation uses Python string character offsets as primary first-slice locators.

PHASE8-IMPL-007 will not implement full byte-to-character source snapshot matching. In this parent, mocked fixtures may include both byte offsets and app-owned `source_locator` objects. The adapter contract must validate byte offsets and preserve them as raw evidence support. Candidate drafts must depend on app-owned `source_locator` and evidence before normalization succeeds.

If character offsets cannot be reliably established, normalized output must be rejected or marked insufficient evidence. No guessed character spans and no generated text may fill locator gaps. Full byte-to-character mapping against real source snapshots is deferred to a later parent.

T004 validators should accept byte offset fields from raw-like records. T005 normalizers should require or derive app-owned source locators from fixture data.

## 7. `g` Field / Identity Guardrail Decision

BookNLP `.book` character field `g` must not be treated as gender identity.

- `g` must not create personal-attribute claims.
- `g` may be stored only as raw aggregate support metadata if used at all.
- Character and alias candidates must rely on source evidence and owner review.
- Any inferred identity or demographic claim is out of scope.

## 8. Coreference / Quote Attribution Guardrail Decision

`COREF` clusters and character IDs are extraction signals only. Coreference may conflate entities. Quote attribution may be wrong or ambiguous.

Speaker attribution must remain candidate support. Ambiguous or low-confidence quote attribution should produce insufficient-evidence/rejected drafts or no candidate. Nothing in this parent approves character truth, alias truth, speaker truth, relationship truth, timeline truth, or causal truth.

## 9. Public API Implementation Split

Future module:

`backend/story_knowledge/booknlp_adapter_contract.py`

Expected public APIs:

- `validate_booknlp_run_manifest(manifest: dict) -> dict`
- `validate_booknlp_raw_artifact_bundle(bundle: dict) -> dict`
- `normalize_booknlp_entity_mentions(bundle: dict, source_map: dict) -> list[dict]`
- `normalize_booknlp_quotes(bundle: dict, source_map: dict) -> list[dict]`
- `normalize_booknlp_events(bundle: dict, source_map: dict) -> list[dict]`
- `build_booknlp_candidate_drafts(bundle: dict, source_map: dict) -> list[dict]`

### T004

Implement:

- module creation
- all six public API symbols immediately, to resolve import/attribute collection failures
- `validate_booknlp_run_manifest`
- `validate_booknlp_raw_artifact_bundle`
- private validation helpers
- raw-like and/or normalized fixture compatibility required by tests
- no candidate draft builder logic except safe placeholder behavior if needed

T004 must make a meaningful subset or all validator tests pass. T004 may return empty lists or fail-closed placeholders from normalizers/builders only where tests allow.

### T005

Implement:

- `normalize_booknlp_entity_mentions`
- `normalize_booknlp_quotes`
- `normalize_booknlp_events`
- evidence/provenance/source locator draft shaping
- unsupported or ambiguous output handling
- no persistence

### T006

Implement or harden:

- `build_booknlp_candidate_drafts`
- fail-closed behavior
- boundary/source scan compliance
- any remaining contract gaps
- validation-only closeout if T004/T005 already make the contract green

If the existing test suite requires all behavior immediately, T004 may implement more than validators, but must not widen scope beyond pure mocked helpers.

## 10. Source-Level Forbidden Terms Decision

The future production module must not contain imports or runtime hooks for:

- `from booknlp`
- `import booknlp`
- `spacy.load`
- `requests`
- `httpx`
- `fastapi`
- `uvicorn`
- `subprocess`
- `open(`
- `.write_text`
- `.mkdir`
- package manager calls
- model clients
- `ollama`
- `openai`

The module must also avoid generation/mutation boundary terms if source-level tests scan literal substrings:

- `generated_prose`
- `rewrite`
- `continuation`
- `write_to_canon`
- `mutate_memory`
- `apply_promotion`
- `world_state`
- `storyform_truth`

T004 must avoid forbidden substrings in comments, docstrings, error messages, constants, and helper names if source-level tests scan raw module source. If accepted artifact names require a forbidden substring, T004 should build those strings from parts only if strictly necessary. Prefer neutral names such as `raw_kind`, `draft`, `blocked_field`, and `promotion_field_parts`. T004 must not weaken source-level tests.

## 11. Data Validation Policy

- All public functions must require dict inputs where applicable.
- Public functions must return copies and never mutate caller input.
- Invalid manifest or bundle structure must raise `ValueError`.
- Structurally valid but ambiguous extraction claims must fail closed as rejected or insufficient-evidence draft shapes.
- Nested source documents, source maps, and source locators should use existing helpers where possible.
- Raw output references should use `evidence.validate_raw_output_reference`.
- No filesystem writes.
- No raw output storage.
- No candidate JSON writes.
- No index updates.

## 12. Candidate Draft Shape Decision

Expected app-owned candidate draft fields:

- `candidate_type`
- `target_category`
- `source_locator`
- `evidence`
- `provenance`
- `confidence`
- `raw_output_refs`
- `normalization_status`

Optional draft fields:

- `candidate_id`
- `project_id`
- `claim`
- `label`
- `notes`
- `uncertainty`
- `source_snapshot_hashes`
- `unsupported_reason`
- `review_questions`

Allowed `normalization_status` values:

- `candidate_draft`
- `insufficient_evidence`
- `rejected_output`

Rules:

- Drafts are not persisted candidate records.
- Drafts are not canon.
- Drafts cannot include `status = "promoted"`.
- Drafts cannot include `owner_decision = "promote"`.
- Drafts cannot include forbidden destinations: `write_to_canon`, `mutate_memory`, `apply_promotion`, `rewrite_scene`, or `generate_prose`.
- Draft confidence must be bounded.
- Draft evidence must include app-owned locator/provenance where available.
- Unsupported raw data must fail closed.

## 13. Relationship to Existing Candidate Schema

PHASE8-IMPL-007 does not change `CORE_CANDIDATE_TYPES`.

Draft outputs may use adapter-local draft labels where the current candidate schema lacks final candidate types. If a draft maps to an existing candidate type, keep it compatible. If a draft needs a future type such as `quote_attribution_candidate` or `semantic_signal_candidate`, record it as future schema-extension work.

T004-T006 should pass current contract tests without schema expansion where possible. Do not modify candidate schema in PHASE8-IMPL-007-T004 unless a later child explicitly authorizes it.

## 14. T004 Handoff

`PHASE8-IMPL-007-T004` is:

`PHASE8-IMPL-007-T004 - Manifest and raw artifact bundle validators`

T004 should:

- create `backend/story_knowledge/booknlp_adapter_contract.py`
- implement all public APIs as needed for import/collection
- implement manifest validation
- implement raw artifact bundle validation
- validate source-map/evidence integration where needed
- support T002-confirmed raw artifacts: tokens, entities, quotes, supersense, book JSON
- treat `.book.html` only as an optional raw output reference, not parser input
- treat events as app-derived from token `event`
- avoid real BookNLP import/run
- avoid filesystem I/O
- avoid package/dependency changes
- keep source-level forbidden terms out of production module
- update roadmap/status
- run targeted tests

T004 should not:

- implement a real BookNLP parser
- install or run BookNLP
- implement source snapshot byte-to-character matching
- persist raw outputs
- persist candidates
- mutate memory/canon
- generate prose

## 15. Deferred Work

- Real BookNLP install.
- Real BookNLP execution.
- Real BookNLP output file parser.
- Real byte-to-character mapping against source snapshots.
- Source snapshot text matching.
- Raw output storage helpers.
- Extraction orchestrator.
- Candidate JSON persistence from adapter outputs.
- Extraction routes.
- Frontend review UI.
- Relationship extraction.
- Timeline extraction.
- Causality extraction.
- Subtxt semantic rubric implementation.
- NCP import/export implementation.
- dramatica-flow-inspired rubric implementation.
- Model-assisted extraction.
- Apply-promotion.
- Memory/canon mutation.
- Training/JSONL/dataset work.

## 16. Accepted Decision

- ACCEPT staged implementation of `booknlp_adapter_contract.py` beginning in T004.
- ACCEPT raw-shape vs normalized-shape separation.
- ACCEPT minimal fixture corrections if required to align tests with T002 official source inventory.
- ACCEPT `booknlp_events` as app-derived from `.tokens.event`, not a real raw output file.
- ACCEPT byte offsets as raw support and app source locators as required for candidate drafts.
- ACCEPT `g` as raw aggregate metadata only, not identity.
- ACCEPT coreference, quote attribution, and event outputs as candidate evidence only.
- ACCEPT T004 creating all public API symbols if needed for test collection.
- DEFER real BookNLP install/run/parsing.
- REJECT external code vendoring/execution.
- REJECT raw output as canon/candidate truth.
- REJECT generated prose, rewrite, continuation, and canon mutation.
