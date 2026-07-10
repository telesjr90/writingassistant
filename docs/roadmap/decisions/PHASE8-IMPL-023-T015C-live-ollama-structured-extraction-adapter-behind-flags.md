# PHASE8-IMPL-023-T015C — Live Ollama structured extraction adapter behind flags

## Decision

**Accepted.** T015C implements a live Ollama structured extraction adapter behind
explicit environment flags in the OMI analysis orchestrator.

## Scope

- Adds `_build_ollama_model_live_runner` to `backend/omi_analysis_orchestrator.py`.
- Wires the live runner into `_resolve_adapter_runner` for adapter `ollama_model`
  only when `OMI_LIVE_TOOLS_ENABLED`, `OMI_LIVE_OLLAMA_ENABLED` are enabled and
  `OMI_LIVE_OLLAMA_BLOCKED` is not enabled.
- Uses Python standard library only (`urllib.request`).
- Calls Ollama `/api/chat` with `stream=false`, a low output token limit
  (`num_predict=2048`), and a finite timeout (30s).
- Sends a system instruction that forces strict JSON output conforming to
  `omi_ollama_structured_extraction.v1`.
- Validates model output through the existing
  `validate_ollama_model_envelope` pipeline (T006 fixture schema).
- Fail-closed on HTTP errors, non-JSON output, prose-like content, unsafe
  truth/canon/approval labels, and schema violations.
- Environment variables used:
  - `OMI_LIVE_TOOLS_ENABLED` (global gate)
  - `OMI_LIVE_OLLAMA_ENABLED` (per-tool gate)
  - `OMI_LIVE_OLLAMA_BLOCKED` (block override)
  - `OMI_LIVE_OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`)
  - `OMI_LIVE_OLLAMA_MODEL` (default `qwen3:8b`)
  - `OMI_LIVE_OLLAMA_MODEL_NAME` (fallback compatibility)
- Default model is `qwen3:8b` per T015A/T015B selection.
- Base URL is configurable for Windows-hosted Ollama reachable from WSL.
- Updated the Ollama unavailable explanation to mention live env flags.

## What was implemented

1. `_build_ollama_model_live_runner` in `backend/omi_analysis_orchestrator.py`.
2. Live path wiring in `_resolve_adapter_runner` for `ollama_model`.
3. Env var name constants for all live Ollama flags.
4. System prompt constant (`_OMI_LIVE_OLLAMA_SYSTEM_PROMPT`) enforcing strict
   JSON-only structured extraction without story prose, rewriting,
   continuation, brainstorming, invented facts, canon/truth/approval claims,
   Memory/Canon mutation, or promotion/apply-promotion.

## Tests added

11 new tests in `tests/test_omi_ollama_model_adapter_contract.py`:

1. `test_live_ollama_disabled_by_default_returns_unavailable`
2. `test_live_ollama_enabled_with_mocked_valid_model_returns_candidates`
3. `test_live_ollama_uses_env_base_url`
4. `test_live_ollama_uses_env_model`
5. `test_live_ollama_uses_env_model_name_compat`
6. `test_live_ollama_http_error_fails_closed`
7. `test_live_ollama_invalid_response_json_fails_closed`
8. `test_live_ollama_missing_message_content_fails_closed`
9. `test_live_ollama_prose_output_fails_closed`
10. `test_live_ollama_unsafe_output_fails_closed`
11. `test_existing_fixture_ollama_tests_still_pass`

All tests mock `urllib.request.urlopen` and do not require real Ollama or
network access.

## Test results

- `tests/test_omi_ollama_model_adapter_contract.py`: **30 passed**
  (19 existing fixture + 11 new)
- `tests/test_omi_live_runtime_preflight_contract.py`: **23 passed**
  (no compatibility update needed)
- `tests/test_omi_tool_assisted_orchestrator_contract.py`: **26 passed**
- `tests/test_omi_tool_assisted_persistence_contract.py`: **5 passed**

## Safety boundaries preserved

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- No real model analysis was run in this task.
- No real `/api/chat` or `/api/generate` call was made during tests.
- No Memory/Canon mutation, automatic promotion records, automatic
  apply-promotion, or story prose behavior was added.
- Live model output is treated as candidate-support material only, never
  truth/canon.
- Fixture/mock contract remains supported and remains scaffolding only.
- No frontend files changed.
- No package/dependency files changed.
- Nothing was staged or committed.

## Related tasks

- T006: fixture-only `ollama_model` contract (schema validation).
- T013: runtime preflight and disabled-by-default flags.
- T015A: Windows Ollama runtime and fixture contract inspection.
- T015B: Ollama HTTP preflight and model availability.
- **T015D (next)**: manual real `qwen3:8b` validation.
