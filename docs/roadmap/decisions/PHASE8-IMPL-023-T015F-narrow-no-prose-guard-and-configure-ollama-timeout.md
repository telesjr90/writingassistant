# PHASE8-IMPL-023-T015F — Narrow No-Prose Guard Scope and Configure Live Ollama Timeout

## Decision

**Accepted.** T015F narrows the no-prose guard scope in
`analyze_omi_raw_idea_with_tools` so owner-authored raw idea input is
accepted as analyzable data even when it looks like prose, and
configures the live Ollama HTTP timeout through
`OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` (default `180` seconds).

## Scope

- Adds `validate_owner_raw_idea_input` to
  `backend/omi_analysis_orchestrator.py` to document and enforce the
  owner-input boundary. The helper validates only the type/baseline
  check (must be a string, returns the stripped value) and explicitly
  does NOT call `is_prose_like_text` on the content.
- Removes the orchestrator-entrypoint `is_prose_like_text(raw_idea_text)`
  fail-closed block in `analyze_omi_raw_idea_with_tools`. The
  orchestrator now passes owner-authored raw idea text through to the
  configured adapters, including the live Ollama path, so the model can
  analyze the text. The empty-string short-circuit and the non-string
  `ValueError` are preserved.
- Keeps the existing strict prose guard on AI/tool/model output
  (`is_prose_like_text(extracted_claim)` in
  `validate_normalized_finding`, `_validate_ollama_finding`,
  `_validate_local_nlp_finding`, `_validate_story_check_finding`,
  and `_validate_context_adapter_finding`). The prose guard remains
  strict on forbidden envelope field names (rewrite, continue, outline,
  draft, polish, improve, expand, imitate, revise, etc.) via
  `_validate_ollama_field_names_no_prose` and the per-adapter
  field-name validators.
- Adds `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var (default `180`) for
  the live Ollama HTTP timeout. Adds `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_ENV`,
  `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_DEFAULT = 180.0`,
  `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MIN = 1.0`, and
  `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX = 1800.0` constants. Adds
  `_env_positive_float` helper that returns the default for missing,
  blank, non-numeric, zero, negative, non-finite, sub-min, or
  over-max values. The HTTP call always uses a finite, positive
  timeout.
- Updates `_build_ollama_model_live_runner` to read the configured
  timeout from `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` and pass it to
  `urllib.request.urlopen(..., timeout=...)`. The hard-coded
  `timeout=30` is replaced with the configured value.
- Preserves all existing T015E behavior: top-level `think: false`,
  `stream: false`, `options.num_predict: 2048`, `message.thinking`
  ignored, `OMI_LIVE_OLLAMA_BASE_URL` / `OMI_LIVE_OLLAMA_MODEL` /
  `OMI_LIVE_OLLAMA_MODEL_NAME` env vars, T006 strict envelope
  validation, fixture contract, fail-closed behavior on HTTP errors /
  non-JSON / prose / unsafe truth/canon output / schema violations /
  missing evidence/source_locator / auto-approved owner decisions.
- Adds 9 new tests in
  `tests/test_omi_ollama_model_adapter_contract.py` covering the
  timeout configuration and the narrowed prose guard, and 4 new
  tests in `tests/test_omi_tool_assisted_orchestrator_contract.py`
  covering the owner-prose input acceptance and the
  `validate_owner_raw_idea_input` helper. Existing tests are updated
  to reflect the narrowed prose-guard scope at the orchestrator
  entrypoint.
- No package/dependency changes.
- No frontend files changed.
- No Memory/Canon mutation, no automatic promotion records, no
  automatic apply-promotion, and no story prose behavior added.

## Why this change is required

T015D rerun (after T015E) confirmed:

- Ollama HTTP API is reachable from WSL at
  `http://172.25.144.1:11434` (version 0.31.2).
- `qwen3:8b` is confirmed available via `/api/tags`.
- T015E `think: false` payload works end-to-end via direct `/api/chat`
  smoke test: trivial "ping" returned valid JSON in 3.7s; full T006
  system prompt returned a valid `omi_ollama_structured_extraction.v1`
  envelope in 111.3s.
- The live adapter path was correctly reached behind env flags
  (`OMI_LIVE_TOOLS_ENABLED=1` + `OMI_LIVE_OLLAMA_ENABLED=1` +
  `OMI_LIVE_OLLAMA_MODEL=qwen3:8b` + base URL).
- The orchestrator path still fail-closed at the
  `urllib.request.urlopen(req, timeout=30)` boundary because
  `qwen3:8b` with the full T006 system prompt takes ~111 seconds on
  the owner's hardware — well above the 30-second hard-coded timeout.
- The orchestrator also fail-closed because the suggested 35-word
  narrative test text triggered the pre-existing
  `is_prose_like_text(raw_idea_text)` guard at the orchestrator
  entrypoint (`text.endswith(".") and len(text.split()) >= 24`
  heuristic). The orchestrator refused to run analysis with
  `analysis_status: "fail_closed"`.

T015F repairs these two blockers so live Ollama can complete real
OMI analysis through the orchestrator path:

1. **Narrow the no-prose guard scope.** The pre-existing T005/T006
   prose guard was applied to BOTH the owner-authored raw idea input
   AND the AI/tool/model output. The guard's intent — and its safety
   value — is on the model output boundary (where the model could
   smuggle generated prose, rewrites, continuations, outlines, drafts,
   polish, expansions, imitations, revisions, truth/canon/approval
   claims, Memory/Canon mutation requests, promotion records, or
   apply-promotion instructions through the strict JSON/schema
   validator). It was not intended to block owner-authored raw idea
   text. Owners legitimately capture scenes, beats, and dialogue
   fragments as raw planning notes. Treating owner input as prose-like
   and refusing to analyze it defeats the entire OMI analysis path.
   The fix preserves the strict guard on model output while
   accepting owner input as analyzable data.

2. **Configure the live Ollama timeout.** The 30-second hard-coded
   timeout is a deliberate finite boundary to prevent indefinite
   blocking, but it is too short for `qwen3:8b` with the full T006
   system prompt (~111s). The fix makes the timeout configurable
   via `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` with a default of 180
   seconds — high enough for the full T006 prompt on the owner's
   hardware, with a finite, positive, clamped range to prevent
   bad-config (zero, negative, infinite, non-numeric) values from
   creating an infinite-block or zero-timeout regression.

## What was implemented

1. `validate_owner_raw_idea_input(raw_idea)` in
   `backend/omi_analysis_orchestrator.py` enforces the type/baseline
   check (non-string raises `ValueError`; whitespace is stripped; the
   returned value is the stripped text). It does NOT call
   `is_prose_like_text` on the content. This helper is the documented
   design boundary for owner-authored raw idea input.

2. The `is_prose_like_text(raw_idea_text)` fail-closed block in
   `analyze_omi_raw_idea_with_tools` is removed. The orchestrator
   now passes owner-authored raw idea text through to the
   configured adapters, including the live Ollama path. The
   empty-string short-circuit (returns
   `analysis_status == "empty"`) and the non-string `ValueError`
   remain.

3. `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_ENV`,
   `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_DEFAULT = 180.0`,
   `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MIN = 1.0`, and
   `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX = 1800.0` constants are
   added to the live Ollama config block in
   `backend/omi_analysis_orchestrator.py`.

4. `_env_positive_float(env, name, *, default, min_value, max_value)`
   helper is added. It returns `default` for missing, blank,
   non-numeric, zero, negative, non-finite, sub-min, or over-max
   values; otherwise it returns the parsed finite float. The
   helper is pure and side-effect free.

5. `_build_ollama_model_live_runner` in
   `backend/omi_analysis_orchestrator.py` now reads the timeout
   from `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` via `_env_positive_float`
   and uses the resulting value as `urllib.request.urlopen(..., timeout=...)`.
   The hard-coded `timeout=30` is removed. The runner's docstring
   records the new env var and the clamped range.

6. The T015C/T015E docstring of `_build_ollama_model_live_runner`
   is updated to document the `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env
   var and the safe-fallback semantics.

7. The module docstring of `backend/omi_analysis_orchestrator.py`
   and the `analyze_omi_raw_idea_with_tools` docstring are updated
   to document the narrowed prose-guard scope: prose guard remains
   strict on AI/tool/model output and on forbidden envelope field
   names; owner-authored raw idea text is accepted as analyzable
   data.

8. The `validate_owner_raw_idea_input` helper is exported as a
   public API so future call sites and tests can use it directly.

## Structured JSON mode/schema (deferred)

T015F considered adding Ollama request `format` support (JSON or
JSON schema) to the `/api/chat` payload. This is intentionally
**deferred** to a future task because:

- The existing T006 envelope/schema validation
  (`validate_ollama_model_envelope`) remains the authoritative
  validator regardless of any `format` hint.
- T015D rerun confirmed that the T015E `think: false` fix alone
  produces valid JSON in `message.content` with `done_reason:
  "stop"` end-to-end against the live Windows-hosted Ollama
  runtime.
- Adding `format` requires live Ollama validation to confirm
  `qwen3:8b` (and any future selected model) honors the JSON mode
  hint; the T015D rerun `done_reason: "stop"` and valid JSON
  response confirms the model already produces valid JSON without
  the hint.
- The task scope explicitly allowed skipping the optional
  `format` addition if it would create uncertainty, and recording
  it as a future improvement.

Recorded as a future improvement in
`docs/roadmap/open_questions.md` (deferred item).

## Tests added

### `tests/test_omi_tool_assisted_orchestrator_contract.py` (4 new tests)

1. `test_owner_prose_input_is_accepted_as_data_at_orchestrator_entrypoint`
   — 35+ word owner-authored raw idea prose is accepted by the
   orchestrator; a test-only `adapter_runners` hook proves the prose
   text reached the runner and produced findings; no raw-idea
   prose-guard failure in the explanation.

2. `test_owner_prose_input_via_validate_owner_raw_idea_input_helper`
   — `validate_owner_raw_idea_input` accepts prose-shaped input,
   strips whitespace, returns empty/whitespace-only as the stripped
   value (the orchestrator short-circuits empty input), and raises
   `ValueError` on non-string input.

3. `test_ai_tool_model_output_prose_still_fails_closed` — model
   output with a prose-shaped `extracted_claim` is still rejected by
   `validate_normalized_finding`.

4. `test_ai_tool_model_output_truth_label_still_fails_closed` —
   model output with a truth/canon/approval `support_label` is
   still rejected by `validate_normalized_finding`.

### Updated test in `tests/test_omi_tool_assisted_orchestrator_contract.py`

- `test_unsafe_prose_output_is_rejected` — updated to reflect the
  narrowed prose-guard scope. The model-output prose rejection
  assertion is preserved. The orchestrator-level assertion is
  updated to verify that the orchestrator does NOT report a
  raw-idea prose-guard failure (the analysis_status may still be
  `empty`/`fail_closed` if no adapter produces findings, but not
  because of the prose-shape of the raw idea).

### `tests/test_omi_ollama_model_adapter_contract.py` (9 new tests)

1. `test_live_ollama_default_timeout_is_180_seconds` — the live
   Ollama HTTP timeout defaults to 180 seconds when
   `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` is unset.

2. `test_live_ollama_env_timeout_override_is_honored` —
   `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=240` produces a 240-second
   timeout on the live HTTP call.

3. `test_live_ollama_invalid_timeout_falls_back_to_default` —
   non-numeric (`abc`), blank (`""`), zero (`0`, `0.0`), negative
   (`-1`, `-3.5`), above-max (`99999`), and infinity/NaN-like
   (`inf`, `nan`) values all fall back to the safe 180s default.

4. `test_live_ollama_missing_timeout_uses_default` — missing
   `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var uses 180s default.

5. `test_live_ollama_think_false_preserved_in_request_payload` —
   T015E `think: false`, `stream: false`, and
   `options.num_predict: 2048` continue to be sent on the
   `/api/chat` request body. The T015E fix is preserved.

6. `test_live_ollama_accepts_owner_prose_input` — 35+ word
   owner-authored raw idea prose reaches the live Ollama adapter;
   the orchestrator does not report a raw-idea prose-guard
   failure; a mocked valid model response produces a normalized
   finding.

7. `test_live_ollama_model_prose_output_still_fails_closed` —
   live Ollama response with prose-shape `extracted_claim` is
   still rejected by the strict envelope validator; no findings;
   no persistence.

8. `test_live_ollama_model_unsafe_truth_output_still_fails_closed`
   — live Ollama response with truth/canon/approval
   `support_label` is still rejected by the strict envelope
   validator; no findings; no persistence.

9. `test_live_ollama_persistence_boundary_remains_safe` —
   `persist_candidates=False` is honored on the live Ollama path;
   no candidate persistence is invoked even when findings are
   produced.

All new tests mock `urllib.request.urlopen` and do not require real
Ollama or network access. No real `/api/chat` or `/api/generate` call
was made in this task.

## Test results

- `tests/test_omi_ollama_model_adapter_contract.py`: **42 passed**
  (33 existing + 9 new T015F)
- `tests/test_omi_tool_assisted_orchestrator_contract.py`: **30
  passed** (26 existing + 4 new T015F; 1 existing test updated)
- `tests/test_omi_tool_assisted_persistence_contract.py`: **5
  passed** (unchanged)
- `tests/test_omi_live_runtime_preflight_contract.py`: **23
  passed** (T015F is not a preflight task; preflight test file
  unchanged)
- `python3 -m py_compile backend/omi_analysis_orchestrator.py
  backend/omi_runtime_preflight.py backend/main.py`: exit `0`
- Combined T015F task validation: **100 passed** across the four
  contract test files.

## Safety boundaries preserved

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- AI/tool/model output remains strict-bound: prose-shape
  `extracted_claim` fails closed; truth/canon/approved/promoted
  labels fail closed; Memory/Canon mutation, candidate
  persistence, promotion records, and apply-promotion
  instructions in model output fail closed.
- The T006 envelope validator remains the authoritative validator
  for `ollama_model` output.
- No real model analysis was run in this task.
- No real `/api/chat` or `/api/generate` call was made during
  tests or implementation.
- No Memory/Canon mutation, automatic promotion records,
  automatic apply-promotion, or story prose behavior was added.
- Tests mock Ollama and do not require real Ollama/network.
- No frontend files changed.
- No package/dependency files changed.
- Nothing was staged or committed.

## What this task is not

- T015F is not a preflight task. T015B preflight and
  `tests/test_omi_live_runtime_preflight_contract.py` are not
  modified.
- T015F is not a rerun of the T015D manual real Ollama validation.
  T015D must be rerun after T015F to validate real `qwen3:8b`
  output through the orchestrator path with the narrowed
  prose-guard scope and the 180s default timeout. T015D final
  result is **not** marked PASS in this task.
- T015F is not a relaxation of the AI/tool/model output safety
  guard. The prose guard, truth-label guard, no-prose-intent
  field-name guard, no-approval/canon/promoted guard, and
  fail-closed schema validation are all preserved unchanged.
- T015F is not a UI-only filter change. The fix is at the
  backend orchestrator boundary; the prose guard is intentionally
  NOT a UI-only defense.
- T015F does not add structured JSON mode/schema (`format`) to
  the Ollama request. This is intentionally deferred as a future
  improvement.
- T015F does not change persistence behavior. No candidate
  persistence is invoked by T015F; the `persist_candidates=False`
  boundary remains intact and is honored by every new test.

## Security design preserved

- Owner-authored raw idea input is treated as untrusted data, not
  as executable instructions. The model receives it as a user
  message and is asked to analyze it (T006 JSON-only system
  prompt), not to write story prose.
- AI/tool/model output is validated by application code. The
  parser only accepts strict JSON that conforms to the T006
  envelope schema (`omi_ollama_structured_extraction.v1` for
  `ollama_model`, equivalent for other adapters). The parser
  never reads `message.thinking`, never parses findings from
  prose, and never trusts forbidden envelope field names.
- The backend validator, not UI-only filtering, remains the
  primary safety boundary. UI filtering (e.g., owner-facing text
  warnings) is defense-in-depth only; the orchestrator's
  per-adapter envelope validators are the authoritative
  boundary.

## Related tasks

- T005: orchestrator contract and adapter-boundary scaffold
  (introduced the no-prose guard for raw idea and adapter
  output; T015F narrows the raw-idea branch to owner input
  while preserving the model-output branch).
- T006: fixture-only `ollama_model` envelope contract
  (`omi_ollama_structured_extraction.v1`; the authoritative
  validator).
- T013: runtime preflight, health checks, and feature flags
  (env-var-driven live tool enablement; T015F follows the
  same pattern for the timeout).
- T015A: Windows Ollama runtime and fixture contract
  inspection.
- T015B: Ollama HTTP preflight and model availability
  (`OMI_LIVE_OLLAMA_BASE_URL` and `OMI_LIVE_OLLAMA_MODEL` env
  vars; T015F follows the same pattern for
  `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS`).
- T015C: live Ollama structured extraction adapter behind flags
  (T015F's base; the `_build_ollama_model_live_runner` function
  is updated in place).
- T015D: manual real Ollama `qwen3:8b` validation (T015D must
  be rerun after T015F to validate real `qwen3:8b` output
  through the orchestrator path with the narrowed prose-guard
  scope and the 180s default timeout).
- T015E: disable Qwen thinking mode for live Ollama structured
  extraction (T015E's `think: false` payload is preserved by
  T015F; new tests assert the payload is unchanged).
- T016: live Story Check integration (next planned child; not
  in T015F scope).
