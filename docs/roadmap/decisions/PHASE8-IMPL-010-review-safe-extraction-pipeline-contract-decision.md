# PHASE8-IMPL-010 Review-Safe Extraction Pipeline Contract Decision

## 1. Decision Summary

- T002 accepts a review-safe extraction pipeline contract before orchestration tests or implementation.
- The first orchestration contract must use synthetic in-memory fixture inputs only.
- The pipeline must not run real BookNLP or spaCy.
- The pipeline must not install or import BookNLP/spaCy.
- The pipeline must not write raw artifacts into real project folders.
- The pipeline must not persist candidate JSON automatically.
- The pipeline must not mutate memory/canon.
- The pipeline must not generate, rewrite, or continue prose.
- Owner review remains required before anything can become approved truth.
- T003 should be tests-first and expected-red if no orchestration module exists.
- Any implementation must remain pure/helper-only until explicitly authorized.

## 2. Evidence Reviewed

T002 reviewed the following existing foundation artifacts:

- `backend/story_knowledge/source_map.py` and `tests/test_writer_assistant_core_source_evidence_contract.py` (source document ref, source map, source locator, source segment validation helpers).
- `backend/story_knowledge/evidence.py` (evidence record, extraction run provenance, raw output reference validation helpers).
- `backend/story_knowledge/raw_extraction_storage.py` and `tests/test_writer_assistant_core_raw_extraction_storage_contract.py` (pure path and manifest validation helpers for `writer_assistant/extractions/{tool_name}/{run_id}/`).
- `backend/story_knowledge/booknlp_fixture_parser.py` and `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py` (in-memory TSV/JSON parser, event derivation, raw artifact bundle builder, fail-closed behavior).
- `backend/story_knowledge/booknlp_adapter_contract.py` and `tests/test_writer_assistant_core_booknlp_adapter_contract.py` (mocked manifest, raw artifact bundle, and candidate draft helpers; candidate-only output; evidence/source-locator integration).
- `backend/story_knowledge/candidate_persistence.py` and `backend/story_knowledge/candidate_index.py` and their contract tests (candidate-only JSON write/read/list/index helpers; no canon mutation path).
- `docs/roadmap/tasks/PHASE8-IMPL-006.md`, `docs/roadmap/tasks/PHASE8-IMPL-007.md`, `docs/roadmap/tasks/PHASE8-IMPL-008.md`, and `docs/roadmap/tasks/PHASE8-IMPL-009.md` (parent task records and final closeout summaries for the foundation).
- `docs/roadmap/inventory/PHASE8-IMPL-009.md` (foundation inventory and accepted BookNLP artifact kinds).
- `docs/roadmap/decisions/PHASE8-IMPL-009-parser-implementation-contract-reconciliation-decision.md` (T002 reconciliation decision that defined the public parser API surface, fail-closed behavior, raw-support output policy, and source-level forbidden-term boundary).

T002 did not perform any new web research, external retrieval, external tool execution, BookNLP runtime, or spaCy runtime work.

## 3. Review-Safe Pipeline Shape

T002 accepts this conceptual pipeline shape for future orchestration:

```text
owner-authored source snapshot
  -> source document ref
  -> source map / source locator validation
  -> synthetic in-memory fixture text
  -> BookNLP fixture parser
  -> raw artifact bundle
  -> raw extraction manifest / raw refs validation
  -> BookNLP adapter bundle validation
  -> candidate draft support
  -> evidence/provenance validation
  -> review handoff
  -> owner decision in a future UI/API
  -> future apply-promotion only if separately approved
```

The shape is conceptual only. T002 is a contract decision and does not execute the pipeline. Real source snapshot text matching, byte-to-character matching, and route/UI/trigger layers remain deferred.

## 4. First Orchestration Mode Decision

T002 accepts the following first orchestration mode:

- First orchestration mode is synthetic fixture orchestration only.
- No real extractor runtime.
- No disk parser input.
- No raw project writes.
- No candidate persistence.
- No route/UI trigger.
- No model calls.
- No source mutation.

The first orchestrator may operate over dictionaries/strings that are already in memory. Inputs and outputs remain in-memory support structures only.

## 5. Future Orchestrator Module/API Decision

Future module name for T003/T004, if authorized:

- `backend/story_knowledge/extraction_orchestrator.py`

Future public APIs to test first:

- `validate_extraction_pipeline_request(request: dict) -> dict`
- `build_fixture_extraction_pipeline_plan(request: dict) -> dict`
- `run_fixture_extraction_pipeline(request: dict) -> dict`

Decision guidance:

- T003 should encode tests for the selected API names.
- T004 may implement minimal pure helpers only if T003 authorizes it.
- APIs should return in-memory support structures only.
- APIs should not persist candidates or artifacts.
- APIs should not call real extraction tools.

## 6. Pipeline Request Shape Decision

The future request dict has the following required fields:

- `project_id`
- `source_document`
- `source_map`
- `run_manifest`
- `raw_output_references`
- `fixture_texts`
- `requested_outputs`
- `human_review_required`
- `persist_candidates`
- `persist_raw_artifacts`
- `allow_runtime_tools`
- `allow_model_calls`
- `allow_canon_write`
- `allow_prose_generation`

Policy flags must be:

- `human_review_required = true`
- `persist_candidates = false`
- `persist_raw_artifacts = false`
- `allow_runtime_tools = false`
- `allow_model_calls = false`
- `allow_canon_write = false`
- `allow_prose_generation = false`

Unknown fields must be rejected unless tests explicitly document compatibility.

## 7. Pipeline Output Shape Decision

The future output dict has the following allowed fields:

- `pipeline_id`
- `project_id`
- `source_document`
- `source_map`
- `run_manifest`
- `raw_artifact_bundle`
- `raw_output_references`
- `candidate_drafts`
- `evidence_records`
- `provenance`
- `warnings`
- `errors`
- `human_review_required`
- `persisted_candidates`
- `persisted_raw_artifacts`
- `canon_write_performed`
- `prose_generated`

Required policy output values:

- `human_review_required = true`
- `persisted_candidates = false`
- `persisted_raw_artifacts = false`
- `canon_write_performed = false`
- `prose_generated = false`

Candidate drafts are in-memory support only, not candidate JSON persistence.

## 8. Candidate Review Handoff Boundary

- Parser/adapter output may become candidate drafts only.
- Candidate drafts are not persisted automatically in PHASE8-IMPL-010.
- Candidate persistence remains deferred to a later owner-approved parent/child.
- Candidate review UI/API remains deferred.
- Approved memory/canon remains untouched.
- Apply-promotion remains deferred.
- Owner review is mandatory before any approved truth update.

## 9. Raw Artifact Boundary

- Raw artifacts remain non-canon and non-candidate.
- Raw artifact storage path helpers exist in `backend/story_knowledge/raw_extraction_storage.py`, but T002 does not authorize raw artifact writes.
- Raw write/read/list helpers remain deferred.
- Fixture orchestration may validate manifests and raw refs in memory.
- Raw artifact persistence into real projects is forbidden in PHASE8-IMPL-010 unless a later owner-approved child explicitly authorizes `tmp_path`-only tests.

## 10. Evidence and Source Locator Boundary

- Evidence/source locators remain required for candidate support.
- No source locator guessing from byte offsets is authorized.
- Byte-to-character matching remains deferred.
- `source_path_hint` remains display/debug metadata only.
- No owner-authored source body mutation is allowed.

## 11. Failure and Quarantine Behavior

Future orchestration should fail closed for the following inputs:

- Invalid source documents.
- Invalid source maps.
- Invalid manifests.
- Invalid raw references.
- Invalid fixture text.
- Unsupported fixture keys.
- Invalid adapter bundle.
- Invalid candidate draft support.
- Missing evidence/provenance.
- Policy flags not set to safe values.
- Any request to persist candidates or raw artifacts.
- Any request to write canon or memory.
- Any request to run external tools.
- Any request to generate, rewrite, or continue prose.

Failures should produce validation errors or rejected/quarantined in-memory support output, not partial project writes.

## 12. T003 Handoff

T003 is `PHASE8-IMPL-010-T003` - Extraction orchestration contract tests.

Expected future test file: `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`.

Expected future module: `backend.story_knowledge.extraction_orchestrator`.

Expected-red behavior:

- If no module exists, `ImportError` limited to missing future module/symbol.
- No skip/xfail/conditional import.
- No implementation in T003.

T003 tests should cover:

- Request validation.
- Policy flags.
- Fixture-only mode.
- No runtime tools.
- No filesystem writes.
- Source/evidence/raw/parser/adapter integration.
- In-memory candidate drafts only.
- No candidate persistence.
- No canon/memory mutation.
- No prose generation.
- Fail-closed invalid inputs.
- Source-level boundary scan for the future module.
- Existing regressions remain green.

## 13. T004/T005/T006 Handoff

T004 is `PHASE8-IMPL-010-T004` - Minimal review-safe orchestration helper.

- Optional minimal pure orchestration helper if T003 and T002 authorize it.
- No real runtime extraction.
- No writes outside `tmp_path` if tests use `tmp_path`.
- No persistence into real projects.

T005 is `PHASE8-IMPL-010-T005` - Candidate review handoff and persistence boundary decision.

- Decide when candidate draft outputs may be converted into candidate records in a later parent.
- Keep owner review and no apply-promotion boundaries.
- Stay docs/decision only unless prior tasks authorize tests.

T006 is `PHASE8-IMPL-010-T006` - Orchestration safety regression or conditional hardening.

- Validate no runtime extraction, filesystem leakage, canon/memory mutation, generated prose, route/UI/package expansion, or external tool execution.
- Conditional repair only if tests reveal gaps and the task explicitly authorizes repair.

## 14. Explicit Rejections

T002 rejects:

- Real BookNLP/spaCy install, import, or execution.
- External tool execution.
- Runtime extraction.
- Parser file reads.
- Raw artifact writes into real projects.
- Automatic candidate persistence.
- Candidate promotion.
- Memory/canon mutation.
- Backend extraction routes.
- Frontend extraction UI.
- Package/dependency changes.
- Model calls.
- Generated prose.
- Rewrite/continuation.
- Training/JSONL/dataset work.

## 15. Accepted Decision

T002 accepts:

- ACCEPT review-safe pipeline contract.
- ACCEPT synthetic fixture orchestration as first mode.
- ACCEPT future tests-first orchestrator contract.
- ACCEPT selected future module/API names.
- ACCEPT strict safe policy flags.
- ACCEPT in-memory candidate draft support only.
- ACCEPT no persistence in PHASE8-IMPL-010.
- ACCEPT owner-review-first handoff.
- ACCEPT fail-closed/quarantine behavior.
- REJECT runtime extraction/tool execution.
- REJECT candidate/canon/memory mutation.
- REJECT generated prose/rewrite/continuation.
