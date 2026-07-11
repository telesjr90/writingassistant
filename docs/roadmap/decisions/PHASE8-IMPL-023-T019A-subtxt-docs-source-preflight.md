# PHASE8-IMPL-023-T019A — Subtxt docs/source preflight

## Task

Implement a focused, read-only Subtxt documentation/source preflight in
`backend/omi_runtime_preflight.py` that replaces the overbroad generic Subtxt
check with a precise inspection of the actual local source at
`.external_sources/subtxt-docs`.

## Source path

`.external_sources/subtxt-docs`

## Previously recorded clone SHA

`ec66121364c039693314dcce4cde464e497bece4`

## Source classification

The local source is a **Nuxt documentation-site repository** (private package
`nuxt-ui-pro-template-docs`), not a live Subtxt analysis runtime.

### Core documentation surfaces found

- `README.md`
- `package.json`
- `content/index.yml`
- `content/1.getting-started/5.key-concepts.md`
- `content/2.narrative-aspects/` (directory with perspectives, overviews,
  players, storypoints, storybeats docs)
- `content/5.narrative-intelligence/0.index.md`
- `content/6.advanced-concepts/0.index.md`
- `content/7.narrative-tasks/0.index.md`
- `content/8.API-reference/0.index.md`

### Package metadata and docs-site scripts

- **Package name:** `nuxt-ui-pro-template-docs`
- **Private:** true
- **Scripts:** `build`, `dev`, `generate`, `preview`, `postinstall`, `lint`,
  `typecheck` — all are Nuxt documentation-site operations, not Subtxt analysis
  or schema-validation commands.

### License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International declared
in README. No root `LICENSE` file was found in the inspected source.

## Decision

1. **No supported local Subtxt analysis runtime found.** The cloned source is a
   documentation/reference repository. No Subtxt CLI, importable analysis
   package, machine schema validator, or local analysis API has been
   established.

2. **API-reference pages are documentation, not proof of a locally callable
   service.** The presence of `content/8.API-reference/` does not imply a
   running Subtxt service.

3. **Documentation availability must not be reported as runtime availability.**
   The probe must distinguish between:
   - `subtxt_docs_reference_available`: whether core docs surfaces are present
     for owner reference.
   - `subtxt_live_runtime_available`: always `False` in T019A because no
     supported Subtxt analysis runtime is established.

4. **Automatic Dramatica/Subtxt truth remains forbidden.** Prior accepted
   boundaries from T005/T007/T009 remain controlling:
   - Subtxt docs are conceptual/reference material.
   - Subtxt remains semantic guardrail/reference only until separately decided.
   - No Subtxt classifier or runtime is currently authorized.
   - No automatic Storyform, Dramatica, CIPS, dynamics, throughline,
     relationship, conflict, or canon truth may be inferred from the
     documentation.
   - The Subtxt Storyform material may be incomplete or placeholder-like.
   - The documentation must not be treated as a machine schema or executable
     analysis engine.

5. **T019A performs no live Subtxt analysis.** The preflight is read-only and
   fail-closed. It never:
   - Executes package scripts.
   - Runs Node, npm, pnpm, Nuxt, shell commands, subprocesses, or network
     calls.
   - Imports code from `.external_sources/subtxt-docs`.
   - Starts the documentation website.
   - Reads project data.
   - Inspects arbitrary configured paths to decide runtime availability.
   - Treats a configured command/path env var as proof that a runtime exists.
   - Mutates the source tree.

6. **T009 remains fixture-only.** T009 already provides fixture-only Subtxt
   diagnostic handoff validation through `omi_subtxt_diagnostic_handoff.v1`.
   T019A does not modify the T009 contract.

7. **No source tree mutation or package operation occurred.** No `npm install`,
   `npm ci`, `pnpm install`, `npm run`, `pnpm run`, or Nuxt operation was
   executed during this task.

## Probe fields

The `_subtxt_docs_source_probe` returns a flat dictionary containing:

- `subtxt_runtime_surface`: `"reference_only"`, `"degraded"`, or `"unavailable"`
  based on core documentation surface availability.
- `subtxt_source_path`: `".external_sources/subtxt-docs"`
- `subtxt_source_available`: boolean
- `subtxt_readme_available`: boolean
- `subtxt_package_json_available`: boolean
- `subtxt_package_json_parseable`: boolean
- `subtxt_content_root_available`: boolean
- `subtxt_content_index_available`: boolean
- `subtxt_key_concepts_available`: boolean
- `subtxt_narrative_aspects_available`: boolean
- `subtxt_storypoints_docs_available`: boolean
- `subtxt_storybeats_docs_available`: boolean
- `subtxt_narrative_intelligence_available`: boolean
- `subtxt_advanced_concepts_available`: boolean
- `subtxt_narrative_tasks_available`: boolean
- `subtxt_api_reference_available`: boolean
- `subtxt_package_name`: `"nuxt-ui-pro-template-docs"` or empty string
- `subtxt_package_private`: boolean
- `subtxt_package_scripts`: sorted list of docs-site script names
- `subtxt_license_declared`: `True` when CC BY-NC-SA 4.0 detected in README
- `subtxt_license_name`: `"CC BY-NC-SA 4.0"` or empty string
- `subtxt_license_source`: `"README.md"` or empty string
- `subtxt_docs_reference_available`: `True` only when core docs are present
- `subtxt_live_runtime_available`: always `False` in T019A
- `subtxt_live_runtime_status`: `"reference_only"` when docs available,
  `"unavailable"` otherwise
- `subtxt_command_env`/`subtxt_command_configured`/`subtxt_command_value`:
  configuration-only command env var
- `subtxt_path_env`/`subtxt_path_configured`/`subtxt_path_value`:
  configuration-only path env var
- `subtxt_detail`: human-readable detail string

## False-availability repair

The previous subtxt branch treated:
- any existing `.external_sources` directory,
- an arbitrary `OMI_LIVE_SUBTXT_COMMAND`, or
- an arbitrary `OMI_LIVE_SUBTXT_PATH`

as proof that a Subtxt runtime is available. The new probe:
- Inspects only `.external_sources/subtxt-docs`.
- Never reports `runtime_dependency_available=True` for command/path env vars.
- Never calls `shutil.which` for the configured command.
- Never calls `Path(path).exists()` for the configured path.
- Always reports `subtxt_live_runtime_available=False`.

## Tests

18 focused mocked tests added to `tests/test_omi_live_runtime_preflight_contract.py`:

1. `test_subtxt_disabled_by_default_remains_read_only`
2. `test_subtxt_full_docs_surface_reports_reference_only`
3. `test_subtxt_docs_reference_does_not_make_live_runtime_available`
4. `test_subtxt_enabled_plus_global_does_not_falsely_report_runnable_runtime`
5. `test_subtxt_source_path_is_exact_subtxt_docs_not_generic_external_sources`
6. `test_subtxt_missing_source_root_reports_unavailable`
7. `test_subtxt_missing_readme_reports_safely`
8. `test_subtxt_missing_malformed_package_json_reports_safely`
9. `test_subtxt_missing_content_root_reports_degraded`
10. `test_subtxt_missing_key_docs_reports_degraded`
11. `test_subtxt_license_detected_from_readme`
12. `test_subtxt_package_metadata_reported_without_executing_scripts`
13. `test_subtxt_command_env_surfaced_as_configuration_only`
14. `test_subtxt_path_env_surfaced_as_configuration_only`
15. `test_subtxt_blocked_flag_overrides_docs_availability`
16. `test_subtxt_preflight_does_not_invoke_subprocess_shell_network_or_npm`
17. `test_subtxt_preflight_does_not_persist_or_mutate`

All tests mock `_subtxt_docs_source_probe` and do not depend on the real
`.external_sources/subtxt-docs` checkout.

## Result

`PASS` — the preflight accurately reports the docs/reference surface and
refuses to overclaim a runtime.

## Next task

`PHASE8-IMPL-023-T019B — Subtxt integration-path decision`

T019B must be a separate owner-controlled decision task that chooses between:

1. An app-owned, evidence-backed, candidate-only semantic-rubric/diagnostic
   implementation derived from allowed Subtxt concepts without copying
   restricted content or claiming Subtxt execution.
2. Explicit owner-blocked status for live Subtxt runtime integration.

T019A does not make that final product decision and does not implement either
path.
