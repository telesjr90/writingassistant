# PHASE8-IMPL-023-T008 Story Check Diagnostic-Only OMI Handoff

## Result

PASS for the fixture-only Story Check diagnostic adapter contract.

`PHASE8-IMPL-023-T008` wires the `story_check` adapter through the existing OMI analysis orchestrator extension point using fixture/mock diagnostic output only. No live Story Check runtime call is performed or enabled.

The next child is `PHASE8-IMPL-023-T009 - NCP/Subtxt/dramatica-flow analysis-only candidate mapping`.

## Implementation

- Extended `backend/omi_analysis_orchestrator.py` with fixture-only Story Check schema support:
  - `OMI_STORY_CHECK_SCHEMA_VERSION = "omi_story_check_diagnostic_handoff.v1"`.
  - `validate_story_check_fixture_envelope`.
  - `_build_story_check_fixture_runner`.
  - `_resolve_adapter_runner` support for `adapter_fixture_outputs["story_check"]`.
- `requested_adapters=["story_check"]` without fixture/runner returns `unavailable` with explanation, no findings, no persistence, and no live runtime call.
- Valid Story Check fixtures may normalize evidence-backed structural diagnostics, storyform/context support, throughline/context support, conflict/uncertainty diagnostics, plot-thread diagnostics, relationship diagnostics, open questions, ambiguity support, and diagnostic questions into candidate-only findings.
- Diagnostic questions are review support only. They must not ask for prose continuation, rewrite, outline, draft, polish, expansion, or revision.
- Story Check findings remain non-persistent, even when `persist_candidates=True`.

## Validation Rules

- Top-level payload must be a JSON object, not an array or scalar.
- Required envelope fields: `schema_version`, `adapter`, `status`, `provenance`, `findings`.
- Only `omi_story_check_diagnostic_handoff.v1` and adapter identity `story_check` are accepted.
- Allowed statuses: `succeeded`, `empty`, `failed_closed`, `error`.
- Non-`succeeded` statuses must carry zero findings.
- Findings must carry type/label/diagnostic claim or question, evidence excerpt, source locator, and provenance.
- Unknown candidate/finding types fail closed.
- Missing evidence, source locator, or provenance fails closed.
- Truth/canon/final/approved/promoted labels fail closed.
- Auto-approved owner decisions and review statuses implying approval fail closed.
- Prose-like claims and rewrite/continue/outline/draft/polish/expand/revise language fail closed.
- Memory/Canon mutation, candidate-persistence requests, promotion-record fields, and apply-promotion fields fail closed.

## Safety

- Story Check output is support only, not truth.
- Owner decision remains pending.
- Review status remains candidate/review-pending.
- AI/tool findings from `story_check` are never persisted in T008.
- `deterministic_fallback` remains off by default, opt-in only via `allow_deterministic_fallback=True`, and marked `fallback_only`.
- `ncp`, `subtxt`, and `dramatica_flow` remain deferred to T009.
- No Memory/Canon mutation, promotion record, apply-promotion, live Story Check runtime call, frontend UI, package change, or story prose generation occurred.

## Tests

- `python3 -m py_compile backend/omi_analysis_orchestrator.py` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_story_check_adapter_contract.py -q` -> `11 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q` -> `10 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_ollama_model_adapter_contract.py -q` -> `19 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> `26 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_contract.py -q` -> `5 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q` -> `4 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> `20 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> `18 passed, 51 deselected`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> `21 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> `7 passed`.

## Boundaries Confirmed

- No live Story Check runtime call.
- No live Ollama/model call.
- No live BookNLP/spaCy runtime call.
- No NCP, Subtxt, or dramatica-flow run.
- No dependency installation.
- No Memory/Canon mutation.
- No promotion/apply-promotion created, run, or enabled.
- No candidates persisted from Story Check findings.
- No frontend UI change.
- No story prose generated.
- No staging, commit, or push.
