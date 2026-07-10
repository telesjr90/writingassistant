# PHASE8-IMPL-023-T018A NCP schema-validator preflight

## Result

PASS.

`PHASE8-IMPL-023-T018A` is complete/PASS. The OMI runtime preflight now
reports a focused, read-only NCP schema-validator surface
(`backend/omi_runtime_preflight.py` + `tests/test_omi_live_runtime_preflight_contract.py`).
NCP remains a schema/interchange validation surface, not an automatic
analysis runtime, not canon/truth, and the T018 NCP candidate-import
validation adapter is intentionally deferred to `PHASE8-IMPL-023-T018B`.

No `npm install`, no `npm audit fix`, no `npm run validate:schema`, no
`npm run validate:file`, no network/server exposure, no candidate
persistence, no Memory/Canon mutation, no automatic promotion record,
no automatic apply-promotion, and no story prose generation occurred.

## Scope

T018A extends the T013 read-only runtime preflight so the OMI
`runtime-preflight` report for the `ncp` tool reports the
schema-validator surface state for the owner-selected NCP source tree
at `.external_sources/narrative-context-protocol`. The probe is
deliberately narrow: it confirms the source tree, the `package.json`,
the schema JSON/YAML files, the two validator scripts, the
corresponding `package.json` script entries, the `node`/`npm` command
availability, and the presence/absence of `node_modules`. It records
the known npm audit caveat (`ajv` moderate, `fast-uri` high) as known
owner evidence without running `npm audit` and without applying any
fix.

T018A does NOT:

- implement an NCP candidate-import adapter
- run `npm install`
- run `npm audit fix`
- run `npm run validate:schema`
- run `npm run validate:file` over project data
- expose NCP as a network/server path
- mutate Memory/Canon
- create candidate persistence
- create promotion records
- run apply-promotion
- generate story prose
- import NCP as a Python module (NCP is a Node/schema surface)

## NCP preflight fields added

The preflight now reports these `ncp_*` fields on the `ncp` tool entry
in `report["tools"][ncp]`. All fields are flat booleans / paths /
detail strings, consistent with the existing T013/T014B/T015B/T016B/T017A
adapter surface fields (e.g. `booknlp_*`, `story_check_*`,
`ollama_*`, `spacy_*`).

- `ncp_runtime_surface` — one of `available` / `unavailable` /
  `degraded`. `degraded` is reported when source, package.json,
  schema JSON/YAML, validator scripts, validate:schema/validate:file
  package scripts, and node/npm are all present but `node_modules`
  is missing (validator scripts would not be runnable; preflight
  does NOT run `npm install`).
- `ncp_source_path` — the constant
  `.external_sources/narrative-context-protocol`.
- `ncp_source_available` — boolean, the source tree exists.
- `ncp_package_json_available` — boolean, the `package.json` is
  present.
- `ncp_schema_json_available` — boolean, `schema/ncp-schema.json` is
  present.
- `ncp_schema_yaml_available` — boolean, `schema/ncp-schema.yaml` is
  present.
- `ncp_validate_schema_script_available` — boolean,
  `tests/validate-schema.js` is present.
- `ncp_validate_file_script_available` — boolean,
  `tests/validate-file.js` is present.
- `ncp_validate_schema_package_script_available` — boolean, the
  `validate:schema` package script is declared in `package.json`.
- `ncp_validate_file_package_script_available` — boolean, the
  `validate:file` package script is declared in `package.json`.
- `ncp_node_available` — boolean, `shutil.which("node")` resolves.
- `ncp_node_path` — string path to `node` if available, else `None`.
- `ncp_npm_available` — boolean, `shutil.which("npm")` resolves.
- `ncp_npm_path` — string path to `npm` if available, else `None`.
- `ncp_node_modules_available` — boolean, the `node_modules` directory
  exists in the NCP source tree.
- `ncp_validator_available` — boolean, all required surface items
  (source, package.json, schema JSON/YAML, validator scripts,
  validate:schema/validate:file package scripts, node, npm) are
  present. `node_modules` presence is reported separately and is
  reflected in `ncp_runtime_surface == "degraded"`, not in
  `ncp_validator_available`.
- `ncp_validator_status` — mirrors `ncp_runtime_surface` for
  convenient consumption by the T018B adapter and the owner-facing
  preflight summary.
- `ncp_audit_caveat` — string, the known npm audit caveat text
  recorded as known owner evidence (not fixed in preflight).
- `ncp_detail` — human-readable summary, including which surface
  items are missing or which items are present. Used as the tool's
  `probe_detail` so blocked/enabled/disabled state reasons remain
  consistent with other tools.

The preflight also preserves the existing T013 live-tool flag map:

- `OMI_LIVE_NCP_ENABLED` is the per-tool enabled flag.
- `OMI_LIVE_NCP_BLOCKED` overrides availability to `blocked`.
- `OMI_LIVE_NCP_BLOCKED_REASON` records the owner reason.

The `ncp` tool is disabled by default and is never classified as
"live analysis runtime" — only as a schema-validator surface probe.

## NCP source path checked

- Source tree: `.external_sources/narrative-context-protocol/`
- `package.json`: `.external_sources/narrative-context-protocol/package.json`
- Schema JSON: `.external_sources/narrative-context-protocol/schema/ncp-schema.json`
- Schema YAML: `.external_sources/narrative-context-protocol/schema/ncp-schema.yaml`
- Validator scripts:
  `.external_sources/narrative-context-protocol/tests/validate-schema.js`
  `.external_sources/narrative-context-protocol/tests/validate-file.js`
- `node_modules`: `.external_sources/narrative-context-protocol/node_modules/`

## Package scripts checked

- `validate:schema` — must be present in `package.json["scripts"]`.
- `validate:file` — must be present in `package.json["scripts"]`.

## Schema paths checked

- `schema/ncp-schema.json` — canonical JSON schema.
- `schema/ncp-schema.yaml` — canonical YAML twin.

## Known npm audit caveat (recorded, not fixed)

The NCP source is shipped with a known audit caveat. It is reported
as part of the preflight, never fixed by it:

- `ajv` — direct dependency, **moderate** severity, ReDoS when using
  the `$data` option.
- `fast-uri` — transitive dependency, **high** severity, path
  traversal / host confusion advisories.

The preflight does not run `npm audit fix`. The preflight does not
expose NCP as a network/server path. The NCP source is not a
candidate-analysis runtime.

## Code change

`backend/omi_runtime_preflight.py` (no edits to
`backend/omi_analysis_orchestrator.py` were required for T018A):

- New NCP path / constant block:
  - `NCP_SOURCE_REL = ".external_sources/narrative-context-protocol"`
  - `NCP_PACKAGE_JSON_REL = ".external_sources/narrative-context-protocol/package.json"`
  - `NCP_SCHEMA_JSON_REL = ".external_sources/narrative-context-protocol/schema/ncp-schema.json"`
  - `NCP_SCHEMA_YAML_REL = ".external_sources/narrative-context-protocol/schema/ncp-schema.yaml"`
  - `NCP_VALIDATE_SCHEMA_SCRIPT_REL = ".external_sources/narrative-context-protocol/tests/validate-schema.js"`
  - `NCP_VALIDATE_FILE_SCRIPT_REL = ".external_sources/narrative-context-protocol/tests/validate-file.js"`
  - `NCP_NODE_MODULES_REL = ".external_sources/narrative-context-protocol/node_modules"`
  - `NCP_VALIDATE_SCHEMA_PACKAGE_SCRIPT = "validate:schema"`
  - `NCP_VALIDATE_FILE_PACKAGE_SCRIPT = "validate:file"`
  - `NCP_AUDIT_CAVEAT` (string literal of the known caveat).
- New read-only helpers:
  - `_safe_read_json(absolute_path)` — read-only, fail-closed JSON
    loader; returns `None` on any failure.
  - `_package_json_script_names(package_json)` — returns the list
    of npm script names declared in a `package.json` dict.
  - `_ncp_runtime_probe()` — read-only schema-validator surface
    probe. Returns the flat dict of `ncp_*` fields documented above.
    Uses `_path_exists`-style absolute paths (not network/server
    paths), `Path.is_file()` / `Path.is_dir()` for file presence,
    `_safe_read_json` for `package.json` parsing, and
    `shutil.which("node")` / `shutil.which("npm")` for command
    availability. Never imports NCP as a Python module; never calls
    `npm install`, `npm audit`, `npm audit fix`, `npm run
    validate:schema`, or `npm run validate:file`.
- `_dependency_probe(adapter="ncp", env)` — replaced the prior stub
  NCP branch with a probe that calls `_ncp_runtime_probe()`, returns
  `runtime_configured = ncp_source_available`, and
  `runtime_dependency_available = ncp_validator_available`. The
  probe result dict carries the new `ncp_*` fields for the tool
  report. Fail-closed; never crashes on missing files.
- `_tool_report(adapter="ncp", env)` — copies the new `ncp_*` fields
  from the dependency probe result into the per-tool `report` entry.
  The blocked-state handling is preserved: when
  `OMI_LIVE_NCP_BLOCKED=1`, the report returns `status="blocked"`,
  the dependency probe result is still populated, and no live
  command is executed.

The T013/T016B/T017A live-tool flag maps
(`OMI_LIVE_TOOL_ENABLED_ENVS["ncp"] == "OMI_LIVE_NCP_ENABLED"`,
`OMI_LIVE_TOOL_BLOCKED_ENVS["ncp"] == "OMI_LIVE_NCP_BLOCKED"`,
`OMI_LIVE_TOOL_BLOCKED_REASON_ENVS["ncp"] == "OMI_LIVE_NCP_BLOCKED_REASON"`)
already existed and remain unchanged. T018A only adds the NCP
schema-validator surface fields; it does not change the live-tool
flag map.

## Safety envelope

The preflight remains read-only and fail-closed for the `ncp` tool:

- `safety.read_only == True`
- `safety.heavy_analysis_executed == False`
- `safety.external_services_called == False`
- `safety.live_models_called == False`
- `safety.candidate_persistence == False`
- `safety.memory_canon_mutation == False`
- `safety.promotion_or_apply_promotion == False`
- `safety.story_prose_generated == False`

The probe does not import NCP as a Python module, does not start a
Node server, does not write to disk, and does not spawn subprocesses.
The audit caveat is recorded as known owner evidence only.

## Tests added

`tests/test_omi_live_runtime_preflight_contract.py` gains 18
T018A-specific tests (all monkeypatched / mock-based; no test
requires the real `.external_sources/narrative-context-protocol`
tree, real node, real npm, or any network access):

1. `test_ncp_preflight_disabled_by_default_remains_safe_read_only` —
   NCP stays `disabled` / `available` with safety envelope all
   true.
2. `test_ncp_all_surfaces_and_node_npm_available_reports_validator_available` —
   all surface items present -> `status="enabled"`, every `ncp_*`
   field reported, audit caveat includes `ajv` and `fast-uri`.
3. `test_ncp_missing_source_reports_unavailable_with_clear_detail` —
   missing source tree -> `unavailable` or `not_configured`, detail
   names the missing source path.
4. `test_ncp_missing_package_json_reports_unavailable_with_clear_detail` —
   missing `package.json` -> unavailable, detail names the missing
   file, the validate-schema/validate-file package script fields
   are False.
5. `test_ncp_missing_schema_json_reports_unavailable_with_clear_detail` —
   missing `ncp-schema.json` -> unavailable, detail names the file.
6. `test_ncp_missing_schema_yaml_reports_unavailable_with_clear_detail` —
   missing `ncp-schema.yaml` -> unavailable, detail names the file.
7. `test_ncp_missing_validate_schema_script_reports_unavailable_with_clear_detail` —
   missing `tests/validate-schema.js` -> unavailable.
8. `test_ncp_missing_validate_file_script_reports_unavailable_with_clear_detail` —
   missing `tests/validate-file.js` -> unavailable.
9. `test_ncp_missing_validate_schema_package_script_reports_unavailable` —
   `package.json` missing the `validate:schema` script entry.
10. `test_ncp_missing_validate_file_package_script_reports_unavailable` —
    `package.json` missing the `validate:file` script entry.
11. `test_ncp_missing_node_reports_unavailable_with_clear_detail` —
    `shutil.which("node")` returns `None` -> unavailable.
12. `test_ncp_missing_npm_reports_unavailable_with_clear_detail` —
    `shutil.which("npm")` returns `None` -> unavailable.
13. `test_ncp_existing_node_modules_is_reported_when_present` —
    `node_modules` reported when present.
14. `test_ncp_missing_node_modules_reports_degraded_with_clear_detail` —
    missing `node_modules` while everything else is present ->
    `ncp_runtime_surface == "degraded"`, status still `enabled` when
    live flags are on (because `ncp_validator_available` is True);
    detail explains the validator scripts would not be runnable and
    preflight does not run `npm install`.
15. `test_ncp_blocked_flag_overrides_validator_availability` —
    `OMI_LIVE_NCP_BLOCKED=1` overrides to `status="blocked"`.
16. `test_ncp_preflight_does_not_run_npm_install_or_audit_fix_or_validate` —
    intercepts `subprocess.run` / `subprocess.Popen` /
    `urllib.request.urlopen` / `subprocess.check_call` /
    `subprocess.check_output` / `subprocess.call` and asserts none
    are called; safety envelope all true. (Ollama probe is also
    mocked so that no real Ollama HTTP request is attempted during
    this test.)
17. `test_ncp_preflight_does_not_persist_or_mutate` — preflight does
    not persist candidate files, mutate the OMI summary, or change
    the project manager state. Safety envelope all true.
18. `test_ncp_audit_caveat_is_reported_verbatim` — `ajv` moderate,
    `fast-uri` high, "npm audit fix" + "recorded, not fixed" appear
    in the reported caveat.

The preflight is mocked in all NCP tests via
`monkeypatch.setattr(preflight, "_ncp_runtime_probe", ...)`. The
real `_ncp_runtime_probe` is never invoked by the new tests; it is
exercised only by the regular `build_omi_runtime_preflight_report`
call and is verified to detect the real
`.external_sources/narrative-context-protocol` tree on the owner
machine during the validation capture below.

## Validation evidence

- `python3 -m py_compile backend/omi_runtime_preflight.py
  backend/omi_analysis_orchestrator.py backend/main.py
  backend/analysis_engine.py` -> exit `0`.
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_live_runtime_preflight_contract.py -q` -> **68
  passed** (50 existing + 18 new T018A).
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py -q` ->
  31 passed (T009 fixture-only NCP adapter contract; not modified by
  T018A).
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> 30
  passed.
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_tool_assisted_persistence_contract.py -q` -> 5
  passed.
- `python3 -m json.tool
  docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json
  >/tmp/phase8-impl-023-enrichment.json.ok` -> valid (T018A scope
  block updated; file is well-formed JSON).
- `git diff --check` -> clean.

Real-machine preflight validation on the owner machine confirms the
NCP surface probe correctly reports the existing
`.external_sources/narrative-context-protocol` source tree:

- `ncp_runtime_surface == "available"`
- `ncp_source_path == ".external_sources/narrative-context-protocol"`
- `ncp_source_available == True`
- `ncp_package_json_available == True`
- `ncp_schema_json_available == True`
- `ncp_schema_yaml_available == True`
- `ncp_validate_schema_script_available == True`
- `ncp_validate_file_script_available == True`
- `ncp_validate_schema_package_script_available == True`
- `ncp_validate_file_package_script_available == True`
- `ncp_node_available == True`,
  `ncp_node_path == "/home/tjrpirateking/.nvm/versions/node/v24.16.0/bin/node"`
- `ncp_npm_available == True`,
  `ncp_npm_path == "/home/tjrpirateking/.nvm/versions/node/v24.16.0/bin/npm"`
- `ncp_node_modules_available == True`
- `ncp_validator_available == True`, `ncp_validator_status == "available"`
- `ncp_audit_caveat` includes `ajv` moderate, `fast-uri` high
- `ncp_detail` names all the surface items present
- `safety.*` all `True`

## Next task

`PHASE8-IMPL-023-T018B — NCP candidate-import validation adapter`
(recommended next). T018B should consume the T018A preflight result
and validate owner-selected structural-context JSON before any
candidate import into the OMI orchestrator's existing fixture-only
NCP context handoff envelope. T018B must run only against
owner-selected NCP JSON, must not run automatically over project
data, must not import NCP as a Python module, must not start a Node
server, must not invoke `npm run validate:file` over project data,
and must not promote anything to canon/Memory.

## No-prose / candidate-only / evidence-backed / provenance

T018A is preflight + tests + docs only. The preflight does not
produce candidate findings, does not write to candidate storage,
does not mutate Memory/Canon, does not create promotion records,
does not run apply-promotion, and does not generate story prose.
The `ncp_audit_caveat` field is a static, owner-known evidence
note; it is not auto-fixed, not auto-applied, and not used to
silently mutate the surface.
