# MVP Owner Acceptance Browser Evidence Harness

## Status

- Task: `MVP-READINESS-OWNER-ACCEPTANCE-002`
- Updated by: `MVP-READINESS-OWNER-ACCEPTANCE-003`
- Updated by: `MVP-READINESS-OWNER-ACCEPTANCE-004`
- Result: **Harness created, WSL Ollama fallback added, and Cyber detective owner-authored fixture automation added; owner run pending**
- Script: `scripts/mvp-owner-acceptance-browser-smoke.mjs`
- Evidence directory: `artifacts/mvp-readiness/owner-acceptance`
- Browser acceptance script status: **not run by Codex**
- MVP readiness decision from this task: **MANUAL_REVIEW_REQUIRED until owner runs and reviews evidence**
- MVP completion: **not complete**
- Owner acceptance: **pending owner decision**

## Purpose

The harness automates the owner MVP acceptance checklist where safe, captures screenshots, performs safe backend/Ollama readiness checks, records browser-visible workflow evidence, and writes structured artifacts:

- `screenshots/*.png`
- `workflow-log.json`
- `checklist-results.json`
- `evidence-report.md`

The result model is:

- `PASS`
- `FAIL`
- `BLOCKED`
- `NOT_EXPOSED`
- `MANUAL_REVIEW_REQUIRED`

The script must not fake `PASS` for absent UI/API surfaces. Missing or unsafe surfaces are recorded as `NOT_EXPOSED` or `MANUAL_REVIEW_REQUIRED`.

## Cyber Detective Fixture

`MVP-READINESS-OWNER-ACCEPTANCE-004` adds `MVP_ACCEPTANCE_FIXTURE=cyber-detective`, which is also the default fixture for the owner acceptance harness.

- Fixture title: `Cyber detective`
- Source type: owner-authored MVP acceptance fixture
- Intended use: analysis/testing boundaries only
- Content warning metadata: mature/violent material, trauma, abuse references, and drug-use references, recorded for internal evidence only
- Harness-created project title: `Cyber detective MVP Acceptance <timestamp>`
- Evidence records fixture title, fixture id/slug, content length, owner-authored status, and that the harness did not generate story prose from it.

The harness must not generate, continue, rewrite, polish, improve, imitate, expand, draft, or outline from the Cyber detective fixture. The fixture content must not become canon or approved memory without an explicit owner-approved workflow, and this harness must not perform that workflow automatically.

The Cyber detective path creates a project through the browser UI, fills the OMI-guided title/source/notes fields, reviews before creation, asserts owner-authored source visibility in the review step, creates the project, and checks that the created project is active in the header, selector, and Overview. OMI/setup evidence remains candidate/planning only, and Memory/Canon evidence remains approved-only/non-canon.

If Story Check or no-prose negative-path inputs are not safely exposed for the created fixture project, the harness records `MANUAL_REVIEW_REQUIRED` or `NOT_EXPOSED` with screenshots instead of faking `PASS`. If a safe Story Check workflow is exposed and run, results may pass only when diagnostic/candidate-first, non-canon, and free of story prose generation.

## Ollama Readiness Handling

The harness checks Ollama readiness only through:

- `GET <selected-ollama-base-url>/api/version`
- `GET <selected-ollama-base-url>/api/tags`

The harness now tries Ollama candidates in this order:

1. `OLLAMA_BASE_URL`
2. `OLLAMA_HOST`
3. `http://localhost:11434`
4. WSL Windows-host fallback, when WSL is detected and the default gateway can be read from `/proc/net/route`

Candidate URLs may be provided as `http://host:11434` or `host:11434`; the harness normalizes missing `http://` and removes trailing slashes before adding `/api/version` or `/api/tags`.

WSL/Ubuntu may not reach Windows-hosted Ollama at `localhost:11434`. If Ollama runs on Windows while the backend or test runs in WSL, use the WSL default gateway:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_HOST="http://$WINDOWS_HOST:11434"
curl "$OLLAMA_HOST/api/version"
```

The generated `workflow-log.json`, `checklist-results.json`, and `evidence-report.md` record the selected Ollama base URL, selected source, attempted candidates, endpoint statuses, and error summaries.

If Ollama is unreachable, the harness records:

- `startup_ollama_unreachable = BLOCKED`
- model-backed checklist sections = `BLOCKED`
- WSL remediation command shown above

The harness does not call Ollama directly for creative generation.

## Backend Startup Note

Inspection of `backend/analysis_engine.py` shows Story Check reads `OLLAMA_BASE_URL`, not `OLLAMA_HOST`, and falls back to `http://localhost:11434`.

If the backend runs in WSL and Ollama runs on Windows, start the backend with:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_BASE_URL="http://$WINDOWS_HOST:11434"
PY=".venv-unsloth-clean/bin/python"
"$PY" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

This is startup/readiness configuration only. It does not change product behavior and does not mark MVP complete.

## Automation Coverage

Automated or partially automated sections:

- Startup Requirements
- Project Isolation
- Manual Workspace Checks
- Runtime Extraction Checks
- Candidate / Review Checks
- Apply-Promotion Checks
- Model-Assisted / Analysis Runtime Checks
- No-Prose Checks
- Final Owner Decision recording

The Final Owner Decision remains pending. The script can output `READY_FOR_OWNER_REVIEW`, `BLOCKED`, or `MANUAL_REVIEW_REQUIRED`, but it cannot choose Accepted and cannot mark MVP complete.

## Safety Boundaries

- No product fixes.
- No frontend/backend product logic changes.
- No generated prose.
- No rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, or story-prose path.
- No BookNLP/spaCy direct execution.
- No NCP/Subtxt/dramatica-flow direct execution.
- No automatic memory/canon mutation.
- No apply-promotion shortcut.
- No training/JSONL/dataset/model artifacts.
- No staging, commit, or push.

## Manual Run Command

```bash
# From repo root, with frontend/backend already running:
node scripts/mvp-owner-acceptance-browser-smoke.mjs

# Optional overrides:
APP_BASE_URL=http://localhost:5173 \
BACKEND_BASE_URL=http://localhost:8000 \
OLLAMA_BASE_URL=http://localhost:11434 \
MVP_ACCEPTANCE_EVIDENCE_DIR=artifacts/mvp-readiness/owner-acceptance \
node scripts/mvp-owner-acceptance-browser-smoke.mjs

# Optional fixture override; default is cyber-detective:
MVP_ACCEPTANCE_FIXTURE=cyber-detective \
node scripts/mvp-owner-acceptance-browser-smoke.mjs
```

For WSL test runs against Windows-hosted Ollama, set:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_HOST="http://$WINDOWS_HOST:11434"
node scripts/mvp-owner-acceptance-browser-smoke.mjs
```

## Current Owner Follow-Up

Owner should start backend, frontend, and Ollama if model-backed workflows will be reviewed, then run the harness and inspect `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`.

This task does not mark MVP complete and does not claim owner acceptance.
