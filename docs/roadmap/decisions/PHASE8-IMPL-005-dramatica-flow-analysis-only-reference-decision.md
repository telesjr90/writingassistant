# PHASE8-IMPL-005 Dramatica-flow Analysis-Only Reference Decision

## 1. Decision Summary

`PHASE8-IMPL-005-T004` accepts **dramatica-flow** as **`reference-only`** for analysis-pattern and diagnostic-rubric inspiration inside the Writer Assistant Core evaluation track.

dramatica-flow is **not** accepted as:

- a runtime dependency
- an extractor adapter
- an imported pipeline
- a tool to execute
- a source of generated outlines, prose, or story truth
- a source of canon or memory mutation

Any future use of dramatica-flow-inspired concepts must be:

- analysis-only
- candidate-first
- evidence/provenance-backed
- owner-reviewed
- no generated prose
- no rewriting
- no continuation
- no outline-as-truth
- no automatic memory/canon mutation
- no direct dramatica-flow runtime execution

Runtime adapter status: **REJECT/DEFER**.

## 2. Why This Decision Exists

`PHASE8-IMPL-005-T003` found useful narrative-state analysis concepts in dramatica-flow official README evidence: causal chains, hook/foreshadowing lifecycle, emotional arcs, relationship networks, timeline/thread activity, information boundaries, and audit dimensions.

T003 also found hard safety risks for runtime adapter use. dramatica-flow documents Writer Agent, Reviser Agent, Architect Agent outline generation, chapter generation, rewrite/revise APIs, continuation-style writing pipeline, world_state/truth-file writes, and LLM-backed generation as core product behavior. That conflicts with the app's analysis-only, owner-controlled boundary.

The app is analysis-only. Owner-authored prose storage and editing are allowed; AI must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose. Candidates are not canon. Tool output does not prove story truth.

This decision is required before `PHASE8-IMPL-005-T005` (NCP/Subtxt structural interpretation) and `PHASE8-IMPL-005-T006` (NLP/extraction adapter strategy) so future extraction planning treats dramatica-flow correctly: reference inspiration only, never runtime generation or canon mutation.

## 3. Evidence Basis

Evidence comes from T003 official source review recorded in:

- `docs/roadmap/inventory/PHASE8-IMPL-005-tool-source-inventory.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`

T004 did not perform new external source retrieval. T003 inventory is the source of truth.

### Useful analysis concepts found

Per T003 dramatica-flow section:

- Causal chain analysis
- Hook/foreshadowing/promise/mystery/conflict lifecycle tracking
- Emotional arc and character state tracking
- Relationship network and relationship-delta tracking
- Multi-thread timeline and thread activity
- Character knowledge / information boundaries (`KnownInfoRecord` with witnessed/hearsay/deduced/document sources in README example)
- Audit dimensions for causality, character, promises, relationships, timeline, and information-boundary consistency

### Prose-generation and revision risks found

Per T003:

- README_EN documents a 5-layer agent pipeline including Writer Agent (generates chapter text) and Reviser Agent
- API endpoints include `/ai-generate/chapter-content`, `/ai-rewrite-segment`, `/api/action/write`, `/api/action/revise`
- Product described as "AI-assisted novel writing platform"
- T002 hard blocker **B1** (generates or rewrites prose as core behavior): **triggered**

### License/source gaps

- MIT claimed via README badge; LICENSE file not retrieved from default GitHub raw paths (404)
- GitHub API returned `license: null`
- Risk: medium — confirm SPDX from repository LICENSE file before any code reuse

### Dependency/runtime risk

- Python 3.11+, FastAPI, multi-layer agent pipeline, LLM abstraction (DeepSeek API, Ollama local, OpenAI-compatible), Web UI SPA, 50+ REST endpoints
- High runtime footprint; not a lightweight NLP library
- T002 blocker **B6** (requires runtime dependency before approved review): triggered if installed as dependency

### World-state/truth-write risk

- Platform uses book/world-state JSON models and narrative-state APIs
- T002 blocker **B5** (cannot constrain to candidate-only output): triggered for runtime adapter — platform writes world_state/truth files
- High contamination risk if generation APIs are reachable

### Candidate-only feasibility limits

- Analysis dimensions map conceptually to Writer Assistant Core candidate types but no documented export to bounded candidate JSON
- Adapter would require custom mapping and strict exclusion of generation outputs
- Reference-only rubric/schema borrowing is feasible; runtime adapter is not

## 4. Safe Reference Concepts Accepted

### Accepted concept A: Causal chain analysis

**What dramatica-flow inspires:** cause/event/effect/decision relationship tracking and causality-gap diagnostics.

**Safe use in our app:**

- Inspire future causal-chain candidate rubrics
- Help classify cause/event/effect/decision relationships
- Support diagnostic questions about whether events have clear causes and consequences

**Candidate mappings:**

- `event_candidate`
- `action_candidate`
- `causal_link_candidate`
- `decision_candidate`
- `consequence_candidate`
- `timeline_event_candidate`

**Guardrail:**

- Do not generate missing events
- Do not continue the story
- Do not rewrite scenes
- Only analyze owner-authored material
- Store output only as candidates with evidence/provenance

### Accepted concept B: Foreshadowing / promise / mystery / conflict lifecycle

**What dramatica-flow inspires:** open narrative commitment tracking across hooks, promises, mysteries, and conflict follow-through.

**Safe use in our app:**

- Inspire future tracking of open narrative commitments
- Identify possible unresolved promises, mysteries, dropped threads, or conflict follow-through gaps

**Candidate mappings:**

- `plot_thread_candidate`
- `open_question_candidate`
- `unresolved_promise_candidate`
- `mystery_candidate`
- `continuity_warning_candidate`
- `dropped_thread_warning_candidate`

**Guardrail:**

- Do not propose new payoffs as prose
- Do not generate resolutions
- Ask diagnostic questions or create candidate warnings only

### Accepted concept C: Emotional arc/state tracking

**What dramatica-flow inspires:** character emotional state and shift tracking for consistency review.

**Safe use in our app:**

- Inspire character state and emotional-shift candidate categories
- Support consistency checks between scenes

**Candidate mappings:**

- `character_state_candidate`
- `emotional_shift_candidate`
- `arc_consistency_warning_candidate`
- `continuity_warning_candidate`

**Guardrail:**

- Do not write emotional beats
- Do not prescribe character development
- Only flag evidence-backed changes or inconsistencies

### Accepted concept D: Relationship network/delta tracking

**What dramatica-flow inspires:** relationship presence and relationship-change tracking over narrative time.

**Safe use in our app:**

- Inspire relationship and relationship-change candidates
- Support approved relationships page later

**Candidate mappings:**

- `relationship_candidate`
- `relationship_change_candidate`
- `alliance_conflict_candidate`
- `relationship_continuity_warning_candidate`

**Guardrail:**

- Do not create relationship canon automatically
- Do not infer relationships without evidence
- Owner approval required before canon

### Accepted concept E: Timeline and thread activity

**What dramatica-flow inspires:** multi-thread timeline activity and inactive-thread detection.

**Safe use in our app:**

- Inspire future timeline/thread activity candidate categories
- Detect possible inactive plot threads or scene-order tension

**Candidate mappings:**

- `timeline_event_candidate`
- `thread_activity_candidate`
- `dropped_thread_warning_candidate`
- `scene_order_warning_candidate`
- `causality_gap_candidate`

**Guardrail:**

- Do not reorganize the manuscript
- Do not insert scenes
- Do not rewrite timeline facts
- Candidate-only diagnostics

### Accepted concept F: Character knowledge / information boundaries

**What dramatica-flow inspires:** POV and knowledge-continuity checks using witnessed/hearsay/deduced/document-style evidence categories.

**Safe use in our app:**

- Inspire POV/knowledge continuity checks
- Identify possible information leaks where a character appears to know something unsupported by approved/owner-authored evidence

**Candidate mappings:**

- `character_knowledge_candidate`
- `information_boundary_warning_candidate`
- `pov_leak_warning_candidate`
- `continuity_warning_candidate`

**Guardrail:**

- Do not rewrite POV
- Do not decide canon automatically
- Show evidence and let owner decide

### Accepted concept G: Audit dimensions without revision loop

**What dramatica-flow inspires:** multi-dimension diagnostic audit reports without automatic revision.

**Safe use in our app:**

Inspire diagnostic dimensions for future analysis reports:

- causality consistency
- character consistency
- unresolved promises
- relationship continuity
- timeline consistency
- information boundary consistency

**Candidate mappings:**

- `continuity_warning_candidate`
- `contradiction_candidate`
- `causality_gap_candidate`
- `plot_thread_warning_candidate`
- `character_consistency_warning_candidate`

**Guardrail:**

- Keep audit diagnostics only
- Reject automatic revision
- Reject rewrite suggestions that create prose
- Use diagnostic questions instead

## 5. Unsafe Concepts Rejected

The following dramatica-flow behaviors are **rejected** for our app:

| Rejected concept | Why rejected |
| --- | --- |
| Writer Agent | Violates no-prose boundary; generates chapter text as core behavior |
| Reviser Agent | Violates no-rewrite boundary; automatic prose revision |
| Architect Agent when used to generate outlines/story content | Violates outline-as-truth and no-prose boundaries; bypasses owner review |
| Generated story outlines as project truth | Risks treating tool output as truth; bypasses owner review and OMI |
| Generated chapter outlines as project truth | Same as above; outline generation is not owner-authored canon |
| Generated chapter prose | Core B1 violation |
| Story continuation | Violates no-continuation boundary |
| Outline continuation as authored content | Treats generated outline as owner-authored material |
| Rewrite segment APIs (`/ai-rewrite-segment`, etc.) | Violates no-rewrite boundary |
| Revise action APIs (`/api/action/revise`, etc.) | Violates no-rewrite boundary |
| Automatic revision loops | Bypasses owner review; risks canon mutation through generated fixes |
| AI writing pipeline (5-layer agent stack) | Generation-heavy core product; incompatible with analysis-only app |
| Summary generation as truth | Risks treating summaries as durable story truth without owner approval |
| world_state writes | Risks canon mutation; B5 blocker for runtime adapter |
| truth-file mutation | Direct project-truth mutation outside OMI/owner promotion path |
| Automatic relationship/emotional/foreshadowing settlement into canon | Silent promotion; violates candidate-first and owner-review requirements |
| LLM backend switching for generation | Enables generation paths; remote LLM options add privacy risk |
| One-click book/chapter generation behavior | Core generation product behavior; B1 violation |

## 6. Candidate Pipeline Mapping

### Accepted future pattern

```text
owner-authored text
→ app-owned analysis adapter/rubric
→ normalized Writer Assistant Core candidate
→ source locator + evidence + provenance
→ OMI/candidate review
→ owner decision
→ future promotion only by explicit owner-approved apply-promotion path
```

### Rejected pattern

```text
owner text
→ dramatica-flow writer/reviser/continuation pipeline
→ generated outline/prose/world_state
→ canon/project truth
```

dramatica-flow may inform rubric vocabulary, diagnostic question templates, and candidate category design only when reimplemented inside app-owned code with evidence/provenance and owner review. It must never be invoked as a runtime pipeline.

## 7. Relationship to T005 and T006

- `PHASE8-IMPL-005-T005` will decide NCP/Subtxt structural interpretation boundaries for approved structural context, import/export, and semantic rubric use.
- `PHASE8-IMPL-005-T006` will decide first extraction strategy among spaCy, segram, BookNLP, GLiNER, LangExtract, Renard, and any reference-only concepts accepted in T004–T005.
- T004 does **not** decide final extraction strategy.
- T004 only decides dramatica-flow's safe reference boundary.

## 8. Future Implementation Requirements

Any future implementation inspired by dramatica-flow must:

- be reimplemented inside our app-owned codebase
- be tests-first in a future parent
- consume only owner-authored or owner-provided material
- produce only candidate records
- attach source locator/evidence/provenance
- pass no-prose/no-rewrite/no-continuation guardrails
- not call dramatica-flow runtime
- not install dramatica-flow
- not import dramatica-flow directly
- not mutate memory/canon
- not create or update NCP exports as truth
- not call Ollama/model unless a future model-assisted extraction parent explicitly authorizes it

Citation rule for future tasks: reference this decision document and T003 inventory evidence. Do not cite dramatica-flow README claims as validated runtime behavior without fresh official-source review in an authorized task.

## 9. Accepted Decision

**Decision:** ACCEPT dramatica-flow as reference-only analysis-pattern inspiration.

**Classification:** `reference-only`

**Runtime adapter status:** REJECT/DEFER.

**Generation/revision/continuation behavior:** REJECTED.

**Safe future use:** candidate-only diagnostic/rubric inspiration after app-owned implementation design.

**Accepted reference concepts (summary):**

- causal chain analysis
- foreshadowing / promise / mystery / conflict lifecycle
- emotional arc/state tracking
- relationship network/delta tracking
- timeline and thread activity
- character knowledge / information boundaries
- audit dimensions without revision loop

## 10. Open Follow-Ups

- **T005:** Decide how NCP/Subtxt handle approved structural context and semantic rubric boundaries.
- **T006:** Decide first extraction path and whether spaCy-first/manual-first/hybrid is preferred; dramatica-flow reference concepts may inform rubric design only if selected.
- **Future parent:** Define tests for causal-chain/open-question/relationship/timeline/information-boundary candidates if selected for implementation.
- **Future legal/dependency review:** Do not reuse dramatica-flow code unless LICENSE/source gaps from T003 are resolved.

## Safety Confirmation

- Docs/decision only.
- No dramatica-flow install, clone, execution, or demo.
- No external source retrieval in T004 beyond T003 inventory.
- No runtime code, tests, routes, UI, package changes, model calls, extraction implementation, training data, JSONL, dataset work, memory/canon mutation, staging, or commits.
