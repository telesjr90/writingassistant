# PHASE8-IMPL-023-T013 Runtime Preflight, Health Checks, and Feature Flags

## Result

PASS for backend/runtime preflight foundation and read-only route support.

## Decision

`PHASE8-IMPL-023-T013` establishes disabled-by-default runtime configuration and preflight reporting for the selected live OMI/analysis tools without connecting or running any live analyzer.

The preflight distinguishes fixture contract existence, runtime configuration, dependency availability, feature-flag enablement, explicit blocked state, and unavailable/not-configured/error outcomes. Preflight readiness does not prove live analysis and does not count as `PHASE8-IMPL-023` MVP completion.

## Runtime Surfaces

- New module: `backend/omi_runtime_preflight.py`.
- New route: `GET /api/projects/{project_name}/omi/runtime-preflight`.
- New tests: `tests/test_omi_live_runtime_preflight_contract.py`.

## Selected Tools

- `spacy`
- `ollama_model`
- `story_check`
- `booknlp`
- `ncp`
- `subtxt`
- `dramatica_flow`
- `deterministic_fallback`

## Status Vocabulary

- `enabled`
- `disabled`
- `available`
- `unavailable`
- `blocked`
- `error`
- `not_configured`

## Feature Flags

- `OMI_LIVE_TOOLS_ENABLED`
- `OMI_LIVE_SPACY_ENABLED`
- `OMI_LIVE_OLLAMA_ENABLED`
- `OMI_LIVE_STORY_CHECK_ENABLED`
- `OMI_LIVE_BOOKNLP_ENABLED`
- `OMI_LIVE_NCP_ENABLED`
- `OMI_LIVE_SUBTXT_ENABLED`
- `OMI_LIVE_DRAMATICA_FLOW_ENABLED`
- `OMI_LIVE_DETERMINISTIC_FALLBACK_ENABLED`
- `OMI_LIVE_RUNTIME_TESTS`

Explicit blocked-state flags are also supported per tool through `OMI_LIVE_<TOOL>_BLOCKED` and `OMI_LIVE_<TOOL>_BLOCKED_REASON`.

## Boundaries

- Runtime preflight is read-only.
- Runtime preflight does not execute heavy analysis by default.
- Runtime preflight does not call external services.
- Runtime preflight does not call live models.
- Runtime preflight does not mutate project files, Memory/Canon, candidate queues, promotion records, or apply-promotion.
- Runtime preflight does not generate story prose.
- CI/default tests do not require heavy local runtimes.
- Missing dependencies or executables return `unavailable` or `not_configured` instead of failing the app.

## Next Step

`PHASE8-IMPL-023-T014 - Live spaCy integration in OMI and analysis` is next. T014 must use the T013 flags/preflight boundary and must not imply MVP completion by itself.
