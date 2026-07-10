# PHASE8-IMPL-023-T015E — Disable Qwen thinking mode for live Ollama structured extraction

## Decision

**Accepted.** T015E disables Qwen3 thinking-mode output for live Ollama
structured extraction by adding top-level `"think": false` to the Ollama
`/api/chat` request payload in the live `ollama_model` runner.

## Scope

- Adds a single top-level field `"think": false` to the live Ollama
  `/api/chat` JSON request body built by
  `_build_ollama_model_live_runner` in
  `backend/omi_analysis_orchestrator.py`.
- Keeps `stream=false`, the finite timeout, the `OMI_LIVE_OLLAMA_BASE_URL` /
  `OMI_LIVE_OLLAMA_MODEL` / `OMI_LIVE_OLLAMA_MODEL_NAME` env vars, and the
  `_OMI_LIVE_OLLAMA_SYSTEM_PROMPT` JSON-only system prompt.
- Keeps all existing fail-closed behavior (empty `message.content`,
  non-JSON content, prose, markdown, unsafe/truth/canon output, schema
  violations, missing/empty evidence/source_locator, auto-approved
  owner decisions, etc.).
- Adds three new focused tests in
  `tests/test_omi_ollama_model_adapter_contract.py` to lock in the new
  request payload and the message.thinking boundary.
- No package/dependency changes.
- No frontend files changed.
- No Memory/Canon mutation, no automatic promotion records, no automatic
  apply-promotion, and no story prose behavior added.
- T015E is not a preflight task; `tests/test_omi_live_runtime_preflight_contract.py`
  was not modified.

## Why this change is required

T015C implemented `_build_ollama_model_live_runner` against the T006 fixture
schema, but it did not disable Qwen3 thinking-mode output. The T015A/T015B
preflight and the T015D manual validation both confirmed that the
Windows-hosted Ollama runtime at `http://172.25.144.1:11434` is reachable
and `qwen3:8b` is available through `/api/tags`, but T015D's manual run
fail-closed on a separate missing-`llama-server.exe` issue before the
thinking-mode failure was observable.

After the owner repaired the Windows Ollama installation
(ollama 0.31.2 with `qwen3:8b` present and WSL reachability to
`http://172.25.144.1:11434` re-confirmed), a direct smoke test against
`/api/chat` reproduced the exact failure shape:

- Without `think: false`:
  - `message.content` was an empty string
  - `message.thinking` contained the model's reasoning trace
  - `done_reason` was `length`
- With top-level `"think": false`:
  - `message.content` returned the expected `OLLAMA_WSL_OK` payload
  - `done_reason` was `stop`

Qwen3 thinking-mode output consumes the response budget that the T006
JSON-only system prompt expects `message.content` to receive, so without
the `think: false` switch the live adapter cannot receive valid JSON in
`message.content` and correctly fail-closes. The owner-confirmed fix is
exactly the top-level `"think": false` field on the `/api/chat` request
body.

The change is intentionally not behind a new opt-in flag. For live
structured extraction, thinking output must be disabled by default so the
adapter receives JSON in `message.content`. The T015C runner still calls
the same `validate_ollama_model_envelope` validator on `message.content`,
and the T006 fail-closed envelope validation continues to apply.

## What was implemented

1. `_build_ollama_model_live_runner` in `backend/omi_analysis_orchestrator.py`
   now sends top-level `think: false` in the `/api/chat` request body.
2. The runner's docstring records the `think: false` field and the
   boundary that `message.thinking` is never parsed as extraction output.
3. `message.thinking` is never read by the runner; extraction JSON is
   parsed only from `message.content`.
4. Empty `message.content` continues to fail closed with no findings and
   no candidate persistence, even when `message.thinking` is non-empty.
5. No new env vars, no new flags, no new opt-in settings.

## Tests added

3 new tests in `tests/test_omi_ollama_model_adapter_contract.py`:

1. `test_live_ollama_request_payload_includes_think_false` — captures
   the live HTTP request body, asserts `think is False`, `stream is False`,
   and `model == "qwen3:8b"`. Adapter must send top-level `think: false`.
2. `test_live_ollama_parses_extraction_json_only_from_message_content` —
   mocks a response where `message.thinking` carries a valid-looking
   extraction envelope and `message.content` carries the canonical
   `_valid_live_model_content()` JSON. The adapter must extract from
   `message.content` only; the thinking trace's labels and claims must
   not appear in the orchestrator's normalized findings.
3. `test_live_ollama_empty_content_with_thinking_fails_closed` — mocks the
   exact Qwen3 thinking-mode failure shape (empty `message.content`,
   non-empty `message.thinking`, `done_reason: "length"`). The adapter
   must fail closed with no findings and no candidate persistence, and
   `message.thinking` must not be parsed as extraction output.

All tests mock `urllib.request.urlopen` and do not require real Ollama or
network access. No real `/api/chat` or `/api/generate` call was made in
this task.

## Test results

- `tests/test_omi_ollama_model_adapter_contract.py`: **33 passed**
  (30 existing + 3 new T015E)
- `tests/test_omi_live_runtime_preflight_contract.py`: **23 passed**
  (no compatibility update needed)
- `tests/test_omi_tool_assisted_orchestrator_contract.py`: **26 passed**
- `tests/test_omi_tool_assisted_persistence_contract.py`: **5 passed**
- `python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py`: exit `0`

## Safety boundaries preserved

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- No real model analysis was run in this task.
- No real `/api/chat` or `/api/generate` call was made during tests or
  implementation.
- No Memory/Canon mutation, automatic promotion records, automatic
  apply-promotion, or story prose behavior was added.
- `message.thinking` is never parsed as extraction output.
- Tests mock Ollama and do not require real Ollama/network.
- No frontend files changed.
- No package/dependency files changed.
- Nothing was staged or committed.

## What this task is not

- T015E is not a preflight task; the T015B preflight and
  `tests/test_omi_live_runtime_preflight_contract.py` are not modified.
- T015E is not a rerun of the T015D manual real Ollama validation. The
  T015D owner-confirmed reasoning trace is recorded in the T015D decision
  record; T015E applies the owner-confirmed fix and adds tests. T015D
  must be rerun after T015E to validate real `qwen3:8b` output with
  `think: false` enabled. T015D final result is **not** marked PASS in
  this task.
- T015E is not a runtime hardening of safety validation; existing
  fail-closed behavior for empty `message.content`, non-JSON, prose,
  unsafe truth/canon/approval output, schema violations, missing
  evidence/source_locator, and auto-approved owner decisions is
  preserved unchanged.
- T015E does not change persistence behavior. No candidate persistence
  is invoked by T015E; the `persist_candidates=False` boundary remains
  intact and is honored by every new test.

## Related tasks

- T006: fixture-only `ollama_model` envelope contract
  (`omi_ollama_structured_extraction.v1`).
- T013: runtime preflight, health checks, and feature flags.
- T015A: Windows Ollama runtime and fixture contract inspection.
- T015B: Ollama HTTP preflight and model availability.
- T015C: live Ollama structured extraction adapter behind flags
  (T015E's base).
- T015D: manual real Ollama `qwen3:8b` validation (T015D must be rerun
  after T015E to validate real `qwen3:8b` output with the
  `think: false` fix).
- T016: live Story Check integration (next planned child).
