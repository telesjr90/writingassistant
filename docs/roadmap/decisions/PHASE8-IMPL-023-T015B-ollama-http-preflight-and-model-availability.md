# PHASE8-IMPL-023-T015B — Ollama HTTP Preflight and Model Availability

## Result

PASS for backend preflight/config/test/docs task.

T015B adds read-only Ollama HTTP API reachability and model availability probing to the existing T013 runtime preflight. No live Ollama analysis adapter was implemented. No model generation was run. No candidates were produced. No backend analysis behavior, frontend code, or package/dependency files were changed beyond preflight/tests/docs.

## Nature

- Backend preflight/config/test/docs task only (T015B).
- T015C (live Ollama structured extraction adapter behind flags) and T015D (manual real `qwen3:8b` validation) are deferred.
- Builds on T015A findings: Ollama CLI is NOT available in WSL; Windows Ollama (0.31.1) IS reachable from WSL at the WSL gateway IP; `qwen3:8b` is the selected MVP model candidate.
- Supports the current environment where Ollama is installed on Windows and reachable from WSL through the Windows host gateway.

## Implementation

### Files Changed

- `backend/omi_runtime_preflight.py` — added Ollama HTTP API probe (`_ollama_http_probe`), updated `_dependency_probe` for `ollama_model`, updated `_tool_report` to include ollama-specific fields.
- `tests/test_omi_live_runtime_preflight_contract.py` — added 9 new Ollama HTTP probe tests, updated 1 existing test.
- `docs/roadmap/decisions/PHASE8-IMPL-023-T015B-ollama-http-preflight-and-model-availability.md` — this decision record.
- `docs/roadmap/decision_log.md` — logged T015B decision.
- `docs/roadmap/implementation_status.md` — updated active frontier.
- `docs/roadmap/task_backlog.md` — updated backlog.
- `docs/roadmap/phase_map.md` — updated phase map.
- `docs/roadmap/open_questions.md` — resolved open question 106 (updated for T015B completion).
- `docs/roadmap/risk_register.md` — unchanged (no new risk).
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` — updated active child sequence.

### Ollama HTTP Probe Behavior

The preflight now probes the Ollama HTTP API using Python standard library only (`urllib.request`). It calls:

- `{base_url}/api/version` — to check API reachability and report Ollama version
- `{base_url}/api/tags` — to check selected model availability

Probe responses are read-only. No `/api/generate`, `/api/chat`, or text-producing endpoints are called.

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `OMI_LIVE_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Override for the Ollama HTTP API base URL (WSL override: Windows host IP) |
| `OMI_LIVE_OLLAMA_MODEL` | `qwen3:8b` | Selected model name for availability check |
| `OMI_LIVE_OLLAMA_MODEL_NAME` | (legacy, preserved) | Fallback if `OMI_LIVE_OLLAMA_MODEL` is not set |
| `OMI_LIVE_OLLAMA_ENABLED` | `false` | Ollama-specific enablement flag (preexisting) |
| `OMI_LIVE_OLLAMA_BLOCKED` | `false` | Explicit override to block Ollama (preexisting) |
| `OMI_LIVE_OLLAMA_BLOCKED_REASON` | (none) | Reason when blocked (preexisting) |

### Preflight Report Fields

New fields in the `ollama_model` tool report:

- `ollama_base_url` — configured base URL
- `ollama_api_available` — whether `/api/version` responded successfully
- `ollama_version` — Ollama version from `/api/version` (or `None`)
- `ollama_model_name` — selected model name
- `ollama_model_available` — whether selected model is in `/api/tags`
- `ollama_probe_detail` — detailed probe reason/message

### Fail-Closed Behavior

- Connection errors (unreachable host, connection refused): `ollama_api_available: false`, `ollama_model_available: false`, clear detail message.
- Timeout: handled by `urllib.request.urlopen(timeout=5)`.
- Invalid JSON from either endpoint: caught by `json.JSONDecodeError`, fail-closed with clear detail.
- Missing `version` field in `/api/version` response: fail-closed.
- Selected model not found in `/api/tags`: `ollama_api_available: true` (API works), `ollama_model_available: false` (model not installed).
- `/api/version` succeeds but `/api/tags` fails: `ollama_api_available: false`, detail explains which endpoint failed.
- Unknown/unexpected exceptions: caught by broad `Exception`, fail-closed with type and message.

### Existing Behavior Preserved

- Global live-tools disabled (`OMI_LIVE_TOOLS_ENABLED=false`) keeps Ollama safe/read-only.
- Ollama-specific flag disabled (`OMI_LIVE_OLLAMA_ENABLED=false`) keeps Ollama disabled/read-only.
- Blocked override (`OMI_LIVE_OLLAMA_BLOCKED=true`) overrides HTTP availability.
- CLI fallback: if HTTP probe fails but `ollama` CLI is available, the tool is still reported as available (legacy behavior preserved).

## Testing

### Tests Added/Updated

All 9 new Ollama HTTP probe tests use monkeypatching/mocking only. No real Ollama or network access is required.

1. **`test_ollama_global_live_tools_disabled_reports_disabled_or_available`** — Global live tools disabled keeps Ollama safe/read-only.
2. **`test_ollama_tool_flag_disabled_reports_available_when_dependency_ready`** — Ollama-specific flag disabled keeps Ollama disabled/read-only.
3. **`test_ollama_blocked_flag_overrides_http_availability`** — Blocked flag overrides HTTP availability.
4. **`test_ollama_http_reachable_with_model_present_reports_available`** — HTTP `/api/version` and `/api/tags` reachable with selected model present reports available.
5. **`test_ollama_http_reachable_but_model_missing_reports_unavailable`** — HTTP reachable but selected model missing reports unavailable with model-specific detail.
6. **`test_ollama_http_endpoint_unreachable_reports_unavailable`** — HTTP endpoint unreachable reports unavailable/error safely.
7. **`test_ollama_invalid_json_fails_closed`** — Invalid JSON from Ollama API fails closed.
8. **`test_ollama_base_url_env_var_changes_reported_url`** — `OMI_LIVE_OLLAMA_BASE_URL` changes reported/probed base URL.
9. **`test_ollama_model_env_var_changes_reported_model`** — `OMI_LIVE_OLLAMA_MODEL` changes selected model name.

Updated:

- **`test_missing_dependencies_return_unavailable_or_not_configured_without_crashing`** — ollama status changed from `not_configured` to `unavailable` (always configured now due to defaults); mocked HTTP probe to avoid real network.

### Test Results

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
```

Expected: all tests pass (existing + new ollama tests).

### Existing Tests Still Pass

- `tests/test_omi_live_runtime_preflight_contract.py` — all existing T013 and T014B tests still pass.
- `tests/test_omi_ollama_model_adapter_contract.py` — unchanged, still passes.
- `tests/test_omi_tool_assisted_orchestrator_contract.py` — unchanged, still passes.

## Safety Boundaries

- Preflight remains read-only. No Memory/Canon mutation.
- No automatic promotion records.
- No automatic apply-promotion.
- No story prose generated.
- No `/api/generate`, `/api/chat`, or text-producing endpoint called.
- No candidates produced.
- Ollama HTTP probe is fail-closed on connection errors, timeouts, invalid JSON, missing fields, and unavailable model.

## Owner's Current WSL Configuration

The WSL gateway IP may change after WSL restart. Owner's current override:

```bash
export OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434
export OMI_LIVE_OLLAMA_MODEL=qwen3:8b
```

No IP is hardcoded in the codebase. The environment variable `OMI_LIVE_OLLAMA_BASE_URL` must be set to the current Windows host IP when running from WSL.

## Next Steps

- **T015C**: Live Ollama structured extraction adapter implementation behind `OMI_LIVE_TOOLS_ENABLED` and `OMI_LIVE_OLLAMA_ENABLED` flags. Adds `_build_ollama_live_runner` to `backend/omi_analysis_orchestrator.py` using `urllib.request` to call `/api/chat` with structured JSON extraction prompts.
- **T015D**: Manual real `qwen3:8b` validation run after T015C, similar to T014D.
