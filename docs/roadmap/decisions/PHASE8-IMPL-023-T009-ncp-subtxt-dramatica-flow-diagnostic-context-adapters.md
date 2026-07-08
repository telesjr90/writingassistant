# PHASE8-IMPL-023-T009 NCP/Subtxt/dramatica-flow Diagnostic Context Adapters

## Result

PASS for fixture-only NCP/Subtxt/dramatica-flow diagnostic/context adapter contracts.

`PHASE8-IMPL-023-T009` wires the `ncp`, `subtxt`, and `dramatica_flow` adapters through the existing OMI analysis orchestrator extension point using fixture/mock diagnostic and context output only. No live NCP, Subtxt, or dramatica-flow runtime call is performed or enabled.

The next child is `PHASE8-IMPL-023-T010 - Candidate fusion, dedupe, conflict handling, and evidence/provenance normalization`.

## Implementation

- Extended `backend/omi_analysis_orchestrator.py` with fixture-only schema support:
  - `OMI_NCP_SCHEMA_VERSION = "omi_ncp_context_handoff.v1"`.
  - `OMI_SUBTXT_SCHEMA_VERSION = "omi_subtxt_diagnostic_handoff.v1"`.
  - `OMI_DRAMATICA_FLOW_SCHEMA_VERSION = "omi_dramatica_flow_analysis_handoff.v1"`.
  - `validate_context_adapter_fixture_envelope`.
  - `_build_context_adapter_fixture_runner`.
  - `_resolve_adapter_runner` support for `adapter_fixture_outputs["ncp"]`, `adapter_fixture_outputs["subtxt"]`, and `adapter_fixture_outputs["dramatica_flow"]`.
- `requested_adapters=["ncp"]`, `["subtxt"]`, or `["dramatica_flow"]` without fixture/runner returns `unavailable` with explanation, no findings, no persistence, and no live runtime call.
- Valid NCP fixtures may normalize evidence-backed project/story context, storyform/context, moment/scene context, throughline/context, authorial-intent/context, relationship/context, open question/ambiguity, source-mapping, and diagnostic question support into candidate-only findings.
- Valid Subtxt fixtures may normalize evidence-backed structural diagnostics, conflict diagnostics, throughline diagnostics, story point/context support, source-of-conflict diagnostics, subject-vs-conflict diagnostics, uncertainty/insufficient-evidence diagnostics, and owner-review diagnostic questions into candidate-only findings.
- Valid dramatica-flow fixtures may normalize evidence-backed causal-chain, promise/payoff or setup/payoff, foreshadowing/mystery/question, conflict-thread, emotional-arc, relationship-network, timeline/thread activity, information-boundary, uncertainty/conflict-group, and diagnostic question support into candidate-only findings.
- Diagnostic questions are review support only. They must not ask for prose continuation, rewrite, outline, draft, polish, expansion, improvement, or revision.
- NCP/Subtxt/dramatica-flow findings remain non-persistent, even when `persist_candidates=True`.

## Validation Rules

- Top-level payload must be a JSON object, not an array or scalar.
- Required envelope fields: `schema_version`, `adapter`, `status`, `provenance`, `findings`.
- Only the T009 schema version matching the requested adapter identity is accepted.
- Allowed statuses: `succeeded`, `empty`, `failed_closed`, `error`.
- Non-`succeeded` statuses must carry zero findings.
- Findings must carry type/label/diagnostic or context claim, evidence excerpt, source locator, and provenance.
- Unknown candidate/finding types fail closed.
- Missing evidence, source locator, or provenance fails closed.
- Truth/canon/final/approved/promoted labels fail closed.
- Auto-approved owner decisions and review statuses implying approval fail closed.
- Prose-like claims and rewrite/continue/outline/draft/polish/expand/improve/revise language fail closed.
- Memory/Canon mutation, candidate-persistence requests, promotion-record fields, and apply-promotion fields fail closed.

## Safety

- NCP/Subtxt/dramatica-flow output is support only, not truth.
- Owner decision remains pending.
- Review status remains candidate/review-pending.
- AI/tool findings from `ncp`, `subtxt`, and `dramatica_flow` are never persisted in T009.
- `deterministic_fallback` remains off by default, opt-in only via `allow_deterministic_fallback=True`, and marked `fallback_only`.
- Fusion/dedupe/conflict handling remains deferred to T010.
- Candidate-only persistence for AI/tool findings remains deferred to T011.
- Grouped owner-review frontend UI remains deferred to T012.
- No Memory/Canon mutation, promotion record, apply-promotion, live NCP/Subtxt/dramatica-flow runtime call, frontend UI, package change, or story prose generation occurred.

## Tests

- `python3 -m py_compile backend/omi_analysis_orchestrator.py` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py -q` -> `31 passed`.
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
- `python3 scripts/check_enrichment.py` -> PASS.
- `python3 scripts/validate_roadmap.py` -> PASS.
- `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null` -> PASS.
- `git diff --check` -> PASS.

## Boundaries Confirmed

- No live NCP runtime call.
- No live Subtxt runtime call.
- No live dramatica-flow runtime call.
- No live Story Check runtime call.
- No live Ollama/model call.
- No live BookNLP/spaCy runtime call.
- No dependency installation.
- No Memory/Canon mutation.
- No promotion/apply-promotion created, run, or enabled.
- No candidates persisted from NCP/Subtxt/dramatica-flow findings.
- No frontend UI change.
- No story prose generated.
- No staging, commit, or push.
