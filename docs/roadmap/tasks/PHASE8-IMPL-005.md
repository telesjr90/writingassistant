# PHASE8-IMPL-005

## ID

`PHASE8-IMPL-005`

## Title

Writer Assistant Core tool evaluation and extraction strategy decision

## Goal

Prepare a controlled evaluation phase for deciding how nine approved tools/references should or should not be used for future Writer Assistant Core extraction, producing an evaluation plan, scoring rubric, source inventory plan, and extraction strategy decision without runtime extraction behavior.

## Why Now

`PHASE8-IMPL-001` through `PHASE8-IMPL-004` completed enough candidate infrastructure to support evaluation planning:

- `PHASE8-IMPL-001`: candidate schema constants.
- `PHASE8-IMPL-002`: candidate record validation, source locator/evidence/provenance validation, and project-local storage path contracts.
- `PHASE8-IMPL-003`: candidate-only JSON write/read/list persistence with candidate JSON files under `writer_assistant/candidates/*.json` as source of truth.
- `PHASE8-IMPL-004`: derived candidate index contract and helper layer at `writer_assistant/index.json`, with candidate JSON files remaining source of truth.

The next safe step is not extraction implementation. The next safe step is evaluation and strategy for the nine approved tool/reference candidates before any adapter, route, UI, or model-backed extraction work begins.

## Dependencies

- Completed parent: `PHASE8-IMPL-004` - Writer Assistant Core candidate index contract and derived index helpers.
- Completed child: `PHASE8-IMPL-004-T007` - Roadmap/status closeout.
- Source evidence:
  - `docs/roadmap/decisions/PHASE8-IMPL-004-candidate-index-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-003-candidate-persistence-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-002-candidate-storage-evidence-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-001-first-runtime-slice-decision.md`
  - `docs/roadmap/writer_assistant_core_candidate_schemas.md`
  - `docs/roadmap/tooling_decisions.md`
  - `docs/roadmap/optional_analysis_extractors.md`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`

## Scope

Include:

- Narrowed nine-tool/reference inventory for evaluation only.
- Evaluation rubric and scoring metrics (decided in T002).
- Extraction fixture plan (decided in T002).
- Official source retrieval policy (recorded in T001; executed in T003).
- License/dependency/privacy/local-first screening (T003).
- Generation-risk screening (T003-T006).
- Candidate-only adapter strategy (T006).
- dramatica-flow analysis-only reference review (T004).
- NCP/Subtxt structural interpretation strategy (T005).
- First extraction path decision: manual-first, rule-based, local NLP, model-assisted, or hybrid (T006).
- Next parent handoff for first extraction architecture/implementation (T007).

Scoped tool/reference candidates (exactly nine):

1. dramatica-flow - analysis-pattern reference; reject generation/revision/continuation behavior.
2. Narrative Context Protocol - optional future schema/import/export target for approved structural context only.
3. Subtxt docs - semantic/Dramatica interpretation rubric only; not automatic truth.
4. spaCy - local NLP baseline candidate for deterministic/rule-assisted extraction support.
5. segram - semantic grammar/action-analysis reference after spaCy baseline is understood.
6. BookNLP - long-form literary extraction candidate for characters, quotes, events, and aliases.
7. GLiNER - fiction-specific custom entity extraction candidate.
8. LangExtract - evidence-grounded structured extraction reference and possible later model-backed extraction candidate.
9. Renard - character-network and relationship extraction reference/candidate.

Explicitly out of scope unless a later owner-approved parent reintroduces them:

- CoreNLP / OpenIE / SUTime
- AI-Reader-V2
- narrative-blueprint
- NovelClaw
- NotebookLM workflow
- llm_finetuning
- ai-llm-project-file-structure-template
- any other external story-generation, writing, outlining, or revision system

## Exclusions

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

## Child-Task Plan

1. `PHASE8-IMPL-005-T001` - Publish tool evaluation and extraction strategy parent. Status: complete.
2. `PHASE8-IMPL-005-T002` - Evaluation scope, fixture plan, and scoring rubric decision. Status: complete.
3. `PHASE8-IMPL-005-T003` - Official source inventory and license/dependency screen. Status: ready.
4. `PHASE8-IMPL-005-T004` - Dramatica-flow analysis-only reference decision. Status: draft.
5. `PHASE8-IMPL-005-T005` - NCP/Subtxt structural interpretation strategy decision. Status: draft.
6. `PHASE8-IMPL-005-T006` - NLP/extraction adapter strategy decision. Status: draft.
7. `PHASE8-IMPL-005-T007` - Roadmap/status closeout. Status: draft.

## Child Task Details

### `PHASE8-IMPL-005-T001` - Publish tool evaluation and extraction strategy parent

- Docs/status/planning only.
- Publish parent, inventory, enrichment JSON, and roadmap/status updates.
- Record narrowed scope to exactly the nine approved tools/references.
- Record official source retrieval policy for later children.
- No evaluation, no source retrieval, no web review, no tool runs, no installs, no code/tests.

### `PHASE8-IMPL-005-T002` - Evaluation scope, fixture plan, and scoring rubric decision

- Docs/decision only.
- Decide evaluation categories, scoring metrics, fixture requirements, source rules, safety gates, and pass/fail thresholds.
- No tool runs, no installs, no runtime code.

### `PHASE8-IMPL-005-T003` - Official source inventory and license/dependency screen

- Docs/research inventory only.
- First child allowed to retrieve official source information.
- Retrieve and inspect only official docs/repos/primary papers for the nine approved candidates.
- Summarize license, maintenance, dependency footprint, local-first/privacy fit, generation risk, evidence/provenance support, and adapter feasibility.
- No cloning, no package installation, no runtime execution.

### `PHASE8-IMPL-005-T004` - Dramatica-flow analysis-only reference decision

- Docs/decision only.
- Decide whether dramatica-flow is reference-only, adapter-candidate, or rejected.
- Explicitly split safe analysis concepts from unsafe generation/revision/continuation behavior.

### `PHASE8-IMPL-005-T005` - NCP/Subtxt structural interpretation strategy decision

- Docs/decision only.
- Decide how Narrative Context Protocol and Subtxt docs should guide approved structural context, import/export, semantic rubric, and Dramatica-informed validation.
- No NCP runtime implementation.

### `PHASE8-IMPL-005-T006` - NLP/extraction adapter strategy decision

- Docs/decision only.
- Compare spaCy, segram, BookNLP, GLiNER, LangExtract, and Renard against the T002 rubric.
- Choose first extraction implementation path: manual-first, rule-based, local NLP, model-assisted, or hybrid.
- Define what the next implementation parent should build.
- Require candidate-only evidence/provenance output.

### `PHASE8-IMPL-005-T007` - Roadmap/status closeout

- Close parent.
- Summarize accepted tool strategy.
- Identify next parent, likely first extraction architecture/implementation parent.
- No runtime implementation.

## Acceptance Criteria

- `PHASE8-IMPL-005` is published as the active Writer Assistant Core parent after completed `PHASE8-IMPL-004`.
- `PHASE8-IMPL-005-T001` publishes the parent, inventory, enrichment JSON, and roadmap/status updates.
- Scope is narrowed to exactly nine approved tools/references.
- Official source retrieval policy records T003 as the first child allowed to retrieve official source information.
- Child tasks T001-T007 are documented with evaluation-first sequencing.
- Scope explicitly blocks extraction implementation, routes, UI, model calls, tool execution in T001, apply-promotion, and memory/canon mutation.
- External tools remain replaceable adapters around app-owned Writer Assistant Core.
- Tool output must become candidates with evidence/provenance, never canon.
- Owner approval remains mandatory.
- No prose generation, rewrite, continuation, or automatic canon mutation is allowed.

## Validation Expectations

For `PHASE8-IMPL-005-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Non-LeanCTX whitespace check on changed docs

Do not run pytest unless runtime code or tests were accidentally changed. Do not run context tools, CCE, Graphify, Repomix, AI Context generation, MCP tools, LeanCTX, app servers, browser/manual validation, frontend build, model calls, Ollama, external repo clone, package install, source retrieval, web review, or broad discovery.

## Safety / Product Boundaries

- The app is analysis-only.
- The app must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Owner-authored prose storage and editing remain allowed only when text is authored by the owner.
- Candidates are not canon.
- Schema validity, storage validity, persistence existence, index existence, or tool output does not prove story truth.
- Candidate records must remain separate from approved memory/canon.
- Tool evaluation must not mutate approved memory, canon, bible, storyform, scenes, notes, materials, project metadata, training data, JSONL records, or dataset manifests.
- OMI remains the central review and future promotion layer.
- Promotion records remain audit-only until future apply-promotion exists.
- Context outputs are evidence, not roadmap truth.
- External tool outputs must become candidate records with evidence/provenance if ever implemented.
- dramatica-flow, NCP, and Subtxt docs are evaluation/reference sources, not runtime dependencies or automatic truth.

## Current Status

`PHASE8-IMPL-005` is active. Last completed child: `PHASE8-IMPL-005-T002` - Evaluation scope, fixture plan, and scoring rubric decision. Active child: `PHASE8-IMPL-005-T003` - Official source inventory and license/dependency screen. Last completed parent: `PHASE8-IMPL-004`. Prior completed child under prior parent: `PHASE8-IMPL-004-T007`.

## T002 Decision Record

- Decision doc: `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`
- Defines evaluation objective, scope, provisional tool grouping, fixture categories (no fixture files), 0–5 scoring rubric with hard blockers and pass/fail gates, and T003 source inventory requirements.
- T003 remains the first child allowed to retrieve official source information.

## Official Source Retrieval Policy

T001 does not retrieve or evaluate tool sources. T001 only records this policy.

The first task allowed to retrieve tool/source information is:

`PHASE8-IMPL-005-T003` - Official source inventory and license/dependency screen

T003 may retrieve information only from official sources for the nine approved candidates.

Allowed retrieval methods in T003:

1. Cursor web access, if available, restricted to the official URLs recorded in the T003 prompt.
2. Read-only terminal fetch of official documentation/README pages with commands such as `curl -L <official-url>` or `python3 - <<'PY'` using `urllib.request` for specific official URLs.
3. User-provided attached source snapshots if Cursor has no web access.

Forbidden retrieval methods in T003:

- `git clone`
- package installation
- running tool code
- running demos
- model calls
- broad discovery
- scraping unrelated sites
- using tutorials/blogs as primary sources when official docs/repos exist
- treating marketing claims as validated behavior
- writing runtime code based on source review

Official source targets for T003 are recorded in the enrichment JSON `official_source_retrieval_policy` field and the parent task prompt.

T003 source-quality rule: prefer official docs/repos and primary papers. Use third-party tutorials only as secondary context and never as the primary authority for license, API, maintenance, or safety decisions.

T003 output rule: the result must be a source inventory and evaluation-readiness screen, not an implementation plan. Each tool must be classified as one of: likely runtime adapter candidate, possible runtime adapter candidate, reference-only, reject/defer. Every classification must include evidence, risk, and what would be required before implementation.

If Cursor cannot access the internet in T003: stop and report that source retrieval was blocked; ask the owner to attach snapshots of the official docs/repos for the nine scoped candidates; do not substitute memory-based tool claims for source evidence; do not proceed to evaluation classifications without source evidence.
