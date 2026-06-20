# PHASE8-IMPL-008 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-008`
- Title: Writer Assistant Core raw extraction artifact storage and BookNLP fixture parser contract
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active (after T001 publication)
- Depends on: completed `PHASE8-IMPL-007` (mocked BookNLP adapter contract implementation and normalization foundation)
- Companion future parent (recommended, not yet published): `PHASE8-IMPL-009` - BookNLP fixture parser helper implementation and raw artifact bundle integration

## 2. Why This Parent Exists

`PHASE8-IMPL-006` established the evidence-first extraction foundation and BookNLP-ready adapter strategy, and produced the expected-red `tests/test_writer_assistant_core_booknlp_adapter_contract.py` for the future production module `backend.story_knowledge.booknlp_adapter_contract`. `PHASE8-IMPL-007` then created that production module as a pure, standard-library-only, mocked-fixture-based implementation, with `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, and `build_booknlp_candidate_drafts`, plus source/evidence/provenance/raw-ref integration and fail-closed behavior. The mocked adapter is fully usable for tests and in-memory review flows, but it does not know where raw extraction artifacts should live on disk and it does not own a parser for BookNLP-like fixture text.

Before any real BookNLP install, the app needs a safe project-local storage boundary for raw extraction artifacts (run folders, manifest, raw TSV/JSON, optional `book.html` raw ref) and a mocked BookNLP-like fixture parser contract that turns in-memory fixture text into raw artifact bundles acceptable to the existing `validate_booknlp_raw_artifact_bundle` API. `PHASE8-IMPL-008` therefore exists to:

- acknowledge the completed mocked adapter contract foundation from `PHASE8-IMPL-007`,
- decide the project-local raw extraction artifact storage root and run-folder shape (T002),
- decide the mocked BookNLP-like fixture parser contract (T005),
- add tests-only contract coverage for both storage and parser (T003, T006),
- optionally add minimal pure path/manifest helpers (T004) and pure fixture parser helpers only if explicitly authorized by later children,
- and preserve non-canon, non-candidate, no-runtime-extraction, no-route, no-UI, no-package-change, no-canon-mutation, no-apply-promotion, and no-generated-prose boundaries.

`PHASE8-IMPL-008` deliberately defers the parser implementation itself to a recommended future parent (`PHASE8-IMPL-009`) so this parent stays at the contract, decision, and tests-only level and avoids widening into a real extractor runtime.

## 3. Existing Inputs

Foundation modules (do not modify in this parent):

- `backend/story_knowledge/source_map.py` - pure source map and source locator validation helpers
- `backend/story_knowledge/evidence.py` - pure evidence record and extraction run provenance validation helpers
- `backend/story_knowledge/booknlp_adapter_contract.py` - pure mocked BookNLP adapter contract module (six public APIs, validators, mocked normalizers, candidate draft builder, fail-closed behavior)
- `backend/story_knowledge/candidate_schema.py` - candidate schema constants
- `backend/story_knowledge/candidate_record.py` - pure candidate record validation helpers
- `backend/story_knowledge/candidate_storage.py` - pure candidate storage path helpers
- `backend/story_knowledge/candidate_persistence.py` - candidate-only JSON write/read/list helpers
- `backend/story_knowledge/candidate_index.py` - derived candidate index build/write/read helpers

Existing test files (do not modify in this parent):

- `tests/test_writer_assistant_core_source_evidence_contract.py` - source/evidence contract coverage
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py` - mocked BookNLP adapter contract coverage

Reference decisions and inventory (read-only evidence):

- `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md` - recorded BookNLP real output kinds (`.tokens`, `.entities`, `.quotes`, `.supersense`, `.book`, `.book.html`), absence of a separate `.events` file, and byte-offset handling
- `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md` - read-only source inventory refresh policy
- `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md` - T003 implementation decision, raw-shape versus normalized-shape policy, event derivation from `.tokens.event`, byte-offset guardrails, `g` identity guardrail, coreference/quote attribution guardrails
- `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-first-booknlp-ready-scope-decision.md` - evidence-first + BookNLP-ready strategy
- `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-source-map-contract-decision.md` - source/evidence contract
- `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md` - BookNLP-ready raw output and adapter contract

Source evidence inputs:

- `docs/feasibility.md`
- `docs/booknlp.md`
- `docs/dramaticaflow.md`
- `docs/subtxt.md`
- `docs/ncp.md`

Read-only local source cache (already cloned, must not be cloned/fetched/pulled, installed, run, imported, vendored, or executed again in this parent):

- `.external_sources/booknlp` - SHA `3d900fc2224e55960c3363826ae28539b77b4204`
- `.external_sources/dramatica-flow` - SHA `890f099bfcb64adbf407fd83ab708c48e92b0766`
- `.external_sources/narrative-context-protocol` - SHA `b1222748376aae3d309176b3bb5afb884eb281ea`
- `.external_sources/subtxt-docs` - SHA `ec66121364c039693314dcce4cde464e497bece4`

## 4. Scope

Include:

- documentation decision for the project-local raw extraction artifact storage root and run-folder shape (T002),
- documentation decision for the mocked BookNLP-like fixture parser contract, in-memory TSV/JSON fixture text shapes, and how parser output feeds `validate_booknlp_raw_artifact_bundle` (T005),
- tests-only contract coverage for the future pure storage path and manifest helper APIs, exercised under `tmp_path` only (T003),
- tests-only contract coverage for the future pure fixture parser API, exercised with in-memory fixture text and in-memory raw artifact bundles only (T006),
- optional pure path and manifest validation helpers (T004) only if explicitly authorized by T003 contract tests and T002 decision,
- optional pure fixture parser helpers only if T005 explicitly widens T006 into tests-first-plus-implementation; otherwise parser implementation is deferred to `PHASE8-IMPL-009`,
- validation of storage and parser contracts against the existing `validate_booknlp_raw_artifact_bundle` API,
- fail-closed contract coverage for unsafe project identifiers, unsafe tool identifiers, unsafe run identifiers, path traversal, forbidden raw paths, missing manifests, invalid manifest fields, missing artifacts, and forbidden fields,
- explicit non-canon, non-candidate guardrails so raw extraction artifacts and parsed fixture output are never approved truth, never OMI candidate records by default, and never trigger apply-promotion,
- source/evidence/provenance/raw-ref integration so parsed fixture bundles carry source-map, evidence, raw output references, and normalization status where the existing `booknlp_adapter_contract` API expects them,
- preservation of the existing mocked BookNLP adapter boundary and the existing source/evidence and candidate contract regressions,
- roadmap/status updates and closeout documentation (T007).

## 5. Non-Scope

Explicitly excluded in this parent:

- real BookNLP install, run, import, or execution,
- real BookNLP output file parsing from files produced by a real BookNLP process,
- real spaCy install, run, or execution,
- real extraction orchestrator that reads project scenes, calls any extractor, and persists candidate records,
- raw artifact writes into real project folders outside tests,
- candidate JSON persistence from parsed fixture output,
- backend extraction routes or extraction API endpoints,
- frontend extraction, review, or parse-preview UI,
- package or dependency file changes,
- model calls, Ollama calls, dramatica-flow runtime, NCP runtime, or Subtxt runtime,
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion of owner-authored story prose,
- automatic Storyform truth, automatic Dramatica/Subtxt labels, automatic CIPS/dynamics/RS/IC truth, or automatic canon mutation,
- apply-promotion,
- memory/canon mutation,
- cloning, fetching, or pulling from any external remote,
- executing, importing, or vendoring external repository code from `.external_sources/` into `backend/` or any app runtime file,
- training data, JSONL records, dataset artifacts, or manifest changes,
- staging, committing, or pushing in T001,
- `.external_sources/` content commits,
- raw extraction artifact files written into real project runtime folders (only `tmp_path` test directories are acceptable in later children if explicitly authorized),
- cloning external source repositories (the existing four `.external_sources/` clones are reused read-only).

## 6. Risks

Include in risk tracking:

- raw extraction artifacts mistaken for approved truth or canon,
- raw extraction artifacts mistaken for OMI candidate records,
- parsed fixture output mistaken for approved truth, canon, or OMI candidate records,
- future storage helpers accidentally writing raw artifacts into real project folders outside tests,
- future storage helpers accidentally writing raw artifacts into forbidden locations (outside `writer_assistant/extractions/`, outside the project tree, absolute paths, path traversal targets),
- future parser tests mistaken for real extraction runtime,
- future parser drifting from real BookNLP output fields,
- unsafe project identifier, tool identifier, or run identifier handling,
- byte/char locator mismatch between raw BookNLP byte offsets and app character offsets,
- quote/speaker/entity/event false positives becoming confident-looking parsed drafts,
- accidental memory/canon mutation via forbidden fields, destinations, or side effects,
- accidental apply-promotion triggered by parsed fixture output,
- accidental BookNLP or spaCy install or execution,
- package/dependency bloat from real BookNLP/spaCy or real extraction dependencies,
- source-cache ignore rule drift (if `.git/info/exclude` is reverted, `.external_sources/` becomes staged again),
- vendor or execute external repository code from `.external_sources/` into `backend/`,
- generate, rewrite, continue, imitate, polish, improve, or expand owner-authored story prose through future fixture parser or storage helpers,
- widen T006 into a real parser implementation and bypass the `PHASE8-IMPL-009` deferral guardrail,
- widen T004 into real project folder writes and bypass the `tmp_path`-only contract,
- bypass the no-route, no-UI, no-package-change boundaries.
