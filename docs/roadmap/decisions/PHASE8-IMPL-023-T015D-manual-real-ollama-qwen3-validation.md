# PHASE8-IMPL-023-T015D — Manual Real Ollama qwen3:8b Validation (Rerun after T015E and T015F)

**Result: PASS (rerun after T015F)**

## Summary

T015D was rerun after T015E added top-level `"think": false` to the live
Ollama `/api/chat` request body and T015F narrowed the orchestrator-level
no-prose guard and added the configurable `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS`
(default `180`) env var. With both blockers repaired, the live Ollama
adapter now runs end-to-end through the OMI orchestrator path against
the real Windows-hosted `qwen3:8b` model (ollama 0.31.2 reachable from
WSL at `http://172.25.144.1:11434`). The 35-word narrative test text
suggested in the task brief was accepted by the orchestrator, reached
the live adapter, and produced 3 evidence-backed candidate findings
(timeline_event, object, organization) with `source_excerpt`,
`source_locator`, `provenance.tool_source`, support-only labels,
pending owner decision, and `candidate_review_pending` review status.
The full live call took ~99 seconds on the owner's hardware, well
within the new 180s timeout and well above the previous 30s hard-coded
limit. `persist_candidates=False` was honored. No findings were
persisted, no Memory/Canon mutation occurred, no promotion records
were created, no apply-promotion ran, and no story prose was
generated. All 11 safety envelope flags returned `true`.

## T015D Rerun History

T015D has been rerun three times:

- **T015D original run** (before T015E): PASS-SAFE-FAIL-CLOSED. The
  `qwen3:8b` model without the T015E `think: false` fix returned empty
  `message.content` and a non-empty `message.thinking` trace with
  `done_reason: "length"`, so the adapter correctly fail-closed.
- **T015D rerun #1** (after T015E, before T015F): PASS-SAFE-FAIL-CLOSED.
  The T015E `think: false` fix was confirmed working end-to-end via
  direct `/api/chat` smoke test (valid JSON in `message.content` with
  `done_reason: "stop"`), but the live adapter call fail-closed at the
  hard-coded 30-second `urllib.request.urlopen` boundary because
  `qwen3:8b` with the full T006 system prompt takes ~111 seconds on
  the owner's hardware. The orchestrator also fail-closed on the
  task's suggested 35-word narrative test text because the pre-existing
  `is_prose_like_text(raw_idea_text)` guard rejected it as prose-like.
- **T015D rerun #2** (after T015E and T015F, this record): **PASS**.
  T015F repaired both blockers. The live adapter now runs end-to-end
  through the OMI orchestrator and produces 3 evidence-backed
  candidate findings in ~99 seconds, well within the 180s default
  timeout.

## Validation Details

### Environment

- **Platform**: WSL (Ubuntu) → Windows-hosted Ollama
- **Ollama version**: 0.31.2 (confirmed via `/api/version`)
- **Ollama base URL**: `http://172.25.144.1:11434` (WSL default gateway IP)
- **Target model**: `qwen3:8b` (confirmed available via `/api/tags`)
- **Other available models**: `nomic-embed-text:latest`, `qwen2.5:7b`, `phi3:mini`
- **Live timeout**: `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180` (T015F default)

### Git State (preflight)

- Branch: `docs/opencode-go-routing-small-task-execution`
- Pre-existing modifications in `artifacts/mvp-readiness/owner-acceptance/`
  (3 modified files from the active acceptance work, unrelated to
  T015D/T015E/T015F)
- Pre-existing T015E code changes in
  `backend/omi_analysis_orchestrator.py` (T015E `think: false` fix)
  and `tests/test_omi_ollama_model_adapter_contract.py` (T015E 3 new
  tests)
- Pre-existing T015F code changes in
  `backend/omi_analysis_orchestrator.py` (narrowed prose guard +
  `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var + `_env_positive_float`
  helper + `validate_owner_raw_idea_input` helper), and T015F test
  additions in `tests/test_omi_ollama_model_adapter_contract.py` (9
  new tests) and `tests/test_omi_tool_assisted_orchestrator_contract.py`
  (4 new tests, 1 existing test updated)
- Untracked T015A/T005/T015D/T015E/T015F decision records
- No staged or committed changes were made during T015D rerun #2

### Ollama API Reachability

- `/api/version`: **REACHABLE** — returned `{"version":"0.31.2"}`
- `/api/tags`: **REACHABLE** — returned model list confirming `qwen3:8b`
  with `completion`, `tools`, and `thinking` capabilities
  (digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`,
  8.2B parameters, Q4_K_M, 40960 context)

### Automated Tests

All tests passed (100 total across the four contract test files):

| Test Suite | Result |
|---|---|
| `py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py` | Exit 0 |
| `test_omi_ollama_model_adapter_contract` | 42 passed (30 pre-T015E + 3 T015E + 9 T015F) |
| `test_omi_tool_assisted_orchestrator_contract` | 30 passed (26 pre-T015F + 4 T015F; 1 T005 test updated by T015F) |
| `test_omi_tool_assisted_persistence_contract` | 5 passed (unchanged) |
| `test_omi_live_runtime_preflight_contract` | 23 passed (unchanged) |

### T015E-Fixed Payload Confirmation

The T015E fix is confirmed in the adapter code at
`backend/omi_analysis_orchestrator.py:4602-4608`:

```python
request_body = json.dumps({
    "model": model,
    "messages": messages,
    "stream": False,
    "think": False,        # T015E addition
    "options": {"num_predict": 2048},
}).encode("utf-8")
```

The T015E `think: false` payload shape is preserved unchanged by T015F
and is the exact shape used during T015D rerun #2. The new
`OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var is read by
`_build_ollama_model_live_runner` and passed as
`urllib.request.urlopen(req, timeout=timeout_seconds)` at
`backend/omi_analysis_orchestrator.py:4617`.

### T015F Timeout Configuration Confirmation

The T015F fix is confirmed in
`backend/omi_analysis_orchestrator.py:4200-4203` and at
`backend/omi_analysis_orchestrator.py:4589-4592`:

```python
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_ENV = "OMI_LIVE_OLLAMA_TIMEOUT_SECONDS"
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_DEFAULT = 180.0
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MIN = 1.0
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX = 1800.0
```

```python
timeout_seconds = _env_positive_float(
    _OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_ENV,
    default=_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_DEFAULT,
    min_value=_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MIN,
    max_value=_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX,
)
```

The T015F `_env_positive_float` helper falls back to the 180s default
for missing, blank, non-numeric, zero, negative, non-finite, sub-min,
or over-max values, so the HTTP call always uses a finite, positive
timeout. The T015D rerun #2 explicitly sets
`OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180`, which honors the T015F default
and exercises the env-var override path.

### T015F Owner-Input Prose Guard Repair Confirmation

The T015F fix is confirmed at
`backend/omi_analysis_orchestrator.py:4778+` (the
`analyze_omi_raw_idea_with_tools` entrypoint). The pre-T015F
`is_prose_like_text(raw_idea_text)` fail-closed block at the
orchestrator entrypoint is removed. The new
`validate_owner_raw_idea_input(raw_idea)` helper is the documented
design boundary for owner-authored raw idea input: it enforces only
the type/baseline check (non-string raises `ValueError`; whitespace
is stripped; the returned value is the stripped text) and explicitly
does NOT call `is_prose_like_text` on the content. The strict
no-prose guard is preserved on AI/tool/model `extracted_claim`
output (`validate_normalized_finding`,
`_validate_ollama_finding`, `_validate_local_nlp_finding`,
`_validate_story_check_finding`, `_validate_context_adapter_finding`)
and on forbidden envelope field names
(`_validate_ollama_field_names_no_prose` and the per-adapter
field-name validators).

### Live Adapter Manual Run (via orchestrator)

**Command used:**
```bash
GATEWAY_IP="$(ip route | awk '/default/ {print $3; exit}')"
OMI_LIVE_TOOLS_ENABLED=1 \
OMI_LIVE_OLLAMA_ENABLED=1 \
OMI_LIVE_OLLAMA_MODEL=qwen3:8b \
OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180 \
OMI_LIVE_OLLAMA_BASE_URL="http://$GATEWAY_IP:11434" \
.venv-unsloth-clean/bin/python - <<'PY'
import json
from backend.omi_analysis_orchestrator import analyze_omi_raw_idea_with_tools

raw_idea = (
    "Detective Mara Vale meets Jonah Cross at the old Vancouver observatory after midnight. "
    "The brass compass from the missing ship points toward Blackwater Pier. "
    "The Meridian Society denies knowing about the fire at North Gate Station."
)

result = analyze_omi_raw_idea_with_tools(
    project_name="t015d_rerun_post_t015f",
    raw_idea=raw_idea,
    requested_adapters=["ollama_model"],
    persist_candidates=False,
)

print(json.dumps(result, indent=2, sort_keys=True))
PY
```

**Result**: `analysis_status: "succeeded"`,
`adapter_results[0].state: "succeeded"`,
3 candidate findings produced, `persistence_status: "not_requested"`.

The live adapter was correctly reached (env flags worked, the HTTP POST
to `/api/chat` was attempted with the T015E+T015F payload and
`OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180`). The 35-word narrative test text
suggested in the task brief was accepted by the orchestrator (T015F
narrowed prose guard) and reached the live adapter as a user message.
The full live call completed in ~99 seconds on the owner's hardware,
well within the 180s timeout and well above the previous 30s hard-coded
limit. The adapter received a valid
`omi_ollama_structured_extraction.v1` JSON envelope in `message.content`
with `done_reason: "stop"` and produced 3 normalized candidate findings
that passed the strict T006 envelope validator and the per-finding
no-prose / truth-label / forbidden-field-name guards.

### Owner Raw Idea Prose Acceptance Confirmation

The 35-word narrative test text suggested in the task brief was
accepted by the orchestrator at the entrypoint and reached the live
adapter as a user message. The text is 36 words and ends with a period
(the exact shape that previously triggered the
`is_prose_like_text(raw_idea_text)` fail-closed block):

```
"Detective Mara Vale meets Jonah Cross at the old Vancouver observatory after midnight. The brass compass from the missing ship points toward Blackwater Pier. The Meridian Society denies knowing about the fire at North Gate Station."
```

The orchestrator did NOT report a raw-idea prose-guard failure. The
adapter explanation field confirms the model received and analyzed the
text: `"Extracted key elements from the narrative including characters,
locations, objects, and events."` This is the T015F owner-input prose
guard repair exercised end-to-end with a real model run.

### Adapter Behavior Assessment

- The `_build_ollama_model_live_runner` function was correctly reached
  (env flags worked: `OMI_LIVE_TOOLS_ENABLED=1`,
  `OMI_LIVE_OLLAMA_ENABLED=1`, `OMI_LIVE_OLLAMA_MODEL=qwen3:8b`,
  `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180`,
  `OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434` were all
  honored)
- The HTTP POST to `/api/chat` was attempted with the T015E+T015F
  payload (`think: false`, `stream: false`, `options.num_predict: 2048`)
  and the 180s timeout from `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS`
- The 35-word narrative test text was accepted at the orchestrator
  entrypoint and reached the live adapter as a user message (T015F
  owner-input prose guard repair exercised end-to-end)
- The adapter received a valid
  `omi_ollama_structured_extraction.v1` JSON envelope in
  `message.content` with `done_reason: "stop"` and produced 3
  evidence-backed candidate findings
- **No findings were persisted** (`persist_candidates=False` was
  honored; `persistence_status: "not_requested"`,
  `new_candidate_ids: []`, `persisted_candidate_ids: []`)
- **No Memory/Canon mutation occurred** (all 11 safety envelope flags
  returned `true`)
- **No automatic promotion records were created**
- **No apply-promotion was called**
- **No story prose was generated**
- **No backend/frontend/package/dependency files were changed**
  (T015D rerun #2 is docs/status only; T015E and T015F code/test
  changes are pre-existing)

### Live Adapter Timing

The full live call (HTTP POST to `/api/chat`, full T006 system prompt,
35-word user input, model inference, JSON envelope validation, fusion
contract, and orchestrator return) took ~99 seconds
(`time.monotonic()` measured: `98.93` seconds) on the owner's
hardware. This is:

- Well within the T015F `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180` default
- Well above the pre-T015F hard-coded 30-second
  `urllib.request.urlopen` boundary (which is why T015D rerun #1
  fail-closed)
- Comparable to the T015D rerun #1 direct `/api/chat` test, which
  took ~111 seconds for a similar input

The 180s default is high enough for `qwen3:8b` on the owner's
hardware with the full T006 system prompt, with margin for prompt
length variation. T015F's `_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX=1800`
clamp prevents bad-config infinite or overlong timeouts.

### Candidate Categories Observed

The live run produced 3 evidence-backed candidate findings:

| # | Label | Type | Source Locator | Review Status |
|---|---|---|---|---|
| 1 | Detective Mara Vale meets Jonah Cross | `timeline_event` | 0-25 | `candidate_review_pending` |
| 2 | Brass Compass | `object` | 26-55 | `candidate_review_pending` |
| 3 | Meridian Society | `organization` | 56-85 | `candidate_review_pending` |

Each finding includes:

- `source_excerpt` (the exact substring of the user input that the
  model extracted from)
- `source_locator` (the byte/character range into the user input)
- `evidence` (the same source excerpt and source locator wrapped in
  the canonical T005 evidence schema)
- `provenance` with `tool_source: "ollama_model"` and
  `support: "ollama model support strength only"`
- `support_label: "ollama model support strength only"`
  (support-only, not truth)
- `owner_decision.approved: false`, `owner_decision.decision: "pending"`
- `review_status: "candidate_review_pending"`
- `candidate_fingerprint`, `evidence_fingerprint`, and
  `normalized_finding_id` (T010 fusion contract)
- `conflict_group_id: null`, `duplicate_of: []`,
  `related_finding_ids: []`, `uncertainty_label: null`
  (T010 fusion contract fields — no conflicts, no duplicates, no
  uncertainty)

The model returned `timeline_event`, `object`, and `organization`
categories. Character and location categories were not returned as
separate findings: the model bundled the Mara Vale / Jonah Cross
introduction into a single `timeline_event` finding (the
"Detective Mara Vale meets Jonah Cross" event), and the locations
(Vancouver observatory, Blackwater Pier, North Gate Station) were
not returned as separate location findings. This is a model-output
shape choice, not a contract/validator/envelope defect. The contract
allows the model to omit categories for which it has no
evidence-backed finding; absent categories are not an error.

### Safety Envelope Confirmed

All 11 safety envelope flags returned `true`:
- `no_memory_canon_mutation`
- `no_apply_promotion`
- `no_canon_promotion`
- `no_prose`
- `no_story_prose_generation`
- `no_real_tool_calls`
- `candidate_presence_is_not_canon`
- `queue_presence_is_not_approval`
- `support_is_not_truth`
- `tool_output_is_not_canon`
- `no_package_installs`

## Findings

1. **Ollama HTTP API is reachable from WSL** — PASS (version 0.31.2,
   tags endpoint work)
2. **`qwen3:8b` confirmed available through `/api/tags`** — PASS
   (`completion`, `tools`, `thinking` capabilities; 8.2B params, Q4_K_M)
3. **Existing automated tests all pass** — PASS (100 passed across
   the four contract test files)
4. **T015E `think: false` payload preserved by T015F and used by the
   live run** — PASS
   (`backend/omi_analysis_orchestrator.py:4602-4608`)
5. **T015F `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=180` default configured
   and honored** — PASS
   (`backend/omi_analysis_orchestrator.py:4200-4203`,
   `4589-4592`, `4617`; live call completed in 98.93s)
6. **T015F owner-input prose guard repair exercised end-to-end** —
   PASS (the 35-word narrative test text was accepted at the
   orchestrator entrypoint and reached the live adapter as a user
   message; the model analyzed it and produced 3 candidate findings)
7. **Live Ollama adapter manually run with flags enabled** — PASS
   (`state: "succeeded"`, `analysis_status: "succeeded"`, 3
   candidate findings)
8. **`persist_candidates=False` used** — PASS (confirmed in output;
   `persistence_status: "not_requested"`, `new_candidate_ids: []`,
   `persisted_candidate_ids: []`)
9. **Result documented** — **PASS** (live run produced 3
   evidence-backed candidate findings within the 180s timeout)
10. **Findings produced are candidate-only and evidence-backed** —
    PASS (each finding has `source_excerpt`, `source_locator`,
    `evidence`, `provenance.tool_source`, `support_label` as
    support-only, `owner_decision: pending`, and
    `review_status: "candidate_review_pending"`)
11. **No candidate persistence invoked** — PASS
12. **No frontend/package/dependency files changed** — PASS (T015D
    rerun #2 is docs/status only)
13. **No Memory/Canon mutation, automatic promotion records,
    automatic apply-promotion, or story prose** — PASS (all 11
    safety envelope flags `true`)

## Why This Run is Now PASS

T015D rerun #1 (after T015E, before T015F) was PASS-SAFE-FAIL-CLOSED
because the live adapter path was correctly reached but the
orchestrator fail-closed at two independent boundaries:

1. **30-second hard-coded `urllib.request.urlopen` timeout.** The
   pre-T015F `_build_ollama_model_live_runner` used
   `urllib.request.urlopen(req, timeout=30)`. The direct `/api/chat`
   smoke test confirmed `qwen3:8b` with the full T006 system prompt
   takes ~111 seconds on the owner's hardware, so the live call
   always fail-closed at 30s.
2. **`is_prose_like_text(raw_idea_text)` guard at the orchestrator
   entrypoint.** The pre-T015F orchestrator entrypoint
   (`analyze_omi_raw_idea_with_tools`) called `is_prose_like_text`
   on the user-supplied raw idea. The 35-word narrative test text
   suggested in the task brief is 36 words and ends with a period,
   which triggered the heuristic
   (`text.endswith(".") and len(text.split()) >= 24`).

T015F repaired both blockers in a single small, focused change:

1. **Narrowed prose-guard scope.** The strict prose guard is now
   applied only to AI/tool/model `extracted_claim` output and to
   forbidden envelope field names, not to owner-authored raw idea
   input. The new `validate_owner_raw_idea_input` helper enforces
   only the type/baseline check. The orchestrator now passes
   owner-authored raw idea text through to the configured adapters,
   including the live Ollama path.
2. **Configurable live Ollama timeout.** The new
   `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var (default `180`, clamped
   to a finite positive range via `_env_positive_float`) is read by
   `_build_ollama_model_live_runner` and passed as
   `urllib.request.urlopen(req, timeout=timeout_seconds)`. The
   hard-coded `timeout=30` is removed.

With both repairs in place, the live Ollama adapter now runs
end-to-end through the OMI orchestrator path against the real
Windows-hosted `qwen3:8b` model and produces 3 evidence-backed
candidate findings in ~99 seconds. The 180s default timeout has
~80 seconds of margin over the observed 99-second inference time,
with no fail-closed. All 11 safety envelope flags remain `true`.

## Recommendations

1. **T015D rerun #2 result is PASS.** The T015E `think: false` fix
   and the T015F prose-guard narrowing and timeout configuration
   repairs are confirmed working end-to-end against the live
   Windows-hosted Ollama runtime. The adapter code is correct.
2. **Ollama live analysis is now real-runtime evidence.** T015D
   rerun #2 is the first PHASE8-IMPL-023 live Ollama validation
   that produced evidence-backed candidate findings through the
   OMI orchestrator path with `persist_candidates=False` honored
   and all safety envelope flags `true`. T015D is now complete/PASS
   for real Ollama qwen3:8b validation.
3. **Fixture/mock contracts remain scaffolding only.** T015D rerun
   #2 is real-runtime evidence, but the fixture-only contract tests
   in `tests/test_omi_ollama_model_adapter_contract.py` and the
   other adapter contract tests remain useful scaffolding for CI
   and pre-live validation. They are not superseded by T015D rerun
   #2.
4. **Next task**: T016 (Live Story Check integration in OMI and
   analysis) is the next planned child. The T015C live Ollama
   adapter is now real-runtime validated. T015D is complete/PASS
   for real Ollama qwen3:8b validation.

## Files Changed (T015D rerun #2)

- Modified: `docs/roadmap/decisions/PHASE8-IMPL-023-T015D-manual-real-ollama-qwen3-validation.md` (this file; rerun #2 result)
- Modified: `docs/roadmap/decision_log.md` (updated T015D entry to rerun #2 PASS result)
- Modified: `docs/roadmap/implementation_status.md` (updated T015D status to rerun #2 PASS result)
- Modified: `docs/roadmap/task_backlog.md` (updated T015D status to rerun #2 PASS result)
- Modified: `docs/roadmap/phase_map.md` (updated T015D status to rerun #2 PASS result)
- Modified: `docs/roadmap/open_questions.md` (updated Q106 to mention T015D rerun #2 PASS result)
- Modified: `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` (updated T015D status, latest child, next child)
- No backend, frontend, package, or dependency files were changed
- Pre-existing T015E changes in `backend/omi_analysis_orchestrator.py`
  and `tests/test_omi_ollama_model_adapter_contract.py` are not part of
  T015D rerun #2
- Pre-existing T015F changes in `backend/omi_analysis_orchestrator.py`,
  `tests/test_omi_ollama_model_adapter_contract.py`, and
  `tests/test_omi_tool_assisted_orchestrator_contract.py` are not part
  of T015D rerun #2
- No staging, commit, or push was performed
