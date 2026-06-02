# Tooling Decisions

## Use Now

- Markdown master plan.
- Supporting Markdown roadmap files.
- Mermaid Gantt inside Markdown.
- Issue-driven task decomposition as a method.
- GitHub Issues/GitHub Projects later, after the safe local baseline is pushed.
- `ai-llm-project-file-structure-template` only as a checklist.
- `llm_finetuning` only as evaluation/training lifecycle inspiration.
- NotebookLM only as candidate packet/evidence aggregation workflow.
- Codex only for repo inspection and documentation updates.

## Do Not Use Now

- Notion.
- Linear.
- Roadmap-Generator-as-Gemini.
- `mouc`.
- `pixel-planner`.
- `generative-ai-project-template`.
- Zero Operators.
- FARM framework.
- React/FastAPI/Ollama starter kits.
- Local-LLM-Chat-Playground.
- `capybara-gpt`.
- NARRATIS.
- StoryExplorer.
- Dramatron/NovelClaw/worldbuilding templates as active implementation plans.

## Reference Repo Role Map

| Reference | Current role |
| --- | --- |
| narrative-context-protocol | NCP/schema inspiration and compatibility reference |
| NovelClaw | Future memory-bank inspiration only |
| dramatron | Blocked/non-goal for generation |
| ai-story-writer | Not an implementation template |
| notebook | Candidate aggregation inspiration only |

## Current Repo Tooling Notes

- Backend: Python FastAPI.
- Frontend: React/Vite.
- Local inference: Ollama.
- Analysis mode switch: `ANALYSIS_MODE=ollama_baseline` uses Ollama and defaults `OLLAMA_MODEL` to `qwen3:8b`; `ANALYSIS_MODE=mock` returns deterministic normalized Story Check diagnostics without Ollama.
- Ollama endpoint config: `OLLAMA_BASE_URL` defaults to `http://localhost:11434` and builds `/api/chat`; WSL-to-Windows Ollama can use `OLLAMA_BASE_URL=http://<windows-gateway-ip>:11434`.
- App-8 live baseline verification: local smoke passed on 2026-06-01 with `OLLAMA_BASE_URL=http://172.25.144.1:11434`, `ANALYSIS_MODE=ollama_baseline`, and `OLLAMA_MODEL=qwen3:8b`; do not pull/install models without owner approval.
- FE-001 rich diagnostics sidebar: `AnalysisSidebar.jsx` renders normalized Story Check sections first and keeps raw JSON in a collapsed advanced view; `frontend/package.json` now defines `npm run build`, and `npm install --include=optional` restored the Vite/Rolldown optional native binding needed for build validation. No frontend test framework is configured beyond the placeholder `npm test` script.
- App-4 scene editor hardening: frontend validation remains `npm run build`; backend route/storage behavior is covered by pytest with temporary project directories so `projects/example` fixture content is not modified.
- App-5 bible/storyform read/write: context editing uses plain JSON textareas in `ProjectContext.jsx`; backend PUT routes require explicit owner-submitted JSON objects, storyform saves validate with the existing schema before writing, and tests use temporary project directories.
- GUARD-002 request-path policy: use `guard_freeform_request` for future freeform assistant/model request fields before model calls. Do not run the request guard on owner-authored content fields such as scene content, bible JSON, storyform JSON, raw ideas, or planning notes.
- Training: Unsloth QLoRA scripts/configs exist.
- Git: initialized/repaired on `main` with `origin https://github.com/telesjr90/writingassistant`; local baseline commit `25ef64d chore: initialize safe project baseline` exists.
- GitHub push: still TODO; do not claim the safe baseline has been pushed.
- Backend dependency manifest: `backend/requirements.txt` exists and remains separate from `training/requirements-unsloth.txt`.
- OMI: App MVP feature, but bounded to analysis-only candidate planning. No prose generation, no story continuation, no rewriting, and no silent promotion into durable truth. Future runtime implementation should use shared `backend/guardrails.py` before model calls; this is a design target only until implemented.
- GitHub Issues/Projects: deferred until after safe baseline push and owner approval.
