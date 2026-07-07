# PHASE8-IMPL-023-T003 Backend Extraction Contract and Deterministic Candidate Schema

## Result

PASS for backend contract/schema implementation only.

`PHASE8-IMPL-023-T003` is complete/PASS. The next child is `PHASE8-IMPL-023-T004 - Deterministic/rule-based MVP extractor`.

No full deterministic extractor, frontend UI, browser harness script, model/Ollama call, Story Check call, BookNLP/spaCy/NCP/Subtxt/dramatica-flow run, Memory/Canon mutation, promotion record, apply-promotion run/enablement, story prose generation, training artifact, staging, commit, or push occurred.

## Backend Contract Added

- Added `OMIExtractionRequest`, `OMIExtractionResponse`, and `OMIExtractedCandidate` models in `backend/main.py`.
- Added `POST /api/projects/{project_name}/omi/extractions`.
- Added `extract_omi_candidates` route helper.
- Added `project_manager.extract_omi_candidates_from_raw_idea` as the contract-level deterministic extraction entrypoint.
- Added extracted candidate type/schema constants and validation helpers in `backend/project_manager.py`.

## Candidate Schema

Allowed extracted candidate types:

- `character`
- `location`
- `timeline_event`
- `relationship`
- `organization`
- `object`
- `plot_thread`
- `story_fact`
- `open_question`
- `storyform_context`

Future extracted candidates must be evidence-backed and include candidate type, label/name, extracted claim, evidence/source excerpt or locator, provenance, status, pending owner decision state, and optional support strength/confidence only as support, not truth.

## Fail-Closed Behavior

Empty raw idea extraction returns `extraction_status: empty`, a clear explanation, no candidates, and no candidate writes.

Non-empty raw ideas currently return `extraction_status: fail_closed`, a clear explanation that the deterministic extractor is not implemented in T003, no candidates, and no candidate writes. This keeps rich raw idea parsing red for T004 without creating placeholder candidates or empty/manual shells.

If `persist_candidates` is true but no evidence-backed candidates exist, no candidates are persisted.

## Safety Boundaries

- Candidate persistence is not canon.
- Queue presence is not approval.
- Confidence/support strength is not truth.
- Extraction does not mutate Memory/Canon.
- Extraction does not create promotion records.
- Extraction does not call apply-promotion.
- Extraction does not call models/Ollama.
- Extraction does not call Story Check.
- Extraction does not generate story prose.

## Validation

- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_contract.py -q` -> `4 passed in 0.21s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q` -> `2 failed, 2 passed in 0.21s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_ui_source_expected_red.py -q` -> `5 failed, 1 passed in 0.07s`.
- Remaining expected-red failures are limited to the T004 rich deterministic candidate extraction logic: non-empty raw idea input does not yet return `succeeded` with evidence-backed candidates.
- Frontend/source expected-red failures remain deferred to T006: missing frontend API helper, extraction action/status/result UI, grouped candidate UI, extracted-claim/evidence/provenance detail UI, and empty/fail-closed UI.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> `20 passed in 0.26s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> `18 passed, 51 deselected in 0.26s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> `21 passed in 0.41s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> `7 passed in 0.07s`.

## Deferred Work

`PHASE8-IMPL-023-T004` must implement the deterministic/rule-based MVP extractor that turns supported raw idea text into non-empty evidence-backed extracted candidates. `PHASE8-IMPL-023-T005` remains responsible for candidate persistence with evidence/provenance/source spans. `PHASE8-IMPL-023-T006` remains responsible for frontend extracted-candidate review UI/UX.
