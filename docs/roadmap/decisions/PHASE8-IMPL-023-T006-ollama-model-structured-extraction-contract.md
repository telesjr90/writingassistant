# PHASE8-IMPL-023-T006 Ollama/Model Structured Extraction Contract

## Result

PASS for fixture-only Ollama/model structured extraction contract.

`PHASE8-IMPL-023-T006` wires the `ollama_model` adapter through the orchestrator extension point using fixture/mock output only. No live Ollama/model call is performed or enabled.

The next child is `PHASE8-IMPL-023-T007 - BookNLP/spaCy local NLP candidate extraction adapters`.

## Implementation

- Repaired the interrupted `backend/omi_analysis_orchestrator.py` edit and kept one active definition of each Ollama helper, resolver, and orchestrator entrypoint.
- Added strict Ollama fixture schema support:
  - `OMI_OLLAMA_SCHEMA_VERSION = "omi_ollama_structured_extraction.v1"`.
  - `validate_ollama_model_envelope`.
  - `_build_ollama_model_fixture_runner`.
  - `_resolve_adapter_runner` fixture/runner/config extension point.
  - `analyze_omi_raw_idea_with_tools(..., adapter_fixture_outputs=None, adapter_runners=None, adapter_config=None)`.
- `requested_adapters=["ollama_model"]` without fixture/runner returns `unavailable` with explanation, no findings, and no live model call.
- Valid `adapter_fixture_outputs["ollama_model"]` may be a JSON string or dict. It is validated, normalized into the T005 normalized finding schema, and returned as candidate-only findings with `source_adapter == "ollama_model"`.
- Invalid fixture output fails closed with an adapter envelope in `failed_closed`/`unavailable` state, no findings, and no persistence.

## Validation Rules

- Top-level payload must be a JSON object, not an array or scalar.
- Required envelope fields: `schema_version`, `adapter`, `status`, `findings`.
- Only `omi_ollama_structured_extraction.v1` and `adapter == "ollama_model"` are accepted.
- Allowed statuses: `succeeded`, `empty`, `failed_closed`, `error`.
- Non-`succeeded` statuses must carry zero findings.
- Required finding fields: `candidate_type`, `label`, `extracted_claim`, `evidence`, `source_locator`.
- Findings must have non-empty evidence and source locators.
- Unknown candidate types fail closed.
- Truth/canon/approved/promoted labels fail closed.
- Auto-approved owner decisions fail closed.
- Prose-like extracted claims fail closed.
- Forbidden prose intent fields fail closed, including `rewrite`, `continue`, `continuation`, `outline`, `draft`, `polish`, `improve`, `expand`, `imitate`, `revise`, `better_version`, `story_text`, `scene_prose`, and `chapter_prose`.

## Safety

- Ollama/model output is support only, not truth.
- Owner decision remains pending.
- Review status remains candidate/review-pending.
- AI/tool findings from `ollama_model` are never persisted in T006, even with `persist_candidates=True`.
- `deterministic_fallback` remains off by default, opt-in only via `allow_deterministic_fallback=True`, and marked `fallback_only`.
- `story_check` remains deferred to T008.
- `booknlp` and `spacy` remain deferred to T007.
- `ncp`, `subtxt`, and `dramatica_flow` remain deferred to T009.
- No Memory/Canon mutation, promotion record, apply-promotion, Story Check/BookNLP/spaCy/NCP/Subtxt/dramatica-flow runtime call, frontend UI, package change, or story prose generation occurred.

## Tests

- `python3 -m py_compile backend/omi_analysis_orchestrator.py` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_ollama_model_adapter_contract.py -q` -> `19 passed in 0.08s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> `26 passed in 0.27s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_contract.py -q` -> `5 passed in 0.19s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q` -> `4 passed in 0.29s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> `20 passed in 0.28s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> `18 passed, 51 deselected in 0.20s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> `21 passed in 0.34s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> `7 passed in 0.04s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_ui_source_expected_red.py -q` -> `5 failed, 1 passed in 0.06s`; this remains expected-red/deferred to T012 frontend analysis-results UI.

## Roadmap Validation

- `python3 scripts/check_enrichment.py` -> PASS.
- `python3 scripts/validate_roadmap.py` -> PASS.
- `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null` -> PASS.
- `git diff --check` -> PASS.

## Boundaries Confirmed

- No live Ollama/model call.
- No Story Check, BookNLP, spaCy, NCP, Subtxt, or dramatica-flow run.
- No Memory/Canon mutation.
- No promotion/apply-promotion created, run, or enabled.
- No frontend UI change.
- No story prose generated.
- No staging, commit, or push.
