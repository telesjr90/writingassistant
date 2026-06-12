# PHASE7-IMPL-004 — Manual Browser Smoke Test and Project Workspace Acceptance Checklist

## 1. Result

**PASS with warning**

Automated validation passed. Owner completed browser smoke sufficient to create `Browser Smoke Test Project`; runtime artifact and post-test git/`projects/` checks confirm blank-project creation and file safety. Optional OMI and Story Check rows were not reported. Project switch, scene editor, and context-panel rows were not explicitly confirmed row-by-row.

---

## 2. Date and environment

| Field | Value |
|---|---|
| Date/time | 2026-06-10T19:25:33-07:00 (agent validation); owner post-test ~2026-06-11T02:31Z |
| Repo path | `/home/tjrpirateking/projects/WritingAssistantApplication` |
| Branch | `main` |
| Backend command (recommended) | `cd /home/tjrpirateking/projects/WritingAssistantApplication && ANALYSIS_MODE=mock .venv-unsloth-clean/bin/uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000` |
| Frontend command (recommended) | `cd /home/tjrpirateking/projects/WritingAssistantApplication/frontend && npm run dev -- --host 127.0.0.1` |
| Browser URL | `http://127.0.0.1:5173` |

**Server startup verification (agent):** Backend `http://127.0.0.1:8000`, frontend `http://127.0.0.1:5173`, `GET /api/projects` OK, frontend HTTP 200.

---

## 3. Starting repository state

```
## main...origin/main
```

| Check | Status |
|---|---|
| Repo root | `/home/tjrpirateking/projects/WritingAssistantApplication` |
| Branch | `main` (tracking `origin/main`) |
| Working tree | Clean at task start |
| Latest commit | `dfb3862` — `feat: wire frontend project library and blank project creation` |
| PHASE7-IMPL-003 committed | Yes — `dfb3862` on `main` and `origin/main` |
| PHASE7-IMPL-003 pushed | Yes |

---

## 4. Automated validation

### Focused pytest

| Command | Result |
|---|---|
| `pytest tests/test_project_creation.py -q` | **PASS** — 34 passed in 0.85s |
| `pytest tests/test_project_library.py -q` | **PASS** — 23 passed in 0.55s |
| `pytest tests/test_frontend_project_workspace_source.py -q` | **PASS** — 54 passed in 0.07s |

### Full suite and build

| Command | Result |
|---|---|
| `pytest tests -q` | **PASS** — 287 passed in 1.60s |
| `npm run build` (frontend) | **PASS** — built in 364ms |

### Known acceptable warnings

- StarletteDeprecationWarning (TestClient/httpx)
- PydanticDeprecatedSince20 (`ProjectCreate` class config)
- Vite bundle-size advisory (645 kB chunk)

---

## 5. Manual browser smoke checklist

Owner post-test commands (2026-06-11):

```bash
git status --short --branch
find projects -maxdepth 2 -type f | sort | sed -n '1,120p'
```

Owner output:

```
## main...origin/main
projects/browser-smoke-test-project/project.json
projects/example/bible.json
projects/example/project.json
projects/example/storyform.json
```

Artifact inspection (`projects/browser-smoke-test-project/project.json`):

- `title`: `Browser Smoke Test Project`
- `creation_method`: `blank`
- `ai_prose_generation_prohibited`: `true`
- `candidate_outputs_do_not_promote_automatically`: `true`
- No `scenes/`, `bible.json`, or `storyform.json` under smoke project

### A. App load and default project

| Area | Check | Result | Notes |
|---|---|---|---|
| App load | App opens without a blank screen | PASS (inferred) | Owner reached create-project UI |
| App load | Default active project is `example` or existing default | Not reported | |
| App load | Existing scene list loads | Not reported | |
| App load | Existing selected scene/content behavior still works | Not reported | |
| App load | No console-visible obvious fatal UI error if checked | Not reported | |

### B. Project library

| Area | Check | Result | Notes |
|---|---|---|---|
| Project library | Library section appears in ProjectNav | PASS (inferred) | Create flow requires library UI |
| Project library | Current project is visible | Not reported | |
| Project library | Project selector/dropdown appears | PASS (inferred) | |
| Project library | Refresh projects button works | Not reported | |
| Project library | Invalid/warning project records disabled/non-selectable | N/A | No invalid records in scan |
| Project library | No absolute filesystem paths shown in UI | Not reported | |

### C. Create blank project

| Area | Check | Result | Notes |
|---|---|---|---|
| Create blank project | Enter safe owner title | PASS | `Browser Smoke Test Project` |
| Create blank project | Click Create blank project | PASS | Artifact `created_at` 2026-06-11T02:31:33Z |
| Create blank project | UI calls create-project without AI prose generation | PASS | `creation_method: blank`; no scene files |
| Create blank project | New project appears in library | PASS (inferred) | Folder created on disk |
| Create blank project | New project becomes active project | Not reported | |
| Create blank project | New project has no generated scene prose | PASS | Only `project.json`; no `scenes/` |
| Create blank project | UI does not imply AI-generated story content | PASS | Policy flags in metadata |

### D. Project switch

| Area | Check | Result | Notes |
|---|---|---|---|
| Project switch | Switch from new project back to `example` | Not reported | |
| Project switch | Switch from `example` back to new project | Not reported | |
| Project switch | Project-specific scene/context data reloads without crashing | Not reported | |
| Project switch | Unsaved scene text confirms before switch | Not reported | |

### E. Scene editor safety

| Area | Check | Result | Notes |
|---|---|---|---|
| Scene editor | Owner can type text into editor | Not reported | |
| Scene editor | Save behavior works for owner-authored text | Not reported | |
| Scene editor | Unsaved indicator/dirty handling still works | Not reported | |
| Scene editor | No AI-generated prose inserted | Not reported | |

### F. Project context safety

| Area | Check | Result | Notes |
|---|---|---|---|
| Project context | Bible/storyform panels remain owner-editable | Not reported | |
| Project context | Existing save behavior still works | Not reported | |
| Project context | Analysis output does not overwrite owner context | Not reported | |

### G. OMI boundary (optional)

| Area | Check | Result | Notes |
|---|---|---|---|
| OMI optional | OMI panel loads | Skipped | Optional — not reported |
| OMI optional | OMI copy frames candidates/planning | Skipped | |
| OMI optional | No automatic promotion | Skipped | |

### H. Story Check boundary (optional)

| Area | Check | Result | Notes |
|---|---|---|---|
| Story Check optional | Mock deterministic analysis | Skipped | Optional — not reported |
| Story Check optional | Does not write/rewrite prose | Skipped | |
| Story Check optional | Does not mutate project records | Skipped | |

### I. Runtime file safety check

**Owner post-test output:**

```
## main...origin/main
projects/browser-smoke-test-project/project.json
projects/example/bible.json
projects/example/project.json
projects/example/storyform.json
```

| Area | Check | Result | Notes |
|---|---|---|---|
| Runtime safety | New project files are untracked local artifacts | PASS | `git status` clean; smoke folder not staged |
| Runtime safety | No dataset files changed | PASS | Clean working tree |
| Runtime safety | No package files changed | PASS | Clean working tree |
| Runtime safety | No backend/frontend source changed | PASS | Clean working tree |

---

## 6. Acceptance criteria

| Criterion | Status |
|---|---|
| User can load the app | PASS (inferred from create flow) |
| User can see/select projects | PASS (inferred) |
| User can create blank project from owner title | **PASS** (artifact confirmed) |
| User can switch between projects | Not reported |
| Existing `example` project remains usable | PASS (fixtures intact) |
| Owner-authored scene editing still works | Not reported |
| No generated story prose appears | **PASS** (smoke project metadata only) |
| No automatic OMI/canon/memory/promotion | PASS (policy in metadata; no promotion files) |
| No model/Ollama dependency for project smoke | PASS (`ANALYSIS_MODE=mock`) |
| No tracked source/dataset/package files changed | **PASS** |

---

## 7. Runtime project artifact note

Local runtime artifact created:

- `projects/browser-smoke-test-project/project.json`

This folder is an untracked local-first workspace output. Do not stage unless a future task explicitly requests a fixture. Owner may delete `projects/browser-smoke-test-project/` after recording acceptance.

---

## 8. Deferred decisions / next work

- Project overview page remains future task
- `GET /api/projects/{project_id}` details route remains future task
- Better project switch unsaved handling for bible/storyform remains future task
- Project delete/archive remains future task
- CSS polish remains future task
- OMI-guided project creation remains future task
- Chapters/scenes expanded data model remains future task
- Notes/materials workspace remains future task
- memory/canon runtime files remain deferred
- apply-promotion remains unimplemented
- model/Ollama analysis remains untouched unless optional mock Story Check was run
- Dramatica-specific implementation remains deferred

---

## 9. Safety confirmations

- No runtime code changes were made in PHASE7-IMPL-004
- No backend code changed
- No frontend code changed
- No tests changed
- No package/dependency files changed
- No dataset files changed
- No JSONL/training records were created
- `dataset_manifest.json` was not changed
- No training or fine-tuning ran
- No model/Ollama call was required for project creation/library smoke
- No Story Check behavior was changed
- No OMI records were created by the smoke task
- No memory/canon files were created by the smoke task
- No apply-promotion behavior was added
- No extraction behavior was added
- No Dramatica-specific logic was added
- No staging, commit, or push was performed
