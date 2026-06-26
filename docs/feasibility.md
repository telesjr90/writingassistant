## Feasibility result: **YELLOW overall, with GREEN subcomponents**

**Yes, an MVP can use this stack safely**, but only if the MVP is explicitly **candidate-first, analysis-only, and approval-gated**.

The safe version is:

> **BookNLP extracts literary evidence → analysis rubrics interpret evidence conservatively → Subtxt/NCP rules prevent overclaiming → NCP imports/exports only approved structural context.**

It becomes **RED** if the app lets BookNLP, dramatica-flow, or an LLM automatically create canon, infer a definitive Storyform, rewrite prose, continue scenes, or mutate “truth”/world-state files.

---

## Component verdicts

| Component                   |        Feasibility | MVP use                                                                                                                                               | Main condition                                                                            |
| --------------------------- | -----------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **BookNLP**                 |          **GREEN** | First-stage literary extraction: characters, aliases, quotes, events, entities, POS/dependency signals, supersense tags                               | Treat all output as evidence-backed **candidates**, not canon                             |
| **dramatica-flow concepts** |         **YELLOW** | Inspiration for analysis-only rubrics: causal chains, timeline/thread activity, foreshadowing, info boundaries, emotional arcs, relationship networks | Do **not** use its generation/revision/state-mutation pipeline directly                   |
| **Subtxt docs**             | **YELLOW / GREEN** | Semantic guardrails: source of conflict, subject matter vs conflict, author-level interpretation, throughlines, story points, diagnostic questions    | Use as interpretation rules; do not claim automatic Storyform truth                       |
| **NCP**                     |          **GREEN** | Approved-context import/export format                                                                                                                 | Validate schema, preserve semantics, and separate candidate imports from approved context |

---

## Why this is feasible

### BookNLP is a good MVP extraction layer

BookNLP is designed for book-length English documents and provides pipeline outputs for POS tagging, dependency parsing, entity recognition, character clustering/coreference, quote speaker attribution, supersense tagging, event tagging, and referential gender inference. ([GitHub][1])

For your app, the useful outputs are especially:

* **characters / aliases / references**
* **entity clusters**
* **quote spans and speaker attribution**
* **asserted events**
* **actions where characters appear as agent or patient**
* **token-level and dependency evidence**
* **supersense / semantic category hints**

BookNLP’s `.book` JSON can include character records, mentions, referential gender, actions, possessions, and modifiers, while `.quotes`, `.entities`, and `.tokens` provide evidence-rich extraction surfaces. ([GitHub][1])

The key limitation is that book-length coreference is still an open research problem, and BookNLP itself warns that full coreference can incorrectly merge distinct entities. ([GitHub][1]) So BookNLP should not decide canon. It should produce **candidate records with source spans and confidence**.

**Verdict:** BookNLP is **GREEN** for candidate extraction, **RED** for automatic canon.

---

### dramatica-flow is useful conceptually, risky operationally

dramatica-flow contains concepts that align well with your planned analysis system: causal-chain modeling, world-state snapshots, truth files, emotional arcs, foreshadowing/hooks, relationship networks, information boundaries, multi-thread tracking, and audit/revision loops. ([GitHub][2])

But the repo is fundamentally an AI-assisted long-form writing/generation platform. Its documented API includes endpoints for generating outlines, detailed outlines, chapter content, rewriting segments, executing write pipelines, auditing, revising, exporting, extracting story state, and running story analysis. ([GitHub][2])

That makes it unsafe as a direct runtime dependency for your MVP unless aggressively wrapped. Your app’s non-negotiable boundary is **analysis-only**, so the safe use is:

> Borrow the analysis concepts, not the prose-generation pipeline.

**Verdict:** dramatica-flow concepts are **YELLOW**. Direct integration of its writing/revision/state-settlement pipeline is **RED**.

---

### Subtxt docs are useful as semantic guardrails

The Subtxt docs are valuable for preventing shallow or automatic Dramatica-style claims. They emphasize that **subject matter is not conflict**, that the app must ask why something is a problem, and that the source of conflict should be identified from an author-level structural perspective rather than from surface content alone. ([GitHub][3])

They also distinguish methods, illustrations, story meaning, storytelling, Storypoints, Storybeats, Throughlines, and Storyform concepts in ways that can become **rubric rules** rather than classifiers. ([GitHub][3])

For example, the MVP can safely say:

> “This passage contains evidence that may support a Relationship Story conflict candidate, but there is insufficient evidence to classify the source of conflict. Ask the writer a diagnostic question.”

It should not say:

> “This is definitely the Relationship Story Throughline and its Problem is X.”

The other blocker is licensing. The Subtxt docs repo states the material is licensed under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0**, so commercial use or adapted documentation/rules should get a license review. ([GitHub][4])

**Verdict:** Subtxt docs are **GREEN** as conceptual guardrails, **YELLOW** for productized/commercial reuse, and **RED** for copied/adapted content without license review.

---

### NCP is a strong fit for approved-context import/export

NCP is explicitly a standardized JSON schema for transporting and preserving authorial intent across multi-agent storytelling systems. It is not a standalone app; it is a context format and interoperability layer. ([GitHub][5])

That fits your architecture well. NCP should represent **approved project context**, not raw extraction output. The repo also provides validation guidance and recommends validating files against the canonical schema. ([GitHub][6])

The semantic grounding docs are especially important for your guardrails. They warn that NCP is not a replacement for Dramatica theory, canonical analysis, Subtxt, or Narrova, and they instruct AI consumers not to silently rewrite `subtext` from `storytelling`, not to collapse Main Character into protagonist, and to mark uncertain structural changes as candidates rather than overwriting Storyform. ([GitHub][7])

NCP also supports narrative status values such as `candidate`, `draft`, and `complete`, and canonical moments live under `story.moments[]`, which is helpful for separating proposed context from approved context. ([GitHub][8])

**Verdict:** NCP is **GREEN** for approved import/export, **YELLOW** for candidate import, and **RED** if treated as automatic truth.

---

## Main blockers

1. **Automatic Storyform inference**

   The MVP should not infer a definitive Dramatica/Subtxt Storyform from BookNLP output, manuscript text, or dramatica-flow-style state analysis. That should remain a reviewed, author-controlled interpretation.

2. **Prose generation and revision leakage**

   dramatica-flow contains writing, rewriting, outline generation, and revision features. Those must be blocked entirely for your app’s analysis-only boundary. ([GitHub][2])

3. **Canon contamination**

   BookNLP outputs, rubric findings, imported NCP drafts, and LLM interpretations must not write directly to approved memory/canon.

4. **BookNLP extraction uncertainty**

   Coreference, speaker attribution, and event extraction can be wrong. The app needs source spans, confidence, review status, and correction workflows.

5. **Subtxt licensing/product-boundary risk**

   The docs can guide your thinking, but copying or adapting the docs into a commercial product needs legal/license review because of the CC BY-NC-SA license. ([GitHub][4])

6. **NCP schema/semantic drift**

   Imports and exports must validate against a pinned NCP schema version and preserve canonical terminology instead of converting everything into your app’s internal labels.

---

## Required wrappers

### 1. `BookNLPAdapter`

Runs BookNLP and converts outputs into your internal candidate format.

It should produce:

```text
CharacterCandidate
RelationshipCandidate
QuoteCandidate
EventCandidate
TimelineCandidate
LocationCandidate
ObjectCandidate
EntityMention
SourceSpan
ToolRunProvenance
```

It should never produce:

```text
ApprovedCharacter
ApprovedRelationship
ApprovedTimelineFact
ApprovedStoryform
```

---

### 2. `EvidenceLedger`

Stores every candidate with:

```text
source_document_id
chapter_id / scene_id
character offsets or token offsets
quoted text span
BookNLP output file
tool version
run timestamp
confidence
extraction method
```

This makes every claim traceable.

---

### 3. `NarrativeRubricEngine`

This is where dramatica-flow concepts can safely inspire analysis-only checks.

Allowed rubrics:

```text
causal_chain_gap_check
promise_payoff_tracker
mystery_setup_resolution_tracker
timeline_thread_activity_check
information_boundary_check
relationship_delta_check
emotional_arc_observation
continuity_warning
```

Forbidden rubrics:

```text
generate_next_scene
rewrite_scene
continue_chapter
create_outline_as_author_content
settle_world_state_as_truth
auto_update_storyform
```

---

### 4. `SemanticGuardrailLayer`

Uses Subtxt/NCP-inspired rules to prevent overclaiming.

Examples:

```text
Do not treat subject matter as conflict.
Do not classify a Throughline without evidence.
Do not treat scene beats as Storybeats automatically.
Do not collapse Main Character into protagonist.
Do not overwrite Subtext from Storytelling.
When evidence is insufficient, ask a diagnostic question.
```

---

### 5. `CandidateStore`

All extracted or inferred material lands here first.

Candidate statuses:

```text
new
needs_review
needs_more_evidence
approved_for_project_memory
dismissed
superseded
```

Only explicit owner approval promotes candidates into approved context.

---

### 6. `NCPGateway`

Handles import/export.

Import rules:

```text
Validate schema.
Respect schema_version.
Import complete/approved NCP context into approved context only after review.
Import candidate/draft NCP material as candidates.
Do not treat omitted fields as deletion.
Do not rewrite subtext from storytelling summaries.
```

Export rules:

```text
Export only approved context by default.
Optionally export candidates under candidate/draft status or app-specific extension namespace.
Validate before writing.
Block export if schema validation fails.
```

---

## Minimal safe MVP architecture

```text
Manuscript text
   ↓
BookNLP job
   ↓
Evidence ledger
   ↓
Candidate extraction layer
   ↓
Analysis-only rubric engine
   ↓
Semantic guardrails
   ↓
Review UI
   ↓
Owner approval
   ↓
Approved project context
   ↓
NCP import/export gateway
```

The important separation is this:

```text
BookNLP output ≠ canon
Rubric finding ≠ canon
LLM interpretation ≠ canon
Imported NCP draft ≠ canon
Owner-approved context = canon
```

---

## Practical MVP recommendation

Build the MVP in this order:

1. **BookNLP extraction prototype**

   Start with characters, aliases, quotes, quote speakers, asserted events, and entity mentions.

2. **Evidence-backed candidate records**

   Every candidate must show “why the app thinks this” with source spans.

3. **Review UI**

   Let the writer approve, dismiss, merge, rename, or ask for more evidence.

4. **NCP approved-context import/export**

   Export only approved project memory first. Add candidate export later.

5. **Analysis-only narrative rubrics**

   Add causal-chain, timeline, promise/payoff, information-boundary, and relationship-change checks.

6. **Subtxt-inspired interpretation guardrails**

   Add insufficient-evidence outcomes and diagnostic questions before any Throughline or Storypoint-style claim.

---

## Final answer

**Yes: the MVP is feasible, but the correct overall status is YELLOW.**

It becomes **GREEN** only if scoped like this:

> BookNLP for evidence extraction, dramatica-flow only as conceptual inspiration for read-only narrative-state rubrics, Subtxt docs as semantic guardrails, and NCP as an approved-context import/export format.

It becomes **RED** if you allow:

```text
automatic Storyform truth
automatic canon updates
prose generation
scene continuation
rewriting
outline generation as authored content
unreviewed NCP imports
dramatica-flow world_state/truth mutation
```

The clean MVP principle is:

> **Extract evidence automatically. Interpret conservatively. Store as candidates. Promote only by owner approval. Export approved context through validated NCP.**

[1]: https://github.com/booknlp/booknlp "GitHub - booknlp/booknlp: BookNLP, a natural language processing pipeline for books · GitHub"
[2]: https://github.com/ydsgangge-ux/dramatica-flow "GitHub - ydsgangge-ux/dramatica-flow: 深度集成 Dramatica 理论与 5 层 Agent 写作管线的下一代 AI 自动写小说引擎，支持因果链管理、多线叙事与伏笔追踪。A causal-driven AI novel creation system based on Dramatica theory, featuring a 5-layer Agent pipeline for deep narrative logic. · GitHub"
[3]: https://github.com/narrative-first/subtxt-docs/blob/main/content/1.getting-started/5.key-concepts.md "subtxt-docs/content/1.getting-started/5.key-concepts.md at main · narrative-first/subtxt-docs · GitHub"
[4]: https://github.com/narrative-first/subtxt-docs "GitHub - narrative-first/subtxt-docs: The official documentation for Subtxt, your storytelling co-pilot. Explore guides, concepts, and tips to get the most out of Subtxt. · GitHub"
[5]: https://github.com/narrative-first/narrative-context-protocol "GitHub - narrative-first/narrative-context-protocol: A standardized, application-agnostic narrative structure schema designed for reliably transporting authorial intent across multi-agentic narrative systems. · GitHub"
[6]: https://github.com/narrative-first/narrative-context-protocol/blob/main/VALIDATION.md "narrative-context-protocol/VALIDATION.md at main · narrative-first/narrative-context-protocol · GitHub"
[7]: https://github.com/narrative-first/narrative-context-protocol/blob/main/NCP_SEMANTIC_GROUNDING.md "narrative-context-protocol/NCP_SEMANTIC_GROUNDING.md at main · narrative-first/narrative-context-protocol · GitHub"
[8]: https://github.com/narrative-first/narrative-context-protocol/blob/main/SPECIFICATION.md "narrative-context-protocol/SPECIFICATION.md at main · narrative-first/narrative-context-protocol · GitHub"
-------------------------------------------------------------------------

## Verdict

**Path A — spaCy-first local deterministic extraction foundation — reaches a useful candidate-review MVP faster.**

I would mark it:

| Path                                                          |  MVP speed |                Boundary safety | Extraction richness | Recommendation                         |
| ------------------------------------------------------------- | ---------: | -----------------------------: | ------------------: | -------------------------------------- |
| **A) spaCy-first**                                            |  **Green** |                      **Green** |              Yellow | **Use for first candidate-review MVP** |
| **B) BookNLP + dramatica-flow + Subtxt + NCP all integrated** | Yellow/Red | Yellow/Red unless wrapped hard |           **Green** | Use later, staged—not as the first MVP |

The reason is simple: **your MVP’s hardest requirement is not “best extraction”; it is safe candidate review with source evidence, provenance, and owner-controlled promotion.** spaCy gives you enough local NLP primitives to build that review loop quickly: tokenization, sentence segmentation, NER, POS tagging, dependency parsing, lemmatization, and rule-based matchers/rulers. spaCy’s official docs describe it as an open-source NLP library with NER, POS tagging, dependency parsing, vectors, and more, and its processing pipeline includes components like `EntityRecognizer`, `DependencyParser`, `SentenceRecognizer`, `Sentencizer`, `Tagger`, `Lemmatizer`, and `EntityRuler`. ([spaCy][1])

## Why Path A wins for the first MVP

Path A lets you build the core product contract first:

**source text → extracted candidate → evidence span → provenance → owner review → approved memory**

That is the real MVP.

With spaCy-first, you can produce useful candidates for:

| Candidate type            | spaCy-first MVP behavior                                                  |
| ------------------------- | ------------------------------------------------------------------------- |
| Characters                | PERSON entities, repeated proper nouns, alias-like surface forms          |
| Locations/settings        | GPE, LOC, FAC entities                                                    |
| Organizations/groups      | ORG entities                                                              |
| Objects/items             | noun chunks + rule-based patterns, clearly marked lower confidence        |
| Timeline/event candidates | sentence-level verb/dependency candidates, not “canon events”             |
| Relationships             | co-occurrence and interaction candidates, not inferred truth              |
| Continuity warnings       | simple repeated-name, location, date, contradiction-adjacent candidates   |
| Evidence/provenance       | char offsets, sentence IDs, document/chapter/scene IDs, extractor version |

spaCy’s rule-based matcher is especially useful for your boundary model because it can run transparent token-pattern rules over existing token annotations, and callbacks can attach custom labels or merge spans. That makes it easier to explain why a candidate was created. ([spaCy][2])

The first useful MVP does **not** need perfect literary coreference, perfect quote attribution, or Dramatica/Subtxt interpretation. It needs the user to see: “The system found possible story knowledge here, here is the exact text span, do you approve it?” That is faster with Path A.

## Why Path B is attractive but slower if done all at once

BookNLP is the strongest extraction component in Path B. It is built specifically for books and long English documents, and it outputs entities, character name clustering/coreference, quote speaker identification, supersense tags, event tags, and referential gender inference. ([GitHub][3]) Its output files are directly relevant to your candidate model: `.tokens` includes paragraph/sentence/token IDs, document token IDs, words, lemmas, byte onset/offset, POS, dependency relation, syntactic head, and event; `.entities` includes coreference IDs, token spans, mention type, entity type, and text; `.quotes` includes quotation spans, attributed mention spans, speaker coreference ID, and quote text; `.book` summarizes recurring characters, references, gender, actions, possessions, and modifiers. ([GitHub][3])

So **BookNLP is very good for your app**—but not necessarily as part of a four-tool first MVP. It adds environment and mapping work, and its docs still note that book-length coreference is an open research problem and that outputs need inspection. ([GitHub][3])

The bigger slowdown is **dramatica-flow**. It has useful analysis concepts—causal chains, hooks/promises/mysteries/conflicts, emotional arcs, relationship networks, multi-thread timelines, and information boundaries. ([GitHub][4]) But the repo is explicitly an AI-assisted novel writing platform. Its architecture includes a Writer Agent that generates chapter text, a Reviser Agent, a Summary Generator, and state settlement that writes positions, emotions, relationships, hooks, and `world_state.json`. ([GitHub][4]) Its API also exposes generation and mutation endpoints such as AI outline generation, chapter content generation, segment rewriting, writing pipeline execution, revision execution, export, story-state extraction, and audit. ([GitHub][4])

That does not mean “don’t use it.” It means **do not integrate it directly into the MVP runtime**. For your app, dramatica-flow should first be treated as an **idea/reference repo for analysis-only candidate types**, not as a trusted component.

## NCP and Subtxt are better as boundaries/rubrics, not first extraction engines

NCP is very aligned with your long-term direction, but it is a transport/schema layer, not an extraction engine. The repo says NCP is a standardized JSON schema for transporting and preserving authorial intent, and it explicitly says there is no standalone app. ([GitHub][5]) It distinguishes Ideation, Subtext, Storytelling, Moments, and Narratives, and supports narrative status values like `candidate`, `draft`, and `complete`. ([GitHub][6]) That is excellent for **import/export after your own candidate/approved-memory model exists**.

The NCP semantic grounding file is also directly relevant to your safety boundaries: it says NCP is a transport format, not a replacement for Dramatica theory, canonical analysis, Storyform diagnosis, Subtxt, Narrova, or Dramatica platform behavior. It also warns that AI systems should not silently rewrite Subtext and should mark uncertainty instead of overwriting Storyform. ([GitHub][7]) That supports your “no canon mutation” rule.

Subtxt docs are useful as semantic guardrails. They explain Throughlines/Perspectives, Storypoints, Storybeats, and the idea that Storypoints identify the source of conflict through Domain → Concern → Issue → Problem. ([GitHub][8]) But Subtxt’s own AI tooling includes idea generation, refinement, review, suggestions, and copying suggestions into Storytelling boxes. ([GitHub][9]) For your app, that means Subtxt should not be used as a prose-generation workflow. Use it only to shape **diagnostic questions, insufficient-evidence outcomes, and rubric language**.

## The faster safe plan

I would build the MVP like this:

### Phase 1: Path A candidate-review MVP

Build a spaCy-first extractor that produces only candidates:

```text
source_document
  → source segments
  → local extraction pass
  → candidate records
  → evidence spans
  → owner review UI
  → approved memory only after explicit user action
```

Every candidate should include:

```json
{
  "candidate_id": "...",
  "candidate_type": "character | location | organization | object | event | relationship | quote | continuity_warning",
  "claim_text": "...",
  "confidence": "low | medium | high",
  "source_locator": {
    "project_id": "...",
    "document_id": "...",
    "chapter_id": "...",
    "scene_id": "...",
    "char_start": 123,
    "char_end": 180
  },
  "evidence_text": "...",
  "extractor": {
    "name": "spacy_candidate_extractor",
    "version": "...",
    "ruleset_version": "..."
  },
  "status": "candidate",
  "approved_by_owner": false
}
```

Hard rule: **no candidate can update approved memory, canon, storyform, world state, or NCP export unless the owner promotes it.**

### Phase 2: Add BookNLP as a second extractor

After the review loop is working, add BookNLP behind the same candidate contract. BookNLP can improve:

| BookNLP output | Candidate use                                                      |
| -------------- | ------------------------------------------------------------------ |
| `.entities`    | character, location, organization candidates with coreference IDs  |
| `.quotes`      | quote candidates with candidate speaker attribution                |
| `.tokens`      | evidence locators, sentence IDs, byte offsets, event tags          |
| `.book`        | character profile candidates: aliases, actions, objects, modifiers |
| `.supersense`  | candidate objects/items, semantic categories                       |
| event layer    | candidate timeline/event records                                   |

This is likely the best medium-term extraction upgrade because BookNLP already outputs the kinds of literary features your app needs.

### Phase 3: Add NCP import/export only around reviewed data

Use NCP for:

```text
approved story context → NCP export
NCP import → candidate records pending owner review
```

Do **not** import NCP as canon automatically. Even though NCP supports `candidate`, `draft`, and `complete`, your app should still treat external NCP files as untrusted until reviewed. NCP’s own validation guide recommends validating files against the canonical schema and treating failures as blocking. ([GitHub][10])

### Phase 4: Add Subtxt/Dramatica rubric diagnostics

Use Subtxt-inspired rules only as diagnostic rubrics:

```text
candidate evidence → possible throughline/storypoint question → owner diagnostic prompt
```

Example safe output:

> “This passage may involve a Main Character concern, but there is insufficient evidence to classify it. Is the conflict primarily about the character’s personal viewpoint, or about the whole cast’s objective problem?”

Unsafe output:

> “This is definitely the Main Character Problem.”

### Phase 5: Use dramatica-flow concepts, not its generation pipeline

From dramatica-flow, borrow these as candidate types:

| dramatica-flow concept | Safe use in your app                                    |
| ---------------------- | ------------------------------------------------------- |
| Causal chain           | candidate cause/event/effect/decision record            |
| Hook lifecycle         | candidate foreshadowing/promise/mystery/conflict record |
| Emotional arcs         | candidate emotional-state observation                   |
| Relationship network   | candidate relationship-change observation               |
| Multi-thread timeline  | candidate thread/activity record                        |
| Information boundary   | candidate “who knows what” record                       |
| Audit diagnostics      | read-only analysis warning                              |

Block or ignore:

```text
AI outline generation
AI chapter generation
AI rewrite segment
write pipeline
revise pipeline
summary generator that mutates truth files
world_state settlement
truth-file mutation
automatic relationship/emotion/hook updates as canon
```

## Final recommendation

Use **Path A now** to reach a working MVP faster.

Then fold in Path B **in pieces**:

1. **BookNLP first**, as a richer second-stage extractor.
2. **NCP second**, for approved-context import/export and schema validation.
3. **Subtxt third**, as semantic diagnostic rubrics and insufficient-evidence rules.
4. **dramatica-flow last**, as analysis concept inspiration or a heavily sandboxed read-only adapter—not as a runtime writing pipeline.

That sequence preserves your core boundaries: **no prose generation, no canon mutation, evidence/provenance on every claim, and owner review before approval.**

[1]: https://spacy.io/usage/linguistic-features?utm_source=chatgpt.com "Linguistic Features · spaCy Usage Documentation"
[2]: https://spacy.io/usage/rule-based-matching?utm_source=chatgpt.com "Rule-based matching · spaCy Usage Documentation"
[3]: https://github.com/booknlp/booknlp "GitHub - booknlp/booknlp: BookNLP, a natural language processing pipeline for books · GitHub"
[4]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/README_EN.md "dramatica-flow/README_EN.md at main · ydsgangge-ux/dramatica-flow · GitHub"
[5]: https://github.com/narrative-first/narrative-context-protocol "GitHub - narrative-first/narrative-context-protocol: A standardized, application-agnostic narrative structure schema designed for reliably transporting authorial intent across multi-agentic narrative systems. · GitHub"
[6]: https://github.com/narrative-first/narrative-context-protocol/blob/main/SPECIFICATION.md "narrative-context-protocol/SPECIFICATION.md at main · narrative-first/narrative-context-protocol · GitHub"
[7]: https://github.com/narrative-first/narrative-context-protocol/blob/main/NCP_SEMANTIC_GROUNDING.md "narrative-context-protocol/NCP_SEMANTIC_GROUNDING.md at main · narrative-first/narrative-context-protocol · GitHub"
[8]: https://github.com/narrative-first/subtxt-docs/blob/main/content/2.narrative-aspects/1.perspectives.md "subtxt-docs/content/2.narrative-aspects/1.perspectives.md at main · narrative-first/subtxt-docs · GitHub"
[9]: https://github.com/narrative-first/subtxt-docs/blob/main/content/5.narrative-intelligence/1.subtxt-ai-tools.md "subtxt-docs/content/5.narrative-intelligence/1.subtxt-ai-tools.md at main · narrative-first/subtxt-docs · GitHub"
[10]: https://github.com/narrative-first/narrative-context-protocol/blob/main/VALIDATION.md "narrative-context-protocol/VALIDATION.md at main · narrative-first/narrative-context-protocol · GitHub"
----------------------------------------------------------

Yes — the initial answer changes in an important way.

The recommendation is **still not “integrate everything first.”** But it should no longer be framed as **plain spaCy-first deterministic extraction**. The better updated path is:

> **Path A+ — tool-informed spaCy candidate-review foundation.**
> Use spaCy as the local extraction/ranking engine, but use BookNLP, dramatica-flow, Subtxt, and NCP to define the candidate ontology, evidence gates, rejection labels, provenance rules, and future evaluation strategy.

That fixes the problem you identified: raw spaCy would create too many low-value candidates. The MVP should not be “spaCy finds everything.” It should be “spaCy proposes only review-worthy candidates that pass strict evidence gates.”

## Updated verdict

| Path                                                                          |                                                      Updated result | Why                                                                                                                                                      |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A0 — raw spaCy-first extraction**                                           |                                                      **Red/Yellow** | Too much garbage; poor literary awareness; weak relationship/event/continuity quality.                                                                   |
| **A+ — tool-informed spaCy + rules + gates + owner-review training loop**     |                                                           **Green** | Fastest useful MVP because the review loop, provenance, rejection data, and safety boundaries become the product foundation.                             |
| **B — full BookNLP + dramatica-flow + Subtxt + NCP integration from day one** |                                                      **Yellow/Red** | More powerful, but slower and riskier because dramatica-flow includes generation/revision/world-state mutation surfaces that must be blocked or wrapped. |
| **Best staged strategy**                                                      | **A+ first, then BookNLP, then NCP/Subtxt/dramatica-flow concepts** | Gives you useful candidate review quickly without letting any external tool mutate canon or generate prose.                                              |

So the updated answer is **not “spaCy alone first.”** It is:

> **Build the candidate-review engine first using spaCy, but design it using the knowledge from the other tools.**

The prior answer correctly said Path A was faster, but it under-emphasized the need for a precision-first gate and training feedback loop. The revised answer should replace “spaCy-first deterministic extraction foundation” with **“tool-informed spaCy candidate-review foundation.”** 

## What changes in the architecture

The old version was roughly:

```text
source text
  → spaCy extraction
  → candidate records
  → owner review
```

The updated version should be:

```text
source text
  → spaCy base pipeline
  → tool-informed candidate generators
  → evidence/provenance gate
  → duplicate/speculation/noise gate
  → owner review
  → approved memory OR rejection reason
  → training/evaluation dataset
```

The critical change is that **candidate generation and candidate acceptance are separated**. spaCy can generate possible spans, but your app decides whether they are review-worthy.

spaCy supports this hybrid approach because its pipelines can combine trainable components, frozen components, and rule/custom components; its training docs also support using earlier/frozen components as annotating components during training. ([spaCy][1]) For your use case, `SpanCategorizer` is more relevant than classic NER because it can label potentially overlapping spans and store scores in `doc.spans[...]`, while `TextCategorizer`/`textcat_multilabel` can score sentence or paragraph usefulness. ([spaCy][2]) ([spaCy][3])

## What each external tool contributes in the updated Path A+

### BookNLP moves earlier — but as a reference and later extractor, not the first UI dependency

BookNLP should influence your candidate schema immediately because it already models literary features you care about: POS/dependency parsing, entity recognition, character name clustering/coreference, quote speaker attribution, supersense tagging, event tagging, and referential gender inference. ([GitHub][4]) Its output files are also useful for provenance: `.tokens`, `.entities`, `.quotes`, `.supersense`, `.book`, and `.book.html`; the `.tokens` file includes paragraph ID, sentence ID, token IDs, lemma, byte onset/offset, POS, dependency relation, syntactic head, and event. ([BookNLP][5])

Updated role:

```text
MVP day one:
  Use BookNLP concepts to design candidate schemas.

After review loop exists:
  Add BookNLP as a second extractor behind the same candidate gate.

Never:
  Let BookNLP output become approved memory automatically.
```

### dramatica-flow becomes a candidate ontology source, not a runtime dependency

dramatica-flow is still dangerous as a direct integration because the repo describes an AI-assisted novel writing platform with causal chain, hooks, emotional arcs, relationship networks, multi-thread narrative, and information boundaries — but its architecture also includes Writer Agent generation, Reviser Agent revision, causal extraction that writes world state, summary generation to truth files, and state settlement into `world_state.json`. ([GitHub][6]) It also exposes endpoints for AI outline generation, chapter content generation, segment rewriting, writing pipeline execution, revision, export, and story-state extraction. ([GitHub][6])

Updated role:

```text
Use:
  causal chain cue
  hook / promise / mystery / conflict cue
  emotional state observation
  relationship change cue
  timeline thread cue
  information boundary cue
  audit diagnostic cue

Block:
  outline generation
  chapter generation
  rewrite
  write pipeline
  revise pipeline
  summary-to-truth
  world_state mutation
```

This is the biggest correction to the initial answer: **dramatica-flow can help Path A immediately, but only as a source of labels and gates, not as imported functionality.**

### Subtxt becomes a diagnostic-question rubric

Subtxt/Dramatica concepts should not be automatic classifiers. They should define what kinds of evidence are required before the app asks a diagnostic question.

Updated role:

```text
Bad:
  "This is the Main Character Throughline."

Good:
  "This passage may contain Main Character perspective evidence. Is the conflict personal to the character’s viewpoint, or objective to the whole cast?"
```

NCP’s semantic grounding supports this caution: it says NCP is a transport format, not a replacement for Dramatica theory, canonical analysis, Storyform diagnosis, Subtxt, Narrova, or Dramatica platform behavior; it also says AI should not silently rewrite Subtext and should mark uncertainty instead of overwriting Storyform. ([GitHub][7]) ([GitHub][7])

### NCP becomes the approved-context boundary

NCP should not drive extraction. It should define how approved context is exported and how imported context is treated. The NCP spec supports `candidate`, `draft`, and `complete` statuses, and it separates Ideation, Subtext, and Storytelling. ([GitHub][8]) Its validation guide says NCP payloads should be validated against the canonical schema and that failures should be treated as blocking. ([GitHub][9])

Updated role:

```text
approved memory → NCP export
NCP import → candidate records pending owner review
invalid NCP → blocking validation failure
external NCP "complete" → still not app canon unless owner accepts it
```

## Updated MVP path

### Phase 1 should not be “extract everything”

The first MVP should extract **fewer things with higher trust**.

Start only with high-precision candidates:

| Candidate type               | MVP approach                                                     |
| ---------------------------- | ---------------------------------------------------------------- |
| Character candidate          | PERSON entities, repeated proper nouns, dialogue speaker cues    |
| Location/setting candidate   | GPE/LOC/FAC + scene/location patterns                            |
| Organization/group candidate | ORG + faction/group cues                                         |
| Object/item candidate        | high-signal noun chunks only, not every noun                     |
| Event candidate              | sentence-level action/state-change with verb/dependency evidence |
| Relationship cue             | two entities + kinship/social/opposition/cooperation cue         |
| Causal cue                   | because/therefore/so/forced/resulted/led-to patterns             |
| Conflict evidence cue        | obstacle, pressure, opposition, inability, contradiction         |
| Mystery/promise cue          | secret, unknown, promised, revealed, unresolved, hidden          |
| Information-boundary cue     | knows, learns, hears, witnesses, discovers, lies, hides          |

Everything else waits.

### Phase 2 is the candidate gate

The gate is now more important than the extractor.

A candidate is rejected before UI review if it lacks:

```text
source document ID
source locator
char_start / char_end or equivalent byte/token locator
evidence text
candidate type
extractor name/version
ruleset version
confidence/rank
non-canon status
```

And it is rejected if it contains:

```text
canon claim
storyform certainty
prose generation
rewrite suggestion
unattributed inference
world-state mutation
approved-memory mutation
```

### Phase 3 captures rejection as training data

This is the part that makes “garbage review” not wasted.

Every owner decision becomes structured feedback:

```json
{
  "candidate_id": "cand_123",
  "decision": "rejected",
  "rejection_reason": "too_generic",
  "candidate_type": "event_candidate",
  "evidence_ok": false,
  "span_boundary_ok": false,
  "speculative": true
}
```

Your first rejection reasons should be:

```text
not_story_knowledge
too_generic
wrong_candidate_type
bad_span_boundary
missing_evidence
duplicate
speculative_inference
canon_claim_risk
prose_generation_risk
```

### Phase 4 fine-tunes only after review data exists

This changes the answer substantially: **do not fine-tune spaCy before you know what your owner-review UI considers useful.**

After 200–500 reviewed examples, fine-tune:

```text
spancat:
  CHARACTER_CANDIDATE
  RELATIONSHIP_CUE
  EVENT_CANDIDATE
  CAUSAL_LINK_CUE
  CONFLICT_EVIDENCE_CUE
  PROMISE_MYSTERY_CUE
  INFO_BOUNDARY_CUE

textcat_multilabel:
  HAS_REVIEW_WORTHY_CANDIDATE
  HAS_EVENT_SIGNAL
  HAS_RELATIONSHIP_SIGNAL
  HAS_CONFLICT_SIGNAL
  LOW_VALUE_NOISE
```

This gives you a practical feedback loop:

```text
rules produce candidates
owner accepts/rejects
rejections become negatives
accepted candidates become positives
spaCy learns ranking/filtering
candidate quality improves
```

## Updated final recommendation

The initial answer’s final recommendation should be rewritten as:

> Use **Path A+ now**: a tool-informed spaCy candidate-review foundation. Do not build raw spaCy extraction, and do not integrate the whole BookNLP/dramatica-flow/Subtxt/NCP stack at once. Use the external tools to define the candidate ontology, evidence rules, rejection labels, and review boundaries. Then add BookNLP as a second extractor after the review engine exists. Add NCP only for reviewed import/export. Add Subtxt/Dramatica only as diagnostic-question rubrics. Use dramatica-flow concepts only as read-only inspiration for candidate types, while blocking all generation, revision, and world-state mutation paths.

That means the updated MVP is no longer:

```text
spaCy-first extraction
```

It is:

```text
tool-informed, precision-first candidate review
```

That is much more likely to produce real progress instead of a pile of noisy candidates.

[1]: https://spacy.io/usage/training "Training Pipelines & Models · spaCy Usage Documentation"
[2]: https://spacy.io/api/spancategorizer "SpanCategorizer · spaCy API Documentation"
[3]: https://spacy.io/api/textcategorizer "TextCategorizer · spaCy API Documentation"
[4]: https://github.com/booknlp/booknlp "GitHub - booknlp/booknlp: BookNLP, a natural language processing pipeline for books · GitHub"
[5]: https://booknlp.pythonhumanities.com/03_files.html "3. The Output Files — Introduction to BookNLP"
[6]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/README_EN.md "dramatica-flow/README_EN.md at main · ydsgangge-ux/dramatica-flow · GitHub"
[7]: https://github.com/narrative-first/narrative-context-protocol/blob/main/NCP_SEMANTIC_GROUNDING.md "narrative-context-protocol/NCP_SEMANTIC_GROUNDING.md at main · narrative-first/narrative-context-protocol · GitHub"
[8]: https://github.com/narrative-first/narrative-context-protocol/blob/main/SPECIFICATION.md "narrative-context-protocol/SPECIFICATION.md at main · narrative-first/narrative-context-protocol · GitHub"
[9]: https://github.com/narrative-first/narrative-context-protocol/blob/main/VALIDATION.md "narrative-context-protocol/VALIDATION.md at main · narrative-first/narrative-context-protocol · GitHub"
