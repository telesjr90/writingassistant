**Recommendation: use BookNLP as a second-stage extraction tool — or, more precisely, as the first automated NLP extractor after your app already has stable project/chapter/scene text storage and source-span indexing.** It is a strong fit for **evidence-backed candidate records**, but it should not be treated as canon, and it should not be the first thing in the pipeline before your own app has stable document IDs, scene/chapter boundaries, byte offsets, and owner-review workflows.

BookNLP is built for **English books and long documents** and includes POS tagging, dependency parsing, entity recognition, character name clustering/coreference, quotation speaker identification, supersense tagging, event tagging, and referential-gender inference. It also offers a smaller model described as more appropriate for personal computers, which matters for your local-first direction. ([GitHub][1])

## Verdict for your writing assistant

**Good fit: yes, but as candidate extraction infrastructure, not as interpretation.**

BookNLP can help populate candidate records for:

| Area                    |           Useful for your app? | Why                                                                                                                                                                                                             |
| ----------------------- | -----------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Characters              |                        **Yes** | It produces a `.book` JSON with characters mentioned more than once, references, inferred referential pronouns, actions as agent/patient, possessions, and modifiers. ([GitHub][1])                             |
| Aliases / coreference   |          **Yes, with caution** | It clusters names and entity mentions under coreference IDs, but the repo explicitly warns that book-length coreference remains an open research problem and can wrongly merge entities. ([GitHub][1])          |
| Quotes / speakers       |                        **Yes** | `.quotes` includes quote start/end, attributed mention span, mention phrase, speaker character/coref ID, and quote text. ([GitHub][1])                                                                          |
| Events                  |     **Yes, medium confidence** | Events are marked in the token output, and the event layer targets asserted events that actually take place in the story world, not hypotheticals or extradiegetic summaries. ([GitHub][1])                     |
| Entities                |                        **Yes** | `.entities` includes coref ID, start/end token span, mention type, entity category, and text for PER, LOC, FAC, GPE, VEH, and ORG. ([GitHub][1])                                                                |
| POS/dependencies        | **Yes, as low-level evidence** | `.tokens` includes paragraph, sentence, token IDs, word, lemma, byte onset/offset, POS, dependency relation, syntactic head, and event flag. ([GitHub][1])                                                      |
| Dramatica/Subtxt claims |           **No, not directly** | BookNLP can provide textual evidence, but it cannot decide throughlines, storyform truth, source of conflict, author intent, or thematic meaning. Those should remain diagnostic/candidate-only in your system. |

## Why second-stage, not first-stage

Your **first stage** should be your own deterministic app layer:

1. Store owner-authored text.
2. Preserve project/chapter/scene/document IDs.
3. Create stable source maps: byte offsets, paragraph IDs, sentence IDs, content hashes.
4. Track whether the text came from owner-authored prose, notes, pasted material, imported NCP, etc.

Then **BookNLP becomes the second stage**: run it over selected documents or scene bundles and convert its outputs into candidate records.

That order matters because BookNLP’s outputs are only useful to your OMI workflow if you can trace every extraction back to a stable source location. Fortunately, BookNLP gives you strong provenance anchors: the `.tokens` file includes byte onset/offset and paragraph/sentence/token IDs, while `.entities` and `.quotes` include token-span boundaries. ([GitHub][1])

## Output-by-output mapping to candidate records

### 1. Characters

BookNLP’s `.book` JSON provides character-level aggregates for characters mentioned more than once: proper/common/pronominal references, referential gender, agent actions, patient actions, possessed objects, and modifiers. The source code confirms fields such as `agent`, `patient`, `mod`, `poss`, `id`, `g`, `count`, and mention buckets for `proper`, `common`, and `pronoun`. ([GitHub][1])

**Candidate types your app could create:**

```json
{
  "candidate_type": "character",
  "label": "Elizabeth Bennet",
  "source_tool": "booknlp",
  "status": "candidate",
  "evidence": [
    {
      "source_document_id": "scene_012",
      "start_token": 1842,
      "end_token": 1843,
      "byte_onset": 9211,
      "byte_offset": 9228,
      "text": "Elizabeth Bennet"
    }
  ],
  "derived_fields": {
    "aliases": ["Elizabeth", "Miss Bennet", "she"],
    "mention_count": 37,
    "referential_pronouns": ["she", "her"]
  },
  "owner_review_required": true
}
```

Important guardrail: referential gender should be stored as **pronoun/reference evidence**, not as the character’s gender identity. BookNLP’s own docs make that distinction explicitly. ([GitHub][1])

### 2. Aliases and coreference

BookNLP clusters variants like “Tom,” “Tom Sawyer,” “Mr. Sawyer,” and “Thomas Sawyer” into one character/entity cluster, and `.entities` stores a coreference ID for each entity mention. ([GitHub][1])

This is valuable for your app, but it must be handled as **possible identity linkage**, not confirmed truth. The README warns that full book-length coreference is still an open research problem and may incorrectly conflate distinct entities. ([GitHub][1])

**Candidate behavior:**

```json
{
  "candidate_type": "alias_cluster",
  "claim": "\"Lizzy\", \"Elizabeth\", and \"Miss Bennet\" may refer to the same character.",
  "confidence": "medium",
  "evidence_count": 12,
  "risk_flags": ["coreference_may_conflate_entities"],
  "owner_review_required": true
}
```

### 3. Quotes and speaker attribution

BookNLP’s `.quotes` output stores the quote span, attributed mention span, attributed mention phrase, speaker/coreference ID, and quotation text. ([GitHub][1])

This is one of the best fits for your app because each quote can become a directly reviewable evidence object.

**Candidate types:**

```json
{
  "candidate_type": "dialogue_attribution",
  "claim": "This quote may be spoken by Character_17.",
  "quote_text": "I shall never forgive him.",
  "speaker_candidate_id": "character_17",
  "evidence": {
    "quote_start_token": 2044,
    "quote_end_token": 2051,
    "mention_start_token": 2054,
    "mention_end_token": 2054,
    "mention_phrase": "she"
  },
  "owner_review_required": true
}
```

This can support future features like “show all lines attributed to this character,” “find unattributed dialogue,” or “detect possible speaker confusion,” while still remaining analysis-only.

### 4. Events

BookNLP’s event layer identifies asserted realis events: events depicted as actually taking place, rather than hypotheticals, future events, or narrator summaries outside the story action. ([GitHub][1])

That is useful for your timeline and plot-thread candidates, but event detection should be treated as **lower confidence** than direct entity or quote spans. The README reports event tagging F1 of 70.6 for the small model and 74.1 for the big model. ([GitHub][1])

**Candidate types:**

```json
{
  "candidate_type": "timeline_event",
  "claim": "A character walked rapidly in this sentence.",
  "event_lemma": "walk",
  "source_tool": "booknlp",
  "confidence": "medium",
  "evidence": {
    "sentence_id": 88,
    "token_id": 1422,
    "byte_onset": 7430,
    "byte_offset": 7436
  },
  "owner_review_required": true
}
```

Best use: not “this is a plot event,” but “this sentence contains an action/event candidate worth reviewing.”

### 5. Entities: locations, organizations, objects-adjacent data

BookNLP’s entity categories include people, facilities, geo-political entities, locations, vehicles, and organizations. It also recognizes named entities, common entities, and pronouns. ([GitHub][1])

This maps well to your approved-memory pages:

| BookNLP category | Candidate mapping                    |
| ---------------- | ------------------------------------ |
| `PER`            | Character candidate                  |
| `LOC`            | Location/setting candidate           |
| `FAC`            | Facility/place candidate             |
| `GPE`            | Political/geographic place candidate |
| `ORG`            | Organization/group candidate         |
| `VEH`            | Object/item or vehicle candidate     |

For **objects/items**, BookNLP is only partially useful. It has `VEH`, `FAC`, supersense categories like artifact, and `.book` possession data, but it is not a full inventory extractor. You would likely combine BookNLP with a later custom object/item extractor.

### 6. POS and dependency data

The `.tokens` file gives you low-level syntactic evidence: lemma, POS tag, dependency relation, syntactic head token ID, and event flag. BookNLP uses spaCy for POS tagging and dependency parsing. ([GitHub][1])

This is useful for evidence-backed candidate enrichment:

```json
{
  "candidate_type": "relationship_signal",
  "claim": "Character A may possess or be associated with object B.",
  "basis": "dependency_relation=poss",
  "source_tool": "booknlp",
  "evidence": {
    "token_id": 391,
    "syntactic_head_id": 392,
    "sentence_id": 22
  },
  "owner_review_required": true
}
```

But dependency data should not become automatic story truth. It is a signal for extraction, not approval.

## Recommended integration pattern

Use BookNLP in your app like this:

```text
Owner-authored text
  → deterministic source map
  → BookNLP run
  → raw BookNLP outputs stored unchanged
  → normalized extraction records
  → candidate records with evidence spans
  → owner review
  → approved memory only after explicit approval
```

Store the raw outputs separately from your app’s candidate records:

```text
writer_assistant/extractions/booknlp/{run_id}/
  source_manifest.json
  booknlp_params.json
  output.tokens
  output.entities
  output.quotes
  output.supersense
  output.book
  extraction_warnings.json
```

Then convert into OMI candidates only through a controlled importer.

## Guardrails I would add

BookNLP should be allowed to say:

> “This span may indicate a character / quote / event / place / alias cluster.”

It should not be allowed to say:

> “This is canon.”
> “This is the true relationship.”
> “This is the correct throughline.”
> “This proves the storyform.”
> “This character’s gender identity is X.”
> “These two mentions are definitely the same person.”

The biggest technical caution is coreference. BookNLP itself warns that book-length coreference is difficult and may wrongly merge entities, so every alias/coreference-derived record needs `owner_review_required: true` and should preserve the individual evidence mentions that produced the cluster. ([GitHub][1])

## Bottom line

**BookNLP is a strong candidate for your extraction stack, especially for Phase 9-style candidate extraction.** I would not use it as the first foundation layer of the app. Use your own app first to establish stable project structure, text ownership, source IDs, and byte-span provenance. Then use BookNLP as the first serious NLP extractor to generate evidence-backed candidates for characters, aliases, quotes, entities, events, and syntactic relationship signals.

For your local-first Dramatica-informed assistant, the clean position is:

> **BookNLP extracts textual evidence. Your app turns that evidence into reviewable candidates. The owner decides what becomes approved memory. Dramatica/Subtxt interpretation remains separate and diagnostic-only.**

[1]: https://github.com/booknlp/booknlp/blob/main/README.md "booknlp/README.md at main · booknlp/booknlp · GitHub"
--------------------------------------------------------------------

Yes. **BookNLP outputs can be connected to source locators, evidence spans, and candidate provenance**, but only if your app treats BookNLP as an **evidence-producing extractor**, not as an authority that creates approved story truth.

The core reason is that BookNLP writes a `.tokens` file with paragraph ID, sentence ID, document token ID, word, lemma, **byte onset**, **byte offset**, POS, dependency head, dependency relation, and an `event` flag; the other structured files then refer back to document token IDs. ([GitHub][1]) That gives you a clean adapter path: join every `.entities`, `.quotes`, `.supersense`, and `.book` reference back to `.tokens`, then derive byte ranges, sentence/paragraph locators, and source snippets.

## Output files relevant to provenance

| File          | What it gives you                                                                                                           |                                                          Locator quality | Candidate use                                                               |
| ------------- | --------------------------------------------------------------------------------------------------------------------------- | -----------------------------------------------------------------------: | --------------------------------------------------------------------------- |
| `.tokens`     | Token-level spine: paragraph, sentence, token ID, word, lemma, byte onset/offset, POS, dependency relation/head, event flag |                                                               **Strong** | Source locator index, event-token evidence, sentence/paragraph anchors      |
| `.entities`   | `COREF`, `start_token`, `end_token`, `prop`, `cat`, `text`                                                                  |                                              **Strong**, via token spans | Characters, locations, organizations, objects/facilities, candidate aliases |
| `.quotes`     | `quote_start`, `quote_end`, `mention_start`, `mention_end`, `mention_phrase`, `char_id`, `quote`                            |                          **Strong**, via quote and speaker-mention spans | Quote attribution candidates                                                |
| `.supersense` | `start_token`, `end_token`, semantic category, text                                                                         |                                              **Strong**, via token spans | Event/theme/object/time/location hint candidates                            |
| `.book`       | Character summaries: mentions, referential gender, agent/patient actions, possessions, modifiers                            | **Medium**: many fields point to token IDs, but it is already aggregated | Character dossiers, relationship/action hints, not source of canon          |
| `.book.html`  | Annotated display of full text with entities/coreference/speakers                                                           |                  **Useful for debugging**, not the canonical data source | Human inspection/debugging only                                             |

BookNLP’s README lists the generated files and explicitly says `.tokens` stores byte onset/offset within the original document, while `.entities`, `.supersense`, and `.quotes` store document-level start/end token IDs. ([GitHub][1]) The implementation also confirms the TSV headers for `.supersense`, `.tokens`, `.entities`, and `.quotes`, including the quote speaker fields and entity coreference fields. ([GitHub][2])

## How to build source locators

For every BookNLP-derived candidate, store both the **BookNLP locator** and your app’s normalized source locator:

```json
{
  "candidate_source": "booknlp",
  "booknlp_output_file": "mybook.entities",
  "booknlp_row_id": 142,
  "booknlp_fields": {
    "start_token": 231,
    "end_token": 231,
    "coref": 123,
    "cat": "PER",
    "prop": "PROP",
    "text": "Emma"
  },
  "source_locator": {
    "project_id": "...",
    "document_id": "...",
    "source_file_hash": "...",
    "paragraph_id": 12,
    "sentence_id": 31,
    "token_start": 231,
    "token_end": 231,
    "byte_start": 1042,
    "byte_end": 1046
  },
  "evidence_text": "Emma",
  "status": "candidate_pending_owner_review"
}
```

The important adapter rule is:

**Token span → token table lookup → byte span + sentence/paragraph locator → evidence snippet.**

For example, `.entities` gives `start_token` and `end_token`; `.tokens` gives each token’s byte onset/offset. So the candidate’s byte span can be derived as:

```text
byte_start = tokens[start_token].byte_onset
byte_end   = tokens[end_token].byte_offset
```

For quotes, do this twice: once for the quote span and once for the attributed speaker mention span.

## Mapping to your candidate records

### 1. Characters

BookNLP is strongest here. It supports entity recognition, character name clustering, coreference, quotation speaker identification, and referential gender inference. ([GitHub][1])

Use `.entities` as the **evidence source** and `.book` as an **aggregation helper**.

Candidate mapping:

```json
{
  "candidate_type": "character",
  "external_cluster_id": "booknlp:coref:123",
  "display_name_candidate": "Emma Woodhouse",
  "aliases": ["Emma Woodhouse", "Emma", "her", "She"],
  "evidence": [
    {
      "source_file": "mybook.entities",
      "row_id": 1,
      "token_start": 4,
      "token_end": 5,
      "byte_start": "...",
      "byte_end": "...",
      "text": "Emma Woodhouse"
    }
  ],
  "confidence_basis": "BookNLP entity/coreference cluster",
  "review_state": "pending_owner_review"
}
```

Caveat: `.book` only includes “characters mentioned more than 1 time,” so single-mention people may exist in `.entities` but not in `.book`. ([GitHub][1])

### 2. Relationships

BookNLP does **not** produce a clean relationship graph like “Emma is daughter of Mr. Woodhouse” as a guaranteed fact. But it gives relationship evidence hints from:

* entity co-occurrence;
* dependency roles;
* possessives;
* common noun mentions such as “her father,” “his daughter,” “her sister”;
* character action summaries in `.book`.

The code builds character-level `agent`, `patient`, `mod`, and `poss` lists using dependency relations and token IDs. ([GitHub][2])

Candidate mapping:

```json
{
  "candidate_type": "relationship",
  "subject_candidate": "booknlp:coref:123",
  "object_candidate": "booknlp:coref:425",
  "relationship_label_candidate": "father",
  "evidence_text": "her father",
  "source_locator": {
    "token_start": 773,
    "token_end": 774,
    "byte_start": "...",
    "byte_end": "..."
  },
  "confidence_basis": "NOM/PER entity phrase + coreference cluster",
  "review_state": "pending_owner_review"
}
```

Important limitation: these should be **relationship candidates**, not approved relationships. Coreference is especially risky in long fiction.

### 3. Events

BookNLP has an event tagger. The README says its event layer identifies asserted realis events, meaning events depicted as actually taking place rather than hypotheticals, future events, or extradiegetic summaries. ([GitHub][1]) In output, event information appears in the `.tokens` file as an `event` column; the implementation marks event tokens as `EVENT`. ([GitHub][2])

Candidate mapping:

```json
{
  "candidate_type": "event",
  "trigger_token": "married",
  "event_status": "booknlp_event_token",
  "source_locator": {
    "paragraph_id": 5,
    "sentence_id": 12,
    "token_start": 341,
    "token_end": 341,
    "byte_start": "...",
    "byte_end": "..."
  },
  "nearby_entities": ["booknlp:coref:84"],
  "review_state": "pending_owner_review"
}
```

Best use: first-stage event trigger extraction. Do **not** treat it as a full timeline event with actor, object, date, cause, or consequence unless your app adds evidence-backed post-processing.

### 4. Timeline

BookNLP gives you **document order**, not story chronology.

You can build timeline candidates from:

* event tokens in `.tokens`;
* paragraph/sentence/token order;
* `noun.time` spans in `.supersense`;
* nearby entities;
* nearby quotes.

The `.supersense` file includes token spans and semantic categories such as `noun.time`, `verb.motion`, `verb.communication`, `noun.person`, and others. ([GitHub][3])

Candidate mapping:

```json
{
  "candidate_type": "timeline_event",
  "event_trigger": "married",
  "temporal_anchor_candidate": "wedding day",
  "source_order": {
    "paragraph_id": 8,
    "sentence_id": 44,
    "token_start": 341
  },
  "chronology_status": "document_order_only",
  "review_state": "pending_owner_review"
}
```

Limitation: BookNLP alone cannot know whether a passage is flashback, summary, backstory, prophecy, or narrated out of order. Your app should label these as **timeline candidates needing owner review**.

### 5. Quote attribution

This is another strong fit. `.quotes` stores quote start/end token IDs, attributed mention start/end token IDs, attributed mention text, character/coreference ID, and quote text. ([GitHub][1]) The sample output from the official repo shows quote spans connected to mention spans and `char_id` values. ([GitHub][4])

Candidate mapping:

```json
{
  "candidate_type": "quote_attribution",
  "quote_text": "Poor Miss Taylor!--I wish she were here again.",
  "speaker_candidate": "booknlp:coref:425",
  "speaker_mention_text": "he",
  "quote_locator": {
    "token_start": 1272,
    "token_end": 1295,
    "byte_start": "...",
    "byte_end": "..."
  },
  "speaker_mention_locator": {
    "token_start": 1266,
    "token_end": 1266,
    "byte_start": "...",
    "byte_end": "..."
  },
  "review_state": "pending_owner_review"
}
```

This is ideal for your app because it can show: “BookNLP thinks this quote is spoken by Character X because this nearby mention/coreference points there.”

## Key limitations and guardrails

BookNLP is useful, but your app should wrap it carefully.

First, it is English-focused; the README describes it as scaling to books and long documents “in English.” ([GitHub][1]) Second, its own README reports non-perfect accuracy: for example, coreference average F1 is listed below 80 for both small and big models, and speaker attribution is also imperfect. ([GitHub][1]) Third, the README explicitly warns that accurate book-length coreference is still an open research problem and says full coreference can conflate distinct entities, so outputs need inspection. ([GitHub][1])

For your application, the right rule is:

**BookNLP may create candidates with evidence and provenance. It must not create approved canon, approved relationships, approved timeline facts, or approved quote truth without owner review.**

## Recommended MVP integration

Use BookNLP as a **first-stage extraction adapter**:

1. Run: `entity,quote,supersense,event,coref`.
2. Store raw outputs under a deterministic extraction run folder.
3. Store run metadata: BookNLP version/commit, model size, pipeline flags, source document hash, timestamp, input encoding.
4. Build a token locator index from `.tokens`.
5. Convert `.entities`, `.quotes`, `.supersense`, and `.book` into candidate records.
6. Every candidate must include:

   * candidate type;
   * raw BookNLP row reference;
   * token span;
   * derived byte span;
   * evidence text;
   * source document hash;
   * extraction run ID;
   * confidence/provenance basis;
   * `pending_owner_review`.

Bottom line: **yes, BookNLP is compatible with your candidate-first architecture**. Its token IDs and byte offsets make evidence-backed provenance practical. Its main limitation is not traceability; it is inference reliability. So the safe design is to use it as a locator-rich extraction engine whose outputs become reviewable candidates, never automatic story truth.

[1]: https://github.com/booknlp/booknlp "GitHub - booknlp/booknlp: BookNLP, a natural language processing pipeline for books · GitHub"
[2]: https://github.com/booknlp/booknlp/blob/main/booknlp/english/english_booknlp.py "booknlp/booknlp/english/english_booknlp.py at main · booknlp/booknlp · GitHub"
[3]: https://raw.githubusercontent.com/booknlp/booknlp/main/examples/158_emma/158_emma.supersense "raw.githubusercontent.com"
[4]: https://raw.githubusercontent.com/booknlp/booknlp/main/examples/158_emma/158_emma.quotes "raw.githubusercontent.com"
