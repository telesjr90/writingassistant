# PHASE8-IMPL-023-T015A — Ollama Runtime and Fixture Contract Inspection

## Result

PASS for inspect/probe/docs only.

T015A inspects the existing Ollama/model fixture contract and verifies the real local Ollama runtime state from WSL (Windows Subsystem for Linux). No live Ollama adapter was implemented. No model analysis was run. No candidates were produced. No backend/frontend/package files were changed.

## Nature

- Inspect/probe/docs task only (T015A).
- T015B (live Ollama adapter implementation) and T015C (manual validation) are deferred.
- The owner confirmed prior to this task that Ollama is installed and running on Windows (Git Bash: `ollama --version` = 0.31.1; `ollama list` shows qwen3:8b, qwen2.5:7b, nomic-embed-text, phi3:mini).
- This task performs safe runtime probes from WSL: `ollama` CLI availability, HTTP API reachability, version, model list, and `ollama show qwen3:8b`.

## WSL Probe Results

### Ollama CLI Availability

- `command -v ollama` → NOT FOUND
- `ollama --version` → NOT AVAILABLE
- Ollama is **not installed inside WSL**.

### Windows Ollama API Reachability from WSL

- **From `127.0.0.1:11434`**: Connection refused (WSL localhost is WSL's own loopback, not Windows').
- **From `172.25.144.1:11434`** (WSL default gateway / Windows host IP): **SUCCESS**.
  - `/api/version` → `{"version":"0.31.1"}`
  - `/api/tags` → 4 models confirmed.
  - `/api/show` with `{"model":"qwen3:8b"}` → Full model metadata returned (8.2B, Q4_K_M, 40960 context, capabilities: completion/tools/thinking).

### Ollama Version

**0.31.1** (confirmed via HTTP API).

### Installed Model IDs

| Model | Parameter Size | Quantization | Context Length | Capabilities |
|---|---|---|---|---|
| `nomic-embed-text:latest` | 137M | F16 | 2048 | embedding |
| `qwen3:8b` | 8.2B | Q4_K_M | 40960 | completion, tools, thinking |
| `qwen2.5:7b` | 7.6B | Q4_K_M | 32768 | completion, tools |
| `phi3:mini` | 3.8B | Q4_0 | 131072 | completion |

### Selected MVP Model Candidate

**`qwen3:8b`** — preferred candidate for T015. Has `tools` and `thinking` capabilities useful for structured JSON extraction. Context window of 40960 tokens is generous for raw idea analysis. Q4_K_M quantization is a reasonable quality/speed trade-off.

Secondary candidate: `qwen2.5:7b` (similar capabilities, slightly smaller context at 32768).

## Existing Ollama Fixture Contract Summary

### Schema Version

`OMI_OLLAMA_SCHEMA_VERSION = "omi_ollama_structured_extraction.v1"` (`backend/omi_analysis_orchestrator.py:1376`).

### Envelope Fields

- `schema_version` (must be `"omi_ollama_structured_extraction.v1"`)
- `adapter` (must be `"ollama_model"`)
- `status` (`succeeded`, `empty`, `failed_closed`, `error`)
- `findings` (array of finding dicts; must be present, empty for non-succeeded)
- `diagnostics` (optional array of strings)

### Finding Fields

- `candidate_type` (allowed types from the OMI_ORCHESTRATOR_FINDING_TYPES)
- `label`
- `extracted_claim`
- `evidence` (non-empty array with `source_excerpt` or `source_locator`)
- `source_locator`
- `source_adapter` (set to `"ollama_model"` during normalization)
- `raw_finding_id`
- `support_label` (must include "support", must not include truth/canon/approved/promoted)
- `confidence` (optional, must not be truth-labeled)
- Additional prose-intent fields (`rewrite`, `continue`, `outline`, `draft`, etc.) are forbidden.

### Validation Rules

- Top-level must be a JSON object (not array or scalar).
- Required envelope fields: `schema_version`, `adapter`, `status`, `findings`.
- Only `omi_ollama_structured_extraction.v1` accepted.
- Non-`succeeded` status must carry zero findings.
- Findings require evidence with source_excerpt or source_locator.
- Unknown candidate types fail closed.
- Truth/canon/approved/promoted labels fail closed.
- Auto-approved owner decisions fail closed.
- Prose-like extracted claims fail closed.
- Forbidden prose intent fields fail closed.

### Fixture-Only Behavior

- `requested_adapters=["ollama_model"]` without fixture output returns `unavailable` with explanation.
- Valid fixture output is normalized into T005 normalized finding schema.
- Invalid fixture output fails closed with no findings and no persistence.
- Ollama findings are NEVER persisted in T006, even with `persist_candidates=True`.

### Test Coverage

`tests/test_omi_ollama_model_adapter_contract.py` → 19 passed (all fixture/mock).

## Existing T013 Preflight/Config Summary

### Feature Flags

| Flag | Scope | Current State |
|---|---|---|
| `OMI_LIVE_TOOLS_ENABLED` | Global gate | Disabled by default |
| `OMI_LIVE_OLLAMA_ENABLED` | Per-tool gate | Disabled by default |
| `OMI_LIVE_OLLAMA_BLOCKED` | Explicit block | Not set by default |
| `OMI_LIVE_OLLAMA_BLOCKED_REASON` | Block reason | Not set by default |

### Model Configuration Env Vars (read by preflight)

- `OMI_LIVE_OLLAMA_MODEL` — model name (e.g., `qwen3:8b`)
- `OMI_LIVE_OLLAMA_MODEL_NAME` — alternative model name env var

### Dependency Probe

- Method: `shutil.which("ollama")` executable probe only.
- No HTTP API probe.
- No model availability check.
- `configured` state: True if either env var is set OR `shutil.which("ollama")` finds the executable.
- `available` state: True only if `shutil.which("ollama")` finds the executable.

### Preflight Gap for WSL/Windows Cross-Platform

The preflight reports Ollama as `unavailable`/`not_configured` when run from WSL because `shutil.which("ollama")` does not find the Windows Ollama executable (it is on the Windows PATH, not the WSL PATH). The HTTP API is actually reachable at the Windows host IP. The preflight needs an HTTP availability probe (e.g., `/api/tags` or `/api/version`) in addition to or instead of the CLI `shutil.which` probe for WSL/Windows cross-platform scenarios.

## T014E Status Correction

The T014E decision record (`docs/roadmap/decisions/PHASE8-IMPL-023-T014E-live-runtime-tool-installation-inventory.md`) states:

> "Ollama is **not installed** in the local environment."

This statement was correct for the WSL environment probed by T014E, but is incomplete: the owner confirmed Ollama IS installed and running on Windows. T015A now provides the full picture:

| Environment | Ollama Installed | Ollama Reachable |
|---|---|---|
| Windows (Git Bash) | YES (0.31.1) | YES (127.0.0.1:11434) |
| WSL (this probe) | NO (not in WSL) | YES (via Windows host IP 172.25.144.1:11434) |
| Preflight (WSL) | NO (`shutil.which`) | Would be YES with HTTP probe at Windows host IP |

The T014E status should be corrected to: **"Ollama installed on Windows (0.31.1); WSL reachability verified at Windows host IP (172.25.144.1:11434); CLI not available in WSL."**

## Gaps for T015B (Live Ollama Adapter Implementation)

1. **No HTTP client/dependency** — The adapter must call the Ollama REST API. The orchestrator currently uses only the standard library and fixture outputs. `urllib.request` (standard library) or `httpx`/`requests` (external) would be needed. The task should prefer `urllib.request` to avoid new dependencies.

2. **No structured extraction prompt** — T015B needs a prompt that asks the model to return `omi_ollama_structured_extraction.v1` schema-compliant JSON. The prompt must be no-prose, schema-bound, and extraction-only.

3. **No base URL configuration** — `OMI_LIVE_OLLAMA_BASE_URL` env var should be defined with default `http://127.0.0.1:11434`. The adapter must document that WSL users must set this to the Windows host IP.

4. **No model availability check** — T015B should probe `/api/tags` or `/api/show` to confirm the configured model exists before running extraction.

5. **Preflight HTTP probe needed** — The `_dependency_probe` in `backend/omi_runtime_preflight.py` for `ollama_model` currently only does `shutil.which("ollama")`. T015B should add an HTTP probe (`/api/version` or `/api/tags`) so the preflight can detect the Windows Ollama service from WSL.

6. **Live runner path** — T015B must add `_build_ollama_model_live_runner` in `backend/omi_analysis_orchestrator.py` (analogous to `_build_spacy_live_runner`), gated behind `OMI_LIVE_TOOLS_ENABLED` + `OMI_LIVE_OLLAMA_ENABLED`.

7. **Prompt safety/envelope** — The model response must be validated as JSON, checked for the `omi_ollama_structured_extraction.v1` schema, and run through the existing normalize/reject-no-prose/reject-truth pipeline.

8. **HTTP timeout/error handling** — Must fail closed on connection errors, timeouts, non-JSON responses, and model errors.

9. **No new package dependencies** — Must use `urllib.request` from the standard library.

## Gaps for T015C (Manual Validation)

1. Run the live Ollama adapter manually with real `qwen3:8b` against a known raw idea.
2. Verify structured JSON extraction output.
3. Verify no-prose guard catches unsafe model output.
4. Verify fail-closed behavior when:
   - Model is unreachable (wrong host/port)
   - Model returns non-JSON
   - Model returns prose-like output
5. Verify `persist_candidates=False` (no writes).
6. Run from WSL with `OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434`.

## Documented Env Vars for Future Live Ollama Path

| Env Var | Default | Purpose |
|---|---|---|
| `OMI_LIVE_TOOLS_ENABLED` | `false` | Global gate for all live tools |
| `OMI_LIVE_OLLAMA_ENABLED` | `false` | Per-tool gate for live Ollama |
| `OMI_LIVE_OLLAMA_BLOCKED` | `false` | Explicit block override |
| `OMI_LIVE_OLLAMA_BLOCKED_REASON` | (none) | Reason for block |
| `OMI_LIVE_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API base URL (NOTE: WSL users set to Windows host IP) |
| `OMI_LIVE_OLLAMA_MODEL` | `qwen3:8b` | Model ID for structured extraction |

## Safety Confirmations

- No live Ollama adapter was implemented.
- No model analysis was run (only version/tags/show API probes).
- No candidates were produced.
- No backend/frontend/package files were changed.
- No Memory/Canon mutation.
- No automatic promotion records or apply-promotion.
- No story prose was generated or analyzed.
- No staging, commit, or push occurred.
