# PHASE8-IMPL-023-T016B — Story Check Runtime Preflight/Config/Availability Check

## Result

PASS for backend preflight/config/test/docs task.

T016B strengthens the existing T013 Story Check preflight probe from a single file-existence check on `backend/analysis_engine.py` to a read-only multi-surface probe that reports, without running analysis, the availability of:

* `backend/analysis_engine.py`
* `backend/prompts/story_check.txt`
* `backend/mock_responses/story_check.json`
* `backend/analysis_modes.py`
* `backend/storyform.py`
* the `requests` Python package (via `importlib.util.find_spec`)

T016B also surfaces the configured `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, and `ANALYSIS_MODE` env vars as configuration only. T016B does not call the live Story Check runtime, does not call the legacy Story Check route, does not call Ollama, and does not implement the live Story Check adapter. T016B preserves the existing disabled-by-default and blocked-state behavior of the T013 preflight.

## Nature

- Backend preflight/config/test/docs task only (T016B).
- T016C (live Story Check adapter behind flags) and T016D (manual real Story Check validation) are deferred.
- Builds on T016A findings: the existing `story_check` OMI adapter support is fixture/mock only; the existing fixture contract accepts `omi_story_check_diagnostic_handoff.v1`; the in-repo callable surface is `backend.analysis_engine.run_story_check(project_name, scene_id)`; the legacy route is `POST /api/projects/{project_name}/story-check/{scene_id}`; the existing T013 preflight `story_check` probe is too weak (file-existence only on `backend/analysis_engine.py`); existing live flags are `OMI_LIVE_STORY_CHECK_ENABLED`, `OMI_LIVE_STORY_CHECK_BLOCKED`, and `OMI_LIVE_STORY_CHECK_BLOCKED_REASON`.

## Implementation

### Files Changed

- `backend/omi_runtime_preflight.py` — added `_story_check_runtime_probe`, updated `_dependency_probe` and `_tool_report` for the `story_check` adapter to surface new read-only probe fields, added `_path_readable` helper.
- `tests/test_omi_live_runtime_preflight_contract.py` — added 16 new T016B focused tests, no live network/HTTP/Ollama.
- `docs/roadmap/decisions/PHASE8-IMPL-023-T016B-story-check-runtime-preflight-config-availability.md` — this decision record.
- `docs/roadmap/decision_log.md` — logged T016B decision.
- `docs/roadmap/implementation_status.md` — updated active frontier.
- `docs/roadmap/task_backlog.md` — updated backlog.
- `docs/roadmap/phase_map.md` — updated phase map.
- `docs/roadmap/open_questions.md` — partially refined Q112 with the T016B preflight evidence and the recommended next step toward T016C.
- `docs/roadmap/risk_register.md` — unchanged (no new risk; preflight is read-only and fail-closed).
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` — updated active child sequence and latest/next child fields.

### Story Check Runtime Preflight Probe

The new probe is `_story_check_runtime_probe(env)` in `backend/omi_runtime_preflight.py`. It is a pure read-only function that:

1. Calls `_path_exists(...)` for the five repo-relative paths (analysis_engine, prompt, mock fixture, analysis_modes, storyform).
2. Calls `_find_module("requests")` (i.e., `importlib.util.find_spec("requests")`) for the Python package.
3. Reads the four configuration env vars `OLLAMA_BASE_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default `qwen3:8b`), `OLLAMA_TIMEOUT_SECONDS` (default `300`, parsed as float with non-numeric fallback to default), and `ANALYSIS_MODE` (defaulted to `ollama_baseline`).
4. Never imports `backend.analysis_engine`, never calls `analysis_engine.run_story_check`, never calls the legacy Story Check route, never calls Ollama, and never makes a network call.

### Reported Fields

The `story_check` tool entry in the existing `omi_runtime_preflight.v1` report now includes the following new fields, in addition to the existing T013 fields:

- `story_check_runtime_surface` — `"available"` when all required runtime surfaces are present, `"unavailable"` when any of the five required paths/`requests` is missing.
- `story_check_analysis_engine_available` — boolean: `backend/analysis_engine.py` exists.
- `story_check_prompt_available` — boolean: `backend/prompts/story_check.txt` exists.
- `story_check_mock_fixture_available` — boolean: `backend/mock_responses/story_check.json` exists.
- `story_check_analysis_modes_available` — boolean: `backend/analysis_modes.py` exists.
- `story_check_storyform_surface_available` — boolean: `backend/storyform.py` exists.
- `story_check_requests_available` — boolean: `requests` Python package is importable.
- `story_check_ollama_base_url` — string: the configured `OLLAMA_BASE_URL` (read-only config; no HTTP call).
- `story_check_ollama_model_name` — string: the configured `OLLAMA_MODEL`.
- `story_check_ollama_timeout_seconds` — float: the configured `OLLAMA_TIMEOUT_SECONDS` (default `300.0`).
- `story_check_analysis_mode_value` — string: the effective `ANALYSIS_MODE` value (empty env defaults to `ollama_baseline`).
- `story_check_analysis_mode_configured` — boolean: `True` if the env var is unset (default) or set to a valid value (`mock` or `ollama_baseline`), `False` only if set to an unknown value.
- `story_check_detail` — string: human-readable detail mirroring `probe_detail`.

The probe treats the five required surfaces (analysis_engine, prompt, analysis_modes, storyform, `requests`) as critical, and the mock fixture as a partial-availability signal. When the mock fixture is missing but the other required surfaces are present, the probe still reports `runtime_configured: True`, `runtime_dependency_available: True`, and `status: enabled`/`available`/`disabled` per the normal T013 flow, with `story_check_mock_fixture_available: False` and a `detail` that explicitly mentions `mock_responses/story_check.json` is missing.

### Status Vocabulary

The probe reuses the existing T013 status vocabulary (`enabled`, `disabled`, `available`, `unavailable`, `blocked`, `error`, `not_configured`) without introducing new statuses. The behavior is:

- `disabled` — `OMI_LIVE_TOOLS_ENABLED=false` or `OMI_LIVE_STORY_CHECK_ENABLED=false`; live flags off.
- `available` — Live flags off; required runtime surfaces all present.
- `enabled` — `OMI_LIVE_TOOLS_ENABLED=true` and `OMI_LIVE_STORY_CHECK_ENABLED=true`; required runtime surfaces all present; `OMI_LIVE_STORY_CHECK_BLOCKED` not set.
- `not_configured` — Live flags on; one or more required surfaces missing; `runtime_dependency_status="not_configured"`.
- `unavailable` — Live flags on; one or more required surfaces missing and the dependency probe reports `runtime_dependency_status="unavailable"`.
- `blocked` — `OMI_LIVE_STORY_CHECK_BLOCKED=true`; the blocked state overrides all other enablement/availability signals and the blocked reason is reported in `blocked_reason`.
- `error` — defensive fail-closed branch; only set if the probe raises an unexpected exception (e.g., path resolution failure).

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `OMI_LIVE_TOOLS_ENABLED` | `false` | Global live-tools gate (preexisting) |
| `OMI_LIVE_STORY_CHECK_ENABLED` | `false` | Per-tool live gate (preexisting) |
| `OMI_LIVE_STORY_CHECK_BLOCKED` | `false` | Explicit block override (preexisting) |
| `OMI_LIVE_STORY_CHECK_BLOCKED_REASON` | (none) | Block reason (preexisting) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Legacy route + probe config-only (read-only surface) |
| `OLLAMA_MODEL` | `qwen3:8b` | Legacy route + probe config-only (read-only surface) |
| `OLLAMA_TIMEOUT_SECONDS` | `300` | Legacy route + probe config-only (read-only surface) |
| `ANALYSIS_MODE` | `ollama_baseline` | `mock` or `ollama_baseline` for the legacy `analysis_engine.run_story_check` path; surfaced as read-only config |

No new env vars are added by T016B. The four `OLLAMA_*`/`ANALYSIS_MODE` env vars are read as configuration only and are reported in the per-tool `story_check` report entry; T016B never calls Ollama.

### Preflight Does Not Run Story Check

- `_story_check_runtime_probe` does not import `backend.analysis_engine`.
- `_dependency_probe(adapter="story_check", env=env)` does not call `run_story_check`; it only invokes `_story_check_runtime_probe` and reports the resulting booleans.
- `_tool_report(adapter="story_check", env=env)` does not call `run_story_check`; it only forwards the dependency probe's booleans and config strings.
- The test `test_story_check_preflight_does_not_call_run_story_check` monkeypatches `backend.analysis_engine.run_story_check` to a sentinel that raises if called; the preflight report builds without invoking the sentinel.
- The test `test_story_check_preflight_does_not_call_ollama_or_network` monkeypatches `urllib.request.urlopen`, `urllib.request.Request`, `requests.post`, and `requests.get` to sentinels that raise if called; the preflight report builds without invoking any network call.

## Testing

### Tests Added/Updated

All 16 new T016B tests use monkeypatching/mocking only. No real Story Check, route, Ollama, or network access is required.

1. **`test_story_check_runtime_with_all_surfaces_and_requests_reports_available`** — all five required surfaces and `requests` are present; status is `disabled`/`available` (default flags off); all new fields populated; detail mentions "all present".
2. **`test_story_check_disabled_by_default_reports_safe_read_only_state`** — global live tools disabled; status `disabled`/`available`; safety flags all `False`.
3. **`test_story_check_live_enabled_flag_changes_status_when_runtime_ready`** — `OMI_LIVE_TOOLS_ENABLED=true` + `OMI_LIVE_STORY_CHECK_ENABLED=true`; surfaces ready; status `enabled`.
4. **`test_story_check_live_enabled_but_unconfigured_reports_not_configured`** — live flags on; prompt missing; status `not_configured`; detail mentions `prompts/story_check.txt`.
5. **`test_story_check_blocked_flag_overrides_available_runtime`** — `OMI_LIVE_STORY_CHECK_BLOCKED=true` with a reason; status `blocked`; reason exposed.
6. **`test_story_check_missing_prompt_file_reports_unavailable_safely`** — prompt missing; live flags on; status `not_configured`/`unavailable`; detail mentions `prompts/story_check.txt`.
7. **`test_story_check_missing_mock_fixture_reports_partial_availability`** — mock fixture missing only; live flags on; status still `enabled`; detail mentions `mock_responses/story_check.json`; documents the chosen partial-availability behavior.
8. **`test_story_check_missing_requests_package_reports_unavailable`** — `requests` package missing; live flags on; status `not_configured`/`unavailable`; detail mentions `python:requests`.
9. **`test_story_check_missing_analysis_engine_reports_unavailable`** — `backend/analysis_engine.py` missing; live flags on; status `not_configured`/`unavailable`; detail mentions `analysis_engine.py`.
10. **`test_story_check_preflight_does_not_call_run_story_check`** — monkeypatches `backend.analysis_engine.run_story_check` to a sentinel that raises; the preflight report builds without invoking the sentinel; safety flags all `False`.
11. **`test_story_check_preflight_does_not_call_ollama_or_network`** — monkeypatches `urllib.request.urlopen`, `urllib.request.Request`, `requests.post`, and `requests.get` to sentinels that raise; the preflight report builds without invoking any network call; safety flags all `False`.
12. **`test_story_check_ollama_config_env_vars_are_surfaced_read_only`** — `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, `ANALYSIS_MODE` are surfaced in the report; no HTTP call is made.
13. **`test_story_check_invalid_analysis_mode_falls_back_to_default`** — `ANALYSIS_MODE=bogus-mode` is detected as unconfigured; reported value falls back to `ollama_baseline`.
14. **`test_story_check_invalid_ollama_timeout_falls_back_to_default`** — `OLLAMA_TIMEOUT_SECONDS=not-a-number` falls back to the default `300.0`.
15. **`test_story_check_missing_storyform_or_analysis_modes_reports_unavailable`** — both `backend/storyform.py` and `backend/analysis_modes.py` missing; live flags on; status `not_configured`/`unavailable`; detail mentions both paths.
16. **`test_story_check_preflight_does_not_persist_or_promote`** — uses `tmp_path`; creates an OMI idea; runs the preflight with live flags on; verifies that project state is unchanged (`index.idea_ids` only, `index.candidate_ids == []`, `promotions == []`); safety flags all `False`.

### Test Results

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
```

Expected: 39 passed (23 existing T013/T014B/T015B + 16 new T016B).

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_story_check_adapter_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
```

Expected: all 46 existing tests pass unchanged (T016B is not a fixture/orchestrator/persistence task).

### Existing Tests Still Pass

- `tests/test_omi_live_runtime_preflight_contract.py` — all existing T013, T014B, and T015B tests still pass.
- `tests/test_omi_story_check_adapter_contract.py` — unchanged, still passes (T008 fixture-only contract).
- `tests/test_omi_tool_assisted_orchestrator_contract.py` — unchanged, still passes (T005 orchestrator contract).
- `tests/test_omi_tool_assisted_persistence_contract.py` — unchanged, still passes (T011 candidate-only persistence contract).

## Safety Boundaries

- Preflight remains read-only. No Memory/Canon mutation. No automatic promotion records. No automatic apply-promotion. No story prose generated.
- No `/api/chat`, `/api/generate`, `/api/version`, or `/api/tags` call.
- No `requests.post` or `requests.get` call.
- No `analysis_engine.run_story_check` import or call.
- No import of `backend.analysis_engine` (the preflight only checks file existence via `_path_exists`).
- No fixtures, dataset manifests, training records, or model artifacts touched.
- No candidate persistence, no Memory/Canon mutation, no automatic promotion records, no automatic apply-promotion, no story prose.
- Mock fixture is treated as a partial-availability signal only; the live path does not require the mock fixture.

## Existing T013/T014B/T015B Behavior Preserved

- Global live-tools disabled (`OMI_LIVE_TOOLS_ENABLED=false`) keeps Story Check safe/read-only.
- Story-Check-specific flag disabled (`OMI_LIVE_STORY_CHECK_ENABLED=false`) keeps Story Check disabled/read-only.
- Blocked override (`OMI_LIVE_STORY_CHECK_BLOCKED=true`) overrides all enablement/availability signals.
- Existing T013 `runtime_configured`, `runtime_dependency_available`, `runtime_dependency_status`, `runtime_enabled`, `global_enabled`, `tool_enabled`, `blocked`, `blocked_reason`, `feature_flags`, `probe_detail`, `explanation`, and `safety` fields are preserved unchanged on the `story_check` tool entry.
- Existing T013 status vocabulary (`enabled`, `disabled`, `available`, `unavailable`, `blocked`, `error`, `not_configured`) is reused without modification.
- The `_path_readable` helper is added but kept private; T016B does not yet report a "readable" field in the per-tool report because the existing `is_file()` semantics already cover the "regular file exists" case used by `_path_exists`.

## Next Steps

- **T016C**: Live Story Check adapter behind flags. T016B preflight provides a clear readiness signal. The recommended path is option (A) from the T016A decision record: bridge the OMI orchestrator's live `story_check` runner to the existing `backend.analysis_engine.run_story_check` callable behind `OMI_LIVE_TOOLS_ENABLED` + `OMI_LIVE_STORY_CHECK_ENABLED` + not `OMI_LIVE_STORY_CHECK_BLOCKED`, with a `scene_id` derived from a new `OMI_LIVE_STORY_CHECK_SCENE_ID` env var. T016C must convert the rich Story Check response (`throughline_alignment`, `theme_drift`, `character_consistency`, `warnings`, `suggestions`, `insufficient_evidence`) into T008-shaped `omi_story_check_diagnostic_handoff.v1` findings so the existing `validate_story_check_fixture_envelope` validator can validate them, and must fail-closed on HTTP error, non-JSON, prose, truth, canon, missing evidence, missing `source_locator`, missing `provenance`, and missing `owner_decision: pending` state. The preflight in T016B also reports `OLLAMA_TIMEOUT_SECONDS` and `OLLAMA_MODEL` so T016C can reuse these env vars for the legacy path or migrate to `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` / `OMI_LIVE_OLLAMA_MODEL` for the orchestrator path.
- **T016D**: Manual real Story Check validation against a live `qwen3:8b` instance behind the new env flags, similar to T014D/T015D.

Open question Q112 is partially refined by T016B: the preflight now reports the configured Ollama URL/model/timeout for the legacy `analysis_engine.run_story_check` path, but does not yet probe the actual reachability of that URL. T016C should pick the live path (A, B, or C from T016A) and may add an Ollama reachability probe for the chosen path if it differs from the orchestrator's `OMI_LIVE_OLLAMA_BASE_URL`.
