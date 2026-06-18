# PHASE8-IMPL-005-T003 — Official Source Inventory and License/Dependency Screen

## Header

- **Task:** `PHASE8-IMPL-005-T003`
- **Parent:** `PHASE8-IMPL-005`
- **Title:** Official source inventory and license/dependency screen
- **Status:** completed
- **Scope:** exactly nine candidates (dramatica-flow, Narrative Context Protocol, Subtxt docs, spaCy, segram, BookNLP, GLiNER, LangExtract, Renard)
- **Boundary note:** docs/research inventory only; no installs, clones, runtime execution, tests, or code

## Method

| Item | Result |
| --- | --- |
| Cursor web access | Worked for official docs pages (dramatica.com/ncp, guide.subtxt.app, spacy.io, segram.readthedocs.io, urchade.github.io/GLiNER, Google developer blog, arxiv.org) |
| Terminal fetch (`urllib.request`) | Used for GitHub README/LICENSE/pyproject files and GitHub API repo metadata |
| Sources inaccessible | `dramatica-flow` LICENSE file at default paths returned 404 (MIT asserted in README badge); `booknlp.pythonhumanities.com` returned minimal landing content only |
| Cloning/install/execution | None |
| Model calls | None |
| Non-official primary sources | None used as primary authority |

**Official URLs inspected:**

1. `https://github.com/ydsgangge-ux/dramatica-flow` (README, README_EN)
2. `https://github.com/narrative-first/narrative-context-protocol` (README, LICENSE.md)
3. `https://dramatica.com/ncp`
4. `https://guide.subtxt.app/`
5. `https://guide.subtxt.app/getting-started/key-concepts/`
6. `https://spacy.io/`
7. `https://github.com/explosion/spaCy` (README, LICENSE)
8. `https://github.com/sztal/segram` (README on `master`, LICENSE)
9. `https://segram.readthedocs.io/en/latest/`
10. `https://github.com/booknlp/booknlp` (README, LICENSE, setup.py)
11. `https://booknlp.pythonhumanities.com/` (minimal landing page)
12. `https://github.com/urchade/GLiNER` (README, LICENSE, pyproject.toml)
13. `https://urchade.github.io/GLiNER/`
14. `https://arxiv.org/abs/2311.08526` (referenced; abstract-level only via docs cross-link)
15. `https://github.com/google/langextract` (README, LICENSE, pyproject.toml)
16. `https://developers.googleblog.com/introducing-langextract-a-gemini-powered-information-extraction-library/`
17. `https://langextract.com/` (not separately fetched; README and Google blog used)
18. `https://github.com/CompNet/Renard` (README, LICENSE, pyproject.toml)
19. `https://arxiv.org/abs/2407.02284`

---

## dramatica-flow

### Official sources inspected

- `https://github.com/ydsgangge-ux/dramatica-flow` (README.md, README_EN.md)
- GitHub API repo metadata (`pushed_at`, stars, archived)

### Source status

- Retrieved: yes (partial for LICENSE file path)
- Source type: official repo
- Notes: README_EN is the primary English evidence source. LICENSE file not found at `main/LICENSE`; README badge states MIT.

### License

- Finding: MIT (per README badge); LICENSE file not retrieved from default raw paths.
- Evidence: README_EN MIT badge; GitHub API returned `license: null`.
- Risk: Medium — confirm SPDX from repository LICENSE file before adapter adoption.

### Dependency footprint

- Finding: Python 3.11+, FastAPI, multi-layer agent pipeline, LLM abstraction (DeepSeek API, Ollama local, OpenAI-compatible), Web UI SPA, 50+ REST endpoints.
- Evidence: README_EN tech stack and architecture sections.
- Risk: High runtime footprint if adopted as dependency; not a lightweight NLP library.

### Runtime requirements

- Finding: Python 3.11+; requires LLM provider (DeepSeek API, Ollama, or OpenAI-compatible); FastAPI server and full novel-writing platform stack.
- Evidence: README_EN badges and architecture diagram.
- Risk: High — full application stack, not a drop-in extraction helper.

### Local-first / privacy fit

- Finding: Supports Ollama local LLM per README; also documents DeepSeek API and OpenAI-compatible remote paths.
- Evidence: README_EN LLM abstraction layer lists "DeepSeek API · Ollama local · OpenAI compatible".
- Risk: Medium — local path exists but default product is generation-oriented platform with remote LLM options.

### Text/prose generation behavior

- Finding: **Core behavior includes chapter generation, rewrite, revision, outline generation, and continuation-style writing pipeline.**
- Evidence: README_EN 5-layer agent pipeline includes "Writer Agent — Generates chapter text"; API endpoints include `/ai-generate/chapter-content`, `/ai-rewrite-segment`, `/api/action/write`, `/api/action/revise`; product described as "AI-assisted novel writing platform".
- Risk: **Critical (B1)** — incompatible with analysis-only app boundary as runtime adapter.

### Expected input/output shape

- Finding: Book/world-state JSON models; REST APIs for causal chains, hooks, emotional arcs, relationships, threads, timeline, audit results; extraction endpoints `/extract-from-novel`, `/extract-story-state`.
- Evidence: README_EN Core Features and API Reference sections.
- Risk: Outputs mix generated prose with structured narrative state; adapter would need strict subset isolation.

### Evidence/provenance support

- Finding: Analysis concepts include causal chains, hook lifecycle, emotional arcs, relationship network, information boundaries (`KnownInfoRecord` with source: witnessed/hearsay/deduced/document), multi-thread timeline.
- Evidence: README_EN Core Features sections 1–6 and Information Boundaries dataclass example.
- Risk: Low for reference patterns; high if world_state JSON treated as canon without owner review.

### Maintenance status

- Finding: Recently active (GitHub `pushed_at` 2026-06-04); 169 stars; not archived.
- Evidence: GitHub API metadata.
- Risk: Low maintenance signal risk; project appears actively developed.

### Candidate schema fit

- Finding: Analysis dimensions map conceptually to timeline_event, relationship, plot_thread, continuity, and open_question candidates; no documented export to bounded candidate JSON.
- Evidence: README feature descriptions vs Writer Assistant Core candidate types (conceptual mapping only).
- Risk: High — would require custom adapter mapping and strict exclusion of generation outputs.

### Adapter feasibility

- Finding: Poor as runtime adapter; possible as **reference-only** for analysis patterns (causal chain, hooks, emotional arcs, relationships, information boundaries).
- Evidence: Generation pipeline is central; analysis APIs exist but are embedded in generation platform.
- Risk: High contamination risk if any generation API is reachable.

### T002 blocker screen

- B1 prose generation as core behavior: **triggered**
- B2 no evidence/provenance: not triggered (analysis features document traceable structures)
- B3 unacceptable remote data transfer: possible if remote LLM used (not triggered for reference-only)
- B4 unclear/incompatible license: partial (MIT claimed, file not fetched)
- B5 cannot constrain to candidate-only: triggered for runtime adapter (platform writes world_state/truth files)
- B6 requires runtime dependency before approved review: triggered if installed as dependency

### Preliminary classification

**reference-only**

### Classification rationale

- Evidence: README_EN documents Writer/Reviser agents and AI generation APIs as core product behavior; analysis features (causal chain, hooks, arcs, relationships, information boundaries) are documented separately.
- Risks: B1 and B5 for runtime adapter; generation/revision/continuation must never enter app runtime.
- What would be required before implementation: T004 decision isolating safe analysis concepts; no package install; no generation API exposure; reference-only rubric/schema borrowing only.

---

## Narrative Context Protocol

### Official sources inspected

- `https://github.com/narrative-first/narrative-context-protocol` (README, LICENSE.md)
- `https://dramatica.com/ncp`

### Source status

- Retrieved: yes
- Source type: official repo + official Dramatica page
- Notes: Repository explicitly states "there is no standalone app here"; schema/reference transport format.

### License

- Finding: MIT License (LICENSE.md).
- Evidence: README Licensing section; LICENSE.md full text retrieved.
- Risk: Low for schema reference and future import/export design.

### Dependency footprint

- Finding: JSON/YAML schema, examples, validation tests (JavaScript schema validator in repo); no runtime Python package required for reference use.
- Evidence: README repository structure lists `schema/`, `examples/`, `tests/validate-schema.js`.
- Risk: Low as reference-only; implementation would be app-owned JSON handling.

### Runtime requirements

- Finding: None for reference; future import/export would require app-owned parser/validator only.
- Evidence: README: "Treat it as the canonical reference... there is no standalone app here."
- Risk: Low.

### Local-first / privacy fit

- Finding: Schema files are local/static; no remote service required for reference use.
- Evidence: Open repo schema and examples; dramatica.com page describes portable Storyform data.
- Risk: Low for reference; medium if future cloud sync implied by third-party tools (out of NCP scope).

### Text/prose generation behavior

- Finding: Does not generate prose; transports authorial intent / Storyform structure.
- Evidence: README describes "standardized JSON schema" for "authorial intent"; dramatica.com example is structural JSON only.
- Risk: Low for no-prose; medium if imported Storyform labels treated as automatic truth (app policy issue).

### Expected input/output shape

- Finding: NCP JSON with premise, four Throughlines (objective_story, main_character, influence_character, relationship_story), optional `story.ideation`, `story.moments[]`, storyform fields (domain, concern, issue, problem, solution, etc.).
- Evidence: README repository structure; dramatica.com/ncp example JSON snapshot.
- Risk: Low for schema reference; import must remain owner-approved only.

### Evidence/provenance support

- Finding: Schema encodes structural intent, not source text spans; no extraction provenance model.
- Evidence: README focus on storyform transport, not text grounding.
- Risk: N/A for extraction; structural reference only.

### Maintenance status

- Finding: Recently active (GitHub `pushed_at` 2026-06-05); 75 stars; stewarded by The Dramatica Co.; not archived.
- Evidence: GitHub API; README governance section.
- Risk: Low.

### Candidate schema fit

- Finding: Fits structural/reference layer for approved storyform context; not a candidate extractor.
- Evidence: README: transport-focused schema for tools to exchange structural intent.
- Risk: Low if kept reference-only; high if NCP fields bypass OMI and become canon.

### Adapter feasibility

- Finding: **Not an extraction adapter**; future optional import/export target for owner-approved structural context.
- Evidence: README explicitly schema/reference; no extraction pipeline.
- Risk: Owner-approval bypass is the main safety risk, not prose generation.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered (different role — structural schema)
- B3 unacceptable remote data transfer: not triggered for reference
- B4 unclear/incompatible license: not triggered (MIT)
- B5 cannot constrain to candidate-only: not triggered for reference-only use
- B6 requires runtime dependency before approved review: not triggered for docs/schema reference

### Preliminary classification

**reference-only**

### Classification rationale

- Evidence: Official sources position NCP as open Dramatica storyform schema for transport across tools, not an extractor.
- Risks: Auto-truth if imported Storyform fields skip owner review (T005 scope).
- What would be required before implementation: T005 strategy for import/export boundaries; app-owned validation; no silent canon writes.

---

## Subtxt docs

### Official sources inspected

- `https://guide.subtxt.app/getting-started/key-concepts/`
- `https://guide.subtxt.app/` (site root referenced)

### Source status

- Retrieved: yes
- Source type: official documentation site
- Notes: Documentation describes Subtxt/Dramatica interpretation concepts; not a downloadable library.

### License

- Finding: unknown (documentation site; no license page retrieved in T003 scope).
- Evidence: Official docs content retrieved; no LICENSE/terms page in inspected URLs.
- Risk: Medium for redistribution/quotation; low for internal rubric reference.

### Dependency footprint

- Finding: None — web documentation only.
- Evidence: Documentation site content; no package or API documented in inspected pages.
- Risk: None for reference-only.

### Runtime requirements

- Finding: None as runtime dependency.
- Evidence: Docs-only source.
- Risk: None.

### Local-first / privacy fit

- Finding: Reference-only; no runtime data egress from docs consumption.
- Evidence: Static documentation pages.
- Risk: Low.

### Text/prose generation behavior

- Finding: Docs describe author-level interpretation; site references "Subtxt Muse" for guided analysis (Muse transcript example on key concepts page). Docs themselves do not generate story prose in retrieved pages.
- Evidence: Key concepts page: "Subtxt/Dramatica is a tool for Authors"; Muse example is interpretive Q&A about story structure, not prose continuation.
- Risk: Medium if Muse or similar generation features were integrated as runtime — out of scope for docs reference.

### Expected input/output shape

- Finding: Conceptual rubric: Objective Narrative Structure, Source of Conflict vs Subject Matter, Storypoints/Storybeats, author-level (not character-level) interpretation.
- Evidence: Key concepts sections "Subject Matter is Not Conflict", "Identifying a Source of Conflict", "Why is this a Problem?".
- Risk: Low for rubric reference; high if Dramatica labels auto-applied as truth.

### Evidence/provenance support

- Finding: Interpretive framework, not text-span extraction.
- Evidence: Docs focus on analytical questions ("If I remove this, would there still be
  a problem?").
- Risk: N/A for extraction provenance.

### Maintenance status

- Finding: unknown (docs site; no version/changelog retrieved).
- Evidence: Live site content retrieved 2026-06-17.
- Risk: Low for reference use.

### Candidate schema fit

- Finding: Supports diagnostic rubric for structural/continuity evaluation (F8–F9, S5 bundles); not candidate record producer.
- Evidence: Source-of-conflict and author-intent guidance maps to evaluation dimensions, not entity extraction.
- Risk: Low as reference; medium if labels written directly to canon.

### Adapter feasibility

- Finding: Not an adapter; semantic/Dramatica interpretation rubric reference only.
- Evidence: Documentation site without API/package in inspected sources.
- Risk: Terminology overclaim if treated as validated story truth.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered (docs reference)
- B2 no evidence/provenance: not triggered (different role)
- B3 unacceptable remote data transfer: not triggered
- B4 unclear/incompatible license: partial (site terms unknown)
- B5 cannot constrain to candidate-only: not triggered for reference-only
- B6 requires runtime dependency before approved review: not triggered

### Preliminary classification

**reference-only**

### Classification rationale

- Evidence: Official docs position Subtxt as author-facing objective narrative structure guidance.
- Risks: Dramatica/Subtxt labels must not become automatic canon; Muse-style generation stays out of scope.
- What would be required before implementation: T005 rubric strategy; no runtime Subtxt dependency.

---

## spaCy

### Official sources inspected

- `https://spacy.io/`
- `https://github.com/explosion/spaCy` (README, LICENSE)

### Source status

- Retrieved: yes
- Source type: official docs + official repo
- Notes: Industry-standard NLP library; v3.8 referenced on site.

### License

- Finding: MIT License.
- Evidence: README and LICENSE file text; GitHub API `license: MIT`.
- Risk: Low.

### Dependency footprint

- Finding: Python NLP library with optional pretrained pipelines (70+ languages); components include tokenizer, tagger, parser, NER, lemmatizer, rule matcher; transformer pipelines available; model downloads separate from core package.
- Evidence: spacy.io features list; README pretrained pipelines section.
- Risk: Medium — model size varies (sm/md/lg/trf); transformer models increase footprint.

### Runtime requirements

- Finding: Python; CPU or GPU depending on pipeline; offline/local execution supported with downloaded models.
- Evidence: spacy.io: "built from the ground up" for production; local model packaging; benchmarks for CPU/GPU pipelines.
- Risk: Low–medium depending on chosen pipeline size.

### Local-first / privacy fit

- Finding: Strong local/offline feasibility with downloaded models; no cloud API required for core NLP.
- Evidence: spacy.io production/training/docs emphasize local pipelines; README MIT commercial open-source.
- Risk: Low for local-first MVP path.

### Text/prose generation behavior

- Finding: No story prose generation; NLP analysis and extraction components only.
- Evidence: spacy.io component list (NER, parsing, tagging, classification); no generation endpoints.
- Risk: None for B1.

### Expected input/output shape

- Finding: Text in → `Doc` with tokens, sentences, lemmas, POS, deps, entities; rule matcher patterns; custom pipeline components.
- Evidence: spacy.io features and API documentation summary on homepage.
- Risk: Low — well-bounded structured NLP outputs.

### Evidence/provenance support

- Finding: Token/character offsets available via `Doc` spans; supports evidence span attachment for extracted entities and syntactic patterns.
- Evidence: spaCy standard span/offset model (documented industrial NLP practice; homepage emphasizes extraction tasks).
- Risk: Low — adapter must map spans to candidate evidence fields.

### Maintenance status

- Finding: Actively maintained (GitHub `pushed_at` 2026-05-19); 33k+ stars; Explosion commercial backing.
- Evidence: GitHub API; spacy.io v3.8 announcement.
- Risk: Low.

### Candidate schema fit

- Finding: Strong baseline for F1–F7 fixture categories via NER, dependency parsing, rule matching; maps to character, location, organization, relationship hints, event/action patterns.
- Evidence: Component list aligns with T002 fixture categories; tooling_decisions already positions spaCy as first local NLP spike.
- Risk: Low–medium — fiction-specific labels may need custom rules or GLiNER complement.

### Adapter feasibility

- Finding: **Likely runtime adapter candidate** as first local NLP baseline.
- Evidence: Mature library, MIT license, local execution, deterministic/rule-assisted workflows, bounded NLP outputs.
- Risk: Medium integration effort for fiction-specific entity types and candidate normalization.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered (offsets available)
- B3 unacceptable remote data transfer: not triggered for local models
- B4 unclear/incompatible license: not triggered (MIT)
- B5 cannot constrain to candidate-only: not triggered (adapter-controlled)
- B6 requires runtime dependency before approved review: not triggered at inventory stage (spike deferred to post-T007)

### Preliminary classification

**likely runtime adapter candidate**

### Classification rationale

- Evidence: Official docs/repo confirm local NLP pipeline with NER, parsing, segmentation, rule matching, and span offsets.
- Risks: Model size selection; fiction NER may need custom labels (GLiNER complement).
- What would be required before implementation: T006 strategy decision; dedicated spike; package install authorization; adapter normalizing to candidate schema with evidence spans.

---

## segram

### Official sources inspected

- `https://github.com/sztal/segram` (README on `master`, LICENSE)
- `https://segram.readthedocs.io/en/latest/`

### Source status

- Retrieved: yes
- Source type: official repo + ReadTheDocs
- Notes: README on `main` branch 404; `master` branch used.

### License

- Finding: MIT License.
- Evidence: LICENSE file (Copyright 2023 Szymon Talaga); ReadTheDocs license section.
- Risk: Low.

### Dependency footprint

- Finding: Python >=3.11, spaCy >=3.4; optional GPU and coreference extras; requires spaCy language models (`en_core_web_trf`, `en_core_web_lg`, optional coreference model).
- Evidence: README and ReadTheDocs requirements tables.
- Risk: Medium–high — stacks on spaCy + transformer models; coreference path adds version constraints (spacy >=3.4,<3.5 for experimental coref).

### Runtime requirements

- Finding: Python 3.11+; spaCy models; English only currently; optional GPU for performance.
- Evidence: ReadTheDocs "Supported languages and models" — English only.
- Risk: Medium — experimental stage and spaCy version coupling.

### Local-first / privacy fit

- Finding: Local execution feasible with downloaded spaCy models; no mandatory cloud API.
- Evidence: ReadTheDocs installation via pip; spaCy local models.
- Risk: Low for local-first if models kept local.

### Text/prose generation behavior

- Finding: No prose generation; semantic grammar / action-oriented parsing.
- Evidence: README: "semantics-oriented grammatical analysis"; action/subject/object detection.
- Risk: None for B1.

### Expected input/output shape

- Finding: Phrase/clause graphs, action/subject/object structures, story/frame organization, hypergraph representations, query matching, serialization for reconstruction.
- Evidence: README and ReadTheDocs feature list.
- Risk: Medium — custom schema; adapter normalization required.

### Evidence/provenance support

- Finding: Parses source text into structured grammatical analyses; serialization preserves parsed structures with source linkage implied through parse graph (span-level mapping adapter responsibility).
- Evidence: README serialization framework; action/subject/object detection from input text.
- Risk: Medium — provenance mapping not documented as ready-made span export for OMI.

### Maintenance status

- Finding: Early stage; last GitHub push 2023-10-01; 6 stars; README warns of "significant changes" and "backward incompatible" future changes.
- Evidence: GitHub API; README note and ReadTheDocs warning.
- Risk: **High maintainability risk.**

### Candidate schema fit

- Finding: Supports F5 (scene/event/action), F7 (relationship hints via action roles), semantic frames; complements spaCy baseline.
- Evidence: Action/subject/object extraction; story/frame organization.
- Risk: Medium — fiction applicability documented as experimental only.

### Adapter feasibility

- Finding: **Possible runtime adapter candidate** after spaCy baseline; not first-path.
- Evidence: spaCy-dependent semantic/action layer; early development status.
- Risk: Maturity, maintenance, and spaCy version constraints.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered (adapter can attach spans)
- B3 unacceptable remote data transfer: not triggered
- B4 unclear/incompatible license: not triggered (MIT)
- B5 cannot constrain to candidate-only: not triggered
- B6 requires runtime dependency before approved review: not triggered at inventory stage

### Preliminary classification

**possible runtime adapter candidate**

### Classification rationale

- Evidence: Official docs describe action-oriented semantic parsing built on spaCy with local execution.
- Risks: Early-stage project, stale commit history, backward-incompatible changes expected.
- What would be required before implementation: spaCy baseline first; spike evaluating fiction text; confirm maintenance/commitment or fork risk acceptance.

---

## BookNLP

### Official sources inspected

- `https://github.com/booknlp/booknlp` (README, LICENSE, setup.py)
- `https://booknlp.pythonhumanities.com/` (minimal landing page)

### Source status

- Retrieved: yes (partial for humanities docs site)
- Source type: official repo (+ minimal docs landing)
- Notes: setup.py lists legacy url `https://github.com/dbamman/book-nlp`; current repo is `booknlp/booknlp`.

### License

- Finding: MIT License.
- Evidence: LICENSE file; setup.py `license="MIT"`.
- Risk: Low.

### Dependency footprint

- Finding: `torch>=1.7.1`, `tensorflow>=1.15`, `spacy>=3`, `transformers>=4.11.3`; requires spaCy model `en_core_web_sm`; two model sizes (`small`, `big`).
- Evidence: setup.py install_requires; README installation section.
- Risk: **High** — dual torch+tensorflow stack; GPU recommended for `big` model.

### Runtime requirements

- Finding: Python (README suggests 3.7 via conda); CPU or GPU; English long-document pipeline; outputs `.entities`, `.tokens`, etc. per book_id.
- Evidence: README usage example and timing table for *The Secret Garden* (99K tokens).
- Risk: Medium–high compute for manuscript scale.

### Local-first / privacy fit

- Finding: Local/offline execution supported after model download; no mandatory cloud API in README.
- Evidence: README local CPU/GPU timing table; pip/conda install instructions.
- Risk: Low for privacy if run locally; medium for resource cost.

### Text/prose generation behavior

- Finding: No prose generation; literary NLP extraction pipeline.
- Evidence: README pipeline features: entity recognition, coreference, quote attribution, events, supersense tagging.
- Risk: None for B1.

### Expected input/output shape

- Finding: Input: book-length plain text file; output files for entities, tokens, quotes, coref clusters, events, supersense tags, gender inference.
- Evidence: README `booknlp.process(input_file, output_directory, book_id)` and pipeline parameter `entity,quote,supersense,event,coref`.
- Risk: Low — structured literary annotations.

### Evidence/provenance support

- Finding: Token-level outputs and entity/quote/event annotations with book offsets (file-based outputs imply traceable positions; exact span schema in output files not verified locally in T003).
- Evidence: README output naming `${book_id}.entities`, `${book_id}.tokens`; character clustering and quote speaker identification documented.
- Risk: Medium — T003 did not verify output file schema locally; adapter must confirm offset fields.

### Maintenance status

- Finding: Last GitHub push 2024-07-31; 922 stars; not archived.
- Evidence: GitHub API metadata.
- Risk: Medium — active but not high-velocity; tensorflow dependency may age.

### Candidate schema fit

- Finding: Strong fit for F1 (characters/aliases), F5 (events), F7 (relationship hints via co-occurrence/ quotes), F10 (evidence attachment).
- Evidence: README feature list maps to character_candidate, timeline_event_candidate, relationship_candidate categories.
- Risk: Medium — English literary bias; fiction manuscript fit good but needs fixture validation.

### Adapter feasibility

- Finding: **Possible runtime adapter candidate** for long-form literary extraction.
- Evidence: Purpose-built book pipeline with character coref, quotes, events.
- Risk: Heavy dependencies; output normalization effort; no local verification in T003.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered (token/entity outputs expected)
- B3 unacceptable remote data transfer: not triggered for local run
- B4 unclear/incompatible license: not triggered (MIT)
- B5 cannot constrain to candidate-only: not triggered
- B6 requires runtime dependency before approved review: not triggered at inventory stage

### Preliminary classification

**possible runtime adapter candidate**

### Classification rationale

- Evidence: Official README documents long-document literary extraction with characters, coref, quotes, events.
- Risks: torch+tensorflow footprint; output schema verification deferred; English-only.
- What would be required before implementation: T006 comparison; dependency spike; fixture evaluation on safe text; confirm span fields in output files.

---

## GLiNER

### Official sources inspected

- `https://github.com/urchade/GLiNER` (README, LICENSE, pyproject.toml)
- `https://urchade.github.io/GLiNER/`

### Source status

- Retrieved: yes
- Source type: official repo + docs site + paper reference
- Notes: README announces GLiNER2 from Fastino Labs as successor project (informational only).

### License

- Finding: Apache-2.0.
- Evidence: LICENSE file; pyproject.toml `license = {text = "Apache-2.0"}`; GitHub API.
- Risk: Low.

### Dependency footprint

- Finding: `torch>=2.0.0`, `transformers`, `huggingface_hub`, `onnxruntime`, `sentencepiece`; optional GPU/onnx/training/serve extras.
- Evidence: pyproject.toml dependencies section.
- Risk: Medium — transformer model weights add download size.

### Runtime requirements

- Finding: Python >=3.10; CPU deployment supported (README: "Runs Anywhere" with CPU, INT8, ONNX); GPU optional.
- Evidence: README Why GLiNER table; docs site describes lightweight alternative to LLMs.
- Risk: Medium — model inference cost scales with text length.

### Local-first / privacy fit

- Finding: Local inference supported on CPU; models from HuggingFace download.
- Evidence: README CPU/INT8/ONNX deployment claims.
- Risk: Low for local-first after model download.

### Text/prose generation behavior

- Finding: No prose generation; zero-shot NER and relation extraction.
- Evidence: README task list; docs site scope.
- Risk: None for B1.

### Expected input/output shape

- Finding: Text + custom entity label list → extracted entities with spans; joint relation extraction via RelEx architecture mentioned in README.
- Evidence: README "Zero-shot Recognition", "NER + Relations", "Build knowledge graphs in a single pass".
- Risk: Medium — false positives on fiction-specific labels; confidence threshold tuning needed.

### Evidence/provenance support

- Finding: Entity extractions include text spans (standard NER output shape); suitable for evidence attachment with char offsets.
- Evidence: README information extraction focus; Google blog/LangExtract contrast implies span-based extraction pattern.
- Risk: Medium — fiction entity feasibility requires fixture validation (not verified in T003).

### Maintenance status

- Finding: Actively maintained (GitHub `pushed_at` 2026-06-16); 3299 stars; GLiNER2 announced as related successor.
- Evidence: GitHub API; README GLiNER2 notice.
- Risk: Low–medium — evaluate GLiNER vs GLiNER2 in future spike.

### Candidate schema fit

- Finding: Strong fit for F1–F4 custom fiction labels (characters, locations, objects, organizations) via zero-shot label definitions.
- Evidence: README "Extract any entity type — no labeled data or task-specific training required".
- Risk: Medium — label design and false positive control required.

### Adapter feasibility

- Finding: **Possible runtime adapter candidate** for custom/zero-shot entity extraction.
- Evidence: Apache-2.0, local CPU path, custom labels, relation extraction option.
- Risk: Model quality on fiction; complement to spaCy rule baseline.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered
- B3 unacceptable remote data transfer: not triggered for local models
- B4 unclear/incompatible license: not triggered (Apache-2.0)
- B5 cannot constrain to candidate-only: not triggered
- B6 requires runtime dependency before approved review: not triggered at inventory stage

### Preliminary classification

**possible runtime adapter candidate**

### Classification rationale

- Evidence: Official sources document zero-shot/custom entity and relation extraction with local CPU deployment.
- Risks: Fiction-specific accuracy unknown until fixtures; GLiNER2 migration question.
- What would be required before implementation: T006 strategy; fixture F1–F4 evaluation; threshold tuning; adapter normalization.

---

## LangExtract

### Official sources inspected

- `https://github.com/google/langextract` (README, LICENSE, pyproject.toml)
- `https://developers.googleblog.com/introducing-langextract-a-gemini-powered-information-extraction-library/`

### Source status

- Retrieved: yes
- Source type: official repo + Google developer announcement
- Notes: `langextract.com` not separately fetched; README and blog sufficient.

### License

- Finding: Apache-2.0.
- Evidence: LICENSE file; pyproject.toml `license = "Apache-2.0"`.
- Risk: Low.

### Dependency footprint

- Finding: Python >=3.10; dependencies include `google-genai`, `google-cloud-storage`, `aiohttp`, `pandas`, `pydantic`; optional OpenAI provider.
- Evidence: pyproject.toml dependencies and optional-dependencies.
- Risk: Medium — cloud-provider dependencies present even for local Ollama path.

### Runtime requirements

- Finding: Default examples use Gemini cloud models (API key required); **Ollama local path documented** (`model_id="gemma2:2b"`, `model_url="http://localhost:11434"`).
- Evidence: README "Using Local LLMs with Ollama" section; Google blog Gemini examples.
- Risk: Medium — cloud path sends text to third-party; local Ollama reduces B3 risk.

### Local-first / privacy fit

- Finding: Hybrid — local Ollama supported; default marketing/examples emphasize Gemini cloud.
- Evidence: README Ollama section; Google blog API key setup for cloud models.
- Risk: **Medium–high** if cloud Gemini used with owner manuscript text.

### Text/prose generation behavior

- Finding: Structured information extraction, not story prose generation; however README notes LLM **world knowledge** may supplement extractions (explicit vs inferred).
- Evidence: README point 7 "Leverages LLM World Knowledge"; Google blog similar disclaimer on inferred information.
- Risk: Medium — inferred extractions may lack strict source grounding (candidate-only + owner review required).

### Expected input/output shape

- Finding: Text/documents + prompt + few-shot examples → structured extractions with classes, text spans, attributes; JSONL output; HTML visualization.
- Evidence: README quick start; Google blog Romeo and Juliet example with `Extraction(extraction_class, extraction_text, attributes)`.
- Risk: Low for shape; medium for grounding discipline on inferred fields.

### Evidence/provenance support

- Finding: **Strong** — "Precise Source Grounding" maps extractions to exact character offsets; visualization highlights source spans.
- Evidence: README and Google blog feature #1; design reference for evidence model.
- Risk: Medium when model supplements with world knowledge beyond source text.

### Maintenance status

- Finding: Actively maintained (GitHub `pushed_at` 2026-05-21); 36k+ stars; Google-backed open source.
- Evidence: GitHub API; CI badge in README.
- Risk: Low.

### Candidate schema fit

- Finding: Flexible schema via few-shot examples; maps to multiple candidate types if adapter defines extraction classes per Writer Assistant Core schema.
- Evidence: README customizable extraction tasks; medication and character examples.
- Risk: Medium — schema enforcement depends on prompt/examples quality.

### Adapter feasibility

- Finding: **Possible runtime adapter candidate** (especially for evidence-grounding design reference); model-assisted path, not first deterministic slice.
- Evidence: Source grounding, structured output, Ollama option; heavy alignment with F10 evidence/provenance.
- Risk: Cloud dependency temptation; inferred-knowledge leakage; requires strict candidate-only + span validation.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered (grounding is core feature)
- B3 unacceptable remote data transfer: **conditional** — triggered if cloud Gemini/default remote used with owner text; mitigated with local Ollama
- B4 unclear/incompatible license: not triggered (Apache-2.0)
- B5 cannot constrain to candidate-only: not triggered (adapter-controlled)
- B6 requires runtime dependency before approved review: not triggered at inventory stage

### Preliminary classification

**possible runtime adapter candidate**

### Classification rationale

- Evidence: Official sources emphasize source grounding and structured extraction with local Ollama support.
- Risks: Cloud API privacy; world-knowledge inferences beyond source text; model cost.
- What would be required before implementation: T006 path decision; mandate local Ollama only for MVP spike; F11/F12 negative tests; block inferred fields without evidence spans.

---

## Renard

### Official sources inspected

- `https://github.com/CompNet/Renard` (README, LICENSE, pyproject.toml)
- `https://arxiv.org/abs/2407.02284`

### Source status

- Retrieved: yes
- Source type: official repo + primary paper (JOSS)
- Notes: HuggingFace demo referenced in README (not executed).

### License

- Finding: GPL-3.0-only.
- Evidence: LICENSE file (GNU GPL v3); pyproject.toml `license = { text = "GPL-3.0-only" }`; GitHub API.
- Risk: **High for adapter integration** — copyleft may affect distribution if linked as library; requires legal/owner review.

### Dependency footprint

- Finding: `torch>=2.7.0`, `transformers`, `nltk`, `networkx`, `tibert`, `grimbert`, `datasets`, `scikit-learn`, etc.; default pip install pulls CUDA torch; CPU-only install path documented.
- Evidence: pyproject.toml dependencies; README installation section.
- Risk: High — PyTorch + transformer stack; modular pipeline with multiple step implementations.

### Runtime requirements

- Finding: Python >=3.9,<3.13; CPU or GPU torch; modular pipeline steps (tokenization, NER, coref, graph extraction).
- Evidence: README and pyproject.toml `requires-python`.
- Risk: Medium–high compute for transformer-based steps.

### Local-first / privacy fit

- Finding: Local execution supported; HuggingFace demo is optional remote UI (not required).
- Evidence: README pip install local; paper describes offline pipeline usage.
- Risk: Low for local pipeline; medium for dependency weight.

### Text/prose generation behavior

- Finding: No prose generation; character network extraction from narrative text.
- Evidence: README and paper: "extract character networks from narrative texts".
- Risk: None for B1.

### Expected input/output shape

- Finding: Text in → NetworkX static or dynamic character graphs; pipeline steps declare requirements/produce metadata; co-occurrence and conversational graph extractors.
- Evidence: README pipeline example; arxiv paper design section and Table of steps/languages.
- Risk: Low for graph output; medium for mapping edges to relationship_candidate records with evidence.

### Evidence/provenance support

- Finding: Graph edges derived from text pipeline; provenance requires adapter to retain source spans from NER/coref steps (not automatic in graph output alone).
- Evidence: Paper modular pipeline design; co-occurrence distance parameters.
- Risk: Medium — relationship candidates need explicit evidence spans, not just graph weights.

### Maintenance status

- Finding: Recently active (GitHub `pushed_at` 2026-05-20); 21 stars; JOSS paper 2024; version 0.7.1 in pyproject.
- Evidence: GitHub API; pyproject.toml version.
- Risk: Medium — smaller community than spaCy/GLiNER; active recent commits.

### Candidate schema fit

- Finding: Strong fit for F7 (relationship extraction) and character network review; complements entity extraction from spaCy/BookNLP/GLiNER.
- Evidence: Paper purpose: static and dynamic character networks for literary analysis.
- Risk: Medium — co-occurrence ≠ Dramatica relationship proof; label as candidates only.

### Adapter feasibility

- Finding: **Possible runtime adapter candidate** for relationship/character-network extraction **after** entity baseline; **GPL license is primary blocker for naive adoption**.
- Evidence: Modular pipeline for narrative documents; NetworkX output.
- Risk: GPL-3.0 copyleft; graph-to-candidate normalization; evidence span attachment.

### T002 blocker screen

- B1 prose generation as core behavior: not triggered
- B2 no evidence/provenance: not triggered (adapter can attach)
- B3 unacceptable remote data transfer: not triggered for local run
- B4 unclear/incompatible license: **conditional** — GPL-3.0 may be incompatible with intended adapter embedding; owner/legal review required
- B5 cannot constrain to candidate-only: not triggered
- B6 requires runtime dependency before approved review: not triggered at inventory stage

### Preliminary classification

**possible runtime adapter candidate**

### Classification rationale

- Evidence: Official paper and repo document modular narrative character-network extraction with local execution.
- Risks: GPL-3.0 license; heavy deps; relationship evidence must be explicit.
- What would be required before implementation: License review; entity baseline first; spike on fiction fixture; graph→relationship_candidate adapter with spans.

---

## Cross-Tool Summary Table

| Tool/reference | Source retrieval | License status | Dependency/runtime risk | Local-first/privacy risk | Generation/prose risk | Evidence/provenance fit | Candidate schema fit | Preliminary classification | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dramatica-flow | yes (partial LICENSE) | MIT claimed; file not fetched | High (full app + LLM) | Medium (Ollama option) | **Critical (B1)** | Medium (analysis concepts) | Medium (conceptual) | reference-only | T004 splits safe analysis vs generation |
| Narrative Context Protocol | yes | MIT (LICENSE.md) | Low (schema only) | Low | None | N/A (structural) | Structural reference | reference-only | T005 import/export strategy |
| Subtxt docs | yes | unknown (site terms) | None | Low | Low (docs); Muse ref | N/A (rubric) | Rubric reference | reference-only | T005 rubric strategy |
| spaCy | yes | MIT | Medium (model-dependent) | Low | None | High (span offsets) | High (F1–F7 baseline) | likely runtime adapter candidate | First local NLP baseline |
| segram | yes | MIT | Medium–high (spaCy stack) | Low | None | Medium | Medium (F5/F7) | possible runtime adapter candidate | Early stage; stale since 2023 |
| BookNLP | yes (partial docs site) | MIT | High (torch+tensorflow) | Low (local) | None | Medium–high | High (F1/F5/F7) | possible runtime adapter candidate | Long-form literary pipeline |
| GLiNER | yes | Apache-2.0 | Medium (transformers) | Low (CPU local) | None | High (spans) | High (F1–F4 custom labels) | possible runtime adapter candidate | Zero-shot fiction entities |
| LangExtract | yes | Apache-2.0 | Medium (LLM deps) | Medium (cloud vs Ollama) | Low (extraction) | **High** (char offsets) | High (flexible classes) | possible runtime adapter candidate | Evidence design reference; cloud caution |
| Renard | yes | GPL-3.0 | High (torch stack) | Low (local) | None | Medium | High (F7 networks) | possible runtime adapter candidate | GPL review required |

---

## T002 Rubric Support (Preliminary Evidence Notes)

T003 does not assign final T006 scores. Evidence-supported direction for later scoring:

| Rubric dimension | Strongest evidence sources |
| --- | --- |
| D1 analysis-only safety | spaCy, segram, BookNLP, GLiNER, Renard (no generation); NCP/Subtxt/dramatica-flow analysis subsets reference-only |
| D2 prose-generation risk (inverse) | dramatica-flow **low inverse (high risk)**; spaCy/BookNLP/GLiNER **high inverse** |
| D3 evidence/provenance | LangExtract (char offsets), spaCy (spans), GLiNER (NER spans), BookNLP (token outputs) |
| D4 candidate schema fit | spaCy, BookNLP, GLiNER, LangExtract (adapter mapping); NCP/Subtxt structural only |
| D5 story-knowledge categories | BookNLP (characters/events/quotes), GLiNER (custom entities), Renard (relationships), segram (actions) |
| D6 local-first/privacy | spaCy, BookNLP, GLiNER, Renard (local models); LangExtract (Ollama path); dramatica-flow/LangExtract cloud paths weaker |
| D7 dependency cost (inverse) | spaCy best; BookNLP/Renard heavy; dramatica-flow highest |
| D8 license risk (inverse) | spaCy/MIT, BookNLP/MIT, GLiNER/LangExtract/Apache-2.0 strong; Renard GPL-3.0 weak; Subtxt docs unknown |
| D9 maintainability | spaCy, GLiNER, LangExtract strong; segram weak; BookNLP moderate |
| D10 determinism/normalizability | spaCy highest; LLM-assisted tools lower |
| D11 integration complexity (inverse) | NCP/Subtxt simplest (reference); dramatica-flow most complex |
| D12 OMI candidate-only fit | All runtime candidates require adapter discipline; reference sources require no-auto-truth policy |
| D13 first-extraction-path suitability | spaCy leading for rule/local NLP first path; manual-first still valid before any install |

---

## Findings Summary

### Strongest likely runtime adapter candidate

- **spaCy** — MIT, local/offline, mature, span-based NLP, rule matcher, aligns with tooling_decisions "first local NLP baseline".

### Strongest possible runtime adapter candidates

- **BookNLP** — long-form literary extraction (characters, coref, quotes, events); heavy deps.
- **GLiNER** — zero-shot custom fiction entity labels; Apache-2.0; CPU feasible.
- **LangExtract** — evidence grounding design reference; Ollama path; cloud/world-knowledge risks.
- **Renard** — character/relationship networks; **GPL-3.0 review required**.
- **segram** — semantic/action parsing after spaCy; early-stage maintenance concern.

### Strongest reference-only candidates

- **Narrative Context Protocol** — schema/import-export reference for approved structural context.
- **Subtxt docs** — semantic/Dramatica interpretation rubric.
- **dramatica-flow** — analysis-pattern reference only; **B1 blocks runtime adapter**.

### Reject/defer candidates

- None fully rejected; **dramatica-flow runtime adapter deferred/rejected** pending T004; **Renard deferred** pending GPL review.

### Unresolved source gaps

- dramatica-flow LICENSE file not retrieved from default paths (MIT badge only).
- Subtxt docs site license/terms not retrieved.
- BookNLP humanities docs site returned minimal content; output file span schema not verified locally.
- LangExtract `langextract.com` not separately fetched.
- GLiNER arXiv paper not fully retrieved (docs/README sufficient for inventory).
- No local runtime verification performed (by design).

### Follow-up questions for T004/T005/T006

- **T004:** Which dramatica-flow analysis dimensions (causal chain, hooks, emotional arcs, relationships, information boundaries, audit) are safe to borrow as reference rubric/diagnostics without any generation API?
- **T005:** How should NCP Storyform import/export interact with owner approval and OMI? How should Subtxt source-of-conflict guidance inform evaluation rubrics without auto-labeling truth?
- **T006:** Confirm spaCy as first extraction path vs manual-first; rank BookNLP vs GLiNER vs LangExtract vs Renard vs segram; decide LangExtract Ollama-only policy; resolve Renard GPL and segram maintenance.

### Nine-tool scope

**Remain unchanged.** All nine candidates have sufficient official source evidence for preliminary classification. No out-of-scope tool reintroduction recommended.

---

## Safety Confirmation

- Docs/research inventory only.
- No tools installed, cloned, or executed.
- No model calls.
- No runtime code, tests, routes, UI, package, training, or memory/canon changes.
- No extraction implementation.
- Classifications are preliminary; final strategy belongs to T004–T006.
