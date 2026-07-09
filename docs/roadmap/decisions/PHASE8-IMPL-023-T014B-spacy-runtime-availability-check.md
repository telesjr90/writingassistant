# PHASE8-IMPL-023-T014B — spaCy Runtime Availability Check

## Status

Accepted/complete/PASS.

## Task

Add read-only spaCy runtime and model availability checking to the T013 runtime preflight.

## Scope

- Enhance `backend/omi_runtime_preflight.py` to report:
  - Whether the `spacy` Python package is importable.
  - Whether the selected spaCy model is available/loadable.
  - The selected spaCy model name, defaulting to `en_core_web_sm`.
  - An optional `OMI_LIVE_SPACY_MODEL` environment variable to override the model name.
- Update `tests/test_omi_live_runtime_preflight_contract.py` with focused mock-based tests for package-missing, model-missing, model-available, env-var-override, blocked-override, and global-disabled scenarios.
- Create this decision record.
- No live spaCy adapter was implemented.
- No spaCy runtime analysis was run.
- No candidates were produced.
- No package/model install/download was performed.
- No Memory/Canon mutation, promotion records, automatic apply-promotion, or story prose were added.

## Implementation

### `backend/omi_runtime_preflight.py`

Added:

- `OMI_LIVE_SPACY_MODEL_DEFAULT = "en_core_web_sm"` — default model name constant.
- `OMI_LIVE_SPACY_MODEL_ENV = "OMI_LIVE_SPACY_MODEL"` — env var name for model override.
- `_spacy_model_probe(model_name)` — read-only probe function that:
  1. Checks spaCy package availability via `importlib.util.find_spec("spacy")`.
  2. If available, lazily imports spaCy and calls `spacy.load(model_name)`.
  3. Returns `spacy_package_available`, `spacy_model_available`, `spacy_model_name`, and `spacy_probe_detail`.
  4. Fail-closed: missing package or unloadable model returns `available=False` with a clear reason.
- Enhanced `_dependency_probe` spaCy branch to call `_spacy_model_probe` and return model-specific fields.
- Enhanced `_tool_report` to pass through `spacy_model_name` and `spacy_model_available` in the per-tool report dict.

### `tests/test_omi_live_runtime_preflight_contract.py`

Existing tests updated:

- `test_per_tool_flags_are_recognized_and_still_require_global_gate` — now uses `_mock_spacy_probe` instead of raw `find_spec` patching.
- `test_preflight_distinguishes_fixture_contract_config_dependency_and_enablement` — same.
- `test_blocked_status_is_explicit_and_overrides_enablement` — same.

New T014B focused tests:

- `test_spacy_package_missing_reports_unavailable_with_clear_reason` — verify package-missing state.
- `test_spacy_model_missing_reports_unavailable_with_model_specific_reason` — verify model-missing state.
- `test_spacy_package_and_model_available_reports_available` — verify fully-available state.
- `test_spacy_model_env_var_changes_reported_model_name` — verify `OMI_LIVE_SPACY_MODEL` overrides the model name.
- `test_spacy_blocked_flag_overrides_availability` — verify blocked flag takes precedence.
- `test_spacy_global_live_tools_disabled_reports_disabled_or_available` — verify global-disabled behavior.

All tests use monkeypatching only. No real spaCy installation or model download is required.

## Key Design Decisions

1. **Two-level availability**: Package availability and model availability are checked separately. Both must be true for `runtime_dependency_available` to be True.
2. **Lazy import**: `import spacy` only happens inside the probe function and only when the package is detected via `find_spec`. No module-level import.
3. **Fail-closed**: Both missing package and missing/unloadable model result in `available=False` with a clear `probe_detail` message.
4. **Default model**: `en_core_web_sm` is the hardcoded default. Can be overridden via `OMI_LIVE_SPACY_MODEL`.
5. **Read-only**: The probe does not download models, write files, or run analysis. It only checks availability.
6. **Mockable**: The `_spacy_model_probe` function is independently monkeypatchable, so tests never require real spaCy.

## Excluded from This Task

- No live spaCy adapter was implemented.
- No spaCy runtime analysis was run on raw idea text.
- No candidate findings were produced.
- No package/model install/download was performed.
- No Memory/Canon mutation, promotion records, automatic apply-promotion, or story prose were added.
- No frontend files were changed.
- No package/dependency files were changed.
- No fixture/mock spaCy contract was changed; it remains scaffolding only.

## Next Scope

`PHASE8-IMPL-023-T014C` — Implement the live spaCy adapter that uses `spacy` to analyze raw idea text and produce normalized candidate findings. This will be the first real runtime adapter that converts spaCy entity/noun-chunk/sentence-segmentation output into the `omi_spacy_local_nlp_extraction.v1` schema and flows through the existing T005 orchestrator and T011 candidate persistence.

## Validation

```bash
python3 -m py_compile backend/omi_runtime_preflight.py backend/main.py backend/omi_analysis_orchestrator.py
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q  # 14 passed
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q  # 10 passed
```
