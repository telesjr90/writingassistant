# PHASE8-IMPL-023-T011 Candidate-Only Persistence for Fused AI/Tool Findings

## Result

PASS for backend/orchestrator candidate-only persistence of fused, evidence-backed OMI AI/tool findings.

`PHASE8-IMPL-023-T011` extends the OMI analysis orchestrator so `persist_candidates=True` can persist fused normalized findings through the existing OMI candidate queue/storage path when a safe project and source OMI idea context exists. `persist_candidates=False` continues to return fused findings without writes.

The next child is `PHASE8-IMPL-023-T012 - Frontend OMI analysis results UI/UX`.

## Implementation

- Added `project_manager.persist_omi_tool_assisted_findings_as_candidates`.
- Validates fused findings before any write, requiring candidate type, label/name, extracted/diagnostic claim, evidence, source locator, provenance, source adapter, support-only metadata, pending owner decision, review-pending status, candidate/evidence fingerprints, normalized finding ID, duplicate metadata, conflict group ID, and uncertainty label where present.
- Requires an existing source OMI idea and matching raw idea snapshot before persistence.
- Maps fused findings into existing OMI candidate records via `create_omi_candidate`.
- Preserves duplicate/conflict/uncertainty metadata and does not discard duplicate evidence.
- Adds duplicate-safe persistence with a deterministic source/finding persistence key; rerunning the same source/finding set reuses existing candidate IDs.
- Adds orchestrator `persistence_status`, `persistence_explanation`, `new_candidate_ids`, and `reused_candidate_ids` response fields.
- Adds `tests/test_omi_tool_assisted_persistence_contract.py`.

## Safety

- Persisted findings are candidate-only review material.
- Queue presence is not approval.
- Candidate persistence is not canon.
- Confidence/support remains support only, not truth.
- Missing source idea context, source snapshot mismatch, or invalid/unsafe finding data writes nothing.
- No Memory/Canon mutation, promotion record, apply-promotion run/enablement, live tool/model runtime call, frontend UI change, package change, or story prose generation occurred.
- Grouped owner-review UI remains deferred to T012.

## Tests

- `python3 -m py_compile backend/omi_analysis_orchestrator.py` -> PASS.
- `python3 -m py_compile backend/project_manager.py` -> PASS.
- `python3 -m py_compile backend/main.py` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q` -> `5 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_fusion_dedupe_contract.py -q` -> `5 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_story_check_adapter_contract.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_ollama_model_adapter_contract.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_contract.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> PASS.

## Boundaries Confirmed

- No live Ollama/model call.
- No live Story Check call.
- No live BookNLP/spaCy runtime call.
- No live NCP/Subtxt/dramatica-flow runtime call.
- No dependency installation.
- Candidates persist only when explicitly requested and source context is safe.
- Persisted candidates remain pending review candidates.
- No Memory/Canon mutation.
- No promotion/apply-promotion created, run, or enabled.
- No frontend UI change.
- No story prose generated.
- No staging, commit, or push.
