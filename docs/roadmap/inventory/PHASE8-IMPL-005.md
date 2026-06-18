# PHASE8-IMPL-005 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-005`
- Title: Writer Assistant Core tool evaluation and extraction strategy decision
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-004` - Writer Assistant Core candidate index contract and derived index helpers

## 2. Why This Parent Exists

`PHASE8-IMPL-001` through `PHASE8-IMPL-004` completed enough candidate infrastructure to support evaluation planning:

- Schema constants, record validation, storage path contracts.
- Candidate-only JSON write/read/list persistence with `writer_assistant/candidates/*.json` as source of truth.
- Derived candidate index contract and helpers at `writer_assistant/index.json`.

Extraction implementation must not begin until the selected tool/reference candidates are evaluated. This parent creates the roadmap-controlled evaluation phase for deciding how nine approved tools/references should or should not be used.

## 3. Scope

This parent prepares a controlled tool evaluation and extraction strategy slice. It focuses on:

- Narrowed nine-tool/reference inventory for evaluation only.
- Evaluation rubric and scoring metrics.
- Extraction fixture plan.
- Official source retrieval policy (recorded in T001; executed in T003).
- License/dependency/privacy/local-first screening.
- Generation-risk screening.
- Candidate-only adapter strategy.
- dramatica-flow analysis-only reference review.
- NCP/Subtxt integration strategy.
- First extraction path decision: manual-first, rule-based, local NLP, model-assisted, or hybrid.
- Next parent handoff for first extraction architecture/implementation.

Scoped tools/references (exactly nine):

| Tool/Reference | Role | Evaluation stance |
| --- | --- | --- |
| dramatica-flow | Analysis-pattern reference for causal chains, foreshadowing, emotional arcs, relationship networks, timeline/thread activity, information-boundary diagnostics, and audit dimensions | Reference-only until proven safe; reject direct prose generation, rewrite, revision, continuation, and outline-as-truth behavior |
| Narrative Context Protocol | Optional future schema/import/export target for approved structural context | Schema/reference only; not candidate source of truth; must not bypass owner approval |
| Subtxt docs | Semantic/Dramatica interpretation rubric for later evaluation | Interpretation reference only; not runtime dependency; not automatic truth |
| spaCy | Local NLP baseline for tokenization, segmentation, lemmatization, POS, dependency parsing, NER, and rule/matcher workflows | Likely first local NLP baseline to evaluate |
| segram | Semantic grammar/action-analysis reference built around spaCy-style NLP | Later semantic/action extraction reference after spaCy baseline is understood |
| BookNLP | Long-form literary text pipeline for books/chapters, characters, aliases, quotations, and events | Evaluate for manuscript-scale literary extraction |
| GLiNER | Custom/zero-shot entity extraction for fiction-specific labels | Evaluate as candidate-only custom entity extractor |
| LangExtract | Structured extraction and source-grounding reference | Evaluate mainly for evidence/source-grounding design and possible model-backed extraction later |
| Renard | Relationship and character-network extraction reference | Evaluate after basic entity/evidence extraction is understood |

## 4. Non-Scope

This parent, and specifically `PHASE8-IMPL-005-T001`, excludes:

- Production runtime code in T001.
- Tests in T001.
- Tool evaluation in T001.
- Official source retrieval in T001.
- Tool installs, clones, demos, or executions in T001.
- Extraction adapters and candidate extraction runtime.
- Backend routes and API helpers.
- Frontend UI.
- Model/Ollama calls and HTTP calls.
- Generated prose, rewriting, continuation, style imitation, or prose improvement.
- Outline generation as project truth.
- Semantic search and Story Check auto-runs.
- Dramatica analysis runtime.
- Apply-promotion and OMI candidate promotion.
- Memory/canon mutation and approved-memory helpers.
- Package/dependency changes.
- Training data, JSONL records, dataset artifacts, and project runtime files.
- Context-tool execution in T001.

Explicitly out of scope unless a later owner-approved parent reintroduces them:

- CoreNLP / OpenIE / SUTime
- AI-Reader-V2
- narrative-blueprint
- NovelClaw
- NotebookLM workflow
- llm_finetuning
- ai-llm-project-file-structure-template
- any other external story-generation, writing, outlining, or revision system

## 5. Risks

- Generation-heavy tools leaking into no-prose app behavior.
- Tool output being mistaken for canon.
- NCP import/export bypassing owner approval.
- Subtxt/Dramatica labels being overclaimed as truth.
- Extraction starting before evaluation.
- External dependencies bloating local-first app.
- Licenses/dependencies being misunderstood.
- Context/tool research producing stale or noisy evidence.
- Future adapters mutating memory/canon silently.
- Unsupported tools being reintroduced without owner approval.
- Cursor/Claude using memory instead of official source evidence.

## 6. Current T001 Inventory Result

`PHASE8-IMPL-005-T001` is docs/status/planning only. It publishes the tool evaluation and extraction strategy parent, child-task plan, inventory, enrichment JSON, and roadmap/status updates. It records the narrowed nine-tool scope and official source retrieval policy for later children. It does not run context tools, evaluate tools, retrieve sources, install tools, or change runtime code, tests, backend/frontend/package files, project runtime files, training data, JSONL records, or dataset manifests.
