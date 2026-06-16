# PHASE7-IMPL-010 Browser / Manual Smoke Checklist

## 1. Task Identity

| Field | Value |
| --- | --- |
| Parent task | `PHASE7-IMPL-010` — Workspace Validation / Browser and Manual Smoke |
| Child task (preparation) | `PHASE7-IMPL-010-T003` — Browser smoke checklist preparation |
| Purpose | Checklist preparation only; no browser execution in T003 |
| Execution deferred to | `PHASE7-IMPL-010-T004` — Browser/manual smoke execution |
| Checklist artifact | This file |
| Validation scope | Completed Phase 7 workspace foundation (`PHASE7-IMPL-004` through `PHASE7-IMPL-009`) plus project creation/selection/switching from `PHASE7-IMPL-001` through `PHASE7-IMPL-003` |

## 2. Preconditions for T004

Before starting browser/manual smoke execution, confirm all of the following:

- [x] `PHASE7-IMPL-010-T001` — inventory and child-task plan — **complete**
- [x] `PHASE7-IMPL-010-T002` — automated regression validation pass — **complete**
- [ ] Automated regression suite passing (frontend source-contract tests, project manager, scene routes, note/material routes, OMI boundary tests)
- [ ] No unexpected runtime code, test, package, or project-file changes since T002
- [ ] Owner is ready to run the app locally (backend + frontend dev servers)
- [ ] Smoke execution is **observational only** unless a later repair task (`PHASE7-IMPL-010-T005`) explicitly authorizes a tiny safe fix
- [ ] Owner understands standard refusal boundary: the app is analysis-only; no generated story prose controls should appear during smoke

## 3. Local Run Instructions (T004 Placeholders)

**Do not run these commands during T003.** T004 fills in the actual values below before execution.

| Item | T004 value (fill in at execution time) |
| --- | --- |
| Backend server command | `ANALYSIS_MODE=mock .venv-unsloth-clean/bin/python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000` |
| Frontend dev server command | `cd frontend && npm run dev` |
| Expected backend localhost URL | `http://localhost:8000` |
| Expected frontend localhost URL | `http://localhost:5173` |
| Browser used | Playwright Chromium headless attempted; **failed** (`libnspr4.so` missing). Cursor browser MCP unavailable. API + server-log + frontend-source fallback used for remaining evidence. |
| Shutdown procedure | Stop background uvicorn and Vite dev processes (SIGTERM on PIDs started for T004). |
| Backend terminal errors observed | None fatal. Uvicorn startup complete; read-only `/api/projects` and project list/load routes returned 200 during smoke. No Story Check/analysis/Ollama routes observed. |
| Frontend terminal errors observed | `npm warn Unknown env config "devdir"` (non-fatal). Vite ready on port 5173. |

Recommended starting context (not executed in T003):

- Use mock analysis mode unless an explicitly allowed analysis path outside this checklist is being tested separately.
- Keep Ollama/model calls out of scope for routine smoke flows.

## 4. Browser Smoke Flows

Execute flows in order unless a stop condition halts the run. Record result and evidence for each flow in Section 6.

---

### Flow A — App loads and project selector/library appears

| Field | Detail |
| --- | --- |
| **Flow ID** | `A` |
| **Flow name** | App loads and project selector/library appears |
| **Steps** | 1. Start backend and frontend per Section 3.<br>2. Open the frontend localhost URL in the browser.<br>3. Observe initial render without interacting with analysis features.<br>4. Locate the project selector or project library UI.<br>5. Confirm existing projects are listed (if any exist in local `projects/`).<br>6. Watch backend/frontend terminals and browser console during load. |
| **Expected result** | App opens without fatal blank screen; project selector/library is visible or reachable; existing projects are listed when present; **no model call is triggered** on load; **no generated prose UI** appears. |
| **Result** | `[x] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | Backend and frontend servers started in mock mode. Frontend HTTP 200; backend `GET /api/projects` listed 6 projects including `example`. Backend access log shows read-only project/scene/note/material/bible/storyform/OMI loads with no analysis endpoints. Interactive browser UI render blocked (Playwright `libnspr4.so` missing; browser MCP unavailable). |
| **Stop condition** | Fatal load failure, blank screen with no recoverable UI, or unexpected model/Ollama activity on load → **stop T004** and record blocker. |

---

### Flow B — Create blank project

| Field | Detail |
| --- | --- |
| **Flow ID** | `B` |
| **Flow name** | Create blank project |
| **Steps** | 1. From project selector/library, start blank project creation.<br>2. Enter an owner-authored title (e.g. `smoke-blank-<timestamp>`).<br>3. Confirm/create using the existing create-project path.<br>4. Observe whether the project opens or appears in the library.<br>5. Inspect project contents: scenes, notes, materials, OMI records, memory/canon files (via UI only; no manual filesystem edits during smoke). |
| **Expected result** | Owner can create a blank project from owner-entered title; project opens or appears in library; blank project does **not** contain generated story content; **no scenes, notes, materials, OMI, or memory/canon records are silently created** except minimal safe metadata already documented; project ID/path behavior appears safe. |
| **Result** | `[x] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | `POST /api/projects` with title `smoke-blank-1781586974` returned 200; project_id `smoke-blank-1781586974` appeared in project list (count 6). Follow-up reads: scenes=0, notes=0, materials=0, OMI candidates=0. No generated content or hidden pre-confirmation writes observed. |
| **Stop condition** | Hidden pre-confirmation writes, generated content in new project, or unsafe path/ID behavior → **stop T004** and record blocker. |

---

### Flow C — Select existing example project

| Field | Detail |
| --- | --- |
| **Flow ID** | `C` |
| **Flow name** | Select existing example project |
| **Steps** | 1. From project selector/library, select a known existing example project with scenes.<br>2. Observe project title and status display.<br>3. Open or observe the scene list.<br>4. Select one scene and note the body text shown before any edit.<br>5. Reload or re-select the same scene without saving. |
| **Expected result** | Example project opens; title/status visible; existing scene list loads; **owner-authored body text is not modified on load**. |
| **Result** | `[x] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | `GET /api/projects/example/scenes/scene_001` returned 1972-char owner-authored body. Repeat read matched exactly (no load-time mutation). Example title from list: `The Princess and the Pea`. |
| **Stop condition** | Scene body changed on load/reload without owner save → **stop T004** and record blocker. |

---

### Flow D — Switch projects

| Field | Detail |
| --- | --- |
| **Flow ID** | `D` |
| **Flow name** | Switch projects |
| **Steps** | 1. With an example project open, note active project title and visible content.<br>2. Switch to a different project (e.g. blank project from Flow B or another existing project).<br>3. If editor has unsaved changes, attempt switch and observe dirty-state warning.<br>4. Confirm active project title/context updates.<br>5. Open a scene/note/material in the new project and verify content belongs to that project only.<br>6. Confirm Overview becomes active when that is the documented behavior on project switch. |
| **Expected result** | Active project title/context updates; dirty editor warnings appear when applicable; **previous project scene/note/material content does not leak** into next project; Overview becomes active per documented behavior. |
| **Result** | `[ ] PASS` `[x] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | API isolation confirmed: blank `smoke-blank-1781586974` has 0 scenes; `example` has 1 scene. No cross-project body leak at API layer. UI dirty-state warning on project switch **not exercised** (browser automation blocked). |

---

### Flow E — Scene editor smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `E` |
| **Flow name** | Scene editor smoke |
| **Steps** | 1. Select a scene with known owner-authored body text.<br>2. Confirm editor shows exact body (no metadata injected).<br>3. Make a small owner-authored edit; confirm dirty state indicator.<br>4. Save via UI control; confirm save success and dirty state clears.<br>5. Reload/re-select scene; confirm saved text persists.<br>6. Test keyboard save (e.g. Ctrl/Cmd+S) **only while editor is focused**.<br>7. Confirm scene title/metadata display remains separate from body. |
| **Expected result** | Selecting a scene loads exact owner-authored scene body; editing marks dirty state; save preserves owner-authored text; keyboard save works only in editor context; scene metadata remains separate from body. |
| **Result** | `[ ] PASS` `[x] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | `PUT /api/projects/example/scenes/scene_001` persisted a smoke edit marker and `GET` confirmed persistence; body reverted after test. UI dirty indicator, Save button, and keyboard-save-in-editor-context **not exercised** (browser blocked). |

---

### Flow F — Notes smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `F` |
| **Flow name** | Notes smoke |
| **Steps** | 1. Open a project with existing notes (or skip with NOT RUN if none exist).<br>2. Confirm notes list loads.<br>3. Select a note; confirm exact owner-authored note body loads.<br>4. Make a small edit; save; reload and confirm persistence.<br>5. Scan note UI for summary/extraction/model actions. |
| **Expected result** | Notes list loads when notes exist; selecting a note loads exact owner-authored note body; editing/saving note body works; metadata is not injected into note body; **no summary/extraction/model action** appears. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[x] NOT RUN` |
| **Evidence / observation** | `GET /api/projects/example/notes` returned empty list. No local note fixtures available to exercise note body load/edit/save in browser. UI would show `No notes yet.` |

---

### Flow G — Materials smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `G` |
| **Flow name** | Materials smoke |
| **Steps** | 1. Open a project with existing materials (or skip with NOT RUN if none exist).<br>2. Confirm materials list loads.<br>3. Select a material; confirm exact owner-provided material body loads.<br>4. If current runtime supports material body editing, make a small edit, save, and confirm persistence.<br>5. Scan for import/upload/external-fetch UI unless already implemented and explicitly authorized. |
| **Expected result** | Materials list loads when materials exist; selecting a material loads exact owner-provided material body; editing/saving material body works when current runtime supports it; metadata/provenance is not injected into material body; **no import/upload/external-fetch behavior** appears unless already implemented and authorized. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[x] NOT RUN` |
| **Evidence / observation** | `GET /api/projects/example/materials` returned empty list. No local material fixtures available to exercise material body load/edit/save in browser. UI would show `No materials yet.` |

---

### Flow H — Shared editor dirty-state and discard safeguards

| Field | Detail |
| --- | --- |
| **Flow ID** | `H` |
| **Flow name** | Shared editor dirty-state and discard safeguards |
| **Steps** | 1. Open a scene, note, or material in the editor.<br>2. Make an unsaved edit.<br>3. Attempt to switch to a different document → observe warning.<br>4. Choose cancel/keep → confirm editor content retained.<br>5. Repeat unsaved edit; attempt project switch → observe warning.<br>6. Choose confirm/discard only when intentional → confirm discard behavior matches choice.<br>7. Simulate or trigger a failed save (if safely reproducible) and confirm editor text is not erased. |
| **Expected result** | Unsaved changes warn before switching document/project; cancel keeps current editor content; confirm discards only when owner chooses; failed save does not erase editor text. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[x] NOT RUN` |
| **Evidence / observation** | Discard/cancel/confirm unsaved-change dialogs require interactive browser. Not exercised due to Playwright dependency failure and unavailable browser MCP. |

---

### Flow I — Project Overview view

| Field | Detail |
| --- | --- |
| **Flow ID** | `I` |
| **Flow name** | Project Overview view |
| **Steps** | 1. Navigate to Overview workspace view.<br>2. Confirm Overview is visible and separate from editor view.<br>3. Observe project title, status, and array-derived counts (scenes, notes, materials).<br>4. Scan for generated summaries, extraction controls, Story Check auto-run, model calls, or semantic search.<br>5. Observe approved-memory snapshot area — confirm placeholder/status only. |
| **Expected result** | Overview is visible as workspace view; overview uses deterministic existing project/list/status data; **no generated summaries** appear; **no extraction, Story Check auto-run, model call, or semantic search** appears; approved-memory snapshot remains placeholder/status only. |
| **Result** | `[ ] PASS` `[x] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | Overview is a frontend workspace view (`ProjectOverview.jsx`). Project metadata available from list (`The Princess and the Pea`). Interactive overview render, count display, and approved-memory placeholder scan **not exercised** in browser. No Story Check auto-run observed in backend logs. |

---

### Flow J — OMI-guided project creation staged shell

| Field | Detail |
| --- | --- |
| **Flow ID** | `J` |
| **Flow name** | OMI-guided project creation staged shell |
| **Steps** | 1. Open OMI-guided project creation entry point.<br>2. Enter owner-authored setup idea text.<br>3. Observe staged setup labels — confirm candidate/planning-only visibility.<br>4. Cancel or reset staged flow → confirm no project is created.<br>5. Restart staged flow; proceed to final confirmation using existing create-project path only.<br>6. During staged steps (before final confirmation), watch network/backend logs for staged setup storage/API calls and OMI writes.<br>7. Confirm no generated prose is created during staged steps. |
| **Expected result** | Owner can enter setup idea text; staged setup labels are visibly candidate/planning only; cancel/reset does not create a project; final confirmation uses existing create-project path; **no backend staged setup storage/API is called**; **no OMI candidate records are written before final confirmation**; no generated prose is created. |
| **Result** | `[ ] PASS` `[x] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | OMI-guided shell is frontend-transient (`OmiGuidedProjectCreation.jsx`). Blank project create produced 0 OMI candidates/ideas via API. Staged cancel/review/final-confirm UI and network watch during staged steps **not exercised** in browser. |

---

### Flow K — Memory / Canon shell

| Field | Detail |
| --- | --- |
| **Flow ID** | `K` |
| **Flow name** | Memory / Canon shell |
| **Steps** | 1. Navigate to Memory / Canon workspace view (`memory-canon`).<br>2. Confirm it is separate from Overview, editor, and OMI candidate panels.<br>3. Verify all nine approved-only categories are visible with empty states:<br>&nbsp;&nbsp;• characters<br>&nbsp;&nbsp;• locations/settings<br>&nbsp;&nbsp;• timeline<br>&nbsp;&nbsp;• plot threads<br>&nbsp;&nbsp;• continuity/consistency<br>&nbsp;&nbsp;• open questions<br>&nbsp;&nbsp;• relationships<br>&nbsp;&nbsp;• organizations/groups<br>&nbsp;&nbsp;• objects/items<br>4. Confirm OMI candidates and promotion/audit records are **not** shown as approved canon.<br>5. Scan for apply-promotion button/action and memory/canon mutation UI. |
| **Expected result** | Memory / Canon is visible as separate workspace view; nine approved-only categories visible with approved-only empty states; OMI candidates and promotion/audit records are not shown as approved canon; **no apply-promotion button/action exists**; **no memory/canon mutation UI exists**. |
| **Result** | `[ ] PASS` `[x] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | `MemoryCanonShell.jsx` defines all nine approved-only categories with empty-state boundary copy and explicit `No apply-promotion in this phase` messaging. Interactive `memory-canon` workspace view navigation **not exercised** in browser. |

---

### Flow L — Boundary and safety smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `L` |
| **Flow name** | Boundary and safety smoke |
| **Steps** | 1. Scan entire workspace UI (nav, editor, overview, OMI panel, memory/canon, project creation) for prohibited controls.<br>2. Navigate, switch projects, open/save documents, and view overview/memory-canon while watching backend logs.<br>3. Confirm no Story Check auto-run on load/switch/save.<br>4. Confirm no hidden project writes outside explicit owner actions (save, create project, etc.). |
| **Expected result** | **No generated prose controls**; no rewrite/continue/improve/polish/story-prose generation path; **no model/Ollama call** unless owner explicitly runs an existing allowed analysis path outside this checklist; no extraction UI; no semantic search UI; no Story Check auto-run on load/switch/save; no apply-promotion; no memory/canon mutation; no hidden project writes outside explicit owner actions. |
| **Result** | `[ ] PASS` `[x] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | Frontend source scan found no prohibited prose-generation control phrases (`rewrite scene`, `continue scene`, `polish prose`, `semantic search`). `apply-promotion` appears only in boundary disclaimers in `MemoryCanonShell.jsx`. Backend smoke logs show no Story Check/analysis/Ollama routes. Full interactive workspace UI scan **not exercised** in browser. |

---

## 5. Stop Conditions for T004

Halt browser/manual smoke execution immediately if any of the following occur:

| # | Stop condition | Action |
| --- | --- | --- |
| 1 | Fatal app load failure | Stop; record FAIL on Flow A; triage in T005 if needed |
| 2 | Project selection cannot proceed | Stop; record blocker |
| 3 | Owner-authored text is modified or lost unexpectedly | Stop; record blocker |
| 4 | Project switch leaks content across projects | Stop; record blocker |
| 5 | Save corrupts body files | Stop; record blocker |
| 6 | Generated prose UI appears | Stop; record boundary violation |
| 7 | Model/Ollama call occurs unexpectedly | Stop; record boundary violation |
| 8 | OMI candidates are treated as approved canon | Stop; record boundary violation |
| 9 | Apply-promotion or memory/canon mutation appears | Stop; record boundary violation |
| 10 | Backend or frontend server cannot start | Stop before flows; record NOT RUN with blocker note |
| 11 | Smoke discovers a runtime bug requiring repair | Stop or complete remaining safe flows; classify in T005 |

When stopped early, still complete Section 6 reporting for all executed flows and mark remaining flows `NOT RUN`.

## 6. T004 Reporting Template

Copy this table into `docs/roadmap/validation/latest_roadmap_validation.md` or a T004-specific results section during execution.

| Flow ID | Flow name | Result | Evidence / observation | Issue classification | Follow-up task needed | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| A | App loads and project selector/library appears | PASS | Servers up; project list API 200 with 6 projects; no analysis routes in logs; browser UI not interactive | deferred | no | Playwright/browser MCP blocked |
| B | Create blank project | PASS | `smoke-blank-1781586974` created; 0 scenes/notes/materials/OMI | — | no | Smoke artifact |
| C | Select existing example project | PASS | `scene_001` 1972 chars; repeat read unchanged | — | no | |
| D | Switch projects | PARTIAL | API isolation OK; dirty-state UI not exercised | repair candidate | yes | T005 triage |
| E | Scene editor smoke | PARTIAL | API save/revert OK; UI dirty/keyboard save not exercised | repair candidate | yes | T005 triage |
| F | Notes smoke | NOT RUN | No note fixtures in local projects | deferred | no | |
| G | Materials smoke | NOT RUN | No material fixtures in local projects | deferred | no | |
| H | Shared editor dirty-state and discard safeguards | NOT RUN | Requires interactive browser dialogs | deferred | yes | T005 triage |
| I | Project Overview view | PARTIAL | Metadata available; overview UI not rendered in browser | deferred | no | |
| J | OMI-guided project creation staged shell | PARTIAL | 0 OMI on blank create; staged UI not exercised | deferred | no | |
| K | Memory / Canon shell | PARTIAL | Source confirms 9 categories + no apply-promotion; UI not rendered | deferred | no | |
| L | Boundary and safety smoke | PARTIAL | Source/log scan clean; full UI scan not exercised | deferred | no | |

**T004 overall result:** `[ ] PASS` `[x] PARTIAL` `[ ] FAIL`

**T004 execution date:** `2026-06-15`

**Early stop triggered:** no — servers started; no fatal load, data loss, boundary violation, or unexpected model call observed. Browser automation environment incomplete.

## 7. Owner Observation Notes

Record free-form observations during T004:

| Prompt | Notes |
| --- | --- |
| Confusing UI | Not assessed interactively (browser automation blocked). |
| Confusing navigation | Not assessed interactively. |
| Missing labels | Not assessed interactively. |
| Unsafe AI / prose-generation implication | Source scan found no prohibited generation controls; Story Check remains manual-only path. |
| Unexpected write (describe action and observed effect) | Only explicit smoke actions: blank project create and reversible scene edit test on `example/scene_001`. |
| Browser console error | Not captured (no interactive browser session). |
| Backend terminal error | None fatal during smoke. |
| Frontend terminal error | `npm warn Unknown env config "devdir"` only. |

## 8. Explicit Exclusions (T003 Scope)

`PHASE7-IMPL-010-T003` does **not**:

- run browser/manual validation
- start backend or frontend servers
- change runtime code
- change tests
- add features
- add model/Ollama calls
- add generated prose
- add extraction
- add semantic search
- add Story Check auto-runs
- add apply-promotion
- add memory/canon mutation
- add backend approved-memory helpers/routes
- add frontend approved-memory API helpers
- add metadata editing UI
- add note/material create/import/upload UI

T003 creates this checklist and updates roadmap/status docs only. Execution belongs to `PHASE7-IMPL-010-T004`.
