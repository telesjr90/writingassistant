# PHASE8-IMPL-007

## ID

`PHASE8-IMPL-007`

## Title

Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation

## Goal

Publish the implementation parent that satisfies the expected-red `tests/test_writer_assistant_core_booknlp_adapter_contract.py` contract from `PHASE8-IMPL-006` by implementing the pure module `backend/story_knowledge/booknlp_adapter_contract.py`. The implementation must be pure, deterministic, mocked-fixture based, standard-library only, free of filesystem I/O, free of package or tool import, free of real BookNLP or spaCy execution, free of routes/UI, and free of memory/canon mutation. Because the owner has already cloned the official source repositories into local read-only `.external_sources/` directories, `PHASE8-IMPL-007` must begin with a read-only official source inventory child before any adapter implementation, so the pure mocked adapter reflects the actual structure and naming of the official sources where useful.

## Why Now

`PHASE8-IMPL-006` closed the evidence-first extraction foundation and BookNLP-ready adapter strategy. It intentionally left the future production module `backend.story_knowledge.booknlp_adapter_contract` unimplemented and produced an expected-red contract test file. The expected-red state is the only remaining future-red handoff in the Phase 8 frontier. Implementing the pure mocked module is now the right next parent because:

- Source maps, source locators, evidence records, extraction run provenance, and raw output references already exist as pure validation helpers in `backend/story_knowledge/source_map.py` and `backend/story_knowledge/evidence.py`.
- The mocked BookNLP-like fixture shapes, raw artifact kinds, run manifest policy, and adapter normalization boundaries were already accepted in `PHASE8-IMPL-006-T005`.
- The expected-red contract test file already defines the future API surface (`validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, `build_booknlp_candidate_drafts`).
- The owner has now cloned the official source repositories (`.external_sources/booknlp`, `.external_sources/dramatica-flow`, `.external_sources/narrative-context-protocol`, `.external_sources/subtxt-docs`) for read-only inspection, so a source inventory child should run before implementation to confirm or refine the mocked fixture shapes, the source-level forbidden runtime dependency terms, and the boundary rules without installing, executing, or vendoring any of those repositories.

## Dependencies

- Completed parent: `PHASE8-IMPL-006` - Writer Assistant Core evidence-first extraction foundation and BookNLP-ready adapter strategy.
- Completed child: `PHASE8-IMPL-006-T007` - Roadmap/status closeout.
- Decision inputs:
  - `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-first-booknlp-ready-scope-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-source-map-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md`
- Source evidence inputs:
  - `docs/feasibility.md`
  - `docs/booknlp.md`
  - `docs/dramaticaflow.md`
  - `docs/subtxt.md`
  - `docs/ncp.md`
- Existing helpers and tests:
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `tests/test_writer_assistant_core_source_evidence_contract.py`
  - `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
- Read-only local source cache (for T002 inventory only):
  - `.external_sources/booknlp`
  - `.external_sources/dramatica-flow`
  - `.external_sources/narrative-context-protocol`
  - `.external_sources/subtxt-docs`

## Source Inventory Inputs (T002)

The owner has already cloned the official source repositories into local read-only paths under `.external_sources/`. These clones exist solely so a later child task can perform a read-only source inventory. They are not app dependencies, must not be vendored into `backend/`, must not be committed, and must remain protected via `.git/info/exclude`.

Local clone paths:

- `.external_sources/booknlp`
- `.external_sources/dramatica-flow`
- `.external_sources/narrative-context-protocol`
- `.external_sources/subtxt-docs`

T002 may inspect these clones read-only. T002 must not:

- clone, fetch, or pull from any remote
- install, run, or import any package from these repositories
- copy or vendor external source code into `backend/` or any app runtime file
- execute any code from these repositories
- build documentation from these repositories

T002 should record:

- the commit SHA of each local clone (so future work can refer back if the owner refreshes the clones)
- which directories/files matter for output shapes, schema fields, and safety boundaries
- the highest-priority BookNLP output files and parser-relevant schema/fields
- dramatica-flow unsafe generation/write paths versus safe analysis-only concepts
- NCP schema/import-export boundaries
- Subtxt docs rubric/semantic guardrail boundaries
- any source-level forbidden runtime dependency terms that future production modules must avoid

T001 does not perform detailed source review. T001 only confirms that the four `.external_sources/` paths exist, contain the expected repository structure, and are protected from commit. Detailed source review belongs to T002.

## Source Inventory Result (T002)

`PHASE8-IMPL-007-T002` is complete as of 2026-06-20.

Created artifacts:

- `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`
- `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`

Local repo SHAs verified with explicit `/usr/bin/git --git-dir` and `--work-tree` probing because plain `git -C` was observed during the interrupted run to misresolve to the parent repository:

- BookNLP: `3d900fc2224e55960c3363826ae28539b77b4204`
- dramatica-flow: `890f099bfcb64adbf407fd83ab708c48e92b0766`
- Narrative Context Protocol: `b1222748376aae3d309176b3bb5afb884eb281ea`
- Subtxt docs: `ec66121364c039693314dcce4cde464e497bece4`

Source-cache safety result:

- `.external_sources/` is ignored by `.git/info/exclude`.
- `/usr/bin/git status --short -- .external_sources` returned clean.
- `/usr/bin/git status --short --ignored -- .external_sources` returned `!! .external_sources/`.
- No `.external_sources/` files were staged or modified.

T002 confirmed:

- BookNLP real examples contain `.tokens`, `.entities`, `.quotes`, `.supersense`, `.book`, and `.book.html`.
- BookNLP has no separate `.events` file in the inspected example output; `booknlp_events` must be treated as an app-owned derived abstraction from `.tokens.event`.
- BookNLP token offsets are byte offsets; app source locators still need careful byte-to-character source-map bridging.
- BookNLP coreference, quote attribution, and event flags remain candidate evidence only.
- dramatica-flow remains blocked/deferred as runtime because the inspected source exposes generation, continuation, rewrite, write/revise, LLM, and world-state/truth-like mutation surfaces.
- NCP remains a future approved-context import/export reference only and must not silently rewrite Storyform/Subtext or become automatic truth.
- Subtxt docs remain semantic guardrail/reference only because of CC BY-NC-SA terms and because the docs provide conceptual guidance, not automatic classifier truth.

T002 did not implement the adapter, did not change tests, did not run BookNLP/spaCy/dramatica-flow/NCP/Subtxt tooling, did not install dependencies, did not execute or vendor external repo code, did not add runtime extraction, did not add backend routes/frontend UI/package changes/project runtime files, did not generate prose, did not mutate memory/canon, and did not stage/commit/push.

## Implementation Decision Result (T003)

`PHASE8-IMPL-007-T003` is complete as of 2026-06-20.

Decision artifact:

- `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`

T003 accepted a staged implementation split:

- T004 creates `backend/story_knowledge/booknlp_adapter_contract.py`, creates all six public API symbols for import/collection, and implements manifest plus raw artifact bundle validators first.
- T005 implements mocked entity, quote, and event normalization helpers.
- T006 implements or hardens the candidate draft builder, fail-closed behavior, and source/boundary checks.
- T007 closes the parent.

T003 raw-vs-normalized decision:

- Raw BookNLP-like fixture inputs should reflect T002-verified source names where practical.
- Adapter-normalized internal records and candidate drafts may use app-owned fields such as `source_locator`, `confidence`, `raw_output_refs`, `normalization_status`, `candidate_type`, `target_category`, `evidence`, and `provenance`.
- Current T006 tests mostly use app-normalized mocked dictionaries; T004 should preserve them where they are testing normalized adapter behavior.

T003 fixture correction policy:

- T004 may make minimal contract-test fixture corrections only if needed to align tests with T002 verified source inventory.
- The main authorized correction is clarifying that `booknlp_events` is app-derived from `.tokens.event`, not a real raw BookNLP output file.
- T004 must not delete safety tests, weaken boundaries, change public API names, add real dependencies, or widen into a real parser.

T003 event, offset, and guardrail decisions:

- `booknlp_events` is app-owned derived support from `.tokens.event`.
- BookNLP byte offsets are raw support only; app-owned `source_locator`/evidence remains required for candidate drafts.
- Full byte-to-character source snapshot matching is deferred.
- `.book` `g` is raw aggregate metadata only, not gender identity.
- Coreference clusters, quote attribution, and event flags remain candidate evidence only and must fail closed when ambiguous.

T003 did not implement the adapter, did not modify tests, did not change backend/frontend/package/project runtime files, did not run BookNLP or spaCy, did not install packages, did not execute or vendor external repo code, did not run context tools, did not generate prose, did not mutate memory/canon, and did not stage/commit/push.

## Scope

Include:

- read-only official source inventory of the four `.external_sources/` clones via T002 before implementation
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

## Exclusions

- real BookNLP install or execution
- real BookNLP output parsing from files
- spaCy install or execution
- dramatica-flow runtime
- NCP import/export implementation
- Subtxt classifier or rubric runtime
- extraction orchestrator implementation
- raw output storage writers
- candidate JSON persistence from adapter output
- backend extraction routes
- frontend extraction/review UI
- package/dependency changes
- model calls, Ollama calls, or any HTTP/network call
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion
- automatic Storyform truth, automatic Dramatica/Subtxt labels, or automatic CIPS/dynamics/RS/IC truth
- apply-promotion
- memory/canon mutation
- cloning, fetching, or pulling from any external remote
- executing, importing, or vendoring external repository code into `backend/`
- training data, JSONL records, dataset artifacts, or manifest changes
- staging, committing, or pushing in T001

## Child-Task Plan

1. `PHASE8-IMPL-007-T001` - Publish BookNLP adapter contract implementation parent and source-inventory-aware child-task plan. Status: in progress at start of T001; complete on T001 success.
2. `PHASE8-IMPL-007-T002` - Official repo retrieval/source inventory and implementation contract refresh. Status: complete.
3. `PHASE8-IMPL-007-T003` - BookNLP adapter implementation decision after source inventory. Status: complete.
4. `PHASE8-IMPL-007-T004` - Manifest and raw artifact bundle validators. Status: complete.
5. `PHASE8-IMPL-007-T005` - Entity/quote/event mocked normalization helpers. Status: complete.
6. `PHASE8-IMPL-007-T006` - Candidate draft builder, fail-closed behavior, and boundary hardening. Status: ready/active.
7. `PHASE8-IMPL-007-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-007-T001` - Publish BookNLP adapter contract implementation parent and source-inventory-aware child-task plan

- Docs/status/planning only.
- Publish parent task record, inventory, enrichment JSON, and roadmap/status updates.
- Mark `PHASE8-IMPL-007` active.
- Mark `PHASE8-IMPL-007-T001` complete on success.
- Mark `PHASE8-IMPL-007-T002` ready/active.
- Confirm that the four `.external_sources/` clones exist and are ignored/protected from commit.
- No runtime code, no tests, no implementation.

### `PHASE8-IMPL-007-T002` - Official repo retrieval/source inventory and implementation contract refresh

- Docs/inventory plus docs/decision only.
- Status: complete as of 2026-06-20.
- Inventory artifact: `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`.
- Use the already-cloned local repositories under `.external_sources/`. Do not clone, fetch, or pull.
- Record the commit SHA of each local clone.
- Inspect only README, LICENSE, package metadata, docs, schemas, and files relevant to output shapes, schema fields, and safety boundaries.
- Highest priority: BookNLP output files and parser-relevant schema/fields.
- Secondary: dramatica-flow unsafe generation/write paths versus safe analysis-only concepts.
- Secondary: NCP schema/import-export boundaries.
- Secondary: Subtxt docs rubric/semantic guardrail boundaries.
- Update or confirm the `PHASE8-IMPL-007` implementation decision based on the inventory.
- Refresh the source-level forbidden runtime dependency term list if the inventory reveals additional terms.
- Do not install, run, import, vendor, or execute external repository code.

### `PHASE8-IMPL-007-T003` - BookNLP adapter implementation decision after source inventory

- Docs/decision only.
- Status: complete as of 2026-06-20.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`.
- Use the T002 source inventory.
- Decide exact implementation boundaries for `backend/story_knowledge/booknlp_adapter_contract.py`.
- Decide whether implementation should be one child or split into validators/normalizers.
- Decide whether current T006 tests need fixture correction before implementation.
- Decide whether T004 should create stubs for all APIs.
- Decide source-level forbidden terms based on T002 findings.
- Decide raw-shape vs normalized-shape naming.
- Decide event derivation from `.tokens.event`.
- Decide BookNLP byte offsets vs app character offsets.
- Confirm exact source-level forbidden terms to avoid.
- Confirm real BookNLP remains deferred.
- No runtime code or tests.
- Result: accepted staged implementation with T004 validators/API symbols first, T005 mocked normalizers, T006 builder/hardening, raw-shape versus normalized-shape separation, minimal fixture correction authorization, event derivation from `.tokens.event`, byte-offset guardrails, `g` identity guardrail, and coreference/quote attribution uncertainty guardrails.

### `PHASE8-IMPL-007-T004` - Manifest and raw artifact bundle validators

- Status: complete as of 2026-06-20.
- Created `backend/story_knowledge/booknlp_adapter_contract.py`.
- Exposed all six public API symbols:
  - `validate_booknlp_run_manifest`
  - `validate_booknlp_raw_artifact_bundle`
  - `normalize_booknlp_entity_mentions`
  - `normalize_booknlp_quotes`
  - `normalize_booknlp_events`
  - `build_booknlp_candidate_drafts`
- Implemented run manifest validation and raw artifact bundle validation.
- Implemented minimal in-memory mocked entity/quote/event draft shaping because the current contract tests assert candidate draft behavior during T004.
- No persistence, no real parser, no source snapshot byte-to-character matching, and no runtime extraction were added.
- Validate raw-like aliases and app-normalized mocked fixture shapes used by the contract.
- Treat `booknlp_events` as app-derived from `.tokens.event`, not as a real raw output file.
- Preserve BookNLP byte offsets as raw support but require app-owned source locators/evidence for successful candidate drafts.
- Keep `g` as raw aggregate metadata only, not identity.
- Test fixture correction: none.
- Validation results:
  - `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_booknlp_adapter_contract.py -q`: PASS, 148 passed.
- Treat coreference, quote attribution, and events as candidate evidence only.
- Avoid forbidden substrings in production source if source-level tests scan raw module text.
- No real BookNLP/spaCy install or execution.
- No filesystem I/O, no project file creation, no candidate JSON writes.
- No routes, UI, or package changes.

### `PHASE8-IMPL-007-T005` - Entity/quote/event mocked normalization helpers

- Status: complete as of 2026-06-20.
- Path: validation-only. T004 supplied the needed mocked normalizer behavior early, and T005 found no runtime or test repair gap.
- Reviewed mocked normalization helpers:
  - `normalize_booknlp_entity_mentions`
  - `normalize_booknlp_quotes`
  - `normalize_booknlp_events`
- Confirmed outputs remain candidate draft shapes only.
- Confirmed entity mentions, quotes, and events remain in-memory and are not persisted candidate records.
- Confirmed source locators, evidence records, provenance, confidence, raw output references, and normalization status are present where current contract tests require them.
- Confirmed unsupported entity types, invalid confidence, missing source locators, ambiguous speaker attribution, and unusable events fail closed through `insufficient_evidence`, `rejected_output`, or `ValueError`.
- Confirmed `booknlp_events` remains app-derived support from `.tokens.event`, not a real raw BookNLP file.
- Confirmed BookNLP byte offsets remain raw support only; no byte-to-character source snapshot matching or source-span guessing is implemented.
- Confirmed `.book` `g` data is not converted into identity or demographic claims.
- Confirmed `COREF`, `char_id`, speaker mentions, and event flags remain uncertain extraction signals only.
- Runtime changes: none.
- Test changes: none.
- Validation results:
  - `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_booknlp_adapter_contract.py -q`: PASS, 148 passed.
- No persistence writes.
- No candidate JSON writes.
- No memory/canon mutation.
- No generated prose.
- No real BookNLP execution.

### `PHASE8-IMPL-007-T006` - Candidate draft builder, fail-closed behavior, and boundary hardening

- Status: ready/active after T005.
- Implement `build_booknlp_candidate_drafts`.
- Combine mocked entity/quote/event normalization outputs.
- Enforce fail-closed behavior.
- Ensure no promoted status, no promote owner decision, no forbidden destinations, no canon/memory mutation fields.
- Run targeted contract/regression tests.
- No new runtime scope beyond `backend/story_knowledge/booknlp_adapter_contract.py`.
- No package/tool install.

If T004-T005 already make the full contract green, T006 should be validation-only and record no runtime changes unless required.

### `PHASE8-IMPL-007-T007` - Roadmap/status closeout

- Close the parent.
- Summarize source inventory, module, helpers, and tests.
- Record that the adapter contract implementation is mocked only.
- Recommend the next parent:
  - real BookNLP schema parser/spike, or
  - raw output storage helpers, or
  - extraction orchestrator contract, or
  - candidate review UI,
  depending on validation results.
- No runtime expansion.

## Acceptance Criteria

- `PHASE8-IMPL-007` is published and active in roadmap docs.
- `PHASE8-IMPL-007-T001` is complete on success.
- `PHASE8-IMPL-007-T002` is complete with source inventory and implementation refresh decision artifacts.
- `PHASE8-IMPL-007-T003` is complete with implementation decision artifact.
- `PHASE8-IMPL-007-T004` is ready/active after T003.
- `PHASE8-IMPL-007-T005` through `PHASE8-IMPL-007-T007` are registered as planned.
- `PHASE8-IMPL-006` remains complete through `PHASE8-IMPL-006-T007`.
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py` is the primary future-implementation target test file and remains expected-red until later children implement `backend/story_knowledge/booknlp_adapter_contract.py`.
- T001 confirms the four `.external_sources/` clones exist locally.
- T001 confirms `.external_sources/` is protected from accidental commit (via `.git/info/exclude`).
- T001 does not stage, commit, or push anything.
- T001 records the expected-red BookNLP adapter handoff from `PHASE8-IMPL-006-T006`.
- T001 records `.external_sources/` as a local read-only evidence cache for T002.
- T003 does not implement the BookNLP adapter.
- T003 does not modify tests.
- T003 does not implement extraction, candidate creation, candidate persistence, routes, UI, package changes, generated prose, apply-promotion, memory/canon mutation, or training/JSONL/dataset work.

## Validation Expectations

For `PHASE8-IMPL-007-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- non-LeanCTX whitespace check on changed docs
- narrow `git diff --check` on changed docs if local hooks allow without LeanCTX; otherwise record as blocked by local tooling policy and rely on the explicit non-LeanCTX whitespace check plus roadmap validators
- source-cache safety check: `git status --short -- .external_sources`, `git check-ignore -v .external_sources/booknlp`, `git check-ignore -v .external_sources/dramatica-flow`, `git check-ignore -v .external_sources/narrative-context-protocol`, `git check-ignore -v .external_sources/subtxt-docs`

Do not run pytest because no tests or runtime code should change in T001. Do not run app servers, frontend build, browser validation, model calls, Ollama, BookNLP, spaCy, CCE, Graphify, Repomix, AI Context, MCP tools, LeanCTX, external repo clone/fetch/pull, package install, demos, or tool execution.

For later children (recorded here for context, executed in their own tasks):

- `PHASE8-IMPL-007-T002` should run roadmap validators and the non-LeanCTX whitespace check.
- `PHASE8-IMPL-007-T003` should run roadmap validators and the non-LeanCTX whitespace check.
- `PHASE8-IMPL-007-T004`-`T006` may run targeted contract pytest, candidate regression pytest, roadmap validators, and the non-LeanCTX whitespace check. BookNLP adapter contract pytest is expected to transition from red to green across T004-T006. No full pytest. No external tools. No app servers.

## Safety / Product Boundaries

- The app is analysis-only.
- BookNLP output is never canon.
- BookNLP-like outputs in this parent are mocked fixtures only.
- Real BookNLP install/run remains deferred.
- spaCy install/run remains deferred.
- Candidate drafts are not persisted or promoted in this parent unless a later child explicitly scopes it.
- Owner review remains mandatory.
- No prose generation, rewrite, continuation, imitation, polish, improvement, or expansion.
- No automatic Storyform truth, automatic Dramatica/Subtxt labels, automatic CIPS/dynamics/RS/IC truth, or automatic canon mutation.
- No apply-promotion, no memory/canon mutation.
- `.external_sources/` is a local read-only evidence cache and must not be vendored into `backend/`, copied into app runtime files, committed, or run.
- T001 does not run context tools, CCE, Graphify, Repomix, AI Context, MCP tools, or LeanCTX.
- T001 does not run external tools, install packages, clone repositories, retrieve web sources, or run BookNLP/spaCy/dramatica-flow/NCP/Subtxt code.

## Current Status

`PHASE8-IMPL-007` is active. Last completed parent: `PHASE8-IMPL-006` - Writer Assistant Core evidence-first extraction foundation and BookNLP-ready adapter strategy. Last completed child under this parent: `PHASE8-IMPL-007-T005` - Entity/quote/event mocked normalization helpers. Active child: `PHASE8-IMPL-007-T006` - Candidate draft builder, fail-closed behavior, and boundary hardening. Next child: `PHASE8-IMPL-007-T007` - Roadmap/status closeout. Prior completed parents: `PHASE8-IMPL-001` through `PHASE8-IMPL-006`. Recommended next parent after `PHASE8-IMPL-007` closes will depend on T006 outcomes.

T003 is complete as docs/decision only. It accepted the exact implementation split and handoff for T004-T006 without implementing the BookNLP adapter, changing tests, changing runtime code, changing package/dependency files, running tools, calling models, generating prose, applying promotion, or mutating memory/canon.

T004 is complete. T004 created the pure standard-library-only mocked adapter-contract module, implemented manifest and raw artifact bundle validators, exposed all public APIs, and added minimal in-memory draft shaping required by the current contract tests. The targeted BookNLP adapter contract test now passes. T005 is complete as validation-only after reviewing the early mocked entity/quote/event normalization behavior and finding no repair gap. T006 is ready/active to review or harden the candidate draft builder and fail-closed boundaries.

## Final Parent Goal (Deferred to T007)

After T007 closes the parent, the final artifact is a pure mocked BookNLP adapter contract implementation that:

- makes `tests/test_writer_assistant_core_booknlp_adapter_contract.py` pass
- provides `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, and `build_booknlp_candidate_drafts` as pure standard-library-only functions
- integrates with existing pure source-map and evidence validation helpers
- fails closed on invalid manifests, invalid bundles, missing source locators, invalid offsets, missing hashes, mutation/prose fields, unsupported candidate types, invalid confidence, and ambiguous speaker attribution
- preserves no-prose, no-canon-mutation, no-auto-promotion, and no-runtime-extraction boundaries

The final recommended next parent after `PHASE8-IMPL-007` will be one of:

- real BookNLP schema parser/spike (only after explicit owner approval)
- raw output storage helpers
- extraction orchestrator contract
- candidate review UI

## Deferred Beyond PHASE8-IMPL-007

- Real BookNLP install.
- Real BookNLP execution.
- Real BookNLP output parsing from files.
- Raw output storage writers.
- Extraction orchestrator implementation.
- Candidate creation from real raw outputs.
- Candidate JSON persistence from adapter output.
- Backend extraction routes.
- Frontend extraction/review UI.
- Source snapshot text matching helper.
- Relationship network extraction.
- Timeline causality extraction.
- Subtxt semantic rubric implementation.
- NCP import/export implementation.
- dramatica-flow-inspired rubric implementation.
- Model-assisted extraction.
- Apply-promotion.
- Memory/canon mutation.
- Training/JSONL/dataset work.
- Cloning, fetching, or pulling from any external remote into the repo.
- Vendoring or executing external repository code from `.external_sources/` into `backend/`.
- Staging, committing, or pushing any `.external_sources/` content.

## Final Boundaries at T001

- No runtime extraction exists yet.
- No BookNLP or spaCy package was installed or run.
- No `backend/story_knowledge/booknlp_adapter_contract.py` implementation exists yet.
- No backend routes, frontend UI, package/dependency files, project runtime files, memory/canon mutation, apply-promotion, model calls, generated prose, rewrite, continuation, training data, JSONL records, datasets, or manifests were added.
- `.external_sources/` is protected from accidental commit via `.git/info/exclude`.
