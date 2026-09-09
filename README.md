# Dramatica-Informed Writing Assistant

Dramatica-Informed Writing Assistant is a local-first, analysis-only writing
workspace. It stores and organizes owner-authored material, runs bounded
structural and continuity analysis, and presents evidence- and
provenance-backed candidates for explicit owner review.

It is not a co-writer. It must never generate, rewrite, continue, imitate,
polish, improve, or expand story prose.

## Start here

This README is onboarding guidance, not roadmap or status authority.

- Durable product and MVP contract: [`PRODUCT.md`](PRODUCT.md)
- Implementation and safety policy: [`AGENTS.md`](AGENTS.md)
- Current machine-readable roadmap state:
  [`docs/roadmap/roadmap_index.yaml`](docs/roadmap/roadmap_index.yaml)
- Detailed current work: the active task, inventory, and enrichment records
  referenced by the roadmap index
- Scoped owner decisions: [`docs/roadmap/decisions/`](docs/roadmap/decisions/)

Historical plans, snapshots, pass counts, and old “next task” statements do not
define the current frontier.

## Safety model

- Owner-authored prose may be stored, edited, saved, and organized.
- Analysis findings remain evidence-backed candidates until the owner acts.
- Confidence, queue presence, review status, and promotion records do not make a
  candidate Canon.
- Promotion records are audit records only.
- Approved project truth can change only through the implemented, separate,
  explicit, confirmed, and audited apply-promotion workflow.
- Raw model, extractor, rubric, or reference output never becomes approved
  Memory/Canon automatically.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## Architecture at a glance

- Backend: Python FastAPI under `backend/`
- Frontend: React/Vite under `frontend/`
- Project-local storage under `projects/`
- Local inference: Ollama with the accepted `qwen3:8b` path
- Analysis pipeline: stable source identity and hashes, immutable manifests and
  raw artifacts, evidence ledger, normalization, deterministic fusion,
  candidate persistence, grouped review, promotion audit, and explicit
  apply-promotion
- NCP: supported local/schema gateway within its accepted roadmap scope
- App-owned deterministic contributors, including
  `dramatica_flow_informed_rubric`

The app-owned `dramatica_flow_informed_rubric` is the approved MVP boundary for
permitted analysis-only concepts and structural reasoning derived from the
upstream reference. It is not the external `dramatica_flow` runtime and is not
evidence that that runtime ran. The external runtime is not MVP-required.

Official paid Subtxt/Dramatica is optional. See `PRODUCT.md` and the accepted
decision records for the required, optional, and deferred integration policy.

## Prerequisites

- WSL/Ubuntu is recommended.
- Use the repository's existing Python environment; do not install or replace
  dependencies unless the active task explicitly authorizes it.
- The documented Node target is `>=22.12.0 <23`.
- `npm` is required for frontend development.
- Ollama and `qwen3:8b` are required for the accepted real local MVP contributor
  path, but mock mode remains available for deterministic development and
  regression checks.

## Local development

Run commands from the repository root.

Mock backend:

```bash
ANALYSIS_MODE=mock \
.venv-unsloth-clean/bin/python -m uvicorn backend.main:app \
  --reload --host 0.0.0.0 --port 8000
```

Frontend, in another terminal from the repository root:

```bash
npm --prefix frontend run dev
```

Open `http://localhost:5173`.

For the local Ollama path, set the accepted runtime configuration before
starting the backend:

```bash
OLLAMA_BASE_URL=http://localhost:11434 \
ANALYSIS_MODE=ollama_baseline \
OLLAMA_MODEL=qwen3:8b \
.venv-unsloth-clean/bin/python -m uvicorn backend.main:app \
  --reload --host 0.0.0.0 --port 8000
```

Environment-specific host routing may require a different
`OLLAMA_BASE_URL`. Follow the active task's preflight and runtime instructions
when validating an integration.

## Validation

Use the commands required by the active task. The ordinary application-only
backend suite, when a broad run is warranted, is:

```bash
python3 -m pytest -q tests --ignore=tests/project_memory
```

The frontend build command is:

```bash
npm --prefix frontend run build
```

Fixtures and mocks are regression evidence; they do not prove a required real
integration edge.

## Repository layout

```text
backend/                 FastAPI backend and analysis pipeline
frontend/                React/Vite frontend
projects/example/        Local example project fixture
docs/                    Product, roadmap, decisions, and reference documents
tests/                   Backend and application validation fixtures
training/                Separately governed deferred training/evaluation work
```

## License and provenance

The MIT License applies to app source code only.

Training data, book sources, packet evidence, datasets, model artifacts, raw
source text, training runs, checkpoints, and outputs require their own
provenance, copyright, license, and owner review. Do not commit raw book/source
text, secrets, virtual environments, caches, or generated model artifacts.
