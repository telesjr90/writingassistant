# PHASE8-IMPL-007 Implementation Source Refresh Decision

## Decision Summary

- `PHASE8-IMPL-007-T002` inspected the official local source clones under `.external_sources/` read-only.
- `PHASE8-IMPL-007` should proceed to implementation decision in `PHASE8-IMPL-007-T003`.
- The BookNLP mocked adapter contract remains valid with refinements from real local output inspection.
- Real BookNLP install/run remains deferred.
- `.external_sources/` remains a local ignored evidence cache, not an app dependency.
- No external repo code is vendored or executed.

## BookNLP Contract Refresh

Accepted raw artifact kinds:

- `booknlp_tokens`
- `booknlp_entities`
- `booknlp_quotes`
- `booknlp_book_json`
- `booknlp_supersense`

Clarified artifact kind:

- `booknlp_events` is not a real raw output file in the inspected BookNLP examples.
- `booknlp_events` is accepted only as an app-owned derived abstraction from `.tokens.event`.
- `booknlp_events` must not be treated as an external raw artifact file.

Fields confirmed from real examples:

- token fields:
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
- entity fields:
  - `COREF`
  - `start_token`
  - `end_token`
  - `prop`
  - `cat`
  - `text`
- quote fields:
  - `quote_start`
  - `quote_end`
  - `mention_start`
  - `mention_end`
  - `mention_phrase`
  - `char_id`
  - `quote`
- supersense fields:
  - `start_token`
  - `end_token`
  - `supersense_category`
  - `text`
- book JSON character/mention fields:
  - character fields: `agent`, `patient`, `mod`, `poss`, `id`, `g`, `count`, `mentions`
  - mention buckets: `proper`, `common`, `pronoun`
  - mention object fields: `c`, `n`

Conservative mocked approximations that remain acceptable:

- app-owned `source_locator`
- app-owned normalized candidate draft fields
- app-owned confidence where the real artifact lacks confidence
- app-owned warnings/uncertainty metadata
- app-owned derived events from token-level `event`

Fixture updates T003 should decide:

- align mocked token fields with real BookNLP names or explicitly separate raw shape from normalized shape.
- derive events from token `event`.
- map byte offsets to app source-map character offsets cautiously.
- avoid treating `g` as an identity attribute.
- preserve coreference, quote attribution, and speaker uncertainty.
- decide whether current T006 tests need fixture correction before implementation.

## Implementation Boundary for PHASE8-IMPL-007

- `PHASE8-IMPL-007-T003` should decide exact implementation split and fixture correction policy.
- `PHASE8-IMPL-007-T004` should implement validators first.
- `PHASE8-IMPL-007-T005` should implement mocked normalizers.
- `PHASE8-IMPL-007-T006` should implement or repair the draft builder and harden boundaries.
- Implementation remains standard-library only.
- Implementation must not import or run BookNLP.
- Implementation must not install BookNLP, spaCy, TensorFlow, PyTorch, transformers, dramatica-flow, NCP tooling, Subtxt/Nuxt tooling, or package managers.
- Implementation must not read from `.external_sources/` at runtime.
- Implementation must not parse project files or real BookNLP output files in this parent unless a later child explicitly changes scope.

## dramatica-flow Boundary Refresh

- Runtime adapter remains blocked/deferred.
- Safe concepts remain reference-only:
  - causal chain
  - foreshadowing/promise lifecycle
  - emotional arc
  - relationship delta
  - thread/timeline activity
  - information boundaries
  - audit dimensions without revision behavior
- Unsafe generation/rewrite/continuation/world-state/truth behaviors remain blocked.
- No direct implementation is authorized in `PHASE8-IMPL-007`.

## NCP/Subtxt Boundary Refresh

- NCP remains future approved-context import/export reference only.
- NCP schema validity must not become automatic story truth.
- Imported NCP content must not become truth automatically.
- Subtxt docs remain future semantic guardrail/rubric reference only.
- Subtxt concepts must not become an automatic classifier or automatic Storyform truth.
- No direct NCP or Subtxt implementation is authorized in `PHASE8-IMPL-007`.

## Accepted Decision

- ACCEPT local official source inventory as implementation evidence.
- ACCEPT BookNLP mocked adapter implementation proceeding after `PHASE8-IMPL-007-T003`.
- ACCEPT real BookNLP install/run remains deferred.
- ACCEPT `.external_sources/` remains ignored local evidence cache.
- ACCEPT fixture refinements based on real BookNLP outputs.
- ACCEPT `booknlp_events` only as app-owned derived support from `.tokens.event`.
- REJECT vendoring external source code.
- REJECT running external tools.
- REJECT raw outputs as canon or candidates.
- REJECT treating coreference, quote attribution, event flags, NCP imports, Subtxt labels, or dramatica-flow state as approved truth.
- REJECT any generated prose, rewrite, continuation, canon mutation, memory mutation, or apply-promotion behavior.

## T003 Handoff

`PHASE8-IMPL-007-T003` is:

`PHASE8-IMPL-007-T003 — BookNLP adapter implementation decision after source inventory`

T003 should:

- read `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`.
- read `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`.
- decide exact implementation split.
- decide whether current T006 tests need fixture correction before implementation.
- decide whether T004 should create stubs for all APIs.
- decide source-level forbidden terms based on T002 findings.
- decide raw-shape vs normalized-shape naming.
- decide event derivation from `.tokens.event`.
- decide handling of BookNLP byte offsets vs app character offsets.
- confirm real BookNLP install/run remains deferred.
- produce docs/decision only.
- avoid runtime code and tests.
