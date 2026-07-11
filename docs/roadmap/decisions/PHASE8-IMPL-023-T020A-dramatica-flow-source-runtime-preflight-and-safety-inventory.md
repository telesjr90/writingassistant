# PHASE8-IMPL-023-T020A — Dramatica-flow source/runtime preflight and safety inventory

## Result

PASS.

T020A implements a focused, read-only dramatica-flow source/runtime preflight in
`backend/omi_runtime_preflight.py` and records the current local source,
editable-install, command, model/network, mutation, license, and authorization
state. The task is inventory and safety preflight only. It does not implement a
live dramatica-flow adapter and does not decide the T020 integration path.

## Source and editable venv evidence

The probe statically inspects only the bounded dramatica-flow source and venv
surfaces:

- `.external_sources/dramatica-flow/pyproject.toml`
- `.external_sources/dramatica-flow/README.md`
- `.external_sources/dramatica-flow/README_EN.md`
- `.external_sources/dramatica-flow/cli/main.py`
- `.external_sources/dramatica-flow/core/validators/__init__.py`
- `.external_sources/venvs/dramatica-flow/bin/python`
- `.external_sources/venvs/dramatica-flow/bin/df`
- `.external_sources/venvs/dramatica-flow/lib/python3.12/site-packages/dramatica_flow-0.1.0.dist-info/direct_url.json`
- `.external_sources/venvs/dramatica-flow/lib/python3.12/site-packages/dramatica_flow-0.1.0.dist-info/entry_points.txt`
- `.external_sources/venvs/dramatica-flow/lib/python3.12/site-packages/dramatica_flow-0.1.0.dist-info/METADATA`

Real read-only source-probe result:

```text
dramatica_flow_source_available = True
dramatica_flow_package_name = "dramatica-flow"
dramatica_flow_package_version = "0.1.0"
dramatica_flow_requires_python = ">=3.11"
dramatica_flow_console_script_name = "df"
dramatica_flow_console_script_target = "cli.main:app"
dramatica_flow_venv_available = True
dramatica_flow_editable_install = True
dramatica_flow_editable_source_matches_expected = True
dramatica_flow_runtime_surface = "installed_reference_surface"
```

The editable source comparison is an exact resolved `file://` source-path
comparison. Malformed, non-file, non-editable, or mismatched direct URLs fail
closed and do not count as an installed reference surface.

## Command inventory

Static AST command discovery from `cli/main.py` reports:

```text
audit
book
create
delete
doctor
export
init
init-templates
list
load
revise
setup
show
status
threads
update
write
```

T020A classifies only detected commands:

```python
analysis_candidate_commands = ["audit", "status"]
prose_production_commands = ["export", "revise", "write"]
```

`doctor` is not classified as an authorized analysis command. It tests API
connectivity and is not a safe analysis runtime path for this application.

## Risk surfaces

The bounded static source inspection detects model/network/server evidence:

- `openai`
- `deepseek`
- `ollama`
- `fastapi`
- `uvicorn`
- LLM/model configuration references

It also detects project/state mutation surfaces:

- `init`
- `book`
- `setup`
- `write`
- `revise`
- `export`
- `threads create/update/delete`
- `world_state`
- truth/story-bible/state file writes
- draft/final chapter reads and writes

These surfaces confirm the prior PHASE8-IMPL-005 decision risk: dramatica-flow
contains useful analysis concepts, but its runtime is generation, revision,
export, server/model, and project-state capable.

## License result

The README files claim MIT through license badges/text:

```text
dramatica_flow_license_claimed = True
dramatica_flow_license_name = "MIT"
dramatica_flow_license_source = "README.md, README_EN.md"
```

No root `LICENSE`/`LICENSE.md`/`LICENSE.txt`/`COPYING` file is present in the
inspected source:

```text
dramatica_flow_license_file_available = False
dramatica_flow_license_verified = False
```

T020A makes no legal conclusion. License verification and any code reuse remain
owner/legal-review items.

## Runtime and authorization result

These values are hard false and must remain false:

```python
dramatica_flow_analysis_only_runtime_authorized = False
dramatica_flow_live_runtime_available = False
runtime_dependency_available = False
```

Source availability, editable-install evidence, configured command/path values,
or enabled flags never authorize or enable a live runtime. The dependency status
for the T013 preflight remains `unavailable` because no runnable dramatica-flow
analysis-only adapter is authorized.

T020A preserves the T009 fixture-only `dramatica_flow` contract and does not
modify the OMI orchestrator, analysis runtime integration, routes, UI,
persistence, Memory/Canon, promotion, or story-prose behavior.

## Tests

T020A adds focused coverage in
`tests/test_omi_live_runtime_preflight_contract.py`, including:

- source unavailable/source-only/full source+venv cases;
- exact package, version, Python, console-script, dist-info, and editable-source
  checks;
- malformed pyproject, malformed CLI source, malformed entry points,
  malformed/non-file/non-editable direct URL, and multiple dist-info fail-closed
  cases;
- command classification and explicit `doctor` exclusion;
- model/network and project-mutation evidence detection;
- README MIT claim versus root license-file verification;
- hard-false runtime and authorization assertions even when flags/command/path
  are configured;
- direct `_dramatica_flow_runtime_probe({})` subprocess/network isolation with
  patched subprocess and network functions;
- full-report dramatica-flow assertions with unrelated probes patched out.

Focused T020A validation:

```text
py_compile backend/omi_runtime_preflight.py tests/test_omi_live_runtime_preflight_contract.py -> PASS
pytest tests/test_omi_live_runtime_preflight_contract.py -k 'dramatica_flow or t020a' -> 42 passed
```

## Next task

`PHASE8-IMPL-023-T020B — Dramatica-flow integration-path and analysis-only boundary decision`

T020B must choose among:

- complete runtime remains owner-blocked/reference-only;
- narrowly audited non-generative/non-mutating subset;
- app-owned dramatica-flow-informed analysis rubric.

T020A does not implement T020B.

## Safety confirmations

- No dramatica-flow import or execution.
- No `df` execution.
- No server/model/network/subprocess/shell call by the probe.
- No install or package-manager operation.
- No `.external_sources/` or `.external_sources/venvs/` mutation.
- No orchestrator, T009 contract, runtime-integration, route, UI, persistence,
  Memory/Canon, promotion, apply-promotion, or prose change.
- No stage, commit, or push.
