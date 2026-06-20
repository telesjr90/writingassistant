# PHASE8-IMPL-008

## ID

`PHASE8-IMPL-008`

## Title

Writer Assistant Core raw extraction artifact storage and BookNLP fixture parser contract

## Status

active (after T001 publication).

## Goal

Publish the next safe Writer Assistant Core parent after the completed `PHASE8-IMPL-007` mocked BookNLP adapter contract implementation. `PHASE8-IMPL-008` prepares the raw extraction artifact storage boundary and the BookNLP-like fixture parser contract before any real extractor runtime exists. The parent defines and tests:

- a project-local raw extraction artifact storage root and run-folder shape under `projects/{project_id}/writer_assistant/extractions/{tool_name}/{run_id}/`,
- pure path and manifest helper contracts for the future `booknlp` extraction storage,
- a mocked BookNLP-like TSV/JSON fixture parser contract that turns in-memory fixture text into in-memory raw artifact bundles suitable for `validate_booknlp_raw_artifact_bundle`,
- explicit non-canon, non-candidate, non-runtime, non-package boundaries for raw extraction artifacts and parsed fixture output,
- and a deferred plan for a real BookNLP installation and runtime that remains out of scope for this parent.

`PHASE8-IMPL-008` does not run real BookNLP, does not run spaCy, does not create raw artifacts in real project folders outside tests, does not implement extraction routes, does not implement a frontend review UI, and does not change package or dependency files.

## Why Now

`PHASE8-IMPL-007` closed the pure mocked BookNLP adapter contract implementation and normalization foundation: `backend/story_knowledge/booknlp_adapter_contract.py` now exposes `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, and `build_booknlp_candidate_drafts`, plus source/evidence/provenance/raw-ref integration and fail-closed behavior. The mocked adapter still consumes raw artifact bundles that are produced in tests and not from disk. Before any real BookNLP installation or runtime, the app needs:

- a safe project-local storage boundary for raw extraction artifacts (run folders, manifest, raw TSV/JSON, optional `book.html` raw ref),
- pure path and manifest helper contracts that the future extraction orchestrator can call without expanding into routes, UI, or package changes,
- a mocked BookNLP-like fixture parser contract that converts in-memory fixture text into raw artifact bundles acceptable to the existing `validate_booknlp_raw_artifact_bundle` API, so future extraction tests and review flows can exercise the full pipeline without real BookNLP,
- and explicit non-canon, non-candidate guardrails so raw extraction artifacts and parsed fixture output never become approved truth, never become OMI candidate records by default, and never trigger apply-promotion.

This is the right next parent because it builds on the completed mocked adapter contract, keeps BookNLP and spaCy install/run deferred, and prepares the next safe layer for a future `PHASE8-IMPL-009` parser implementation and integration parent.

## Dependencies

- Completed parent: `PHASE8-IMPL-007` - Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation.
- Completed child: `PHASE8-IMPL-007-T007` - Roadmap/status closeout.
- Foundation modules and tests:
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `backend/story_knowledge/booknlp_adapter_contract.py`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`
  - `tests/test_writer_assistant_core_source_evidence_contract.py`
  - `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
- Reference inventory and decisions:
  - `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`
- Source evidence (read-only, already inventoried):
  - `docs/feasibility.md`
  - `docs/booknlp.md`
  - `docs/dramaticaflow.md`
  - `docs/subtxt.md`
  - `docs/ncp.md`
- Read-only local source cache (no new clone, fetch, pull, install, run, import, vendor, or execute):
  - `.external_sources/booknlp`
  - `.external_sources/dramatica-flow`
  - `.external_sources/narrative-context-protocol`
  - `.external_sources/subtxt-docs`

## Scope

Include:

- documentation of the project-local raw extraction artifact storage root and run-folder shape decision,
- documentation of a mocked BookNLP-like fixture parser contract decision (in-memory TSV/JSON fixture text only),
- tests-only contract coverage for the future pure raw artifact storage path and manifest helpers, exercised under `tmp_path` only,
- tests-only contract coverage for the future pure BookNLP fixture parser, exercised with in-memory fixture text and in-memory artifact bundles,
- optional pure path/manifest helpers and pure fixture parser helpers in later children when explicitly authorized by contract tests and T002/T005 decisions,
- validation of the storage and parser contracts against `validate_booknlp_raw_artifact_bundle`,
- fail-closed contract coverage for unsafe project identifiers, unsafe run identifiers, path traversal, forbidden raw paths, missing manifests, invalid manifest fields, missing artifacts, and forbidden fields,
- explicit non-canon, non-candidate guardrails so raw extraction artifacts and parsed fixture output are never approved truth and never enter the OMI candidate pipeline by default,
- source/evidence/provenance/raw-ref integration so parsed fixture bundles carry source-map, evidence, raw output references, and normalization status where the current `booknlp_adapter_contract` API expects them,
- preservation of the mocked BookNLP adapter boundary and the existing source/evidence and candidate contract regressions.

## Exclusions

Explicitly excluded in this parent:

- real BookNLP install, run, import, or execution,
- real BookNLP output file parsing from disk produced by a real BookNLP process,
- real spaCy install, run, or execution,
- real extraction orchestrator that reads project scenes, calls any extractor, and persists candidate records,
- raw artifact writes into real project folders outside tests,
- candidate JSON persistence from parsed fixture output,
- backend extraction routes or extraction API endpoints,
- frontend extraction, review, or parse-preview UI,
- package or dependency file changes,
- model calls, Ollama calls, dramatica-flow, NCP, or Subtxt runtime,
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion of owner-authored story prose,
- automatic Storyform truth, automatic Dramatica/Subtxt labels, automatic CIPS/dynamics/RS/IC truth, or automatic canon mutation,
- apply-promotion,
- memory/canon mutation,
- cloning, fetching, or pulling from any external remote,
- executing, importing, or vendoring external repository code from `.external_sources/` into `backend/` or any app runtime file,
- training data, JSONL records, dataset artifacts, or manifest changes,
- staging, committing, or pushing in T001,
- `.external_sources/` content commits,
- raw extraction artifact files written into real project runtime folders (only `tmp_path` test directories are allowed in later children if explicitly authorized).

## Child-Task Plan

1. `PHASE8-IMPL-008-T001` - Publish raw extraction artifact storage and BookNLP fixture parser contract parent. Status: complete on success of T001.
2. `PHASE8-IMPL-008-T002` - Raw extraction artifact storage contract decision. Status: ready/active after T001.
3. `PHASE8-IMPL-008-T003` - Extraction artifact storage path and manifest contract tests. Status: planned/draft.
4. `PHASE8-IMPL-008-T004` - Minimal extraction artifact storage helpers. Status: planned/draft.
5. `PHASE8-IMPL-008-T005` - BookNLP fixture parser contract decision. Status: planned/draft.
6. `PHASE8-IMPL-008-T006` - BookNLP fixture parser contract tests. Status: planned/draft.
7. `PHASE8-IMPL-008-T007` - Roadmap/status closeout. Status: planned/draft.

## Child Task Details

### `PHASE8-IMPL-008-T001` - Publish raw extraction artifact storage and BookNLP fixture parser contract parent

- Docs/status/planning only.
- Create parent task record at `docs/roadmap/tasks/PHASE8-IMPL-008.md`.
- Create inventory at `docs/roadmap/inventory/PHASE8-IMPL-008.md`.
- Create enrichment JSON at `docs/roadmap/enrichment/PHASE8-IMPL-008.enrichment.json`.
- Mark `PHASE8-IMPL-008` active in `docs/roadmap/roadmap_index.yaml` and `docs/roadmap/implementation_status.md`.
- Register `PHASE8-IMPL-008-T001` through `PHASE8-IMPL-008-T007` per local style.
- Mark `PHASE8-IMPL-008-T001` complete on success.
- Mark `PHASE8-IMPL-008-T002` ready/active.
- Confirm `backend/story_knowledge/booknlp_adapter_contract.py` and `tests/test_writer_assistant_core_booknlp_adapter_contract.py` remain the foundation (no edits).
- Confirm `.external_sources/` is ignored/protected from commit and no `.external_sources/` content is staged.
- No runtime code, no tests, no implementation, no raw artifact writes, no BookNLP/spaCy install/run/import.
- No context tools, no external tools, no source/web retrieval.

### `PHASE8-IMPL-008-T002` - Raw extraction artifact storage contract decision

- Docs/decision only.
- Use the completed `PHASE8-IMPL-007` adapter contract, source/evidence contract, and source inventory as foundation.
- Decide project-local raw extraction artifact storage root: `projects/{project_id}/writer_assistant/extractions/`.
- Decide run-folder shape: `projects/{project_id}/writer_assistant/extractions/{tool_name}/{run_id}/`.
- Decide that the first tool-specific child folder will be `booknlp` for BookNLP-like outputs.
- Decide run identifier format, tool identifier format, and `manifest.json` shape for raw extraction artifacts.
- Decide how the manifest and raw output references integrate with the existing source-map and evidence helpers.
- Decide whether T003 is tests-only.
- Decide forbidden locations (outside `writer_assistant/extractions/`, outside the project tree, absolute paths, path traversal).
- Decide forbidden side effects (no project file mutation, no memory/canon mutation, no candidate persistence from raw artifacts).
- Confirm raw extraction artifacts are non-canon and non-candidate.
- Confirm real BookNLP install/run remains deferred.
- No runtime code, no tests, no implementation, no raw artifact writes, no BookNLP/spaCy install/run/import.

### `PHASE8-IMPL-008-T003` - Extraction artifact storage path and manifest contract tests

- Tests-only contract coverage.
- Expected-red contract tests for the future pure storage path and manifest helper APIs.
- Tests may use `tmp_path` and in-memory dictionaries only; no real project folder writes, no real BookNLP/spaCy runtime.
- Tests must cover safe and unsafe project identifiers, safe and unsafe tool identifiers, safe and unsafe run identifiers, path traversal rejection, manifest validation, forbidden fields, and forbidden locations.
- Tests must confirm raw artifact storage helpers do not mutate project source files, do not write memory/canon, do not create candidate records, and do not promote anything.
- No implementation; no real BookNLP/spaCy install/run; no raw artifacts in real project folders.

### `PHASE8-IMPL-008-T004` - Minimal extraction artifact storage helpers

- Implement only the pure storage path and manifest validation helpers explicitly authorized by T003 contract tests and T002 decision.
- No raw file write/read/list unless T002/T003 explicitly authorize it; even then only `tmp_path` test directories are acceptable in this parent.
- No real BookNLP runtime.
- No routes, no UI, no package/dependency changes, no project runtime file creation.
- No candidate JSON persistence from raw artifacts.
- No memory/canon mutation.
- No apply-promotion.

### `PHASE8-IMPL-008-T005` - BookNLP fixture parser contract decision

- Docs/decision only.
- Use T002 verified source inventory facts about BookNLP real output fields and the existing `PHASE8-IMPL-007` mocked adapter contract.
- Decide the mocked BookNLP-like fixture parser API surface, in-memory TSV/JSON fixture text shapes, and how parser output feeds `validate_booknlp_raw_artifact_bundle`.
- Confirm the parser is in-memory only; no filesystem read of real BookNLP output.
- Confirm the parser never writes real project artifacts.
- Confirm the parser output remains raw support data and is non-canon and non-candidate.
- Confirm owner review remains mandatory before any future converter turns parsed fixture output into candidate records.
- Decide whether T006 is tests-only and whether parser implementation is deferred to `PHASE8-IMPL-009`.
- No runtime code, no tests, no implementation, no BookNLP/spaCy install/run/import.

### `PHASE8-IMPL-008-T006` - BookNLP fixture parser contract tests

- Tests-only contract coverage.
- Expected-red contract tests for the future pure fixture parser API.
- Tests use in-memory TSV/JSON fixture text and in-memory raw artifact bundles only.
- No filesystem read of real BookNLP output; no project runtime file creation.
- Tests must cover safe and unsafe fixture shapes, missing required fields, extra forbidden fields, byte-to-character offset boundary handling, and downstream compatibility with `validate_booknlp_raw_artifact_bundle`.
- Tests must confirm parsed fixture output is in-memory and is not persisted, not promoted, and not converted into candidate records by the parser.
- No implementation; no real BookNLP/spaCy install/run; no raw artifacts in real project folders.

### `PHASE8-IMPL-008-T007` - Roadmap/status closeout

- Docs/status closeout only.
- Close `PHASE8-IMPL-008` as complete.
- Summarize T002/T005 decisions, T003/T006 tests-only contract coverage, and T004 minimal storage helpers.
- Preserve no-runtime-extraction, no-real-BookNLP/spaCy, no-route, no-UI, no-package-change, no-canon-mutation, no-apply-promotion, no-generated-prose boundaries.
- Recommend the next parent: `PHASE8-IMPL-009` - BookNLP fixture parser helper implementation and raw artifact bundle integration (parser implementation deferred from T006 per T005 decision).
- No runtime expansion.

## Recommended Storage Targets (for T002 decision, not implementation in T001)

The T002 decision is expected to record, at minimum:

- storage root: `projects/{project_id}/writer_assistant/extractions/`
- per-tool folder: `projects/{project_id}/writer_assistant/extractions/{tool_name}/`
- per-run folder: `projects/{project_id}/writer_assistant/extractions/{tool_name}/{run_id}/`
- BookNLP-specific folder for the first child slice: `projects/{project_id}/writer_assistant/extractions/booknlp/{run_id}/`
- expected manifest at `projects/{project_id}/writer_assistant/extractions/booknlp/{run_id}/manifest.json`
- expected raw artifacts: `raw/tokens.tsv`, `raw/entities.tsv`, `raw/quotes.tsv`, `raw/supersense.tsv`, `raw/book.json`, optional `raw/book.html` as raw ref only
- derived event records (`derived/events.json`) only if explicitly authorized by a later child

T001 does not create these paths, files, helpers, or artifacts. T001 only records them as future decision targets for T002.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-008.md` created.
- `docs/roadmap/inventory/PHASE8-IMPL-008.md` created.
- `docs/roadmap/enrichment/PHASE8-IMPL-008.enrichment.json` created.
- `PHASE8-IMPL-008` is registered as active in `docs/roadmap/roadmap_index.yaml` and `docs/roadmap/implementation_status.md`.
- `PHASE8-IMPL-008-T001` is complete on success of T001.
- `PHASE8-IMPL-008-T002` is registered as ready/active.
- `PHASE8-IMPL-008-T003` through `PHASE8-IMPL-008-T007` are registered as planned/draft.
- `PHASE8-IMPL-007` remains complete through `PHASE8-IMPL-007-T007` and the adapter contract module and test file are unchanged.
- `backend/story_knowledge/booknlp_adapter_contract.py` remains the foundation; no edits.
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py` remains the existing contract test file; no edits.
- No runtime extraction is added.
- No raw extraction artifact helpers, files, or paths are created by T001.
- No BookNLP or spaCy install, run, or import is performed.
- No backend routes, frontend UI, package/dependency files, or project runtime files are changed.
- No apply-promotion, no memory/canon mutation, no generated prose behavior is added.
- No training data, JSONL records, datasets, or manifests are created or changed.
- No staging, commit, or push is performed.
- `.external_sources/` remains ignored/protected from commit; no `.external_sources/` content is staged.
- No context tools, no external tools, no source/web retrieval, no demos, no model calls, no Ollama calls, no BookNLP/spaCy execution are performed.

## Validation Expectations

For `PHASE8-IMPL-008-T001`:

- `python3 scripts/check_enrichment.py` PASS.
- `python3 scripts/validate_roadmap.py` PASS.
- non-LeanCTX whitespace check on changed docs PASS.
- narrow `git diff --check` on changed docs (if local hooks allow without LeanCTX) PASS; otherwise record as blocked by local tooling policy and rely on the explicit non-LeanCTX whitespace check plus the two roadmap validators.
- source-cache safety checks PASS:
  - `/usr/bin/git status --short -- .external_sources` empty/clean.
  - `/usr/bin/git status --short --ignored -- .external_sources | head -50` shows `!! .external_sources/`.
  - if `.external_sources/` is untracked, report PARTIAL.

Do not run pytest because no tests or runtime code change in T001. Do not run app servers, frontend build, browser validation, model calls, Ollama, BookNLP, spaCy, CCE, Graphify, Repomix, AI Context, MCP tools, LeanCTX, external repo clone/fetch/pull, package install, demos, or tool execution. Do not stage, commit, or push.

For later children (recorded here for context, executed in their own tasks):

- `PHASE8-IMPL-008-T002` should run roadmap validators and the non-LeanCTX whitespace check.
- `PHASE8-IMPL-008-T003` should add expected-red contract tests; targeted pytest may remain red or green depending on T002/T005 scope, but no real BookNLP/spaCy runtime and no real project folder writes are allowed.
- `PHASE8-IMPL-008-T004` should run targeted storage helper contract pytest, the existing source/evidence and BookNLP adapter contract regression pytest, the candidate contract regression pytest, the focused OMI/project regression pytest, roadmap validators, and the non-LeanCTX whitespace check. No real BookNLP/spaCy install/run. No real project folder writes. No full pytest. No external tools. No app servers. No frontend build.
- `PHASE8-IMPL-008-T005` should run roadmap validators and the non-LeanCTX whitespace check.
- `PHASE8-IMPL-008-T006` should add expected-red contract tests; targeted pytest may remain red or green depending on T005 scope, but no real BookNLP/spaCy runtime and no real project folder writes are allowed.
- `PHASE8-IMPL-008-T007` should run the full focused pytest set, roadmap validators, the non-LeanCTX whitespace check, the narrow `git diff --check`, and the source-cache safety checks. No full pytest. No external tools. No app servers. No frontend build. No BookNLP/spaCy install/run/import.

## Safety / Product Boundaries

- The app is analysis-only.
- Raw extraction artifacts are never canon, never project truth, and never memory/canon records.
- Raw extraction artifacts are never OMI candidate records and never enter the candidate pipeline by default; a future reviewed converter must explicitly create candidate records.
- BookNLP-like outputs in this parent are mocked fixtures only.
- Real BookNLP install/run remains deferred.
- spaCy install/run remains deferred.
- Parsed fixture output remains raw support data only; it is not promoted and is not memory/canon.
- Owner review remains mandatory before any future converter or apply-promotion can change memory/canon.
- No prose generation, rewrite, continuation, imitation, polish, improvement, or expansion.
- No automatic Storyform truth, automatic Dramatica/Subtxt labels, automatic CIPS/dynamics/RS/IC truth, or automatic canon mutation.
- No apply-promotion, no memory/canon mutation.
- `.external_sources/` is a local read-only evidence cache and must not be vendored into `backend/`, copied into app runtime files, committed, or run.
- T001 does not run context tools, CCE, Graphify, Repomix, AI Context, MCP tools, or LeanCTX.
- T001 does not run external tools, install packages, clone repositories, retrieve web sources, or run BookNLP/spaCy/dramatica-flow/NCP/Subtxt code.
- T001 does not write raw extraction artifact files, helpers, or paths.
- T001 does not modify `backend/story_knowledge/booknlp_adapter_contract.py` or `tests/test_writer_assistant_core_booknlp_adapter_contract.py`.

## Current Status

`PHASE8-IMPL-008` becomes active after T001. After T001: last completed parent remains `PHASE8-IMPL-007`; last completed child remains `PHASE8-IMPL-007-T007`; active parent is `PHASE8-IMPL-008`; active child is `PHASE8-IMPL-008-T002` (ready/active). Prior completed parents are `PHASE8-IMPL-001` through `PHASE8-IMPL-006`. Recommended future parent (after `PHASE8-IMPL-008` closes) is `PHASE8-IMPL-009` - BookNLP fixture parser helper implementation and raw artifact bundle integration, not yet published.

T001 is docs/status/planning only. It publishes this parent task record, the inventory, the enrichment JSON, and the roadmap/status updates. T001 does not implement extraction, does not create raw artifact helpers, does not create raw artifact files, does not implement a BookNLP fixture parser, does not change the existing mocked adapter contract module or test, does not run BookNLP or spaCy, does not install any package, does not stage/commit/push, and does not run context tools, external tools, or source/web retrieval.

## Deferred Beyond PHASE8-IMPL-008

- Real BookNLP install.
- Real BookNLP execution.
- Real BookNLP output file parsing from files produced by a real extractor runtime.
- Real extraction orchestrator.
- Raw artifact writes into real project folders outside tests.
- Candidate JSON persistence from parsed fixture output.
- Apply-promotion.
- Memory/canon mutation.
- Source snapshot text matching helper.
- Relationship network extraction.
- Timeline causality extraction.
- Subtxt semantic rubric implementation.
- NCP import/export implementation.
- dramatica-flow-inspired rubric implementation.
- Model-assisted extraction.
- Training/JSONL/dataset work.
- Cloning, fetching, or pulling from any external remote into the repo.
- Vendoring or executing external repository code from `.external_sources/` into `backend/`.
- Staging, committing, or pushing any `.external_sources/` content.

## Final Boundaries at T001

- No runtime extraction exists yet.
- No raw extraction artifact storage helpers exist yet.
- No raw extraction artifact files exist yet under any project runtime folder.
- No BookNLP fixture parser exists yet.
- No BookNLP or spaCy package was installed, imported, or run.
- No `backend/story_knowledge/booknlp_adapter_contract.py` implementation change exists in T001.
- No `tests/test_writer_assistant_core_booknlp_adapter_contract.py` change exists in T001.
- No backend routes, frontend UI, package/dependency files, project runtime files, memory/canon mutation, apply-promotion, model calls, generated prose, rewrite, continuation, training data, JSONL records, datasets, or manifests were added.
- `.external_sources/` is protected from accidental commit via `.git/info/exclude`.
