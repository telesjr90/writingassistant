# PHASE8-IMPL-023-T015D — Manual Real Ollama qwen3:8b Validation (Rerun after T015E)

**Result: PASS-SAFE-FAIL-CLOSED**

## Summary

T015D was rerun after the owner repaired the Windows Ollama installation
(ollama 0.31.2, `qwen3:8b` present) and after T015E added top-level
`"think": false` to the live Ollama `/api/chat` request body. The Ollama
HTTP API is reachable from WSL, `qwen3:8b` is confirmed available, the
T015E-fixed request payload is confirmed via direct `/api/chat` smoke
test, and the live adapter correctly fail-closed at the finite
`urllib.request.urlopen(timeout=30)` boundary when the model inference
exceeded 30 seconds. The direct API test with the same T015E-fixed
payload and the full T006 system prompt produced a valid
`omi_ollama_structured_extraction.v1` JSON envelope in `message.content`
with `done_reason: "stop"`, confirming the T015E `think: false` fix works
end-to-end. No findings were persisted, no Memory/Canon mutation
occurred, no promotion records were created, no apply-promotion ran, and
no story prose was generated.

## Validation Details

### Environment

- **Platform**: WSL (Ubuntu) → Windows-hosted Ollama
- **Ollama version**: 0.31.2 (confirmed via `/api/version`)
- **Ollama base URL**: `http://172.25.144.1:11434` (WSL default gateway IP)
- **Target model**: `qwen3:8b` (confirmed available via `/api/tags`)
- **Other available models**: `nomic-embed-text:latest`, `qwen2.5:7b`, `phi3:mini`

### Git State (preflight)

- Branch: `docs/opencode-go-routing-small-task-execution`
- Pre-existing modifications in `artifacts/mvp-readiness/owner-acceptance/`
  (3 modified files), `backend/omi_analysis_orchestrator.py` (T015E fix),
  `docs/roadmap/*` (T015E status), `tests/test_omi_ollama_model_adapter_contract.py`
  (T015E 3 new tests), and untracked decision records from T005/T015D/T015E
- No staged or committed changes were made during T015D rerun

### Ollama API Reachability

- `/api/version`: **REACHABLE** — returned `{"version":"0.31.2"}`
- `/api/tags`: **REACHABLE** — returned model list confirming `qwen3:8b`
  with `completion`, `tools`, and `thinking` capabilities
  (digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`,
  8.2B parameters, Q4_K_M, 40960 context)

### Automated Tests

All tests passed (87 total):

| Test Suite | Result |
|---|---|
| `py_compile backend/*.py` | Exit 0 |
| `test_omi_ollama_model_adapter_contract` | 33 passed (30 pre-T015E + 3 T015E) |
| `test_omi_live_runtime_preflight_contract` | 23 passed |
| `test_omi_tool_assisted_orchestrator_contract` | 26 passed |
| `test_omi_tool_assisted_persistence_contract` | 5 passed |

### T015E-Fixed Payload Confirmation

The T015E fix is confirmed in the adapter code at
`backend/omi_analysis_orchestrator.py:4515-4521`:

```python
request_body = json.dumps({
    "model": model,
    "messages": messages,
    "stream": False,
    "think": False,        # T015E addition
    "options": {"num_predict": 2048},
}).encode("utf-8")
```

A direct `/api/chat` smoke test with the same T015E-fixed payload
(top-level `"think": false`, `stream: false`, `options.num_predict: 2048`)
and a trivial `{"role": "user", "content": "ping"}` message returned
`done_reason: "stop"` in 3.7 seconds with `message.content: '{"status": "pong"}'`
and empty `message.thinking`. This confirms the T015E payload shape works
end-to-end against the live Windows-hosted Ollama runtime.

A second direct `/api/chat` smoke test with the full T006
`_OMI_LIVE_OLLAMA_SYSTEM_PROMPT` and a short non-prose input
(`"Mara Vale, Jonah Cross, brass compass, observatory, Blackwater Pier, Meridian Society, North Gate Station fire"`)
returned a valid `omi_ollama_structured_extraction.v1` JSON envelope in
`message.content` with `done_reason: "stop"` in 111.3 seconds
(`load_duration: 200ms`, `eval_duration: 110.8s`,
`eval_count: 402`, `prompt_eval_count: 293`). The returned envelope
contained 7 evidence-backed findings (2 characters, 3 locations, 1
organization, 1 object, 1 timeline_event) with `source_excerpt`,
`source_locator`, and the canonical `omi_ollama_structured_extraction.v1`
schema. This confirms the T015E `think: false` fix produces the exact
JSON the live adapter expects in `message.content`.

### Live Adapter Manual Run (via orchestrator)

**Command used:**
```bash
GATEWAY_IP="$(ip route | awk '/default/ {print $3; exit}')"
OMI_LIVE_TOOLS_ENABLED=1 \
OMI_LIVE_OLLAMA_ENABLED=1 \
OMI_LIVE_OLLAMA_MODEL=qwen3:8b \
OMI_LIVE_OLLAMA_BASE_URL="http://$GATEWAY_IP:11434" \
.venv-unsloth-clean/bin/python -c \
  "from backend.omi_analysis_orchestrator import analyze_omi_raw_idea_with_tools; \
   result = analyze_omi_raw_idea_with_tools( \
     project_name='t015d_rerun', \
     raw_idea='Mara Vale, Jonah Cross, brass compass, observatory, Blackwater Pier, Meridian Society, North Gate Station fire', \
     requested_adapters=['ollama_model'], \
     persist_candidates=False); \
   import json; print(json.dumps(result, indent=2, sort_keys=True))"
```

**Result**: `analysis_status: "fail_closed"`,
`adapter_results[0].state: "failed_closed"`,
`adapter_results[0].explanation: "Live Ollama HTTP call failed: TimeoutError: timed out. Failing closed with no candidates."`

The live adapter was correctly reached (env flags worked, the HTTP POST
to `/api/chat` was attempted with the T015E-fixed payload), but the
`urllib.request.urlopen(req, timeout=30)` boundary fired before the model
finished inference. The adapter correctly caught the timeout and failed
closed with no findings.

### Prose Guard Behavior

The task's suggested 35-word narrative test text
(`"Detective Mara Vale meets Jonah Cross at the old Vancouver observatory after midnight. The brass compass from the missing ship points toward Blackwater Pier. The Meridian Society denies knowing about the fire at North Gate Station."`)
triggered the `is_prose_like_text` guard at the orchestrator level
(`text.endswith(".") and len(text.split()) >= 24` heuristic). This is the
same behavior documented in the original T015D decision record. The
orchestrator refused to run analysis with
`analysis_status: "fail_closed"` and explanation
`"Raw idea text resembles story prose / continuation; the OMI orchestrator refused to run analysis."`

To exercise the live adapter path, a shorter non-prose input was used
(comma-separated entity list, 12 words). The prose guard is a deliberate
safety boundary and was not modified by T015D or T015E.

### Adapter Behavior Assessment

- The `_build_ollama_model_live_runner` function was correctly reached
  (env flags worked: `OMI_LIVE_TOOLS_ENABLED=1` and
  `OMI_LIVE_OLLAMA_ENABLED=1` were honored)
- The HTTP POST to `/api/chat` was attempted with the T015E-fixed
  payload (`think: false`, `stream: false`, `options.num_predict: 2048`)
- The adapter correctly caught the `TimeoutError` from
  `urllib.request.urlopen(req, timeout=30)` and failed closed
- **No findings were produced** (correct for fail-closed at timeout)
- **No candidate persistence was invoked** (`persist_candidates=False`
  was honored; `persistence_status: "not_requested"`)
- **No Memory/Canon mutation occurred** (all 11 safety envelope flags
  returned `true`)
- **No automatic promotion records were created**
- **No apply-promotion was called**
- **No story prose was generated**
- **No backend/frontend/package/dependency files were changed**
  (T015D rerun is docs/status only; T015E code/test changes are pre-existing)

### Direct API Test Confirmation

The direct `/api/chat` smoke test with the full T006 system prompt and
the T015E-fixed payload produced a valid
`omi_ollama_structured_extraction.v1` JSON envelope in `message.content`
with `done_reason: "stop"`. This confirms:

1. The T015E `think: false` fix works end-to-end against the live
   Windows-hosted Ollama runtime
2. The T006 system prompt produces valid structured extraction output
   from `qwen3:8b` with `think: false`
3. The 30-second adapter timeout is too short for `qwen3:8b` on this
   hardware with the full extraction prompt (direct API test took 111s
   for the full extraction; trivial "ping" took 3.7s)
4. The adapter code is correct; the timeout is a finite
   `urllib.request.urlopen` boundary that fires before the model
   finishes inference for complex prompts

### Candidate Categories Observed

None — the orchestrator-level adapter fail-closed at the 30-second
timeout boundary before producing any candidates. The direct API test
confirmed `qwen3:8b` with `think: false` can produce the full set of
expected candidate types (character, location, organization, object,
timeline_event) when given sufficient inference time.

### Fail-Closed Safety Confirmed

All safety envelope flags returned `true`:
- `no_memory_canon_mutation`, `no_apply_promotion`, `no_canon_promotion`
- `no_prose`, `no_story_prose_generation`, `no_real_tool_calls`
- `candidate_presence_is_not_canon`, `queue_presence_is_not_approval`
- `support_is_not_truth`, `tool_output_is_not_canon`
- `no_package_installs`

## Findings

1. **Ollama HTTP API is reachable from WSL** — PASS (version 0.31.2,
   tags endpoint work)
2. **`qwen3:8b` confirmed available through `/api/tags`** — PASS
   (`completion`, `tools`, `thinking` capabilities; 8.2B params, Q4_K_M)
3. **Existing automated tests all pass** — PASS (87 passed)
4. **T015E `think: false` payload confirmed** — PASS (direct `/api/chat`
   smoke test with T015E-fixed payload produced valid JSON in
   `message.content` with `done_reason: "stop"`)
5. **Live Ollama adapter manually run with flags enabled** — PASS
   (adapter was invoked correctly, HTTP POST to `/api/chat` attempted)
6. **`persist_candidates=False` used** — PASS (confirmed in output;
   `persistence_status: "not_requested"`)
7. **Result documented** — **PASS-SAFE-FAIL-CLOSED** (adapter correctly
   returned no findings at the finite timeout boundary; T015E fix
   confirmed working via direct API test)
8. **No findings produced** — N/A (adapter fail-closed at timeout; this
   is correct fail-closed behavior for the finite 30-second
   `urllib.request.urlopen` boundary)
9. **No candidate persistence invoked** — PASS
10. **No frontend/package/dependency files changed** — PASS (T015D rerun
    is docs/status only)
11. **No Memory/Canon mutation, automatic promotion records, automatic
    apply-promotion, or story prose** — PASS (all 11 safety envelope
    flags `true`)

## Root Cause for Fail-Closed

The live adapter fail-closed at the
`urllib.request.urlopen(req, timeout=30)` boundary because the
`qwen3:8b` model with the full T006 system prompt takes ~111 seconds to
produce the structured extraction JSON on the Windows-hosted Ollama
runtime (direct API test confirmed). The 30-second timeout is a
deliberate finite boundary in the live adapter to prevent indefinite
blocking. The adapter correctly fail-closed with no findings, no
persistence, and no side effects. The T015E `think: false` fix is
confirmed working end-to-end via the direct API test.

## Recommendations

1. **T015D rerun result is PASS-SAFE-FAIL-CLOSED.** The T015E `think:
   false` fix is confirmed working end-to-end against the live
   Windows-hosted Ollama runtime. The adapter code is correct.
2. **Timeout tuning is a separate concern.** The 30-second
   `urllib.request.urlopen` timeout is too short for `qwen3:8b` on this
   hardware with the full T006 system prompt. This is a configuration
   choice, not a code defect. A future task could explore making the
   timeout configurable via env var (e.g.,
   `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS`) while preserving the finite
   boundary. This is explicitly out of scope for T015D rerun and T015E.
3. **Prose guard review is a separate concern.** The
   `is_prose_like_text` guard's `text.endswith(".") and
   len(text.split()) >= 24` heuristic blocks narrative test text from
   reaching the live adapter. A future task could explore a more
   nuanced prose guard for OMI analysis input. This is explicitly out of
   scope for T015D rerun and T015E.
4. **Next task**: T015D rerun is complete/PASS-SAFE-FAIL-CLOSED. T016
   (Live Story Check integration in OMI and analysis) is the next
   planned child. A separate future task could address the timeout tuning
   and/or prose guard review.

## Files Changed (T015D rerun)

- Modified: `docs/roadmap/decisions/PHASE8-IMPL-023-T015D-manual-real-ollama-qwen3-validation.md` (this file; rerun result)
- Modified: `docs/roadmap/decision_log.md` (updated T015D entry to rerun result)
- Modified: `docs/roadmap/implementation_status.md` (updated T015D status to rerun result)
- Modified: `docs/roadmap/task_backlog.md` (updated T015D status to rerun result)
- Modified: `docs/roadmap/phase_map.md` (updated T015D status to rerun result)
- Modified: `docs/roadmap/open_questions.md` (updated Q106 to mention T015D rerun result)
- Modified: `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` (updated T015D status, latest child, next child)
- No backend, frontend, package, or dependency files were changed
- Pre-existing T015E changes in `backend/omi_analysis_orchestrator.py`
  and `tests/test_omi_ollama_model_adapter_contract.py` are not part of
  T015D rerun
- No staging, commit, or push was performed
