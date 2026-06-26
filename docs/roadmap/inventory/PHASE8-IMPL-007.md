# PHASE8-IMPL-007 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-007`
- Title: Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-006`

## 2. Why This Parent Exists

`PHASE8-IMPL-006` closed the evidence-first extraction foundation and BookNLP-ready adapter strategy. It intentionally left the future production module `backend.story_knowledge.booknlp_adapter_contract` unimplemented and produced an expected-red contract test file at `tests/test_writer_assistant_core_booknlp_adapter_contract.py`. The expected-red state was preserved so a future owner-approved parent could implement the pure mocked adapter without racing the contract.

`PHASE8-IMPL-006` deliberately revised the next-parent direction from spaCy-first-only to evidence-first + BookNLP-ready, so that BookNLP could become the first serious literary extractor candidate after source maps/provenance existed. `PHASE8-IMPL-006` also accepted the BookNLP-ready raw output and adapter contract decision, which defined mocked fixture shapes, raw artifact kinds, run manifest policy, and adapter normalization boundaries.

The owner has now cloned the official source repositories into local read-only `.external_sources/` directories:

- `.external_sources/booknlp`
- `.external_sources/dramatica-flow`
- `.external_sources/narrative-context-protocol`
- `.external_sources/subtxt-docs`

These clones exist so that a later child task can perform a read-only official source inventory to confirm or refine the mocked fixture shapes, source-level forbidden runtime dependency terms, and boundary rules. They are not app dependencies, must not be vendored into `backend/`, and must not be committed.

`PHASE8-IMPL-007` therefore exists to:

- acknowledge the expected-red handoff from `PHASE8-IMPL-006`
- begin with a read-only official source inventory child (`PHASE8-IMPL-007-T002`) before any implementation
- implement the pure mocked `backend/story_knowledge/booknlp_adapter_contract` module so the expected-red `tests/test_writer_assistant_core_booknlp_adapter_contract.py` contract turns green
- keep BookNLP-like outputs as mocked fixtures only
- preserve no-prose, no-canon-mutation, no-auto-promotion, and no-runtime-extraction boundaries

This parent moves from contract definition to pure mocked adapter contract implementation without real BookNLP runtime.

## 3. Source Inventory Inputs

Local clone paths (read-only cache for T002 only):

- `.external_sources/booknlp`
- `.external_sources/dramatica-flow`
- `.external_sources/narrative-context-protocol`
- `.external_sources/subtxt-docs`

`T002` must inspect these clones read-only and record commit SHAs. `T002` must not:

- clone, fetch, or pull from any remote
- install, run, or import any package from these repositories
- copy or vendor external source code into `backend/` or any app runtime file
- execute any code from these repositories
- build documentation from these repositories

`T002` should inspect only:

- README files
- LICENSE files
- package metadata
- docs/
- schemas (where present)
- files relevant to output shapes, schema fields, and safety boundaries

Priority for `T002`:

1. Highest priority: BookNLP output files and parser-relevant schema/fields.
2. Secondary: dramatica-flow unsafe generation/write paths versus safe analysis-only concepts.
3. Secondary: NCP schema/import-export boundaries.
4. Secondary: Subtxt docs rubric/semantic guardrail boundaries.

`T001` does not perform detailed source review. `T001` only confirms the four `.external_sources/` paths exist and are protected from commit.

## 4. Scope

Include:

- read-only official source inventory before implementation (T002)
- pure BookNLP-like run manifest validation helper
- pure raw artifact bundle validation helper
- mocked entity mention normalization helper (entity mentions -> candidate draft shape)
- mocked quote normalization helper (quote records -> candidate draft shape)
- mocked event normalization helper (event records -> candidate draft shape)
- candidate draft builder that combines mocked entity/quote/event normalization outputs
- fail-closed behavior for invalid manifests, invalid bundles, missing source locators, invalid offsets, missing hashes, mutation/prose fields, unsupported candidate types, invalid confidence, and ambiguous speaker attribution
- integration with the existing pure source-map and evidence validation helpers
- source-level no-runtime/no-tool/no-prose/no-canon-mutation boundary checks against the future module
- contract regression validation using `tests/test_writer_assistant_core_booknlp_adapter_contract.py`

## 5. Non-Scope

Explicitly excluded:

- real BookNLP install
- real BookNLP execution
- real BookNLP output parsing from files
- spaCy install/run
- dramatica-flow runtime
- NCP import/export implementation
- Subtxt classifier or rubric runtime
- extraction orchestrator
- raw output storage writers
- candidate JSON persistence from adapter output
- backend extraction routes
- frontend extraction/review UI
- package/dependency changes
- model calls, Ollama calls, or any HTTP/network call
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion
- automatic Storyform truth, automatic Dramatica/Subtxt labels, automatic CIPS/dynamics/RS/IC truth, or automatic canon mutation
- apply-promotion
- memory/canon mutation
- cloning, fetching, or pulling from any external remote
- executing, importing, or vendoring external repository code from `.external_sources/` into `backend/`
- training data, JSONL records, dataset artifacts, or manifest changes
- staging, committing, or pushing in T001
- `.external_sources/` content commits

## 6. Risks

Include in risk tracking:

- `.external_sources/` accidentally committed
- expected-red tests misunderstood as runtime failure
- mocked fixtures drifting from real BookNLP schema (still acceptable because the parent is mocked-fixture based)
- future module accidentally importing or running BookNLP
- raw output treated as canon
- candidate drafts mistaken for persisted candidates
- quote/speaker/entity/event false positives becoming confident-looking drafts
- source locator/evidence mismatch causing invalid offsets to slip through validation
- generated prose field leakage into candidate drafts
- memory/canon leakage via forbidden fields or destinations
- package/dependency bloat if implementation drifts beyond standard library
- over-widening into real extraction too early before owner approval
- clone directories accidentally vendored into `backend/` or app runtime files
- source-cache ignore rule drift (if `.git/info/exclude` is reverted, `.external_sources/` becomes staged again)
