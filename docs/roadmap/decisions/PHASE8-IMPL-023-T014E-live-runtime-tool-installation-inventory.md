# PHASE8-IMPL-023-T014E — Live Runtime Tool Installation Inventory

> **Supersession note (2026-07-11):** this inventory remains historical
> evidence of the surfaces available when T014E ran. Its statements that
> Subtxt needed an owner decision or could be owner-blocked are superseded by
> `docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`.
> Full Subtxt runtime is authorized; PHASE8-IMPL-025 T005 performs the current
> technical surface inventory. No T014E completion evidence for other tools is
> invalidated.

## Result

PASS. All selected tools probed, documented, and no installs/downloads performed.

## Task

Inspect/probe/docs task to inventory the local/runtime tool installation state for all selected PHASE8-IMPL-023 live tools so the owner can install missing tools deliberately before continuing live validation.

## Probe Summary

### Git State

- Branch: `docs/opencode-go-routing-small-task-execution`
- Modified tracked files: 3 (artifacts only — `checklist-results.json`, `evidence-report.md`, `workflow-log.json`)
- Untracked files: `PHASE8-IMPL-023-T006-context-files.zip`, `docs/Writing Assistant_OMI.pdf`, `docs/roadmap/decisions/PHASE8-IMPL-023-T005-tool-assisted-orchestrator-contract-adapter-boundaries.md`
- No whitespace errors.

### Ollama Probe

```text
command -v ollama -> ollama_not_found
ollama --version -> ollama_version_not_available
ollama list -> ollama_list_not_available
```

Ollama is **not installed** in the local environment.

### Python Package Probe

```text
spacy_available= False
booknlp_available= False
```

Both spaCy and booknlp Python packages are **not available**.

### spaCy Import Probe

```text
spacy_import=False
spacy_import_error= ModuleNotFoundError No module named 'spacy'
```

spaCy is not importable. `en_core_web_sm` model cannot be loaded.

### Runtime Surface Files Found

```
./.external_sources/booknlp/
./.external_sources/dramatica-flow/
./.external_sources/narrative-context-protocol/
./.external_sources/subtxt-docs/
./backend/story_knowledge/booknlp_adapter_contract.py
./backend/story_knowledge/booknlp_fixture_parser.py
./backend/analysis_engine.py
```

External source directories exist for BookNLP, dramatica-flow, NCP, and Subtxt docs. In-repo BookNLP adapter/fixture modules exist. Story Check is an in-repo module (`backend/analysis_engine.py`).

## Runtime Tool Inventory Table

| Tool | Runtime surface | Installed now? | Required install/setup | Existing preflight/config support? | Existing live adapter? | Manual validation status | Next task | Blocker/owner action |
|---|---|---|---|---|---|---|---|---|
| spaCy | Python package + model (`en_core_web_sm`) | NO | `pip install spacy` + `python -m spacy download en_core_web_sm` | YES: `OMI_LIVE_SPACY_ENABLED`, `OMI_LIVE_SPACY_MODEL`, `OMI_LIVE_SPACY_BLOCKED`, `_spacy_model_probe` in preflight | YES (T014C) | PASS-WITH-BLOCKED-RUNTIME (T014D) | T014 re-run after install, or proceed to T015 if owner blocks spaCy | Owner install spaCy + model; re-run T014D |
| Ollama / local model | Standalone executable (`ollama`) + downloaded model | NO | Install Ollama from https://ollama.com, then `ollama pull <model>` | YES: `OMI_LIVE_OLLAMA_ENABLED`, `OMI_LIVE_OLLAMA_MODEL`, `OMI_LIVE_OLLAMA_MODEL_NAME`, executable probe in preflight | NO (T006 fixture-only) | NOT_ATTEMPTED | T015 — Live Ollama integration | Owner install Ollama separately; select MVP local model |
| Story Check | In-repo module (`backend/analysis_engine.py`) | N/A (in-repo) | None — in-repo module | YES: `OMI_LIVE_STORY_CHECK_ENABLED`, file-existence probe in preflight | NO (T008 fixture-only) | NOT_ATTEMPTED | T016 — Live Story Check integration | Live adapter needs implementation |
| BookNLP | Python package (`booknlp`) + external model data; source at `.external_sources/booknlp/` | NO | `pip install booknlp` (exact command unconfirmed) | YES: `OMI_LIVE_BOOKNLP_ENABLED`, module/executable probe in preflight | NO (T007 fixture-only) | NOT_ATTEMPTED | T017 — Live BookNLP integration | Needs owner research for exact install command |
| NCP | Protocol/schema; reference sources at `.external_sources/narrative-context-protocol/` | N/A (protocol, not runtime tool) | NEEDS-OWNER-DECISION: exact runtime surface unknown | YES: `OMI_LIVE_NCP_ENABLED`, `OMI_LIVE_NCP_COMMAND`, `OMI_LIVE_NCP_PATH` env vars, external-sources probe | NO (T009 fixture-only) | NOT_ATTEMPTED | T018 — Live NCP integration | NEEDS-OWNER-DECISION on what "live NCP" means |
| Subtxt | Reference documentation; sources at `.external_sources/subtxt-docs/` | N/A (reference docs, not runtime tool) | NEEDS-OWNER-DECISION: exact runtime surface unknown | YES: `OMI_LIVE_SUBTXT_ENABLED`, `OMI_LIVE_SUBTXT_COMMAND`, `OMI_LIVE_SUBTXT_PATH` env vars, external-sources probe | NO (T009 fixture-only) | NOT_ATTEMPTED | T019 — Live Subtxt integration | NEEDS-OWNER-DECISION on what "live Subtxt" means |
| dramatica-flow | Reference/analysis sources at `.external_sources/dramatica-flow/`; reference-only per PHASE8-IMPL-005 | N/A (reference-only) | NEEDS-OWNER-DECISION: runtime adapter REJECT/DEFER per PHASE8-IMPL-005 | YES: `OMI_LIVE_DRAMATICA_FLOW_ENABLED`, `OMI_LIVE_DRAMATICA_FLOW_COMMAND`, `OMI_LIVE_DRAMATICA_FLOW_PATH` env vars, external-sources probe | NO (T009 fixture-only) | NOT_ATTEMPTED | T020 — Live dramatica-flow integration | NEEDS-OWNER-DECISION; dramatica-flow is reference-only per PHASE8-IMPL-005 |

## Preflight/Config/Adapter Details per Tool

### spaCy

- Feature flags: `OMI_LIVE_TOOLS_ENABLED` (global gate), `OMI_LIVE_SPACY_ENABLED` (per-tool), `OMI_LIVE_SPACY_BLOCKED` (blocked flag), `OMI_LIVE_SPACY_BLOCKED_REASON` (reason)
- Model config: `OMI_LIVE_SPACY_MODEL` (default `en_core_web_sm`)
- Preflight probe: `_spacy_model_probe` in `backend/omi_runtime_preflight.py:87-128` — probes package importability + model loadability
- Live adapter: `_build_spacy_live_runner` in `backend/omi_analysis_orchestrator.py` (T014C) — lazy spaCy import, entity/noun-chunk extraction, fail-closed
- Tests: `tests/test_omi_booknlp_spacy_adapter_contract.py` (17 passed, all mock spaCy), `tests/test_omi_live_runtime_preflight_contract.py` (14 passed)
- Manual validation: T014D confirmed spaCy not installed; live adapter run not attempted; all fixture/mock tests pass
- Owner install commands (confirmed from T014D):
  ```bash
  source .venv-unsloth-clean/bin/activate
  pip install spacy
  python -m spacy download en_core_web_sm
  ```
- Next after install: Re-run T014D manual validation; then proceed to T015

### Ollama

- Feature flags: `OMI_LIVE_TOOLS_ENABLED` (global), `OMI_LIVE_OLLAMA_ENABLED` (per-tool), `OMI_LIVE_OLLAMA_BLOCKED` (blocked)
- Model config: `OMI_LIVE_OLLAMA_MODEL` or `OMI_LIVE_OLLAMA_MODEL_NAME`
- Preflight probe: `shutil.which("ollama")` executable probe only (no HTTP/model call)
- Live adapter: None — T006 is fixture-only; no live adapter exists yet
- Tests: `tests/test_omi_ollama_model_adapter_contract.py` (19 passed, all fixture/mock)
- Owner install commands (proposed, not repo-confirmed):
  ```bash
  # Install Ollama from https://ollama.com (platform-specific)
  # Then:
  ollama pull <model_name>  # model needed for T015
  ```
- Next: T015 — Live Ollama/local model integration in OMI and analysis

### Story Check

- Feature flags: `OMI_LIVE_STORY_CHECK_ENABLED`
- Preflight probe: `_path_exists("backend/analysis_engine.py")` — checks in-repo module existence
- Live adapter: None — T008 is fixture-only
- Live Story Check already exists separately as `backend/analysis_engine.py` with `run_story_check` route at `POST /api/projects/{project_name}/story-check/{scene_id}`
- Tests: `tests/test_omi_story_check_adapter_contract.py` (11 passed, all fixture/mock)
- Next: T016 — Live Story Check integration in OMI and analysis

### BookNLP

- Feature flags: `OMI_LIVE_BOOKNLP_ENABLED`
- Preflight probe: `importlib.util.find_spec("booknlp")` or `shutil.which("booknlp")`
- Live adapter: None — T007 is fixture-only
- Reference source: `.external_sources/booknlp/` (local clone)
- In-repo adapter code: `backend/story_knowledge/booknlp_adapter_contract.py`, `backend/story_knowledge/booknlp_fixture_parser.py`
- Install command: NOT CONFIRMED from repo docs — proposed `pip install booknlp` but exact command needs owner research
- Next: T017 — Live BookNLP integration; needs install command confirmed first

### NCP

- Feature flags: `OMI_LIVE_NCP_ENABLED`
- Preflight probe: `OMI_LIVE_NCP_COMMAND`, `OMI_LIVE_NCP_PATH` env vars, or `_path_exists(".external_sources")`
- Live adapter: None — T009 is fixture-only
- Reference source: `.external_sources/narrative-context-protocol/` (local clone)
- Runtime surface: UNKNOWN — NCP is a protocol/schema, not a standalone runtime tool
- Install command: NEEDS-OWNER-DECISION
- Next: T018 — Live NCP integration or explicit owner-blocked decision

### Subtxt

- Feature flags: `OMI_LIVE_SUBTXT_ENABLED`
- Preflight probe: `OMI_LIVE_SUBTXT_COMMAND`, `OMI_LIVE_SUBTXT_PATH` env vars, or `_path_exists(".external_sources")`
- Live adapter: None — T009 is fixture-only
- Reference source: `.external_sources/subtxt-docs/` (local clone)
- Runtime surface: UNKNOWN — Subtxt docs are reference/guardrail material
- Install command: NEEDS-OWNER-DECISION
- Next: T019 — Live Subtxt integration or explicit owner-blocked decision

### dramatica-flow

- Feature flags: `OMI_LIVE_DRAMATICA_FLOW_ENABLED`
- Preflight probe: `OMI_LIVE_DRAMATICA_FLOW_COMMAND`, `OMI_LIVE_DRAMATICA_FLOW_PATH` env vars, or `_path_exists(".external_sources")`
- Live adapter: None — T009 is fixture-only
- Reference source: `.external_sources/dramatica-flow/` (local clone)
- Runtime status: Reference-only per PHASE8-IMPL-005-T004; runtime adapter is REJECT/DEFER
- Install command: NEEDS-OWNER-DECISION
- Next: T020 — Live dramatica-flow integration or explicit owner-blocked decision

## Owner-Confirmed Install Commands

### spaCy (confirmed from T014D docs)

```bash
source .venv-unsloth-clean/bin/activate
pip install spacy
python -m spacy download en_core_web_sm
```

### Ollama (proposed, not repo-confirmed — owner must confirm)

```bash
# Install Ollama from https://ollama.com
# Then pull MVP model:
ollama pull <model>  # exact model TBD: qwen3:8b, llama3, or other per owner decision
```

## Changes

- New decision record: `docs/roadmap/decisions/PHASE8-IMPL-023-T014E-live-runtime-tool-installation-inventory.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/open_questions.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json`
- No backend/frontend/package files changed
- No installs/downloads performed
- No staging, commit, or push performed

## Confirmations

- No installs or downloads of spaCy, Ollama, BookNLP, or any runtime occurred.
- No package/dependency files were changed.
- No backend or frontend runtime behavior was edited.
- No candidate persistence, Memory/Canon mutation, promotion records, apply-promotion, or story prose occurred.
- No staging, commit, or push was performed.
- Read-only probes only: `git status`, `git diff`, `command -v ollama`, `importlib.util.find_spec`, Python import attempt, `find` for runtime surfaces.

## Next Recommended Task Order

1. Owner installs spaCy + `en_core_web_sm` model — re-runs T014D manual validation
2. Owner installs Ollama + selects MVP model — starts T015 live Ollama integration
3. T016 — Live Story Check integration (in-repo module, no install needed)
4. T017 — Live BookNLP integration (requires owner research on install command)
5. T018/T019/T020 — NCP/Subtxt/dramatica-flow (require owner decision on what "live" means)
6. T021–T026 — Cross-tool fusion, persistence validation, UI, automated/manual tests, closeout
