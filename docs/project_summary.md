# Project Summary

## 1. Purpose and Product Direction

This project is a local, writer-controlled fiction planning and analysis tool inspired by Subtxt and informed by Dramatica-style story analysis. The intended product shape is a single writing environment where the writer remains the author of all durable story content, while AI acts as an analyst, diagnostic reader, and question-asking planning assistant.

The structural backbone is the Narrative Context Protocol (NCP), copied into `docs/repo_knowledge.md` from `open_source_repos/narrative-context-protocol/schema/ncp-schema.json`. In the current implementation, each project has a `storyform.json` file that is validated against that schema and summarized into prompt context for analysis. The NCP model treats `story.narratives[]` as complete Dramatica-style argument structures with subtext and storytelling layers: perspectives, players, dynamics, story points, story beats, overviews, and moments.

The current codebase implements the minimal writing and story-check loop:

- Load a local project and list scene Markdown files.
- Edit a selected scene in a TipTap-powered editor.
- Save the scene back to local disk.
- Run a Dramatica-aware story check against the scene, story bible, and NCP storyform.
- Display coherence score, warnings, suggestions, and raw JSON analysis.

The desired OMI direction is writer-controlled planning: the writer supplies ideas, chooses the kind of planning artifact wanted, reviews/edit AI-produced analysis or questions, then explicitly promotes selected material into durable project memory. Nothing should become durable story memory without writer action. In the current repository this OMI layer is not yet implemented.

## 2. Overall Architecture

The application is split into a React single-page frontend and a FastAPI backend.

- Frontend: `frontend/src/App.jsx` is a Vite React app with a three-column writing workspace: project navigation, central editor, and analysis sidebar.
- Backend: `backend/main.py` exposes REST endpoints under `/api`.
- Storage: local project files under `projects/<project_name>/`; there is no database in the current implementation.
- Analysis: `backend/analysis_engine.py` calls a local Ollama chat endpoint. The current default model is `qwen3:8b`, configured by environment variable.
- Story structure: `projects/<name>/storyform.json` is the source of truth for the storyform and is validated against the NCP schema.

Request flow:

1. The React app calls `frontend/src/api.js`.
2. Vite proxies `/api` requests to `http://localhost:8000`.
3. FastAPI routes in `backend/main.py` call `project_manager`, `storyform`, and `analysis_engine`.
4. Local files are loaded from `projects/<name>/`.
5. Story checks are sent to Ollama through `requests.post(...)`.
6. The frontend renders the returned JSON analysis.

The current architecture is intentionally local-first. Docker Desktop is available in the environment but not used by the repository. Hugging Face models are planned for fine-tuning a future analyst model, but no fine-tuning pipeline is present in the codebase yet.

## 3. Backend Details

### `backend/main.py`

`backend/main.py` defines the FastAPI app and all current HTTP routes. It enables permissive CORS for development and uses a small Pydantic model, `SceneUpdate`, for scene save payloads.

Current API endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/projects/{project_name}/scenes` | Returns available scene IDs from `projects/<project_name>/scenes/*.md`. |
| `GET` | `/api/projects/{project_name}/scenes/{scene_id}` | Loads one scene and returns `{ "content": "..." }`. Missing or empty scenes currently return 404. |
| `PUT` | `/api/projects/{project_name}/scenes/{scene_id}` | Saves scene text from `{ "content": "..." }` to the local Markdown scene file. |
| `GET` | `/api/projects/{project_name}/bible` | Loads and returns `projects/<project_name>/bible.json`. |
| `POST` | `/api/projects/{project_name}/story-check/{scene_id}` | Runs the local LLM story check for one scene. |
| `GET` | `/api/projects/{project_name}/storyform-context` | Returns the prompt-ready storyform summary generated from `storyform.json`. |

There are no OMI endpoints in the current backend.

### `backend/storyform.py`

`backend/storyform.py` owns NCP schema loading, storyform validation, and conversion of the structured storyform into prompt context.

Important responsibilities:

- Defines `Storyform`, a frozen dataclass around the loaded storyform dictionary.
- Reads the NCP JSON schema from the first JSON code block in `docs/repo_knowledge.md`.
- Validates storyform data with `jsonschema.Draft7Validator`.
- Loads project storyforms from `projects/<project_name>/storyform.json`.
- Provides `from_questionnaire(responses)` as an MVP placeholder that ignores responses and returns a hardcoded valid quest storyform.
- Provides `to_prompt_context()`, which summarizes the story title, logline, players, dynamics, throughlines, story points, story beats, and storytelling overviews.

The hardcoded MVP storyform is `Quest for the Ember Crown`, centered on Mara Vell and Sir Calen Rook. It includes Objective Story, Main Character, Influence Character, and Relationship Story material. This is useful for testing the NCP pipeline, but it currently does not match the sample Elena scene.

### `backend/project_manager.py`

`backend/project_manager.py` provides file-based project storage.

Implemented functions:

- `load_bible(project_name: str) -> dict`
- `save_bible(project_name: str, data: dict) -> None`
- `load_scene(project_name: str, scene_id: str) -> str`
- `save_scene(project_name: str, scene_id: str, content: str) -> None`
- `list_scenes(project_name: str) -> list[str]`

The module resolves paths under `projects/` and protects against path traversal by requiring `project_name` and `scene_id` to be single path components. It creates parent directories when saving bible or scene data.

### `backend/analysis_engine.py`

`backend/analysis_engine.py` performs the current Story Check.

Workflow:

1. Loads `projects/<project_name>/storyform.json` through `Storyform.from_file(...)`.
2. Converts it to prompt text with `to_prompt_context()`.
3. Loads the selected scene from `projects/<project_name>/scenes/<scene_id>.md`.
4. Loads and JSON-formats the project bible from `projects/<project_name>/bible.json`.
5. Reads the prompt template from `backend/prompts/story_check.txt`.
6. Sends a non-streaming chat request to Ollama.
7. Parses the returned assistant message content as JSON.

Ollama configuration:

- `OLLAMA_CHAT_URL` defaults to `http://localhost:11434/api/chat`.
- `OLLAMA_MODEL` defaults to `qwen3:8b`.
- `OLLAMA_TIMEOUT_SECONDS` defaults to `300`.
- Request uses the Ollama chat API with:
  - `format: "json"`
  - `think: false`
  - `stream: false`
  - `temperature: 0`
  - `num_predict: 512`

If the LLM response cannot be parsed as a JSON object, `_parse_story_check_response(...)` returns:

```json
{
  "coherence_score": 0,
  "warnings": ["Failed to parse LLM response"],
  "suggestions": []
}
```

The current analysis engine catches broad exceptions and returns `{ "error": "..." }`. Because `backend/main.py` also catches exceptions around story check, analysis failures are returned as JSON instead of structured HTTP error responses.

### `backend/prompts/story_check.txt`

The story check prompt instructs the model to act as a senior fiction editor and Dramatica-aware story analyst. It asks the model to audit:

- Dramatica coherence across Overall Story, Main Character, Influence Character, and Relationship throughlines.
- Theme drift.
- Character consistency.

It requires exactly one JSON object with:

- `coherence_score`
- `warnings`
- `suggestions`

### `backend/prompts/extract_elements.txt`

This file exists but is currently empty.

### `backend/omi_manager.py`

The requested architecture includes an `omi_manager.py` module, but this file is not present in the current repository. Based on the product direction, this module should eventually own OMI item storage, status changes, editing, and promotion into durable project files such as `bible.json`, `planning_notes.md`, new scene files, or future memory banks.

## 4. NCP Storyform as Structural Backbone

The NCP storyform is the main structural contract between the writer's plan and the analysis engine.

Current usage:

- `projects/example/storyform.json` stores the project's structural storyform.
- `backend/storyform.py` validates it against the NCP schema embedded in `docs/repo_knowledge.md`.
- `Storyform.to_prompt_context()` turns structured data into a compact text briefing for the LLM.
- `backend/analysis_engine.py` includes that briefing in every Story Check prompt.

The current prompt context includes:

- Story title and logline.
- Narrative title and status.
- Players and roles.
- Dynamics such as Main Character Resolve, Story Outcome, and Story Judgment.
- Throughline summaries grouped by Objective Story, Main Character, Influence Character, and Relationship Story.
- Storybeats sorted by sequence.
- Storytelling overviews.

This means the LLM is not asked to analyze a scene in isolation. It is asked to compare the scene against the project's declared structure. The current implementation does this through prompt text rather than through a deeper symbolic rules engine.

## 5. Frontend Details

### `frontend/src/main.jsx`

This is the React entrypoint. It imports `App.jsx` and `styles.css`, then mounts the app into `#root` with `React.StrictMode`.

### `frontend/src/App.jsx`

`App.jsx` owns the current application state and main layout.

Important state:

- `scenes`
- `selectedSceneId`
- `sceneContent`
- `storyformContext`
- `analysisReport`
- loading and error flags for scenes, scene content, saving, and analysis

Important data flow:

1. On load, `App.jsx` fetches scene IDs and storyform context in parallel.
2. Selecting a scene fetches the scene content and clears prior analysis.
3. Editing updates `sceneContent`.
4. Save writes `sceneContent` through the API. `Ctrl+S` and `Cmd+S` also save.
5. Running Story Check posts to the backend and stores the JSON report in `analysisReport`.

The current UI is a single Write view. It does not include routing, tabs, an OMI view, or project switching.

### `frontend/src/components/ProjectNav.jsx`

`ProjectNav.jsx` renders the left scene list. It accepts scenes as strings or objects, normalizes them, and displays each as a button. The active scene receives an `is-active` class.

### `frontend/src/components/Editor.jsx`

`Editor.jsx` wraps TipTap with `StarterKit`.

Behavior:

- Converts stored text into simple HTML paragraphs for TipTap.
- Calls `onChange(...)` with `editor.getText({ blockSeparator: "\n\n" })`.
- Provides Bold, Italic, and Save buttons.
- Updates editor content when a new scene is selected.
- Toggles editability when no scene is selected or a scene is loading.

Important limitation: scene files are stored as `.md`, but the current editor path treats the content mostly as plain text. TipTap marks such as bold and italic are not serialized back to Markdown; saving uses plain text from `getText(...)`.

### `frontend/src/components/AnalysisSidebar.jsx`

`AnalysisSidebar.jsx` renders the right analysis panel.

Behavior:

- Shows a disabled or enabled Story Check button depending on selected scene and loading state.
- Validates reports by checking for object shape, no `error`, no parse-failure warning, and a numeric `coherence_score`.
- Displays coherence score with good/warning/danger color classes.
- Displays warnings, suggestions, and raw JSON.
- Falls back to raw response display for errors or malformed reports.

### `frontend/src/components/OmiPanel.jsx`

The requested architecture includes `OmiPanel.jsx`, but this file is not present in the current repository. The current frontend has no OMI panel, no OMI state, and no OMI API service methods.

### `frontend/src/api.js`

`api.js` creates an Axios client with `baseURL: "/api"` and exports:

- `fetchScenes()`
- `fetchScene(sceneId)`
- `saveScene(sceneId, content)`
- `runStoryCheck(sceneId)`
- `fetchStoryformContext()`

The project ID is currently hardcoded:

```js
const PROJECT_ID = 'example';
```

There are no functions for OMI item generation, listing, editing, promotion, or discard.

### Vite Proxy

`frontend/vite.config.js` configures the React plugin and proxies `/api` to `http://localhost:8000`.

## 6. Project File Structure and Storage

Filtered source structure:

```text
codex.yml
docs/
  plan.md
  repo_knowledge.md
  project_summary.md
backend/
  __init__.py
  main.py
  storyform.py
  project_manager.py
  analysis_engine.py
  run.ps1
  prompts/
    story_check.txt
    extract_elements.txt
frontend/
  index.html
  public/
    index.html
  package.json
  package-lock.json
  vite.config.js
  src/
    main.jsx
    App.jsx
    api.js
    styles.css
    components/
      ProjectNav.jsx
      Editor.jsx
      AnalysisSidebar.jsx
projects/
  example/
    bible.json
    storyform.json
    scenes/
      scene_001.md
tests/
  test_project_manager.py
  test_storyform.py
```

Project storage convention:

```text
projects/<project_name>/
  bible.json
  storyform.json
  scenes/
    <scene_id>.md
```

The requested long-term storage shape also includes:

```text
projects/<project_name>/
  omi_items.json
  planning_notes.md
```

Those files do not exist in the current `projects/example/` project and are not read or written by current backend code.

Current sample project:

- `projects/example/storyform.json`: NCP storyform for `Quest for the Ember Crown`, with Mara Vell and Sir Calen Rook.
- `projects/example/bible.json`: sample bible for Elena, The Stranger, Whispering Woods, and Elena's Village.
- `projects/example/scenes/scene_001.md`: sample Elena scene about a wounded stranger and the choice between reaching the watchtower or helping him.

The sample bible and scene do not match the Ember Crown storyform, which is the most visible current data mismatch.

## 7. Agent Configuration

`codex.yml` defines a multi-agent project setup:

| Agent | Responsibility |
| --- | --- |
| `repo_retriever` | Clones open-source repos and extracts key schemas, prompts, and reference files. |
| `storyform_agent` | Implements the NCP schema and storyform handler. |
| `project_agent` | Manages local project folders and files. |
| `editor_ui_agent` | Builds the React frontend, editor, and analysis sidebar. |
| `analysis_agent` | Builds the analysis engine and prompts. |
| `orchestrator` | Coordinates tasks, sets up FastAPI, wires frontend/backend, and creates sample project data. |

The current request was executed as the orchestrator role, which is appropriate because this summary crosses backend, frontend, storage, and roadmap concerns.

## 8. Current Feature Set

### Implemented Write View

Implemented in `frontend/src/App.jsx`, `ProjectNav.jsx`, `Editor.jsx`, `AnalysisSidebar.jsx`, and `frontend/src/api.js`.

Current capabilities:

- Lists scenes from `projects/example/scenes/*.md`.
- Loads a selected scene into the editor.
- Edits scene text in TipTap.
- Saves scene text back to local disk.
- Supports keyboard save with `Ctrl+S` or `Cmd+S`.
- Shows storyform prompt context above the editor.
- Runs Story Check against the selected scene.
- Displays coherence score, warnings, suggestions, and raw JSON.

### Implemented Story Check

Implemented in `backend/analysis_engine.py` and `backend/prompts/story_check.txt`.

Current capabilities:

- Combines storyform context, bible summary, and current scene text.
- Sends the analysis prompt to local Ollama.
- Requests strict JSON output.
- Returns a numeric coherence score, warnings, and suggestions when parsing succeeds.

### Planned OMI View

The requested OMI feature set is not implemented yet, but the intended behavior is clear:

- Accept a writer-provided idea.
- Let the writer choose an output type such as character seed, outline prompt, scene question, thematic diagnostic, or planning note.
- Generate planning artifacts that ask questions, analyze fit, or structure options without writing durable story prose on behalf of the writer.
- Let the writer review and edit generated items.
- Promote selected items into scene drafts, `bible.json`, `planning_notes.md`, or future memory banks.
- Discard unwanted items.

The important product rule is manual control: AI output should not become durable story memory unless the writer explicitly promotes it.

### Manual Control

The implemented code already follows this rule for current features:

- Story Check is read-only and returns analysis.
- Scene content changes become durable only when the writer saves.
- There is no automatic mutation of `bible.json`, `storyform.json`, or scene files from the analysis engine.

The planned OMI layer should preserve the same rule with explicit review, edit, promote, and discard actions.

## 9. Known Rough Edges

- OMI is not implemented: no `backend/omi_manager.py`, no `frontend/src/components/OmiPanel.jsx`, no OMI endpoints, no `omi_items.json`, and no `planning_notes.md`.
- The sample storyform is a hardcoded Ember Crown quest, while the current bible and scene are about Elena in the Whispering Woods.
- `Storyform.from_questionnaire(...)` ignores questionnaire responses and returns the hardcoded quest storyform.
- The frontend project ID is hardcoded to `example`.
- The editor uses `.md` files but saves plain text from TipTap, so Markdown formatting is not fully preserved.
- Empty scene files are treated as 404 by `GET /api/projects/{project_name}/scenes/{scene_id}`.
- Story Check is single-scene only; it does not yet analyze multi-scene progression, continuity, or scene order.
- There is no NovelClaw-style memory bank in the active code, though `docs/repo_knowledge.md` summarizes memory-bank concepts such as `session_profile`, `task_briefs`, `story_premise`, `style_guide`, `chapter_briefs`, `entity_state`, `world_state`, `continuity_facts`, `revision_notes`, and `working_set`.
- `backend/prompts/extract_elements.txt` is empty.
- `backend/run.ps1` installs backend dependencies every time it runs.
- There is no explicit Ollama health check before a story check request.
- Analysis errors are returned as JSON objects rather than normalized HTTP errors.
- There are backend unit tests for `storyform.py` and `project_manager.py`, but no tests for FastAPI routes, `analysis_engine.py`, or frontend behavior.
- Docker Desktop is not used by the repository.
- Hugging Face fine-tuning is planned but not implemented.

## 10. Immediate Next Steps

1. Align the sample data.
   - Either rewrite `projects/example/storyform.json` to match Elena, the Stranger, Whispering Woods, and the watchtower premise, or replace the sample scene and bible with Mara/Calen Ember Crown material.

2. Implement the OMI backend.
   - Add `backend/omi_manager.py`.
   - Add `projects/<name>/omi_items.json` and `planning_notes.md`.
   - Define an OMI item schema with fields such as `id`, `type`, `source_idea`, `content`, `status`, `created_at`, `updated_at`, and `promotion_target`.
   - Add endpoints for generate, list, update, promote, and discard.

3. Implement the OMI frontend.
   - Add `frontend/src/components/OmiPanel.jsx`.
   - Add a Write/OMI view switch in `App.jsx`.
   - Extend `frontend/src/api.js` with OMI endpoints.
   - Add explicit review, edit, promote, and discard controls.

4. Deepen Story Check.
   - Add route and engine tests with mocked Ollama responses.
   - Include neighboring scene context and project-level continuity.
   - Add structured checks for missing throughline representation, signpost coverage, and theme drift.

5. Add memory-bank support.
   - Start with local JSON memory banks before vector storage.
   - Keep manual promotion as the gate for durable memory.
   - Model the bank categories after the NovelClaw summary in `docs/repo_knowledge.md`.

6. Prepare model replacement.
   - Keep the Ollama API boundary stable.
   - Add configuration for swapping `qwen3:8b` with a fine-tuned local analyst model.
   - Build a Hugging Face fine-tuning and evaluation path separately from the app runtime.

7. Improve project ergonomics.
   - Add project listing and creation.
   - Remove the hardcoded `PROJECT_ID`.
   - Add bible editing and safe storyform update flows.

## 11. Technologies

Current repository technologies:

- Python
- FastAPI
- Pydantic
- jsonschema
- requests
- pytest
- React
- TipTap
- Vite
- Axios
- Ollama
- PowerShell scripts
- Node.js and npm

Available or planned technologies:

- Docker Desktop: available but not yet used.
- Hugging Face models: planned for future fine-tuning of a dedicated story analyst model.
- Fine-tuned local analyst model: planned replacement for the current default `qwen3:8b` Ollama model.

## 12. Accuracy Notes

This summary reflects the current source files in the repository as inspected on 2026-05-25. It intentionally separates implemented behavior from requested or planned OMI behavior because several requested files and flows are not present in the current codebase.
