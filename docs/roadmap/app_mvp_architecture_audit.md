# App MVP Architecture Audit

## 1. Executive Summary

The current Dramatica-Informed Writing Assistant is a local FastAPI plus React/Vite app with Ollama as the configured inference path. It is analysis-only by product boundary, with the current backend default model set to `qwen3:8b` and the future `dramatica-analyst:8b` target blocked behind non-smoke training, evaluation, and model-swap gates.

Implemented today:

- FastAPI routes for listing scenes, loading one scene, saving one scene, loading bible JSON, running Story Check, and returning storyform prompt context.
- Local file project storage under `projects/{project_name}` for `bible.json`, `storyform.json`, and `scenes/{scene_id}.md`.
- Storyform validation against the NCP-style schema embedded in `docs/repo_knowledge.md`.
- Story Check prompt assembly from storyform context, bible JSON, and scene text.
- Ollama chat call through `requests.post()` with `format: "json"` and low-temperature options.
- Story Check response parsing that supports a rich schema shape, preserves diagnostics, normalizes warnings/questions, and falls back safely on malformed JSON.
- React UI for project scene selection, scene editing/saving, storyform context display, Story Check triggering, and simple analysis rendering.
- Backend unit tests for project storage, storyform validation/context, Story Check parsing, and dataset validator basics.

Missing for App MVP:

- Clean Phase 0 push state: the safe baseline has not been verified as pushed, and the current working tree is not clean.
- A documented project file model beyond the current implicit files.
- A designed NCP/storyform MVP subset.
- OMI schema/lifecycle/storage/API/UI design and implementation.
- Runtime no-prose guardrails before model calls and after model output.
- Explicit analysis mode routing for mock vs Ollama baseline.
- Route tests for FastAPI endpoints.
- Frontend tests and richer diagnostics rendering.
- Sample project alignment; the current example scene/bible use Elena/Whispering Woods while the storyform is Quest for the Ember Crown/Mara.

Immediate recommended next task: App-2 Project file model, paired with App-3 NCP compatibility subset and OMI-001 schema/lifecycle design before any OMI runtime work.

## 2. Verified Repo/Setup State

- Working directory: `/home/tjrpirateking/projects/WritingAssistantApplication`.
- Git branch: `main`.
- Remote: `origin https://github.com/telesjr90/writingassistant`.
- Latest commit: `25ef64d chore: initialize safe project baseline`.
- Working tree clean: no. The working tree has uncommitted documentation changes from the master-plan/status sync work.
- Phase 0 status: not fully complete. The local baseline exists, but the clean-tree gate failed during the Phase 0 push attempt, so no push was attempted and the GitHub push remains pending.

`training/reports/phase_0_repo_baseline_completion_report.md` exists locally and records the blocked push. It is currently ignored by `.gitignore` because `training/reports/*` is ignored except for whitelisted setup reports.

## 3. Backend Inventory

Files inspected:

- `backend/main.py`
- `backend/analysis_engine.py`
- `backend/project_manager.py`
- `backend/storyform.py`
- `backend/prompts/story_check.txt`
- `backend/prompts/extract_elements.txt`
- `backend/requirements.txt`
- `backend/run.ps1`

FastAPI routes found in `backend/main.py`:

| Method | Route | Current behavior |
| --- | --- | --- |
| `GET` | `/api/projects/{project_name}/scenes` | Returns `{"scenes": [...]}` from Markdown scene files under `projects/{project_name}/scenes`. |
| `GET` | `/api/projects/{project_name}/scenes/{scene_id}` | Loads `projects/{project_name}/scenes/{scene_id}.md`; returns `{"content": ...}` or 404 if missing/empty. |
| `PUT` | `/api/projects/{project_name}/scenes/{scene_id}` | Saves request body field `content` to the scene Markdown file; returns `{"status": "saved"}`. |
| `GET` | `/api/projects/{project_name}/bible` | Loads and returns `projects/{project_name}/bible.json`. |
| `POST` | `/api/projects/{project_name}/story-check/{scene_id}` | Calls `analysis_engine.run_story_check(project_name, scene_id)` and returns its dict; catches broad exceptions and returns `{"error": ...}`. |
| `GET` | `/api/projects/{project_name}/storyform-context` | Loads and validates storyform, then returns `{"context": loaded_storyform.to_prompt_context()}`. |

Project loading/saving:

- `project_manager.PROJECTS_DIR` points to repo-local `projects/`.
- Project names and scene IDs are validated as single path components.
- `load_bible()` requires `bible.json` to be a JSON object.
- `save_bible()` creates the project directory if needed.
- `load_scene()` reads Markdown text.
- `save_scene()` creates the scenes directory if needed.
- `list_scenes()` returns sorted Markdown stems from the scenes directory and ignores non-Markdown files.

Story Check route behavior:

- `POST /story-check` delegates to `analysis_engine.run_story_check()`.
- Errors are returned as JSON bodies with an `error` field rather than raised HTTP errors.
- There is no route-level request body; Story Check always analyzes the selected saved scene and the current project context.

Ollama call path:

- `backend/main.py` route -> `analysis_engine.run_story_check()` -> `Storyform.from_file()` -> `project_manager.load_scene()` / `load_bible()` -> `backend/prompts/story_check.txt` formatting -> `requests.post(OLLAMA_CHAT_URL, ...)`.
- The call sends `model`, a single user message containing the full prompt, `format: "json"`, `think: False`, `temperature: 0`, `num_predict: 512`, and `stream: False`.

Environment/config variables currently used:

- `OLLAMA_CHAT_URL`, default `http://localhost:11434/api/chat`.
- `OLLAMA_MODEL`, default `qwen3:8b`.
- `OLLAMA_TIMEOUT_SECONDS`, default `300`.

`.env.example` also defines `ANALYSIS_MODE=ollama_baseline`, but no runtime code currently reads `ANALYSIS_MODE`.

Error handling notes:

- Scene `GET` maps missing/empty scene content to 404.
- Story Check catches all exceptions inside `analysis_engine.run_story_check()` and returns `{"error": str(e)}`. The route also catches exceptions, but the inner function already converts most failures to error dictionaries.
- Storyform context route does not catch validation or missing-file errors.
- Bible route does not catch missing/invalid file errors.
- CORS allows all origins.

Backend gaps:

- No project creation/listing route.
- No editable bible/storyform routes beyond reading bible and context.
- No route tests for FastAPI behavior.
- No explicit `ANALYSIS_MODE` implementation.
- No mock analysis mode.
- No runtime pre-model no-prose input guard.
- Output guard is partial: suggestions that look like prose-generation requests are dropped, but there is no full post-model refusal/guardrail layer.
- No OMI backend routes, storage, manager, or lifecycle code.
- No durable candidate-analysis storage model.

## 4. Frontend Inventory

Files inspected:

- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/api.js`
- `frontend/src/App.jsx`
- `frontend/src/components/ProjectNav.jsx`
- `frontend/src/components/Editor.jsx`
- `frontend/src/components/AnalysisSidebar.jsx`
- `frontend/src/main.jsx`
- `frontend/src/styles.css`

Current component structure:

- `App.jsx` owns app state and composes `ProjectNav`, `Editor`, and `AnalysisSidebar`.
- `ProjectNav.jsx` renders a static project heading, normalizes scene strings/objects, and calls `onSelectScene`.
- `Editor.jsx` wraps TipTap with StarterKit and converts plain text to paragraph HTML for editing.
- `AnalysisSidebar.jsx` renders Story Check controls and a basic report display.
- `api.js` wraps Axios calls to `/api`.

Project/scenes loading:

- `App.jsx` loads scenes and storyform context on mount using `fetchScenes()` and `fetchStoryformContext()`.
- The frontend assumes a single project via `PROJECT_ID = 'example'` in `api.js`.
- Selecting a scene loads `/api/projects/example/scenes/{sceneId}` and resets current analysis state.

Editor save behavior:

- `Editor.jsx` emits plain text through TipTap `getText({ blockSeparator: '\n\n' })`.
- `App.jsx` saves the current scene with `PUT /api/projects/example/scenes/{sceneId}`.
- Ctrl/Cmd+S is wired to save.
- There is a short `Saved!` status, but no dirty-state model, conflict detection, autosave, or save/reload verification.

Story Check button/request behavior:

- `AnalysisSidebar` disables the button when no scene is selected or analysis is running.
- `App.jsx` calls `runStoryCheck(selectedSceneId)` and stores the returned object in `analysisReport`.
- API errors are converted to an `error` field for raw display.

AnalysisSidebar rendering:

- Valid reports require a numeric `coherence_score`, no `error`, and a warnings list that does not include the exact string `Failed to parse LLM response`.
- It renders score, warnings, suggestions, and a raw JSON block.
- If the report is invalid, it renders the entire response as raw JSON.
- It does not yet render rich fields such as throughline alignment, theme drift, character consistency, schema errors, or insufficient evidence as first-class UI sections.

Hardcoded values:

- `PROJECT_ID = 'example'` in `frontend/src/api.js`.
- `ProjectNav` displays `Novel Draft` as the project title.
- Backend base URL is Vite-proxied via `/api`.

Frontend gaps:

- No project selection or project creation.
- No frontend OMI surface.
- No mode visibility for mock vs baseline Ollama.
- No rich Story Check diagnostics UI.
- No frontend tests.
- No explicit empty-scene Story Check handling beyond button state.
- No dirty-state protection before scene changes.

## 5. Project Storage Inventory

Current implemented project structure:

```text
projects/
  {project_name}/
    bible.json
    storyform.json
    scenes/
      {scene_id}.md
```

Current sample project files:

- `projects/example/bible.json`
- `projects/example/storyform.json`
- `projects/example/scenes/scene_001.md`

Known mismatch:

- `bible.json` contains Elena, The Stranger, Whispering Woods, and Elena's Village.
- `scene_001.md` is an Elena/Whispering Woods scene.
- `storyform.json` is Quest for the Ember Crown, centered on Mara Vell and Sir Calen Rook.
- This mismatch remains present and is a risk for MVP evaluation because Story Check receives an internally inconsistent project context.

Owner-approved truth vs candidate output boundaries:

- Current durable project truth is effectively whatever is saved in `bible.json`, `storyform.json`, and scene Markdown.
- There is no candidate-analysis artifact store.
- Story Check output is transient in the frontend state and is not persisted by the app.
- There is no owner approval workflow for promoting model output into durable truth.

Missing project model pieces:

- No `project.json`.
- No `owner_memory.json`.
- No `planning_notes`.
- No analysis artifact/candidate file model.
- No OMI item store.
- No explicit provenance/status fields for candidates or promotions.

## 6. Story Check Flow

End-to-end path:

1. User selects a scene in `ProjectNav`.
2. `App.jsx` loads scene content and storyform context.
3. User clicks `Run Story Check` in `AnalysisSidebar`.
4. `frontend/src/api.js` posts to `/api/projects/example/story-check/{sceneId}`.
5. `backend/main.py` calls `analysis_engine.run_story_check(project_name, scene_id)`.
6. `analysis_engine` loads storyform context, scene text, and bible JSON.
7. `analysis_engine` formats `backend/prompts/story_check.txt`.
8. `analysis_engine` posts to Ollama at `OLLAMA_CHAT_URL` using `OLLAMA_MODEL` default `qwen3:8b`.
9. `analysis_engine` parses `payload.message.content` as JSON.
10. `_normalize_story_check()` returns UI-compatible `coherence_score`, `warnings`, `suggestions`, and `diagnostics`.
11. The frontend renders score/warnings/suggestions and raw JSON.

Prompt behavior:

- The prompt instructs the model to return exactly one JSON object.
- It includes storyform context, bible summary, and scene text.
- It asks for all four throughlines, theme drift, character consistency, warnings, suggestions, and insufficient evidence.
- It explicitly says not to write, rewrite, continue, imitate, or improve story prose.
- Suggestions are required to be writer-focused questions, not prose instructions.

Parser behavior:

- Malformed JSON returns a safe fallback with score `0`, a factual warning, empty suggestions, parser diagnostics, and truncated raw content.
- Legacy small schema responses with score/warnings/suggestions still normalize.
- Rich Story Check responses are schema-checked against `training/schemas/story_check.schema.json` when `jsonschema` is installed and the schema file exists.
- Warning prefixes are normalized to one of the approved categories; unknown warnings receive `[Factual]`.
- Suggestions are limited to questions and filtered if they match a prose-generation request pattern.

Minimal schema currently supported:

- `coherence_score`
- `warnings`
- `suggestions`

Rich schema target:

- `task`
- `coherence_score`
- `throughline_alignment`
- `theme_drift`
- `character_consistency`
- `warnings`
- `suggestions`
- `insufficient_evidence`

Missing normalizer/schema validation:

- Story Check rich schema validation exists in the parser, but it is not enforced as a route contract.
- The frontend does not render rich diagnostics as structured sections.
- There is no generic runtime schema validation layer for all future analysis tasks.
- There is no mock fixture path for deterministic Story Check responses.

The qwen3 baseline path is configured in code, but this audit did not run Ollama or verify a local model response.

## 7. Runtime No-Prose Guardrail State

What exists now:

- Product docs, README, and Story Check prompt contain no-prose rules.
- `story_check.txt` tells the model not to write, rewrite, continue, imitate, or improve story prose.
- `_normalize_suggestions()` drops suggestions that are not questions or that match a prose-generation request regex.
- `training/schemas/out_of_scope_refusal.schema.json` defines a refusal output shape.

Current guardrail classification:

- Mostly prompt-only.
- Partial post-output filtering exists for suggestions only.
- No general runtime pre-model guard blocks prose-generation requests before a model call.
- No general post-model guard detects prose in warnings, diagnostics, raw model output, or future task responses.

Likely later insertion points:

- Before model call in `analysis_engine.run_story_check()` or a future request orchestration layer.
- After model output parsing and before returning data to frontend.
- At future OMI candidate generation request boundaries.
- As shared backend guardrail utilities covered by tests.

This task did not implement runtime guardrails.

## 8. OMI Architecture Readiness

OMI code state:

- No backend OMI routes were found.
- No `omi_manager.py` or equivalent storage manager was found.
- No frontend OMI components were found.
- No OMI API methods were found in `frontend/src/api.js`.
- OMI currently exists in planning docs only.

Current MVP OMI requirement:

- OMI is included in the MVP as bounded analysis/planning.
- It must be candidate-first and owner-controlled.
- It must not generate story prose, continue story text, rewrite, imitate, polish, or improve prose.
- It must not silently promote raw ideas, candidates, model output, or NotebookLM output into durable project truth.

Required OMI boundaries:

- `raw_idea`
- `candidates`
- `owner_decision`
- `destination`
- `provenance`
- `status`

Storage/API/UI questions to resolve before implementation:

- Where are OMI items stored relative to `project.json`, `bible.json`, `storyform.json`, scenes, and future planning notes?
- Are OMI candidates immutable snapshots, editable drafts, or both?
- What destinations are supported in MVP: planning notes, bible candidate, storyform context candidate, scene prompt context candidate, template starter candidate, discard?
- What status transitions are valid from draft/candidate/owner_review/approved/rejected/promoted/archived?
- What evidence/provenance is required for promotion?
- Does promotion create a candidate patch for owner review, or write directly after final confirmation?
- What route and UI names should avoid implying prose generation?

No prose generation and no silent promotion requirements:

- OMI must produce candidate planning material only.
- Owner approval, destination, provenance, and status are required before promotion.
- OMI must not mutate `bible.json`, `storyform.json`, scenes, planning notes, or future owner memory automatically.

## 9. NCP/Storyform State

Current loading/validation:

- `Storyform.from_file(project_name)` loads `projects/{project_name}/storyform.json`.
- `Storyform.validate_data()` validates data against a JSON schema extracted from the first JSON block in `docs/repo_knowledge.md`.
- `Storyform.from_questionnaire({})` ignores responses and returns a hardcoded Quest for the Ember Crown storyform.
- `to_prompt_context()` summarizes title, logline, players, dynamics, throughlines, storypoints, and storybeats into text for the model prompt.

Subset currently used by the app:

- App runtime uses prompt-context text, not a structured NCP object in the frontend.
- The prompt context emphasizes players, dynamics, all four throughlines, storypoints, and storybeats.
- The frontend displays the context as raw preformatted text.

Known overclaim risks:

- A schema-valid storyform can still be story-incompatible with the scene/bible, as shown by the Elena vs Ember Crown sample mismatch.
- Full Dramatica verifier parity is not implemented.
- The app cannot prove CIPS, dynamics, IC, or RS truth merely from a schema-valid storyform.
- `from_questionnaire()` is a placeholder, not an actual questionnaire mapper.

Separate NCP subset design needed:

- Define which NCP fields are required for MVP Story Check.
- Decide how unresolved/owner-deferred fields are represented.
- Decide how the frontend should show storyform context without implying all fields are owner-approved truth.
- Decide what evidence is required before IC/RS/CIPS/dynamics can be treated as positive truth.

## 10. Test Coverage Inventory

Tests found:

- `tests/test_analysis_engine.py`
- `tests/test_project_manager.py`
- `tests/test_storyform.py`
- `tests/test_validate_dataset.py`

Coverage by area:

- `test_analysis_engine.py`: rich Story Check parsing, legacy small schema normalization, malformed output fallback, schema error preservation, and dropping prose-like suggestions.
- `test_project_manager.py`: bible save/load, non-object bible rejection, scene save/load, scene listing, missing scenes directory behavior, and path component safety.
- `test_storyform.py`: hardcoded questionnaire placeholder validity, loading/validating project storyform files, invalid storyform rejection, and prompt-context summary content.
- `test_validate_dataset.py`: empty JSONL and invalid JSONL validation behavior.

Missing test areas:

- FastAPI route tests.
- Story Check route integration tests.
- Mock mode tests.
- Ollama baseline smoke test, if local Ollama is available.
- Runtime no-prose pre-call guard tests.
- Runtime post-output guard tests beyond suggestion filtering.
- Rich diagnostics frontend rendering tests.
- Scene dirty-state/save/reload frontend tests.
- OMI schema/lifecycle tests.
- OMI no-prose and no-silent-promotion tests.

Tests were not run during this audit. The audit is source inspection and command inventory only.

## 11. App MVP Gap List

Phase 1 project model/NCP/OMI design/sample alignment gaps:

- Define project file model: `project.json`, owner memory, candidate analysis artifacts, promotion state, and planning notes.
- Define NCP/storyform MVP subset.
- Define OMI schema/lifecycle and status/destination rules.
- Resolve sample project mismatch.
- Decide what project truth is owner-approved vs candidate-only.

Phase 2 backend guardrails/schema foundation gaps:

- Add runtime no-prose guardrails before model call and after model output.
- Define shared refusal response behavior.
- Formalize Story Check normalizer as route-level contract.
- Add schema validation approach for rich outputs and future OMI-relevant paths.
- Add insufficient-evidence handling as a first-class response path.
- Implement `ANALYSIS_MODE` routing.

Phase 3 mock/baseline Story Check gaps:

- Implement deterministic mock mode.
- Add Story Check route tests.
- Verify qwen3/Ollama baseline locally before claiming it works.
- Add baseline evaluation fixtures.
- Track malformed output and refusal behavior in fixture tests.

Phase 4 frontend diagnostics gaps:

- Render throughline alignment, theme drift, character consistency, schema errors, and insufficient evidence as structured UI.
- Show mock/baseline mode.
- Improve error and malformed-output display.
- Add scene dirty-state handling.
- Handle empty scene behavior deliberately.
- Add frontend tests.

Phase 5 OMI implementation gaps:

- No OMI storage.
- No OMI backend routes.
- No OMI frontend components.
- No owner decision/destination flow.
- No provenance/status display.
- No promotion guard.
- No tests for no-prose/no-silent-promotion behavior.

Phase 6 hardening gaps:

- Project navigation reliability.
- Save/reload regression tests.
- App smoke checklist.
- Documentation cleanup after implementation choices.
- Clean Git/Phase 0 publication state.

## 12. Recommended Next Tasks

1. App-2 Project file model.
2. App-3 NCP compatibility subset.
3. OMI-001 OMI MVP schema and lifecycle.
4. Sample project alignment decision.
5. Phase 2 backend guardrails/schema foundation.

## 13. Open Questions for Owner

- Should the MVP sample project be owner-created or public-domain-derived?
- Should OMI candidates be editable by the owner before approval, or immutable snapshots plus owner notes?
- Which OMI destinations are required in MVP: planning notes, bible candidate, storyform context candidate, scene prompt context candidate, template starter candidate, discard?
- Should promoted OMI material write directly after final confirmation, or create an intermediate owner-review patch/artifact?

## 14. Verification Appendix

Commands run:

```bash
pwd
git status --short --branch
git log --oneline --max-count=5
git remote -v
find backend -maxdepth 3 -type f | sort
find frontend -maxdepth 4 -type f | sort
find tests -maxdepth 3 -type f | sort
find training/schemas -maxdepth 2 -type f | sort
```

Summarized outputs:

- `pwd`: `/home/tjrpirateking/projects/WritingAssistantApplication`.
- `git status --short --branch`: branch `main` with uncommitted documentation changes.
- `git log --oneline --max-count=5`: `25ef64d chore: initialize safe project baseline`.
- `git remote -v`: `origin https://github.com/telesjr90/writingassistant` for fetch and push.
- `find backend`: source files plus ignored `__pycache__` files were present.
- `find frontend`: source files were present; the required command also listed ignored `frontend/node_modules` and `frontend/dist` content.
- `find tests`: four test files plus ignored `__pycache__` files were present.
- `find training/schemas`: Story Check, throughline classification, writer questions, out-of-scope refusal, and SFT record schemas were present.

Additional read-only inspection commands were used to read backend modules, frontend components, sample project files, schemas, tests, prompts, and roadmap docs. No runtime tests, Ollama calls, server starts, commits, pushes, or GitHub operations were performed.
