# PHASE8-IMPL-007 Official Source Inventory

## Inventory Summary

- Task ID: `PHASE8-IMPL-007-T002`
- Date: 2026-06-20
- Purpose: inspect the already-cloned local official source caches read-only so `PHASE8-IMPL-007` can refresh its mocked BookNLP adapter contract before implementation.
- Boundary: no install, no run, no import, no clone, no fetch, no pull, no vendoring, no app runtime copy, no package changes, no BookNLP/spaCy/dramatica-flow/NCP/Subtxt execution.
- Local source cache paths:
  - `.external_sources/booknlp`
  - `.external_sources/dramatica-flow`
  - `.external_sources/narrative-context-protocol`
  - `.external_sources/subtxt-docs`
- Source-cache protection: `/usr/bin/git status --short -- .external_sources` returned clean; `/usr/bin/git status --short --ignored -- .external_sources` returned `!! .external_sources/`; each child path is ignored by `.git/info/exclude:10:.external_sources/`.
- Git discovery note: the interrupted Claude run observed plain `git -C .external_sources/<repo> rev-parse HEAD` walking up to the parent repository. T002 re-verified SHAs with explicit `/usr/bin/git --git-dir=<repo>/.git --work-tree=<repo> rev-parse HEAD`.

| Repository | Local path | Commit SHA |
| --- | --- | --- |
| BookNLP | `.external_sources/booknlp` | `3d900fc2224e55960c3363826ae28539b77b4204` |
| dramatica-flow | `.external_sources/dramatica-flow` | `890f099bfcb64adbf407fd83ab708c48e92b0766` |
| Narrative Context Protocol | `.external_sources/narrative-context-protocol` | `b1222748376aae3d309176b3bb5afb884eb281ea` |
| Subtxt docs | `.external_sources/subtxt-docs` | `ec66121364c039693314dcce4cde464e497bece4` |

## BookNLP Inventory

- Repo path: `.external_sources/booknlp`
- Commit SHA: `3d900fc2224e55960c3363826ae28539b77b4204`
- License: MIT, copyright David Bamman, 2021.
- Source files inspected:
  - `README.md`
  - `LICENSE`
  - `setup.py`
  - `examples/158_emma/158_emma.tokens`
  - `examples/158_emma/158_emma.entities`
  - `examples/158_emma/158_emma.quotes`
  - `examples/158_emma/158_emma.supersense`
  - `examples/158_emma/158_emma.book`
  - `examples/158_emma/158_emma.book.html`
  - `booknlp/booknlp.py`
  - selected `booknlp/english/*` and `booknlp/common/*` paths by focused search only.
- Package metadata:
  - `setup.py` package name: `booknlp`
  - version: `1.0.7`
  - declared license: `MIT`
  - key dependencies: `torch>=1.7.1`, `tensorflow>=1.15`, `spacy>=3`, `transformers>=4.11.3`
- Output artifacts found under `examples/158_emma/`:
  - `.tokens`
  - `.entities`
  - `.quotes`
  - `.supersense`
  - `.book`
  - `.book.html`
- No separate `.events` file was found in the real example output directory.

Real `.tokens` columns:

```text
paragraph_ID
sentence_ID
token_ID_within_sentence
token_ID_within_document
word
lemma
byte_onset
byte_offset
POS_tag
fine_POS_tag
dependency_relation
syntactic_head_ID
event
```

Real `.entities` columns:

```text
COREF
start_token
end_token
prop
cat
text
```

Real `.quotes` columns:

```text
quote_start
quote_end
mention_start
mention_end
mention_phrase
char_id
quote
```

Real `.supersense` columns:

```text
start_token
end_token
supersense_category
text
```

Real `.book` character structure:

- top-level object has `characters`
- each inspected character object has:
  - `agent`
  - `patient`
  - `mod`
  - `poss`
  - `id`
  - `g`
  - `count`
  - `mentions`
- `mentions` buckets:
  - `proper`
  - `common`
  - `pronoun`
- mention bucket objects contain:
  - `c`
  - `n`
- `g` is referential pronoun distribution from BookNLP output context, not gender identity.

BookNLP README/source implications:

- The README identifies event tagging as a token-level pipeline output and the real `.tokens` file includes an `event` column.
- The README warns that book-length coreference remains an open research problem and can conflate distinct entities.
- The README describes referential gender as pronoun distribution rather than identity.
- Quote attribution links quotations to attributed mentions and coreference IDs; this is useful evidence, not owner-approved truth.

### BookNLP Raw Artifact Mapping

| Artifact kind | Real source artifact | Source evidence role | Candidate support role | Locator/evidence fields | Unknown/deferred fields |
| --- | --- | --- | --- | --- | --- |
| `booknlp_tokens` | `.tokens` | token order, words, lemmas, byte offsets, POS/dependency, event flag | supports entity, quote, event, supersense source localization | `token_ID_within_document`, `byte_onset`, `byte_offset`, `paragraph_ID`, `sentence_ID`, `event` | app-owned byte-to-character bridge; source hash validation against exact stored snapshot |
| `booknlp_entities` | `.entities` | entity/coreference mention spans and categories | candidate entity mention support only | `COREF`, `start_token`, `end_token`, `prop`, `cat`, `text` | confidence absent; owner review required; nested entity policy deferred |
| `booknlp_quotes` | `.quotes` | quote token range and attributed mention range | quote/speaker candidate evidence only | `quote_start`, `quote_end`, `mention_start`, `mention_end`, `mention_phrase`, `char_id`, `quote` | speaker certainty absent; ambiguous attribution handling remains app-owned |
| `booknlp_book_json` | `.book` | character aggregate mentions, referential pronoun distribution, agents/patients/modifiers/possessions | alias/coreference and character candidate support only | `characters[*].id`, `count`, `g`, `mentions.proper/common/pronoun[*].c/n`, `agent`, `patient`, `mod`, `poss` | do not treat `g` as identity; cluster conflation risk; exact candidate schema mapping deferred |
| `booknlp_supersense` | `.supersense` | lexical semantic spans | optional semantic support for candidate review | `start_token`, `end_token`, `supersense_category`, `text` | confidence absent; category-to-app taxonomy mapping deferred |
| `booknlp_events` | no real separate file; derived from `.tokens.event` | app-owned derived event abstraction | candidate event/action support only | `.tokens.event`, token IDs, token byte offsets | derivation rules, grouping, confidence, and event text span policy deferred |

### Comparison Against Current Mocked T006 Fixture Shapes

- Current mocked artifact kinds remain directionally valid: tokens, entities, quotes, book JSON, supersense, and event-like support are appropriate.
- The mocked `booknlp_events` artifact must be explicitly documented as app-owned derived data from `.tokens.event`, not a raw external file.
- Mocked token fields should either use real BookNLP names or be clearly separated into raw-shape fixtures and adapter-normalized fixtures.
- App-owned `source_locator` fields remain acceptable because real BookNLP output has byte offsets and token ranges, while the app evidence contract uses character offsets over exact UTF-8 decoded source snapshots.
- App-owned normalized candidate draft fields remain acceptable when clearly separated from raw BookNLP source records.
- App-owned confidence remains acceptable only as adapter-normalized or review workflow metadata; the inspected raw files do not provide confidence columns.

### Recommended PHASE8-IMPL-007 Corrections Or Confirmations

- Align raw fixture field names with real BookNLP headers or make raw-vs-normalized naming explicit.
- Treat `booknlp_events` as a derived/app-owned abstraction from `.tokens.event`.
- Bridge `.tokens` byte offsets to app source-map character offsets cautiously and fail closed on mismatch.
- Preserve quote token ranges, mention ranges, mention text, and `char_id` as candidate evidence only.
- Preserve coreference clusters as candidates pending owner review because conflation risk is explicitly documented.
- Do not treat `g` as gender identity.
- Keep all BookNLP artifacts as raw support evidence; none are canon, approved memory, promotion, or durable project truth.

## dramatica-flow Inventory

- Repo path: `.external_sources/dramatica-flow`
- Commit SHA: `890f099bfcb64adbf407fd83ab708c48e92b0766`
- License/license gap:
  - no root `LICENSE` or `LICENSE.md` file found by local file check.
  - README badge claims MIT, but the license text file is absent in the inspected clone.
- Source files inspected:
  - `README.md`
  - `README_EN.md`
  - `core/server.py`
  - `core/pipeline.py`
  - `core/state/`
  - `demo_ollama.py`
  - `docs/OLLAMA_GUIDE.md`
  - selected docs/templates discovered by focused file listing.
- Unsafe generation/revision/continuation/write behaviors verified:
  - `POST /api/books/{book_id}/ai-generate/arc-events`
  - `POST /api/books/{book_id}/continue-writing`
  - `POST /api/books/{book_id}/ai-generate/setup`
  - `POST /api/books/{book_id}/ai-generate/outline`
  - `POST /api/books/{book_id}/ai-continue/outline`
  - `POST /api/books/{book_id}/ai-generate/chapter-outlines`
  - `POST /api/books/{book_id}/ai-generate/detailed-outline`
  - `POST /api/books/{book_id}/ai-generate/chapter-content`
  - `POST /api/books/{book_id}/ai-rewrite-segment`
  - `POST /api/action/write`
  - `POST /api/action/revise`
- World-state/truth-like mutation:
  - `core/pipeline.py` writes drafts, summaries, causal links, emotional arcs, and world-state/current-state style truth files through its state manager.
  - `core/state/` provides the persistence layer for those truth-like files.
- LLM/demo surfaces:
  - `demo_ollama.py`
  - `docs/OLLAMA_GUIDE.md`
  - `core/server.py` provider construction for Ollama/OpenAI-compatible providers.
- Safe analysis-only concepts if kept reference-only:
  - causal chain thinking
  - foreshadowing/promise lifecycle
  - emotional arc tracking
  - relationship deltas
  - thread/timeline activity
  - information-boundary concept
  - audit dimensions when stripped of rewrite/generation behavior
- Blocked runtime behaviors:
  - writing, rewriting, revising, continuation, outline/chapter generation, generated summaries, LLM provider execution, world-state truth mutation, and automatic canon settlement.
- PHASE8-IMPL-007 implication:
  - no direct implementation role.
  - dramatica-flow remains deferred/reference-only and must not be imported, executed, copied, or adapted as runtime in this parent.

## Narrative Context Protocol Inventory

- Repo path: `.external_sources/narrative-context-protocol`
- Commit SHA: `b1222748376aae3d309176b3bb5afb884eb281ea`
- License: MIT, Narrative First, Inc. plus USC ETC stewardship/copyright context.
- Source files inspected:
  - `LICENSE.md`
  - `COPYRIGHT.md`
  - `README.md`
  - `SPECIFICATION.md`
  - `VALIDATION.md`
  - `NCP_SEMANTIC_GROUNDING.md`
  - `schema/ncp-schema.json`
  - `schema/ncp-schema.yaml`
  - selected examples under `examples/`
  - selected terminology docs under `docs/terminology/`
- Canonical schemas:
  - `schema/ncp-schema.json`
  - `schema/ncp-schema.yaml`
- Relevant fields/concepts for future approved-context import/export:
  - story/narrative separation
  - `story.moments[]`
  - `story.ideation`
  - `narratives[].subtext`
  - Storypoints, Storybeats, Perspectives/Throughlines, Dynamics, narrative functions, mappings, and canonical labels.
- Candidate/import-review boundaries:
  - schema validity is transport validity, not project truth.
  - imported NCP data must remain owner-reviewed approved context or candidate context depending on provenance.
  - partial updates must not be treated as deletion.
  - missing data must not be filled by inference.
- Guardrail confirmed:
  - the semantic grounding doc states that tools should not silently rewrite Subtext and should mark uncertainty instead of overwriting Storyform data.
- PHASE8-IMPL-007 implication:
  - no direct implementation role.
  - NCP remains future approved-context import/export reference only.
  - NCP import/export must not become automatic canon or automatic Storyform truth.

## Subtxt Docs Inventory

- Repo path: `.external_sources/subtxt-docs`
- Commit SHA: `ec66121364c039693314dcce4cde464e497bece4`
- Site type: Nuxt docs site.
- License/terms status:
  - no root `LICENSE` or `LICENSE.md` file found.
  - README states Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.
  - NonCommercial/ShareAlike terms keep the docs reference-only for this app.
- Source files inspected:
  - `README.md`
  - `package.json`
  - `nuxt.config.ts`
  - `content/1.getting-started/5.key-concepts.md`
  - `content/2.narrative-aspects/5.storypoints.md`
  - `content/2.narrative-aspects/6.storybeats.md`
  - `content/4.the-develop-workspace/1.forming/1.the-four-throughlines.md`
  - `content/4.the-develop-workspace/1.forming/4.storyform.md`
  - selected `content/4.the-develop-workspace/*` and `content/6.advanced-concepts/*` matches by focused search.
- Semantic guardrail concepts confirmed:
  - "Subject Matter is Not Conflict"
  - "Source of Conflict"
  - Domain to Concern to Issue to Problem layering
  - diagnostic question pattern, especially asking why a method/storypoint is a problem.
  - Four Throughlines completeness and perspective separation.
- Insufficient-evidence/diagnostic-question implications:
  - Subtxt concepts can guide future app-owned rubric prompts and uncertainty labels.
  - They must not become automatic classifiers or automatic Storyform truth.
- PHASE8-IMPL-007 implication:
  - no direct implementation role.
  - Subtxt remains semantic guardrail/reference only.
  - no Subtxt classifier, runtime, or Storyform labeling is authorized.

## Cross-Tool Implementation Findings

- Directly changes or confirms the BookNLP mocked adapter contract:
  - raw artifact names should center on real `.tokens`, `.entities`, `.quotes`, `.supersense`, and `.book` outputs.
  - `.book.html` is useful visual output but not an adapter-normalization input for T004-T006.
  - `booknlp_events` is not a raw file; it is app-owned derived support from `.tokens.event`.
  - token offsets are byte offsets; app evidence locators remain character-offset based and need a bridge.
  - quote, speaker, entity, event, and coreference outputs are evidence support, not truth.
- Deferred:
  - real BookNLP install/run.
  - real output parser from filesystem.
  - raw output storage helpers.
  - byte-to-character source-map bridge implementation.
  - NCP import/export.
  - Subtxt-inspired semantic rubric checks.
  - dramatica-flow-inspired rubric checks.
- Must remain blocked:
  - generation, rewrite, continuation, writing, revision, generated summaries, world-state truth mutation, automatic Storyform truth, automatic canon, apply-promotion, external code execution, and dependency installation.
- Risks to carry forward:
  - BookNLP coreference conflation.
  - quote speaker ambiguity.
  - byte offset to app character offset mismatch.
  - false treatment of referential pronoun distribution as identity.
  - missing confidence fields in raw artifacts.
  - dramatica-flow missing license file despite README badge.
  - Subtxt CC BY-NC-SA license terms.
- Recommended T003 implementation decision focus:
  - decide raw-shape vs normalized-shape naming.
  - decide whether tests should be corrected before implementation.
  - decide event derivation policy from `.tokens.event`.
  - decide byte-offset bridging scope for the mocked adapter.
  - decide source-level forbidden dependency/runtime terms.
  - decide whether T004 stubs all APIs or implements only validators plus stubs for importability.

## Source Gaps

- Missing licenses:
  - dramatica-flow has no root license file in the inspected clone, despite README badge.
  - Subtxt docs has no root license file; README states CC BY-NC-SA 4.0.
- Missing field docs:
  - BookNLP real sample headers are authoritative, but full formal schema docs for every output field were not found.
  - `.book` `g`, `agent`, `patient`, `mod`, and `poss` structures need later parser-level confirmation if used beyond candidate evidence.
- Unclear schema fields:
  - NCP schema is broad; exact import/export subset remains future work.
  - Subtxt docs are conceptual, not a machine schema for app runtime.
- Insufficient repo docs:
  - dramatica-flow license metadata is inconsistent between README badge and missing license file.
  - Subtxt `Storyform` page is placeholder-like in inspected local docs.
- Requires later real-run verification:
  - BookNLP output variations across models, books, and pipeline subsets.
  - byte offsets against the app's exact source snapshots.
  - quote/coreference/event behavior on owner-authored project material.
- Conservative fixture shape requirements:
  - keep confidence, source locators, candidate drafts, warnings, and uncertainty as app-owned normalized fields.
  - keep raw artifact fixtures separate from normalized candidate draft shape.
  - keep raw output and normalized candidates non-canon until owner review.
