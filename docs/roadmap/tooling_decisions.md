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
- Training: Unsloth QLoRA scripts/configs exist.
- Git: initialized/repaired on `main` with `origin https://github.com/telesjr90/writingassistant`; local baseline commit `25ef64d chore: initialize safe project baseline` exists.
- GitHub push: still TODO; do not claim the safe baseline has been pushed.
- Backend dependency manifest: `backend/requirements.txt` exists and remains separate from `training/requirements-unsloth.txt`.
- OMI: App MVP feature, but bounded to analysis-only candidate planning. No prose generation, no story continuation, no rewriting, and no silent promotion into durable truth. Future runtime implementation should use shared `backend/guardrails.py` before model calls; this is a design target only until implemented.
- GitHub Issues/Projects: deferred until after safe baseline push and owner approval.
