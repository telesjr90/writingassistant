# Dramatica-Informed Writing Assistant

Dramatica-Informed Writing Assistant is a local-first structural analysis tool for writers. It helps inspect narrative coherence, throughline alignment, missing evidence, and diagnostic questions while preserving the writer's authorship.

This project is analysis-only. It must not write, rewrite, continue, imitate, improve, polish, or generate story prose. When a request crosses that boundary, the expected refusal is:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## Architecture

- Backend: FastAPI app in `backend/`.
- Frontend: React and Vite app in `frontend/`.
- Inference: local Ollama chat endpoint, configured by environment variables.
- Project storage: local files under `projects/`; local writing/project content is not safe to commit without separate review.
- Current baseline model: `qwen3:8b`.
- Future non-smoke target model: `dramatica-analyst:8b`, only after separate fine-tuning and evaluation gates pass.

Fine-tuning is a separate, currently gated track. The MVP does not require a fine-tuned model, and smoke-training artifacts are not deployable app models.

## Setup

Backend dependencies are kept separate from training dependencies:

```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

The frontend targets Node `>=22.12.0 <23`:

```bash
cd frontend
npm install
npm run dev
```

Copy `.env.example` values into your local shell or local environment manager as needed. Do not commit real secrets or machine-specific credentials.

## Configuration

Safe default placeholders are provided in `.env.example`:

```text
OLLAMA_CHAT_URL=http://localhost:11434/api/chat
OLLAMA_MODEL=qwen3:8b
ANALYSIS_MODE=ollama_baseline
```

`ANALYSIS_MODE=ollama_baseline` is the current baseline path. `ANALYSIS_MODE=mock` is planned for deterministic fixtures. `dramatica-analyst:8b` remains a future target after non-smoke evaluation, not a current default.

## License Scope

The app source code is licensed under the MIT License. The MIT License does not apply to excluded materials pending separate provenance, copyright, and owner review, including:

- training data
- book sources and raw book text
- packet evidence
- datasets
- model artifacts
- training runs, checkpoints, and outputs
- secrets, virtual environments, and caches

These excluded materials should remain out of the safe commit scope unless they receive explicit separate review and approval.
