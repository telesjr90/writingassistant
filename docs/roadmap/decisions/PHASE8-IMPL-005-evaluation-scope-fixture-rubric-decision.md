# PHASE8-IMPL-005 Evaluation Scope, Fixture Plan, and Scoring Rubric Decision

## 1. Decision Identity

- Parent: `PHASE8-IMPL-005`
- Child: `PHASE8-IMPL-005-T002`
- Title: Evaluation scope, fixture plan, and scoring rubric decision
- Track: Writer Assistant Core
- Status: accepted
- Date: 2026-06-17
- Dependencies:
  - completed `PHASE8-IMPL-005-T001`
  - completed `PHASE8-IMPL-004`
  - `docs/roadmap/writer_assistant_core_candidate_schemas.md`
  - `docs/roadmap/tooling_decisions.md`
  - `docs/roadmap/optional_analysis_extractors.md`

## 2. Decision Summary

`PHASE8-IMPL-005-T002` defines the controlled evaluation framework for the nine approved tools/references before any extraction implementation. T002 does not evaluate tools, retrieve sources, install dependencies, create fixtures, or change runtime code.

Accepted outcomes:

- A bounded evaluation objective and scope for T003–T006.
- Provisional tool/reference grouping classes for evaluation planning only; final classification requires T003 official source evidence.
- A fixture category plan only; no fixture files are created in T002.
- A 0–5 scoring rubric with hard blockers and pass/fail gates.
- A T003 source inventory checklist for all nine scoped candidates.
- Adapter strategy implications that preserve candidate-only, evidence-backed, owner-approved workflow.

## 3. Evaluation Objective

Decide, using evidence from T003 onward, which of the nine scoped tools/references should be:

1. **Likely runtime adapter candidate** — reasonable first-path extraction support after owner-approved implementation parent.
2. **Possible runtime adapter candidate** — useful later or in hybrid path after additional screening.
3. **Reference-only** — informs schemas, rubrics, diagnostics, or adapter design without runtime dependency.
4. **Reject/defer** — blocked by safety, license, privacy, maintenance, or fit until a later owner-approved parent reintroduces it.

The evaluation must answer:

- Can the tool/reference support **candidate-only** Writer Assistant Core output with **evidence/provenance**?
- Can it operate within the app's **analysis-only** boundary?
- Is it compatible with **local-first/privacy** expectations after T003 screening?
- Does it fit the existing candidate schema and OMI review workflow?
- Which tool(s) should inform the **first extraction implementation path** decided in T006?

Tool output never becomes canon. Schema validity, extractor confidence, and reference interpretation do not prove story truth.

## 4. Evaluation Scope

In scope for T003–T006 evaluation of exactly nine candidates:

| # | Tool/Reference | Provisional evaluation role |
| --- | --- | --- |
| 1 | dramatica-flow | Analysis-pattern and continuity/reference review |
| 2 | Narrative Context Protocol | Structural schema/import-export reference |
| 3 | Subtxt docs | Semantic/Dramatica interpretation rubric reference |
| 4 | spaCy | Local NLP baseline candidate |
| 5 | segram | Semantic grammar/action-analysis reference |
| 6 | BookNLP | Long-form literary extraction candidate |
| 7 | GLiNER | Custom/zero-shot entity extraction candidate |
| 8 | LangExtract | Evidence-grounded structured extraction reference |
| 9 | Renard | Character-network and relationship extraction reference |

Evaluation dimensions cover:

- Analysis-only safety and prose-generation risk.
- Evidence/provenance support and candidate schema fit.
- Supported story-knowledge categories (see Section 6 fixture categories).
- Local-first/privacy fit, dependency/runtime cost, license/adoption risk, maintainability.
- Output determinism/normalizability and integration complexity.
- OMI candidate-only workflow fit and first-extraction-path suitability.

Evaluation artifacts are documentation only until a future implementation parent explicitly authorizes runtime work.

## 5. Non-Scope

Explicitly excluded from this evaluation parent unless a later owner-approved parent reintroduces them:

- CoreNLP / OpenIE / SUTime
- AI-Reader-V2
- narrative-blueprint
- NovelClaw
- NotebookLM workflow
- llm_finetuning
- ai-llm-project-file-structure-template
- Dramatron, ai-story-writer, Inkos, and other generation-heavy story-engine systems
- Any tool not listed in the nine scoped candidates

T002 also excludes:

- Official source retrieval (deferred to T003).
- Tool installs, clones, demos, executions, and model calls.
- Runtime extraction adapters, routes, UI, apply-promotion, and memory/canon mutation.
- Fixture file creation, training data, JSONL records, and dataset manifest entries.
- Memory-based tool classification without T003 source evidence.
- Generated, rewritten, continued, polished, or imitated story prose.

## 6. Tool/Reference Grouping

These are **provisional evaluation classes** for planning T003–T006. They are not final classifications. T003 must verify each tool's actual capabilities, boundaries, and risks from official docs/repos/primary sources before T004–T006 use them for decisions.

### 6.1 Structural/reference candidates

Purpose: guide approved structural context, schema shape, import/export boundaries, and interpretation rubrics without becoming automatic truth.

| Tool/Reference | Provisional placement | T003 must verify |
| --- | --- | --- |
| Narrative Context Protocol | Primary structural/reference class | Schema scope, license, import/export behavior, owner-approval implications |
| Subtxt docs | Primary structural/reference class | Interpretation rubric scope, terminology boundaries, analysis-only use |
| dramatica-flow | Secondary structural/reference class | Which features are analysis/reference vs generation/revision/continuation |

### 6.2 NLP/entity extraction candidates

Purpose: deterministic or model-backed named-entity and literary element extraction from owner-authored or fixture text.

| Tool/Reference | Provisional placement | T003 must verify |
| --- | --- | --- |
| spaCy | Primary NLP/entity extraction class | NER, tokenization, dependency parsing, rule/matcher support, local/offline feasibility |
| BookNLP | Primary NLP/entity extraction class | Character, alias, quote, event extraction; long-document pipeline; runtime requirements |
| GLiNER | Primary NLP/entity extraction class | Custom entity labels, model requirements, confidence thresholds, local feasibility |

### 6.3 Linguistic/graph/semantic extraction candidates

Purpose: semantic action analysis, relationship graphs, and narrative-structure signals beyond basic NER.

| Tool/Reference | Provisional placement | T003 must verify |
| --- | --- | --- |
| segram | Primary linguistic/graph/semantic class | spaCy dependency, supported tasks, fiction/story applicability, maturity |
| Renard | Primary linguistic/graph/semantic class | Static/dynamic character networks, relationship extraction, pipeline modularity |

### 6.4 LLM-assisted extraction candidates

Purpose: schema-guided or source-grounded extraction that may require model/provider calls and needs strict candidate-only constraints.

| Tool/Reference | Provisional placement | T003 must verify |
| --- | --- | --- |
| LangExtract | Primary LLM-assisted extraction class | Provider/model requirements, local model support, source grounding, privacy risks |
| dramatica-flow | Possible secondary LLM-assisted class | Whether agent/pipeline behavior includes model-backed generation or rewrite paths |

### 6.5 Story/continuity/reference candidates

Purpose: continuity, contradiction, plot-thread, timeline, causality, and open-question diagnostics without prose generation or canon mutation.

| Tool/Reference | Provisional placement | T003 must verify |
| --- | --- | --- |
| dramatica-flow | Primary story/continuity/reference class | Safe analysis dimensions vs unsafe writer/reviser/continuation behavior |
| Subtxt docs | Secondary story/continuity/reference class | Source-of-conflict and author-level interpretation guidance only |

### 6.6 Grouping rules

- A tool may appear in more than one provisional class until T003 narrows it.
- Reference/docs-only sources may score highly on rubric dimensions for **reference value** while scoring low on **runtime adapter feasibility**.
- T004 focuses on dramatica-flow within the story/continuity/reference and structural classes.
- T005 focuses on NCP and Subtxt within the structural/reference class.
- T006 compares spaCy, segram, BookNLP, GLiNER, LangExtract, and Renard using the full rubric after T003 inventory.

## 7. Fixture Plan

T002 defines **fixture categories only**. No fixture files are created in T002. Fixture creation, if authorized later, must follow this plan.

### 7.1 Fixture policy

- Prefer **owner-authored safe fixture text** or **clearly public-domain-safe text**.
- Do **not** use raw copyrighted book source text.
- Do **not** treat fixture outputs as story truth; outputs remain **candidate-only**.
- Do **not** add fixture files to training data, JSONL records, or `dataset_manifest.json`.
- Fixture text is evaluation input only, not canon, not approved memory, and not OMI truth.
- Short excerpts are preferred over full manuscripts for early evaluation.
- Evidence spans in evaluation outputs must reference fixture source locators, not invented prose.

### 7.2 Proposed fixture categories

Each category maps to Writer Assistant Core candidate types in `docs/roadmap/writer_assistant_core_candidate_schemas.md` and to one or more evaluation passes.

| Fixture category | Target candidate types | Minimum evaluation intent |
| --- | --- | --- |
| F1 — Character extraction | `character_candidate` | Named characters, aliases, role hints, evidence spans |
| F2 — Location/setting extraction | `location_candidate` | Places, settings, hierarchy hints, scene linkage |
| F3 — Object/item extraction | `object_candidate` | Artifacts, props, owned objects, holder hints |
| F4 — Organization/group extraction | `organization_candidate` | Groups, factions, memberships, affiliations |
| F5 — Scene/event/action extraction | `timeline_event_candidate`, scene/event review fields | Actions, events, participants, scene boundaries |
| F6 — Timeline/causality extraction | `timeline_event_candidate`, causality notes | Ordering, before/after, cause/effect candidates |
| F7 — Relationship extraction | `relationship_candidate` | Subject/object pairs, relationship labels, network edges |
| F8 — Plot-thread/open-question extraction | `plot_thread_candidate`, `open_question_candidate` | Open threads, unresolved questions, payoff hints |
| F9 — Continuity/contradiction extraction | `continuity_warning_candidate`, `contradiction_candidate` | Conflicts, inconsistencies, affected candidate links |
| F10 — Evidence/provenance attachment | all candidate types | Source locators, excerpts, offsets/lines, `quote_exact`, provenance metadata |
| F11 — No-prose-generation behavior | n/a (negative test) | Tool must not emit replacement/bridge/continuation prose as primary output |
| F12 — Candidate-only output normalization | all candidate types | Output maps to bounded candidate schema without canon writes |

### 7.3 Recommended fixture shapes (categories, not files)

| Shape ID | Description | Suggested use |
| --- | --- | --- |
| S1 — Short scene bundle | 2–4 short scenes with overlapping entities | F1–F7, F10–F12 |
| S2 — Alias/coreference bundle | Same entity referenced under multiple names | F1, F7, F10 |
| S3 — Timeline tension bundle | Events with explicit and implicit ordering | F5, F6, F8 |
| S4 — Continuity conflict bundle | Deliberate inconsistency for contradiction screening | F9, F10 |
| S5 — Minimal structural rubric bundle | Outline/metadata-only inputs for reference tools | Structural/reference class review in T004–T005 |

Future fixture work may reuse existing public-domain project examples only if they remain license-safe and are not treated as canon. T002 does not create or modify any fixture files.

### 7.4 Fixture gating for later evaluation

Before any tool is scored against fixtures in a future authorized task:

1. T003 source inventory must be complete for that tool.
2. Fixture category coverage must map to the tool's provisional class.
3. A no-prose negative check (F11) must be included for any runtime adapter candidate.
4. Normalized outputs must be reviewable as candidate records with evidence/provenance (F10, F12).

## 8. Scoring Rubric

### 8.1 Scale

Each rubric dimension uses **0–5**:

| Score | Meaning |
| --- | --- |
| 0 | Unknown/unverified — default until T003 evidence exists |
| 1 | Poor / high risk / strong blocker tendency |
| 2 | Weak / major gaps |
| 3 | Acceptable with significant conditions |
| 4 | Good fit with minor conditions |
| 5 | Strong fit for intended evaluation role |

Scores of 0 are expected for T002. T003 fills license/dependency/runtime facts; T004–T006 assign non-zero scores using evidence.

### 8.2 Rubric dimensions

| ID | Dimension | What it measures |
| --- | --- | --- |
| D1 | Analysis-only safety | Can the tool/reference be constrained to analysis, labeling, extraction, and diagnostics only? |
| D2 | Prose-generation risk (inverse) | 5 = lowest risk; 0 = unknown; 1 = core behavior generates/rewrites/continues prose |
| D3 | Evidence/provenance support | Can outputs cite source spans, locators, excerpts, or grounding metadata? |
| D4 | Candidate schema fit | Can outputs normalize to Writer Assistant Core bounded candidate types? |
| D5 | Supported story-knowledge categories | Coverage of F1–F9 fixture categories relevant to the tool's class |
| D6 | Local-first/privacy fit | Offline/local execution feasibility; data leaving the machine |
| D7 | Dependency/runtime cost (inverse) | 5 = lightest practical cost; 1 = heavy GPU/model/service burden |
| D8 | License/adoption risk (inverse) | 5 = clear compatible license; 1 = unclear/incompatible license |
| D9 | Maintainability | Active maintenance, release cadence, documentation quality |
| D10 | Output determinism/normalizability | Stable, testable, adapter-normalizable outputs |
| D11 | Integration complexity (inverse) | 5 = simplest adapter boundary; 1 = deeply invasive integration |
| D12 | OMI candidate-only workflow fit | Supports review, rejection, revision, and promotion gating without silent canon writes |
| D13 | First extraction path suitability | Usefulness as manual-first, rule-based, local NLP, model-assisted, or hybrid first step |

### 8.3 Weighting guidance

| Evaluation path | Primary dimensions |
| --- | --- |
| Reference-only decision (T004–T005) | D1, D2, D3, D8, D12 |
| Runtime adapter comparison (T006) | D1–D7, D10–D13 |
| Privacy/local-first gate | D6, D7, D8 |
| Evidence-first gate | D3, D4, D10, D12 |

No weighted total is computed in T002. T006 may compute a documented comparison matrix using these dimensions after T003 evidence exists.

### 8.4 Hard blockers

Any confirmed hard blocker forces classification to **reject/defer** for runtime adapter use unless the owner explicitly approves a constrained reference-only role in T004–T005.

| Blocker ID | Condition |
| --- | --- |
| B1 | Generates or rewrites prose as core behavior |
| B2 | Cannot preserve evidence/provenance for extracted claims |
| B3 | Requires unacceptable remote/private data transfer for normal operation |
| B4 | Unclear or incompatible license for intended use |
| B5 | Cannot be constrained to candidate-only output |
| B6 | Requires runtime dependency adoption before approved review and strategy decision |

Hard blockers must be evidenced from T003 official sources, not memory.

### 8.5 Pass/fail gates

| Gate | Requirement |
| --- | --- |
| G1 — Source evidence | T003 inventory complete for the tool before non-zero rubric scoring |
| G2 — Safety minimum | Runtime adapter candidates must score **D1 ≥ 4** and **D2 ≥ 4** after T003–T006 review |
| G3 — Evidence minimum | Runtime adapter candidates must score **D3 ≥ 3**, **D4 ≥ 3**, **D10 ≥ 3** |
| G4 — Workflow minimum | All scoped tools must score **D12 ≥ 3** or be classified reference-only/reject |
| G5 — No hard blockers | No B1–B6 confirmed for runtime adapter adoption |
| G6 — Owner approval | Implementation remains blocked until T007 closeout and future implementation parent |
| G7 — Reference-only path | Tools may pass as reference-only with G1 + documented safe subset even if D13 is low |

Fail any G2–G5 gate for runtime adapter candidacy → classify as reference-only or reject/defer.

## 9. Evidence/Source Collection Plan for T003

T003 is the **first child allowed to retrieve official source information**. T002 does not collect sources. T003 must collect the inventory defined in Section 10 for all nine scoped candidates using only the official URLs recorded in `PHASE8-IMPL-005.enrichment.json` `official_source_retrieval_policy.official_targets`.

T003 output artifact (future): source inventory document or structured inventory section added to roadmap docs. T003 must not write runtime code.

T003 classification output per tool:

- likely runtime adapter candidate
- possible runtime adapter candidate
- reference-only
- reject/defer

Each classification requires: cited source evidence, identified risks, hard-blocker screening result, and prerequisites before any implementation parent.

## 10. T003 Source Inventory Requirements

For **each** of the nine scoped candidates, T003 must collect:

| Field | Required content |
| --- | --- |
| Official documentation URL or official repository | Primary authoritative link(s) from enrichment JSON targets |
| License | SPDX or stated license terms from official source |
| Dependency footprint | Runtime deps, model deps, optional extras, approximate install weight |
| Runtime requirements | Python version, GPU/CPU, OS constraints, external services |
| Local vs remote execution | Whether normal operation is offline/local, hybrid, or remote-only |
| Text/prose generation | Whether the tool generates, rewrites, continues, or outlines prose |
| Expected input/output shapes | Documented inputs and outputs relevant to extraction/adapters |
| Evidence/provenance support | Source grounding, span citation, attribution, or traceability features |
| Maintenance status | Recent activity, release status, archived/unmaintained signals |
| Adapter feasibility | How cleanly outputs could map to candidate schema + evidence model |
| Privacy/local-first concerns | Data egress, telemetry, cloud API requirements, credential needs |

T003 must also record:

- Provisional class confirmation or reclassification vs Section 6.
- Hard blocker screening (B1–B6) with source citations.
- Initial rubric scores where evidence supports non-zero values; otherwise leave 0/unknown.

## 11. Safety, License, and Privacy Screening Dimensions

T003 executes screening; T002 defines the dimensions:

| Screen | Questions |
| --- | --- |
| No-prose | Does the tool write, rewrite, continue, polish, or imitate story prose? |
| Candidate-only | Can outputs be stored as candidates without silent canon/memory mutation? |
| Owner approval | Can the app preserve owner review before durable truth? |
| License | Is license compatible with local adapter use and redistribution constraints? |
| Privacy | Does normal use send owner text to third-party services? |
| Local-first | Can evaluation and likely MVP usage run on owner-controlled hardware? |
| Dependency risk | Are dependencies maintained, auditable, and proportionate? |
| Evidence integrity | Can claims be tied to source spans/locators? |
| OMI alignment | Can outputs flow through OMI review and promotion gates? |
| Generation-as-truth | Does the tool promote outlines, summaries, or labels as automatic truth? |

Any screen failure must be documented with official source evidence and mapped to rubric dimensions and hard blockers.

## 12. Adapter Strategy Implications

Accepted adapter principles:

1. **App-owned orchestration** — External tools are replaceable adapters around Writer Assistant Core, not replacements for candidate schema, evidence model, or OMI review.
2. **Candidate-only boundary** — Adapter output normalizes to `writer_assistant/candidates/{candidate_id}.json`; never writes memory/canon, bible, storyform, scenes, or promotions directly.
3. **Evidence first** — Adapters must attach or enable evidence spans and provenance compatible with `docs/roadmap/writer_assistant_core_candidate_schemas.md`.
4. **Reference vs runtime split** — dramatica-flow, NCP, and Subtxt docs may inform rubrics/schemas even if they never become runtime dependencies.
5. **Staged adoption** — No package installs until after T007 strategy closeout and a dedicated implementation parent.
6. **First path options for T006** — manual-first, rule-based, local NLP, model-assisted, or hybrid; T002 does not choose among them.
7. **Negative adapter tests** — Future adapter evaluation must include F11 no-prose and F12 candidate-only normalization checks.

Future documentation-only module shape remains as recorded in `docs/roadmap/tooling_decisions.md`; T002 does not create modules.

## 13. How Evaluation Supports T004–T006

| Child | Uses T002 outputs |
| --- | --- |
| T003 | Section 10 inventory checklist; Section 6 provisional classes; Section 8 rubric with 0/unknown baseline; Section 11 screening dimensions |
| T004 | dramatica-flow provisional classes; D1/D2/D12 and B1/B5; story/continuity fixture categories F8–F9; reference-only vs adapter gate G7 |
| T005 | NCP/Subtxt structural classes; schema/import-export screening; S5 structural rubric bundle; no auto-truth and owner-approval gates |
| T006 | Full rubric D1–D13; NLP/semantic/LLM classes; fixture categories F1–F12; comparison matrix for spaCy, segram, BookNLP, GLiNER, LangExtract, Renard; first extraction path decision |
| T007 | Summarize accepted strategy, deferred tools, and next implementation parent scope |

T004–T006 must not score tools from memory alone. T003 evidence is mandatory for non-zero rubric values and final classifications.

## 14. Deferred Decisions

Remaining for later children:

1. Final tool classifications after T003 official source review.
2. Whether dramatica-flow is reference-only, partial adapter, or rejected (T004).
3. NCP import/export and Subtxt rubric strategy without auto-truth (T005).
4. First extraction implementation path: manual-first, rule-based, local NLP, model-assisted, or hybrid (T006).
5. Actual fixture file creation and storage location.
6. Adapter module implementation and orchestrator design.
7. Extraction trigger policy (automatic vs manual vs batch).
8. Package:threshold for UI surfacing of candidates.
9. Package/dependency adoption and spike branch authorization.
10. Apply-promotion, memory/canon mutation, routes, and UI.

## 15. Safety and Product Boundaries

- The app remains analysis-only.
- Standard refusal message unchanged: `I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`
- Candidates are not canon.
- Tool output does not prove story truth.
- Promotion records remain audit-only until future apply-promotion exists.
- T002 creates documentation only: no runtime code, tests, fixtures, training data, source retrieval, tool execution, model calls, staging, or commits.
