# Dramatica-Informed Writing Assistant

Dramatica-Informed Writing Assistant is a local-first writing assistant for structural narrative analysis. It is Dramatica-informed, uses Narrative Context Protocol (NCP) and storyform context as its structural backbone, and helps a writer inspect narrative coherence without taking over authorship.

This is an analysis-only tool, not a prose generation tool.

## MVP Status

The App MVP is local-ready with notes.

- Tag: `app-mvp-local-ready`
- Backend validation: `176 passed`
- Frontend validation: `npm run build` passed with the existing non-blocking Vite large-chunk warning
- GitHub roadmap: labels, milestones, and post-MVP issues exist for follow-up work
- Fine-tuning remains separate from MVP
- Optional extractors remain post-MVP
- Future apply-promotion behavior remains separate and unimplemented

The app does not claim full Dramatica verifier parity. It provides bounded, candidate diagnostics and requires insufficient-evidence handling when the current project context does not support a confident claim.

## Non-Negotiable Boundary

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

The app must not:

- generate story prose
- rewrite story prose
- continue story prose
- imitate style
- polish or improve prose
- silently promote candidate analysis into project truth

Story Check output is candidate diagnostics only. Raw model output, NotebookLM output, optional extractor output, and retrieved definitions are candidate or reference material only. Owner-approved truth remains separate from candidate analysis.

## Current MVP Features

- Local FastAPI backend
- React/Vite frontend
- File-based local project storage
- Scene editor with save and dirty-state behavior
- Bible and storyform JSON read/write through explicit owner saves
- Story Check
- Normalized rich diagnostics sidebar
- Insufficient-evidence handling
- Request and output guardrails for the no-prose boundary
- Mock mode for deterministic Story Check demos and tests
- qwen3/Ollama baseline mode
- Bounded OMI workflow:
  - raw ideas
  - structured candidates
  - owner decisions
  - destinations
  - provenance and status display
  - promotion records only
  - no durable truth mutation

## Architecture

- Backend: Python FastAPI in `backend/`
- Frontend: React/Vite in `frontend/`
- Local inference: Ollama
- Current baseline model: `qwen3:8b`
- Future target model: `dramatica-analyst:8b`
- Structural context: NCP/storyform-informed project context
- Storage: local files under `projects/`

`dramatica-analyst:8b` is a future target only. It should not be treated as locally available or production-ready until a non-smoke fine-tuned model passes evaluation gates and is explicitly imported into Ollama.

## Prerequisites

- WSL/Ubuntu recommended
- Python virtual environment used by this project: `.venv-unsloth-clean`
- Node target from project docs: `>=22.12.0 <23`
- `npm`
- Ollama is optional for baseline mode
- `qwen3:8b` is optional for live baseline mode

Mock mode does not require Ollama or `qwen3:8b`.

## Quick Start: Mock Mode

From the project root:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication

ANALYSIS_MODE=mock \
.venv-unsloth-clean/bin/python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication/frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Quick Start: qwen3/Ollama Baseline Mode

If Ollama is running on Windows and the app is running from WSL, find the Windows host gateway and check Ollama:

```bash
WINDOWS_HOST=$(ip route | awk '/default/ {print $3}')
curl http://$WINDOWS_HOST:11434/api/tags
```

Then start the backend with the explicit Ollama baseline configuration:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication

OLLAMA_BASE_URL="http://$WINDOWS_HOST:11434" \
ANALYSIS_MODE=ollama_baseline \
OLLAMA_MODEL=qwen3:8b \
.venv-unsloth-clean/bin/python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend separately:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication/frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Tests

Backend:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication
.venv-unsloth-clean/bin/python -m pytest tests -q
```

Frontend build:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication/frontend
npm run build
```

The frontend build currently passes with a known non-blocking Vite large-chunk warning.

## Evaluation Harness

Offline Story Check baseline evaluation:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication

.venv-unsloth-clean/bin/python training/scripts/run_story_check_baseline_eval.py \
  --fixtures-dir tests/fixtures/story_check \
  --output /tmp/story_check_baseline_eval.json \
  --pretty
```

This harness uses app-level fixtures under `tests/fixtures/story_check/`. They are not training data and are not part of `training/data` or `dataset_manifest.json`.

## OMI Safety Notes

OMI means Organize My Idea. In this MVP it is bounded to candidate planning material only.

- OMI candidates are not project truth.
- Promotion records are records only.
- Apply-promotion behavior is not implemented.
- OMI cannot write scenes or rewrite prose.
- OMI does not call model paths for candidate generation in the current MVP.
- Future truth mutation workflows require owner approval, destination choice, provenance, evidence where required, safe target validation, and final confirmation.

OMI promotion records do not mutate `bible.json`, `storyform.json`, `scenes/`, `project.json`, owner memory, training data, or `dataset_manifest.json`.

## Project Structure

```text
backend/                 FastAPI backend, analysis modes, guardrails, project storage helpers
frontend/                React/Vite frontend
projects/example/        Local example project fixture
docs/                    Project plans and public documentation
docs/roadmap/            MVP, OMI, extractor, tooling, and post-MVP roadmap docs
tests/                   Backend and app-level validation fixtures
training/scripts/        Evaluation and training utility scripts
training/reports/        Ignored/local-only reports
training/data/           Excluded from app MVP docs and not modified by app validation
```

## License and Provenance

The MIT License applies to app source code only.

Training data, book sources, packet evidence, datasets, model artifacts, raw source text, training runs, checkpoints, and outputs are excluded pending separate provenance, copyright, license, and owner review.

Do not commit raw book/source text, secrets, virtual environments, caches, or generated model artifacts.

## Post-MVP Roadmap

Post-MVP work is tracked in GitHub Issues with labels and milestones. The first issues to review are:

- Issue #1: apply-promotion workflow design for approved OMI candidates
- Issue #2: apply-promotion safety tests before any truth mutation

Other post-MVP areas include:

- apply-promotion workflow design and safety tests
- frontend test runner setup
- README and documentation polish
- optional extractor research
- fine-tuning dataset gate review
- RunPod/cloud training preparation
- GGUF export and Ollama import planning
- future `dramatica-analyst:8b` only after non-smoke evaluation passes

Optional extractors are candidate-only research. They must route through OMI candidates, preserve provenance, avoid direct truth mutation, and never generate story prose.

## Configuration Notes

`.env.example` documents the main local settings:

```text
ANALYSIS_MODE=ollama_baseline
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Use `ANALYSIS_MODE=mock` for deterministic local Story Check demos and tests without Ollama. Use `ANALYSIS_MODE=ollama_baseline` with `OLLAMA_BASE_URL` and `OLLAMA_MODEL=qwen3:8b` for the current live baseline mode.
