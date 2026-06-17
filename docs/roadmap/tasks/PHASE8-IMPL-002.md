# PHASE8-IMPL-002

## ID

`PHASE8-IMPL-002`

## Title

Writer Assistant Core candidate storage contract and evidence/provenance validation

## Goal

Prepare the next safe Writer Assistant Core runtime slice after candidate schema constants by defining tests-first candidate record, source locator, evidence, provenance, status, decision, destination, and path-safety contracts before any extraction runtime, routes, UI, model calls, storage writes, apply-promotion, or memory/canon mutation exists.

## Why Now

`PHASE8-IMPL-001` is complete through `PHASE8-IMPL-001-T007`. It established Writer Assistant Core as the post-Phase-7 frontier, collected targeted context, selected the first runtime slice, added candidate schema contract tests, and implemented minimal constants-only schema metadata in `backend/story_knowledge/candidate_schema.py`.

That parent intentionally stopped before extraction, candidate creation runtime, candidate storage writes, backend routes, frontend extraction UI, model/Ollama calls, apply-promotion, OMI candidate promotion, memory/canon mutation, package changes, training data, JSONL records, dataset artifacts, or project runtime files. The next safe step is candidate storage and evidence/provenance validation contracts.

## Dependencies

- Completed parent: `PHASE8-IMPL-001` - Writer Assistant Core implementation readiness and first runtime slice plan.
- Completed child: `PHASE8-IMPL-001-T007` - Roadmap/status closeout.
- Source evidence:
  - `docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-001-first-runtime-slice-decision.md`
  - `docs/roadmap/writer_assistant_core_candidate_schemas.md`
  - `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
  - `docs/roadmap/omi_mvp_schema_lifecycle.md`
  - `docs/roadmap/omi_storage_model.md`
  - `docs/roadmap/project_memory_canon_storage_model.md`
  - `docs/roadmap/project_memory_canon_page_structure_spec.md`
  - `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`
  - `tests/test_writer_assistant_core_candidate_schema_contract.py`
  - `backend/story_knowledge/candidate_schema.py`

## Scope

Include:

- Define storage/evidence/provenance contracts before runtime behavior expands.
- Keep candidate records project-local and candidate-only.
- Lock candidate record shape before storage writes.
- Lock source locator shape and path-safety assumptions.
- Lock evidence span/support shape.
- Lock provenance/origin shape.
- Lock confidence and uncertainty fields.
- Lock owner decision, status, and destination fields.
- Align typed candidate targets with `candidate_schema.py`.
- Add tests before helpers.
- Add only tiny pure validation helpers after tests authorize the shape.
- Consider storage path tests before any storage helper skeleton.

## Exclusions

- Production runtime code in T001.
- Tests in T001.
- Runtime extraction.
- Candidate extraction from owner text.
- Candidate storage writes in T001.
- Model/Ollama calls.
- Backend extraction routes.
- Frontend extraction UI.
- Story Check auto-runs.
- Semantic search.
- Dramatica analysis.
- Generated prose, rewriting, continuation, style imitation, prose improvement, or summaries as durable truth.
- Apply-promotion.
- OMI candidate promotion.
- Memory/canon mutation.
- Backend approved-memory routes/helpers.
- Frontend approved-memory API helpers.
- Package/dependency changes.
- Training data, JSONL records, dataset manifests, or model artifacts.
- Project runtime artifacts.
- Context-tool execution in T001.

## Child-Task Plan

1. `PHASE8-IMPL-002-T001` - Publish candidate storage/evidence validation parent and child-task plan. Status: complete.
2. `PHASE8-IMPL-002-T002` - Candidate storage and evidence/provenance contract decision. Status: complete.
3. `PHASE8-IMPL-002-T003` - Candidate storage/evidence contract tests. Status: complete.
4. `PHASE8-IMPL-002-T004` - Candidate record validation helpers. Status: complete.
5. `PHASE8-IMPL-002-T005` - Project-local candidate storage path contract tests. Status: complete.
6. `PHASE8-IMPL-002-T006` - Candidate storage helper skeleton. Status: complete.
7. `PHASE8-IMPL-002-T007` - Roadmap/status closeout. Status: active.

## Child Task Details

### `PHASE8-IMPL-002-T001` - Publish candidate storage/evidence validation parent and child-task plan

- Docs/status/planning only.
- Publish parent, inventory, enrichment JSON, and roadmap/status updates.
- No code, tests, storage writes, context tools, runtime behavior, routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-002-T002` - Candidate storage and evidence/provenance contract decision

- Docs/decision only.
- Decide the exact first contract shape for candidate records, source locators, evidence, provenance, owner decisions, status, destination, target category, and path safety.
- Decide whether T003 is tests-only or test-plus-helper.
- No runtime implementation.
- Completed decision: `docs/roadmap/decisions/PHASE8-IMPL-002-candidate-storage-evidence-contract-decision.md`.
- Selected sequence: T003 tests-only, T004 tiny pure validation helpers, T005 path contract tests, T006 conditional storage helper skeleton.
- No storage writes authorized before T005/T006.

### `PHASE8-IMPL-002-T003` - Candidate storage/evidence contract tests

- Tests-first.
- Add contract tests for record shape, source locator, evidence/provenance, status/destination, path safety, and forbidden mutation.
- Completed test file: `tests/test_writer_assistant_core_candidate_record_contract.py`.
- Defines the expected T004 helper API on `backend.story_knowledge.candidate_record`.
- Targeted pytest is expected red until T004 implements pure validation helpers.
- No production helpers added in T003.

### `PHASE8-IMPL-002-T004` - Candidate record validation helpers

- Implement tiny pure validation helpers only.
- No storage writes, routes, UI, extraction, model calls, apply-promotion, OMI candidate promotion, or memory/canon mutation.
- Completed helper module: `backend/story_knowledge/candidate_record.py`.
- Exports: `validate_candidate_record`, `validate_source_locator`, `validate_evidence_item`, `validate_provenance`.
- Targeted candidate record contract pytest now passes; pure validation only with no file I/O.

### `PHASE8-IMPL-002-T005` - Project-local candidate storage path contract tests

- Tests-first.
- Define where typed Writer Assistant Core candidates may live under project-local storage.
- Verify path safety and read/list/write boundaries before adding writes.
- Completed test file: `tests/test_writer_assistant_core_candidate_storage_contract.py`.
- Defines the expected T006 helper API on `backend.story_knowledge.candidate_storage`.
- Targeted pytest is expected red until T006 implements pure path helpers.
- T005 authorizes T006 for pure path helper skeleton only; JSON read/write/list remains deferred.
- No production storage helpers or storage writes added in T005.

### `PHASE8-IMPL-002-T006` - Candidate storage helper skeleton

- Implement a minimal pure path helper skeleton authorized by T005.
- Completed helper module: `backend/story_knowledge/candidate_storage.py`.
- Exports: `candidate_storage_dir`, `candidate_index_path`, `candidate_record_path`, `validate_candidate_storage_path`.
- Candidate-only storage under `projects/{project_id}/writer_assistant/`.
- Pure path helpers only; no filesystem side effects.
- Targeted storage contract pytest now passes; JSON read/write/list remains deferred.
- No extraction, routes, UI, apply-promotion, OMI candidate promotion, or memory/canon mutation.

### `PHASE8-IMPL-002-T007` - Roadmap/status closeout

- Close the parent.
- Summarize tests, helpers, and storage contract decisions.
- Identify the next roadmap-authorized parent or decision point.

## Acceptance Criteria

- `PHASE8-IMPL-002` is published as the active Writer Assistant Core parent after completed `PHASE8-IMPL-001`.
- `PHASE8-IMPL-002-T001` publishes the parent, inventory, enrichment JSON, and roadmap/status updates.
- `PHASE8-IMPL-002-T002` is identified as the next child task.
- Child tasks T001-T007 are documented with tests-first sequencing.
- Scope explicitly prioritizes candidate storage contracts and evidence/provenance validation before extraction/runtime expansion.
- Non-scope explicitly blocks extraction, routes, UI, model calls, storage writes in T001, apply-promotion, and memory/canon mutation.
- The context tools policy records that T001 does not run context tools and that the PHASE8-IMPL-001 targeted context report is sufficient evidence unless a later child authorizes a narrow collect task.

## Validation Expectations

For `PHASE8-IMPL-002-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Non-LeanCTX whitespace check on changed docs

Do not run pytest unless runtime code or tests were accidentally changed. Do not run context tools, CCE, Graphify, Repomix, AI Context generation, MCP tools, LeanCTX, app servers, browser/manual validation, frontend build, model calls, Ollama, or broad discovery.

## Safety / Product Boundaries

- The app is analysis-only.
- The app must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Owner-authored prose storage and editing remain allowed only when text is authored by the owner.
- Candidates are not canon.
- Schema validity, storage validity, or evidence validity does not prove story truth.
- Candidate records must remain separate from approved memory/canon.
- Storage helpers must not mutate approved memory, canon, bible, storyform, scenes, project metadata, training data, JSONL records, or dataset manifests.
- OMI remains the central review and future promotion layer.
- Promotion records remain audit-only until future apply-promotion exists.
- Context outputs are evidence, not roadmap truth.

## Current Status

`PHASE8-IMPL-002` is active. Active child: `PHASE8-IMPL-002-T007` - Roadmap/status closeout. Next child: none published after T007 closeout. Last completed child: `PHASE8-IMPL-002-T006` - Candidate storage helper skeleton. Prior completed child: `PHASE8-IMPL-002-T005` - Project-local candidate storage path contract tests. Prior completed child: `PHASE8-IMPL-002-T004` - Candidate record validation helpers. Prior completed child: `PHASE8-IMPL-002-T003` - Candidate storage/evidence contract tests. Prior completed child: `PHASE8-IMPL-002-T002` - Candidate storage and evidence/provenance contract decision. Prior completed child: `PHASE8-IMPL-002-T001` - Publish candidate storage/evidence validation parent and child-task plan. Last completed parent: `PHASE8-IMPL-001`. Prior completed child under prior parent: `PHASE8-IMPL-001-T007`.

T002 accepted the storage record contract in `docs/roadmap/decisions/PHASE8-IMPL-002-candidate-storage-evidence-contract-decision.md`. T003 added tests-only contract coverage in `tests/test_writer_assistant_core_candidate_record_contract.py`. T004 added pure validation helpers in `backend/story_knowledge/candidate_record.py` and satisfied the T003 contract tests. T005 added tests-only storage path contract coverage in `tests/test_writer_assistant_core_candidate_storage_contract.py` for `writer_assistant/candidates/` and `writer_assistant/index.json` boundaries. T006 added pure path helpers in `backend/story_knowledge/candidate_storage.py` and satisfied the T005 storage contract tests; JSON read/write/list remains deferred. No storage writes, extraction, routes, UI, model calls, apply-promotion, or memory/canon mutation are authorized by T002/T003/T004/T005/T006.
