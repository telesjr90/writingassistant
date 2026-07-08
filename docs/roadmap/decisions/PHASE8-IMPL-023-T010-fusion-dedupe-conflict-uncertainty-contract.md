# PHASE8-IMPL-023-T010 Fusion, Dedupe, Conflict, and Uncertainty Contract

## Result

PASS for backend/orchestrator-contract fusion, dedupe, conflict, and uncertainty handling over normalized OMI tool-assisted findings.

`PHASE8-IMPL-023-T010` extends the existing OMI analysis orchestrator with a deterministic post-normalization fusion pass. The pass annotates normalized findings from fixture-only adapters with stable candidate fingerprints, duplicate links, related finding IDs, conflict group IDs, uncertainty labels, and a small `fusion_summary`.

The next child is `PHASE8-IMPL-023-T011 - Candidate-only persistence for fused AI/tool-assisted findings`.

## Implementation

- Added `fuse_normalized_findings` to `backend/omi_analysis_orchestrator.py`.
- Recomputed deterministic `candidate_fingerprint`, `evidence_fingerprint`, and `normalized_finding_id` values after normalization.
- Grouped exact or shallow near-equivalent findings by normalized candidate type, whitespace/case-insensitive label, and support-claim signature.
- Marked duplicates with `duplicate_of` and linked duplicate evidence with `related_finding_ids`.
- Preserved every duplicate finding instead of deleting evidence or provenance.
- Assigned deterministic `conflict_group_id` values when normalized candidate type/label match but claim signatures differ.
- Marked conflict findings with `uncertainty_label = "conflict_support"` without choosing a true claim.
- Marked diagnostic questions, open questions, ambiguity, low support, insufficient evidence, and context-only support with support-only uncertainty labels.
- Added `fusion_summary` counts for total input/output findings, duplicate groups, duplicate findings, conflict groups, uncertain findings, and adapters contributing findings.
- Preserved optional support/confidence metadata through adapter normalization and fusion.

## Safety

- Fusion/dedupe output remains candidate-only review material.
- Conflict handling does not decide which claim is true.
- Conflict handling does not merge conflicting claims into canon or truth.
- Confidence/support remains support only, not truth.
- Candidate persistence for AI/tool findings remains deferred to T011.
- Grouped owner-review UI remains deferred to T012.
- No Memory/Canon mutation, promotion record, apply-promotion run/enablement, live tool/model runtime call, frontend UI change, package change, or story prose generation occurred.

## Tests

- `python3 -m py_compile backend/omi_analysis_orchestrator.py` -> PASS.
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
- `python3 scripts/check_enrichment.py` -> PASS.
- `python3 scripts/validate_roadmap.py` -> PASS.
- `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null` -> PASS.
- `git diff --check` -> PASS.

## Boundaries Confirmed

- No live Ollama/model call.
- No live Story Check call.
- No live BookNLP/spaCy runtime call.
- No live NCP/Subtxt/dramatica-flow runtime call.
- No dependency installation.
- No candidates persisted from AI/tool findings.
- No Memory/Canon mutation.
- No promotion/apply-promotion created, run, or enabled.
- No frontend UI change.
- No story prose generated.
- No staging, commit, or push.
