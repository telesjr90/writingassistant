# PHASE8-IMPL-023-T002 OMI Extraction Expected-Red Tests

## Result

PASS for tests-first expected-red coverage only.

`PHASE8-IMPL-023-T002` is complete/PASS. The next child is `PHASE8-IMPL-023-T003 - Backend extraction contract and deterministic candidate schema`.

No extractor, backend route, backend helper, frontend product UI, browser harness script, runtime extraction, model/Ollama call, candidate promotion, Memory/Canon mutation, apply-promotion run, or story prose generation occurred for this task.

## Expected-Red Backend Coverage

Added `tests/test_omi_extraction_expected_red.py`.

The backend expected-red tests pin the future raw idea extraction contract:

- `OMIExtractionRequest` request model.
- `POST /api/projects/{project_name}/omi/extractions`.
- `extract_omi_candidates` route helper.
- `project_manager.extract_omi_candidates_from_raw_idea` helper.
- Raw idea text with evidence-backed candidates for character, location, timeline event, relationship, organization, object, plot thread, story fact, open question, and supportable storyform context.
- Candidate fields: `candidate_type`, `label` or `name`, `extracted_claim`, evidence/source support, provenance, status, and pending owner decision.
- Confidence/support, if present, must be labeled as support rather than truth.
- Empty raw idea extraction must return `empty` or `fail_closed` with explanation and no placeholder candidate shells.
- Persisted extracted candidates must remain candidate-first, non-canon, non-promoted, pending owner decision, and must not mutate project truth files or create promotion records.
- Extraction must not call model/Story Check paths.

Expected-red command:

```bash
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q
```

Result:

```text
4 failed in 0.25s
```

Failure reasons are intentional and limited to missing extraction contract/surfaces:

- Missing `class OMIExtractionRequest`.
- Missing `extract_omi_candidates`.
- Missing `POST /api/projects/{project_name}/omi/extractions`.
- Missing project-manager raw idea extraction helper.

## Expected-Red Frontend/Source Coverage

Added `tests/test_omi_extraction_ui_source_expected_red.py`.

The frontend/source expected-red tests pin the future UI/API surface:

- `extractOMICandidates` API helper calling `/omi/extractions`.
- OMI extraction action, status, and result surface.
- Grouped extracted candidates by candidate type.
- Extracted candidate detail fields for extracted claim, source excerpt/locator, support strength, evidence, and provenance.
- Empty and fail-closed extraction state.
- Explicit separation from Memory/Canon and apply-promotion.
- No generated prose controls, no automatic promotion controls, and no Memory/Canon mutation controls.

Expected-red command:

```bash
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_ui_source_expected_red.py -q
```

Result:

```text
5 failed, 1 passed in 0.08s
```

Failure reasons are intentional and limited to missing future frontend/source surfaces:

- Missing `extractOMICandidates` API helper.
- Missing extraction action/status/result markers in `OMIPanel.jsx`.
- Missing grouped extracted candidate markers.
- Missing extracted claim/evidence/provenance detail markers.
- Missing empty/fail-closed extraction state markers.

The one passing test confirms no generated-prose, automatic-promotion, or Memory/Canon mutation controls were introduced by this expected-red task.

## Existing OMI Regression Boundary

Existing OMI regressions remain the required green baseline and were not weakened by T002:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> `20 passed in 0.38s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> `18 passed, 51 deselected in 0.24s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> `21 passed in 0.34s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> `7 passed in 0.07s`.

These preserve the current manual-shell/no-model/no-canon/no-apply-promotion boundaries until later children implement the extraction path.

Roadmap validation:

- `python3 scripts/check_enrichment.py` -> PASS.
- `python3 scripts/validate_roadmap.py` -> PASS.
- `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null` -> PASS.

## Safety Notes

- Candidate persistence is not canon.
- Queue presence is not approval.
- Owner approval does not mutate Memory/Canon.
- Apply-promotion remains separate, guarded, audited, owner-confirmed, and outside extraction.
- Empty/fail-closed extraction must create no misleading shells.
- Extraction output and support strength are not truth.
- No generated prose path is authorized.

## Deferred Work

Implementation is deferred.

`PHASE8-IMPL-023-T003` should implement the backend extraction contract and deterministic candidate schema without implementing the full extractor. Deterministic/rule-based extraction remains planned for `PHASE8-IMPL-023-T004`; persistence remains planned for `PHASE8-IMPL-023-T005`; frontend extraction UI remains planned for `PHASE8-IMPL-023-T006`.
