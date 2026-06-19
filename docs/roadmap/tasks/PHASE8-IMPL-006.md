# PHASE8-IMPL-006

## ID

`PHASE8-IMPL-006`

## Title

Writer Assistant Core evidence-first extraction foundation and BookNLP-ready adapter strategy

## Goal

Publish and execute an evidence-first extraction foundation parent that prepares Writer Assistant Core for automated extraction without implementing extraction in T001. The parent prioritizes stable source maps, source locator contracts, an Evidence Ledger/provenance layer, raw tool output policy, candidate normalization, candidate-only persistence boundaries, no-prose/no-model/no-canon guardrails, and a BookNLP-ready adapter contract.

## Why Now

`PHASE8-IMPL-005` completed tool evaluation and extraction strategy through `PHASE8-IMPL-005-T007`. It recommended a spaCy-first local deterministic/rule-assisted extraction foundation.

After closeout, the owner saved follow-up analysis in five local answer files. Those files show the safer next parent is not a generic spaCy-only implementation parent. The next parent should be evidence-first and BookNLP-ready, with spaCy remaining a lightweight baseline/support option and BookNLP becoming the first serious literary extractor candidate once source maps and provenance are stable.

## Dependencies

- Completed parent: `PHASE8-IMPL-005` - Writer Assistant Core tool evaluation and extraction strategy decision.
- Completed child: `PHASE8-IMPL-005-T007` - Roadmap/status closeout.
- Existing candidate infrastructure:
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`

## Evidence Inputs

- `docs/feasibility.md`
- `docs/booknlp.md`
- `docs/dramaticaflow.md`
- `docs/subtxt.md`
- `docs/ncp.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-dramatica-flow-analysis-only-reference-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-ncp-subtxt-structural-interpretation-strategy-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-nlp-extraction-adapter-strategy-decision.md`

## Scope

Include:

- stable source map contracts
- source document locator contracts
- Evidence Ledger design
- extraction run provenance model
- raw tool output storage policy
- candidate normalization contract
- candidate-only persistence boundaries
- no-prose/no-model/no-canon-mutation guardrails
- BookNLP-ready adapter contract
- optional spaCy baseline decision point
- future dramatica-flow-inspired analysis rubric mapping
- future Subtxt semantic guardrail mapping
- future NCP approved-context import/export mapping

## Exclusions

- extraction implementation in T001
- BookNLP install or execution
- spaCy install or execution
- package/dependency changes
- external repository clone
- external tool execution
- context tool execution
- web/source retrieval
- model/Ollama calls
- runtime code
- tests in T001
- backend routes
- frontend UI
- runtime project files
- training data, JSONL records, datasets, or manifests
- generated prose, rewrite, continuation, imitation, polish, improvement, or expansion
- automatic Storyform truth
- apply-promotion
- memory/canon mutation

## Child-Task Plan

1. `PHASE8-IMPL-006-T001` - Publish evidence-first extraction foundation parent and scope decision. Status: complete.
2. `PHASE8-IMPL-006-T002` - Evidence/source-map contract decision. Status: complete; decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-source-map-contract-decision.md`.
3. `PHASE8-IMPL-006-T003` - Evidence/source-map contract tests. Status: complete; test artifact: `tests/test_writer_assistant_core_source_evidence_contract.py`.
4. `PHASE8-IMPL-006-T004` - Minimal source-map/evidence helper implementation. Status: complete; helper modules: `backend/story_knowledge/source_map.py`, `backend/story_knowledge/evidence.py`.
5. `PHASE8-IMPL-006-T005` - BookNLP-ready raw output and adapter contract decision. Status: complete; decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md`.
6. `PHASE8-IMPL-006-T006` - BookNLP-ready adapter contract tests. Status: complete; test artifact: `tests/test_writer_assistant_core_booknlp_adapter_contract.py`; expected-red future module: `backend.story_knowledge.booknlp_adapter_contract`.
7. `PHASE8-IMPL-006-T007` - Roadmap/status closeout. Status: complete.

## Acceptance Criteria

- `PHASE8-IMPL-006` is published and complete in roadmap docs.
- Parent scope is evidence-first + BookNLP-ready, not spaCy-only.
- The five local answer files are referenced as evidence inputs.
- `PHASE8-IMPL-005` remains complete through `PHASE8-IMPL-005-T007`.
- `PHASE8-IMPL-006-T001` is marked complete if successful.
- `PHASE8-IMPL-006-T004` is complete.
- `PHASE8-IMPL-006-T005` is complete if successful.
- `PHASE8-IMPL-006-T006` is complete if successful.
- `PHASE8-IMPL-006-T007` is complete.
- No runtime extraction is claimed.
- No external tools are installed, cloned, or executed.
- No production adapter code is changed in T006.
- No generated prose/rewrite/continuation behavior is added.
- No memory/canon mutation is added.

## Validation Expectations

For `PHASE8-IMPL-006-T006`:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_booknlp_adapter_contract.py -q`
- `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_source_evidence_contract.py tests/test_writer_assistant_core_candidate_schema_contract.py tests/test_writer_assistant_core_candidate_record_contract.py tests/test_writer_assistant_core_candidate_storage_contract.py tests/test_writer_assistant_core_candidate_persistence_contract.py tests/test_writer_assistant_core_candidate_list_contract.py -q`
- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- non-LeanCTX whitespace check on changed T006 files
- narrow `git diff --check` if local hooks allow it without LeanCTX

The targeted BookNLP adapter contract pytest is expected red until the future module exists; acceptable failure is limited to missing `backend.story_knowledge.booknlp_adapter_contract` or missing future API symbols. Do not run full pytest, app servers, frontend build, browser validation, model calls, Ollama, BookNLP, spaCy, CCE, Graphify, Repomix, AI Context, MCP tools, LeanCTX, external repo clone, package install, demos, or tool execution.

## Safety / Product Boundaries

- The app is analysis-only.
- BookNLP is not canon.
- spaCy is not the sole center of this parent.
- dramatica-flow remains analysis-only/reference or future wrapped rubric source.
- Subtxt remains semantic guardrail/rubric source.
- NCP remains approved-context import/export target.
- Owner review remains mandatory.
- All outputs remain candidates until owner approval.
- No automatic canon mutation is allowed.

## Current Status

`PHASE8-IMPL-006` is complete. Last completed child: `PHASE8-IMPL-006-T007` - Roadmap/status closeout. Last completed parent: `PHASE8-IMPL-006`. Prior completed parent: `PHASE8-IMPL-005`. Recommended next parent: `PHASE8-IMPL-007` - Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation.

`PHASE8-IMPL-006-T001` is docs/status/planning only and created the parent, inventory, enrichment JSON, and scope decision.

`PHASE8-IMPL-006-T002` is complete as a docs/decision-only child. It accepted app-owned source document identity, source map, source locator, offset, source hash/snapshot, Evidence Ledger, evidence record, extraction run provenance, raw output, BookNLP-ready mapping, and candidate normalization contracts in `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-source-map-contract-decision.md`. T002 decided that first-slice evidence uses exact Python string character offsets over the UTF-8 decoded source snapshot, keeps byte offsets as future/raw-tool mapping support, treats raw tool outputs and candidates as non-canon, and requires owner review before any approved memory/canon path. T002 does not implement runtime extraction, tests, package/tool installation, backend routes, frontend UI, model calls, generated prose behavior, or memory/canon mutation.

T003 handoff: add tests-first contract coverage, likely in `tests/test_writer_assistant_core_source_evidence_contract.py`, for future `backend.story_knowledge.source_map` and `backend.story_knowledge.evidence` helpers. T003 should cover required fields, allowed source document types, path-safe IDs, hash/snapshot fields, offsets, locator precision, evidence kinds, provenance run type/status values, no arbitrary/external/training paths, candidate-only boundaries, BookNLP-ready raw output references, no generated prose fields, no source-map writes in tests, and no external tool execution. T003 may be expected red until T004 creates helpers.

`PHASE8-IMPL-006-T003` is complete as a tests-first child. It created `tests/test_writer_assistant_core_source_evidence_contract.py`, which defines the future API for `backend.story_knowledge.source_map` and `backend.story_knowledge.evidence`: source document reference validation, source segment validation, source map validation, source locator validation, evidence record validation, extraction run provenance validation, and raw output reference validation. The targeted T003 pytest is expected red until T004 creates the future helper modules; the current failure is limited to the missing `backend.story_knowledge.evidence` import during collection. Existing candidate contract regressions remain green. T003 does not implement runtime extraction, production helpers, package/tool installation, backend routes, frontend UI, model calls, generated prose behavior, or memory/canon mutation.

`PHASE8-IMPL-006-T004` is complete as a narrow pure-helper implementation child. It created `backend/story_knowledge/source_map.py` and `backend/story_knowledge/evidence.py` with standard-library-only validation helpers for source document refs, source segments, source maps, source locators, evidence records, extraction run provenance, and raw output references. The helpers validate shape only, return copies, reject invalid input with `ValueError`, perform no filesystem I/O, create no candidates, write no project files, build no indexes, call no tools/models, and mutate no source, memory, or canon records. The targeted source/evidence contract pytest now passes, existing candidate contract regressions pass, and focused project/OMI regressions pass.

`PHASE8-IMPL-006-T005` is complete as a docs/decision-only child. It accepted `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md` as the BookNLP-ready raw output and adapter contract. The decision defines future BookNLP-like raw artifact kinds, raw output storage boundaries, run manifest shape, raw output reference policy, mocked fixture shapes for T006, adapter normalization boundaries, candidate/evidence mapping expectations, and fail-closed behavior. It chooses `backend.story_knowledge.booknlp_adapter_contract` as the preferred future tests-first module name for T006, with `tests/test_writer_assistant_core_booknlp_adapter_contract.py` as the expected test file. T005 does not install or run BookNLP/spaCy, implement adapter code, create runtime project files, add routes/UI, change code/tests, call models, generate prose, or mutate memory/canon.

T006 handoff: add tests-first BookNLP-ready adapter contract coverage using mocked BookNLP-like fixture dictionaries only. T006 should test mocked token/entity/quote/book JSON/supersense/event artifact shapes, run manifest validation, raw artifact bundle validation, source locator/evidence integration, candidate draft normalization shape, unsupported candidate handling, fail-closed behavior, and no tool execution/package import/filesystem writes/runtime invocation. T006 may be expected red until a later implementation child or parent creates `backend.story_knowledge.booknlp_adapter_contract`.

`PHASE8-IMPL-006-T006` is complete as a tests-first contract child. It created `tests/test_writer_assistant_core_booknlp_adapter_contract.py`, which defines the expected future API for `backend.story_knowledge.booknlp_adapter_contract`: `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, and `build_booknlp_candidate_drafts`. The tests use mocked BookNLP-like in-memory dictionaries only and cover run manifests, raw artifact bundles, mocked token/entity/quote/book JSON/supersense/event artifacts, source locator/evidence integration, entity/quote/event normalization draft shape, combined candidate draft building, fail-closed behavior, runtime/tool boundary source scanning for the future module, and existing helper integration. The targeted T006 pytest is expected red until a later implementation creates the future module; the current failure is limited to `ImportError: cannot import name 'booknlp_adapter_contract' from 'backend.story_knowledge'`. T006 does not implement runtime extraction, create `backend/story_knowledge/booknlp_adapter_contract.py`, install or run BookNLP/spaCy, change package files, add routes/UI, call models, generate prose, apply promotion, mutate memory/canon, create project runtime files, or create training/JSONL/dataset artifacts.

`PHASE8-IMPL-006-T007` is complete as a docs/status closeout child. It closed the parent, recorded final artifacts and behavior, preserved the expected-red BookNLP adapter handoff, and recommended `PHASE8-IMPL-007` as the next parent. T007 did not implement extraction, create `backend/story_knowledge/booknlp_adapter_contract.py`, install or run BookNLP/spaCy, change package files, add routes/UI, create project runtime files, call models, generate prose, apply promotion, mutate memory/canon, or create training/JSONL/dataset artifacts.

## Final Parent Summary

Final result: `COMPLETE`.

`PHASE8-IMPL-006` delivered the evidence-first extraction foundation and BookNLP-ready adapter strategy without runtime extraction. The parent established source-map/evidence decisions, tests-first contract coverage, pure validation helpers, BookNLP-ready raw output and adapter contract decisions, and an expected-red adapter contract handoff for the next parent.

Completed child summary:

- `PHASE8-IMPL-006-T001`: published the evidence-first + BookNLP-ready parent and scope decision.
- `PHASE8-IMPL-006-T002`: accepted app-owned evidence/source-map contracts before extractor runtime.
- `PHASE8-IMPL-006-T003`: added expected-red source/evidence contract tests.
- `PHASE8-IMPL-006-T004`: implemented pure validation helpers in `backend/story_knowledge/source_map.py` and `backend/story_knowledge/evidence.py`.
- `PHASE8-IMPL-006-T005`: accepted the BookNLP-ready raw output and adapter contract decision.
- `PHASE8-IMPL-006-T006`: added expected-red mocked BookNLP-ready adapter contract tests in `tests/test_writer_assistant_core_booknlp_adapter_contract.py`.
- `PHASE8-IMPL-006-T007`: closed the parent.

Final artifacts:

- Scope decision: `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-first-booknlp-ready-scope-decision.md`.
- Evidence/source-map decision: `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-source-map-contract-decision.md`.
- BookNLP-ready raw output/adapter decision: `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md`.
- Source/evidence tests: `tests/test_writer_assistant_core_source_evidence_contract.py`.
- BookNLP adapter contract tests: `tests/test_writer_assistant_core_booknlp_adapter_contract.py`.
- Helper modules: `backend/story_knowledge/source_map.py`, `backend/story_knowledge/evidence.py`.

Final runtime/test behavior now available:

- Pure source document reference validation.
- Pure source segment validation.
- Pure source map validation.
- Pure source locator validation.
- Pure evidence record validation.
- Pure extraction run provenance validation.
- Pure raw output reference validation.
- Source/evidence contract tests passing.
- Existing Writer Assistant Core candidate contract regressions passing.
- BookNLP adapter contract tests added as expected-red handoff.

Expected-red future handoff:

- Future module: `backend.story_knowledge.booknlp_adapter_contract`.
- Future APIs: `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, and `build_booknlp_candidate_drafts`.
- The expected-red state is intentional until a future implementation creates the module and APIs.

## Next Parent Recommendation

Recommended next parent:

`PHASE8-IMPL-007` - Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation.

Recommended scope:

- Implement `backend/story_knowledge/booknlp_adapter_contract.py`.
- Make `tests/test_writer_assistant_core_booknlp_adapter_contract.py` pass.
- Keep implementation pure and mocked-fixture based.
- Do not install or execute BookNLP or spaCy unless a later child explicitly authorizes it.
- Validate BookNLP-like run manifests and raw artifact bundles.
- Normalize mocked entity, quote, and event outputs into candidate draft shapes.
- Preserve source/evidence/provenance boundaries.
- Fail closed on missing or ambiguous evidence.
- Keep raw artifacts non-canon and non-candidate.
- Do not add runtime extraction, routes, UI, package changes, memory/canon mutation, or generated prose.

## Deferred Beyond PHASE8-IMPL-006

- Real BookNLP install.
- Real BookNLP execution.
- Real BookNLP output parsing.
- Raw output storage helpers.
- Extraction orchestrator.
- Candidate creation from real raw outputs.
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

## Final Boundaries

- No runtime extraction exists yet.
- No BookNLP or spaCy package was installed or run.
- No `backend/story_knowledge/booknlp_adapter_contract.py` implementation exists.
- No backend routes, frontend UI, package/dependency files, project runtime files, memory/canon mutation, apply-promotion, model calls, generated prose, rewrite, continuation, training data, JSONL records, datasets, or manifests were added.
