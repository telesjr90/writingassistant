# PHASE8-IMPL-005 NLP/Extraction Adapter Strategy Decision

## 1. Decision Identity

- Parent: `PHASE8-IMPL-005`
- Child: `PHASE8-IMPL-005-T006`
- Title: NLP/extraction adapter strategy decision
- Track: Writer Assistant Core
- Status: accepted
- Date: 2026-06-18
- Scope: docs/decision only
- In-scope candidates: `spaCy`, `segram`, `BookNLP`, `GLiNER`, `LangExtract`, `Renard`
- Reference-only context carried forward: `dramatica-flow`, Narrative Context Protocol, Subtxt docs

## 2. Decision Summary

`PHASE8-IMPL-005-T006` selects a **spaCy-first, local, deterministic/rule-assisted, candidate-only extraction foundation** as the safest first extraction strategy path for the next implementation parent.

The next parent should **not** begin with model-assisted extraction, manuscript-scale literary pipelines, semantic graph extraction, or relationship-network automation. It should first build a bounded extraction foundation that can:

- segment owner-authored source documents safely
- attach stable source locators and evidence spans
- emit bounded candidate-only records
- normalize simple named entities into existing Writer Assistant Core candidate categories
- preserve no-prose and no-canon-mutation boundaries
- route everything through reviewable candidate storage/index infrastructure

This means the next parent should be classified as:

- **primary path:** `spaCy-first`
- **operating style:** `local`, `deterministic`, `rule-assisted`, `candidate-only`
- **fallback discipline:** `manual-first review and normalization around extractor output`
- **not selected as first path:** fully manual-only, model-assisted-first, LangExtract-first, BookNLP-first, segram-first, Renard-first, or broad hybrid-from-day-one

The first extraction slice should target only the narrowest story-knowledge categories that fit the existing candidate storage/evidence contracts with the lowest safety and dependency risk.

## 3. Evidence Basis

This decision uses completed local roadmap artifacts and runtime-adjacent candidate contract files. T006 performs no new external source retrieval, installs, clones, executions, demos, or model calls.

### Primary decision artifacts read

- `docs/roadmap/tasks/PHASE8-IMPL-005.md`
- `docs/roadmap/inventory/PHASE8-IMPL-005.md`
- `docs/roadmap/inventory/PHASE8-IMPL-005-tool-source-inventory.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-005.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-dramatica-flow-analysis-only-reference-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-ncp-subtxt-structural-interpretation-strategy-decision.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/roadmap_index.yaml`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/master_plan.md`
- `docs/roadmap/validation/latest_roadmap_validation.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/tooling_decisions.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_storage.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`

### Decision-support constraints carried forward

From T002:

- runtime adapter work must satisfy evidence/provenance, candidate-only, local-first/privacy, and no-prose gates
- blockers B1-B6 remain active
- T006 may use qualitative or estimated rubric scoring, but not runtime-verification certainty

From T003:

- `spaCy` is the only tool preliminarily classified as a **likely runtime adapter candidate**
- `segram`, `BookNLP`, `GLiNER`, `LangExtract`, and `Renard` are only **possible runtime adapter candidates**
- `Renard` has unresolved GPL-3.0 adoption risk
- `LangExtract` has conditional remote-data/privacy risk if cloud defaults are used
- `BookNLP` and `segram` both have higher dependency/runtime or maintainability cost than `spaCy`

From T004 and T005:

- `dramatica-flow`, NCP, and Subtxt remain reference-only
- they may inform evaluation language, evidence discipline, and later rubric design
- they must not be reintroduced as first runtime extraction adapters in this parent

From existing runtime contracts:

- candidate storage/index infrastructure already exists and is JSON-based, candidate-first, and local
- candidate validation expects bounded target categories, source locators, evidence arrays, provenance, owner decisions, and destinations
- this favors a first extractor that can produce deterministic spans and simple normalized outputs over one that depends on opaque multi-stage model inference

## 4. Strategy Decision

### 4.1 Selected first path

**Accepted first extraction path:**

`spaCy-first, local, deterministic/rule-assisted, candidate-only extraction foundation`

### 4.2 Why this path wins

`spaCy` best matches the current readiness level because it combines:

- strong analysis-only safety
- no prose-generation behavior
- local-first execution model
- mature maintenance and documentation
- clear MIT license
- stable token/span/dependency outputs that fit evidence-first normalization
- lower dependency/runtime cost than BookNLP, LangExtract, or Renard
- better determinism and normalizability than model-assisted-first approaches
- better maturity and maintainability than segram for a first parent

It also best aligns with the current app state:

- candidate schema, validation, persistence, and derived index helpers already exist
- what is missing is not deep semantic interpretation first; it is a safe extraction-to-candidate pipeline with evidence discipline
- the first implementation parent should prove the app-owned adapter boundary, not maximize extraction ambition

### 4.3 Path classification language

For roadmap and implementation planning, the chosen path should be described as:

- **manual-first?** no, not as the primary strategy
- **rule-based?** yes, as part of the selected path
- **spaCy-first?** yes, this is the accepted first path
- **model-assisted?** deferred
- **hybrid?** deferred until after the baseline candidate/evidence pipeline exists

More precisely, the next parent should be treated as a **spaCy-first baseline with manual review and rule-assisted normalization**, not as an equal-weight hybrid of all tools.

## 5. Candidate Comparison Outcome

The table below uses T002 rubric dimensions qualitatively. These are decision-support estimates from T003 official-source inventory and local contract fit, not runtime verification.

| Candidate | Provisional T006 classification | First-path decision | Main reasons |
| --- | --- | --- | --- |
| `spaCy` | accepted first-path baseline | **accept** | strongest local-first fit, mature MIT stack, deterministic spans, lower integration risk, best contract fit for first candidate/evidence pipeline |
| `segram` | deferred later semantic/action reference | defer | useful action/semantic layer, but depends on spaCy baseline, has early-stage/stale maintenance risk, and is too specialized for the first parent |
| `BookNLP` | deferred later long-form literary spike | defer | strong literary extraction potential, but high dependency/runtime cost and too much scope for the first parent |
| `GLiNER` | deferred later custom-entity spike | defer | promising for fiction-specific labels, but model-backed custom extraction should follow baseline evidence/normalization discipline |
| `LangExtract` | deferred later local-only model-assisted spike | defer | strongest grounding design reference, but model-assisted path adds privacy/inference variability too early |
| `Renard` | deferred later relationship-network spike | defer | useful later for relationships/networks, but GPL-3.0 review plus evidence-linking complexity makes it unsafe for first adoption |

### 5.1 spaCy

Final provisional strategy classification: **accepted first implementation direction**.

Why:

- best fit for T002 D1, D3, D6, D7, D8, D10, D11, D12, and D13
- strongest match to current candidate schema/evidence/index groundwork
- enables sentence/document segmentation, token/offset/span-based evidence, and simple entity candidates without requiring cloud or opaque inference

### 5.2 segram

Final provisional strategy classification: **defer as later semantic/action extraction reference or adapter**.

Why deferred:

- depends conceptually and operationally on a spaCy-style baseline
- early-stage maintenance signal is weak in T003
- more specialized than the first parent needs
- first parent should prove basic evidence-first extraction before semantic action graphs

### 5.3 BookNLP

Final provisional strategy classification: **defer as later manuscript-scale literary extraction candidate**.

Why deferred:

- strong long-form literary promise for character/coref/quote/event work
- dependency footprint is much heavier than the first parent needs
- first parent should not begin with torch + tensorflow style literary pipeline adoption
- output normalization and scale concerns are better addressed after the baseline review flow exists

### 5.4 GLiNER

Final provisional strategy classification: **defer as later custom entity extraction candidate**.

Why deferred:

- strong later fit for fiction-specific labels
- likely useful after basic entity/evidence normalization exists
- still model-based and threshold-sensitive relative to a simpler deterministic first slice
- better positioned as a second-step complement to spaCy than as the baseline itself

### 5.5 LangExtract

Final provisional strategy classification: **defer as later local-only model-assisted extraction path**.

Why deferred:

- strongest evidence/provenance design reference among model-assisted options
- local Ollama path is promising, but cloud/default remote behavior remains too risky for first adoption
- world-knowledge/inference behavior increases candidate-overclaim risk before the baseline evidence discipline is established
- first parent should avoid normalizing model-assisted claims before proving deterministic extraction plumbing

### 5.6 Renard

Final provisional strategy classification: **defer pending GPL/license review and later relationship-network need**.

Why deferred:

- useful relationship-network reference later
- not needed to prove first extraction plumbing
- GPL-3.0 review remains an adoption blocker for naive runtime integration
- graph outputs require extra evidence-linking discipline beyond what the first parent should tackle

## 6. First Extraction Slice Scope

The first extraction slice should stay narrow.

### 6.1 Accepted first target categories

The next parent should target only these categories first:

1. **document segmentation and source locators**
   - scene/note/material document boundaries
   - sentence/section/span locators
   - deterministic source locator normalization compatible with existing candidate contracts

2. **simple named-entity candidates**
   - `character_candidate`
   - `location_candidate`
   - `organization_candidate`
   - `object_candidate` only where simple deterministic heuristics are safe enough

3. **evidence/provenance attachment**
   - bounded evidence item generation
   - excerpt/offset/line locator normalization where available
   - provenance metadata marking extractor/tool origin and human review requirements

4. **candidate normalization and dedup-ready shaping**
   - mapping extractor spans into bounded `candidate_type`, `target_category`, `destination`, and candidate content structures
   - preserving uncertainty instead of overclaiming roles or relationships

5. **candidate-only safety contracts**
   - no prose generation
   - no direct memory/canon mutation
   - no silent promotion
   - no durable truth writes beyond candidate JSON and derived index refresh if later authorized

### 6.2 First-slice output focus

The first slice should emphasize:

- candidate creation from local owner-authored or owner-provided source documents
- reviewable evidence and provenance
- low-ambiguity entity extraction
- bounded, explainable normalization

The first slice should **not** optimize for literary sophistication, semantic completeness, or automation breadth.

## 7. Deferred Categories

The next parent must defer these categories until after the baseline exists:

### 7.1 Deferred to later parent/spike

- `relationship_candidate` extraction beyond simple future placeholders
- `timeline_event_candidate` extraction beyond trivial source-locator groundwork
- `plot_thread_candidate`
- `open_question_candidate` extraction from model interpretation
- `continuity_warning_candidate`
- `contradiction_candidate`
- `navigation_summary_candidate`
- `annotation_candidate`
- `scene_event_causality_review_candidate`

### 7.2 Why these stay deferred

These categories require more interpretive risk, more normalization logic, or more review UI maturity than the first parent should absorb.

Specifically:

- relationships need cross-entity disambiguation and evidence-linking discipline
- events/timeline/causality need stronger action extraction and ordering logic
- contradiction/continuity detection risks false authority if introduced before side-by-side evidence workflows mature
- summaries and open questions can drift toward generated prose or model-authored interpretation if introduced too early
- plot threads are high-value but structurally ambiguous and too easy to overclaim without later rubric support

## 8. Evidence and Candidate-Only Constraints

The next parent must enforce the following hard rules.

### 8.1 Evidence/provenance requirements

Every extraction output must:

- resolve to one bounded candidate record shape
- include a source locator compatible with `candidate_record.py`
- include an evidence array, even if minimal
- include provenance with human review required
- preserve extractor identity/version or equivalent provenance markers where available
- preserve uncertainty rather than silently upgrading weak signals into fact

### 8.2 Candidate-only requirements

The next parent must ensure that extractor output:

- writes only candidate records and related derived candidate metadata
- never writes `memory/*.json`
- never writes `bible.json`, `storyform.json`, scene Markdown, or note/material bodies
- never creates or applies canon/memory truth
- never bypasses OMI review or owner approval
- never treats extractor confidence as truth certainty

### 8.3 No-prose requirements

The next parent must:

- reject or strip prose-generation behavior from extraction results
- treat summaries, paraphrases, or narrative completions as out of scope for this first slice
- keep diagnostic labels and metadata compact, bounded, and structural
- preserve the standard refusal boundary for any prose-writing request

### 8.4 Local-first/privacy requirements

The next parent must:

- assume local-only execution for the selected first path
- avoid remote provider defaults
- avoid any dependency whose normal use sends owner text off-machine
- keep LangExtract-style cloud/default behavior blocked unless a later parent explicitly approves a local-only path

## 9. What the Next Parent Should Build

The next implementation parent should build only the minimum app-owned extraction foundation necessary to test the chosen strategy.

### 9.1 Build

1. **app-owned extraction adapter contract for the first baseline**
   - a bounded adapter/orchestrator shape around the existing candidate storage model

2. **source-document segmentation and locator helpers**
   - deterministic locators for scenes, notes, and materials
   - evidence span normalization compatible with existing candidate record validation

3. **spaCy-first extraction normalization flow**
   - narrow entity extraction path into bounded candidate records
   - destination/target-category mapping for first-slice categories only

4. **candidate-only write path integration**
   - safe persistence through existing candidate persistence/index layers
   - no memory/canon writes

5. **tests and validation for extraction boundaries in that later parent**
   - no-prose behavior
   - candidate-only output
   - evidence/provenance presence
   - local deterministic normalization
   - fail-closed handling for unsupported/ambiguous output

6. **manual review handoff expectations**
   - extracted candidates are review material only
   - no automatic approval or promotion behavior

### 9.2 Explicitly do not build

The next parent must explicitly not build:

- BookNLP runtime integration
- GLiNER runtime integration
- LangExtract runtime integration
- Renard runtime integration
- segram runtime integration
- cloud extraction paths
- OMI auto-promotion
- memory/canon apply-promotion
- contradiction or continuity automation
- relationship-network or timeline graph extraction
- summary generation or rewrite helpers
- prose-generation, continuation, or revision flows
- backend routes or frontend UI beyond what a later parent explicitly authorizes
- package/dependency expansion beyond the narrowly approved first-path spike scope

## 10. Why Other Strategic Paths Are Rejected for First Use

### 10.1 Manual-first only

Rejected as the primary path because it does not actually decide the first extractor direction and would postpone the adapter/evidence decision T006 is supposed to make.

A manual review layer is still required around extractor output, but manual-only is too conservative for the next implementation parent given that the candidate schema/persistence/index baseline already exists.

### 10.2 Model-assisted first

Rejected because:

- it adds privacy and determinism risk too early
- it weakens normalizability before the app has proven a stable evidence-first extraction path
- it increases overclaim risk for story knowledge categories

### 10.3 Broad hybrid first

Rejected because:

- it expands scope too early
- it obscures which tool is responsible for which extraction behavior
- it makes failures harder to isolate
- it invites dependency sprawl before the app-owned adapter boundary is proven

### 10.4 BookNLP-first

Rejected because manuscript-scale literary extraction is too heavy and too broad for the first bounded parent.

### 10.5 GLiNER-first

Rejected because custom-label model extraction should come after a deterministic baseline and review discipline exist.

### 10.6 LangExtract-first

Rejected because evidence grounding is attractive, but model-assisted inference and privacy constraints should be introduced only after the baseline candidate/evidence architecture is stable.

## 11. Relationship to T004 and T005

This decision does not reopen prior decisions.

- `dramatica-flow` remains `reference-only`
- NCP remains `reference-only` now and optional future `approved-context import/export candidate`
- Subtxt remains `reference-only` now and optional future `semantic rubric candidate`

Safe influence from those prior decisions:

- evidence-before-label discipline
- no automatic truth or canon settlement
- candidate-first review pipeline
- author-level interpretation caution
- diagnostic questions over invented structure

Unsafe use that remains rejected:

- using dramatica-flow as a runtime extraction dependency
- using NCP as automatic structural truth
- using Subtxt labels as automatic story classification

## 12. Deferred Decisions

Still deferred beyond T006:

1. exact package approval and installation timing for the next implementation parent
2. exact extraction trigger policy: manual action, save-triggered, or batch
3. exact first evidence locator format priority: offsets, lines, or hybrid
4. exact first-slice destination set for candidate review UI exposure
5. whether `object_candidate` should be in the very first spike or held behind characters/locations/organizations only
6. when to introduce GLiNER as a complement to spaCy for custom labels
7. when to introduce BookNLP for long-form literary pipelines
8. whether LangExtract local-only evaluation is worth a later dedicated parent after baseline proof
9. whether Renard can ever be adopted after GPL review, or should remain reference-only
10. whether segram should remain reference-only or become a later semantic/action adapter

## 13. Accepted Decision

**Decision:** Accept `spaCy` as the safest first implementation direction.

**Decision:** Classify the next parent as `spaCy-first`, `local`, `deterministic`, `rule-assisted`, and `candidate-only`.

**Decision:** Defer `segram`, `BookNLP`, `GLiNER`, `LangExtract`, and `Renard` from first-path implementation.

**Decision:** Limit the first extraction slice to source segmentation/locators, simple entity candidates, evidence/provenance attachment, and bounded candidate normalization.

**Decision:** Keep relationships, events/timeline causality, plot threads, continuity/contradictions, summaries, and model-assisted extraction deferred until after the baseline candidate/evidence pipeline exists.

**Decision:** Require all future extraction output to remain candidate-only, evidence-backed where possible, owner-reviewed, no-prose, and blocked from direct canon/memory mutation.

## 14. Recommended Next Parent Shape

Recommended next parent after `PHASE8-IMPL-005-T007` closeout:

- app-owned extraction foundation parent
- tests-first and boundary-first
- narrow first slice around local document segmentation, evidence locator normalization, and simple spaCy-backed entity candidate creation
- no review UI expansion unless separately authorized
- no model-assisted path yet

Suggested emphasis for T007 handoff language:

- build the extraction foundation before ambitious extractors
- prove candidate-only evidence plumbing first
- defer literary, semantic, graph, and model-assisted extractors until the baseline is stable

## 15. Safety Confirmation

- Docs/decision only.
- No extraction implementation added.
- No external packages installed.
- No repositories cloned.
- No demos or external tool execution.
- No model calls.
- No backend routes added.
- No frontend UI added.
- No tests added or changed.
- No runtime code changed.
- No project runtime files created.
- No memory/canon mutation.
- No JSONL, dataset, or training artifacts created.
- No prose generation, rewrite, continuation, polish, or improvement behavior introduced.
