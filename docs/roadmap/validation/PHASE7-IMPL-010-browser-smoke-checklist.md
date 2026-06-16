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

- [ ] `PHASE7-IMPL-010-T001` — inventory and child-task plan — **complete**
- [ ] `PHASE7-IMPL-010-T002` — automated regression validation pass — **complete**
- [ ] Automated regression suite passing (frontend source-contract tests, project manager, scene routes, note/material routes, OMI boundary tests)
- [ ] No unexpected runtime code, test, package, or project-file changes since T002
- [ ] Owner is ready to run the app locally (backend + frontend dev servers)
- [ ] Smoke execution is **observational only** unless a later repair task (`PHASE7-IMPL-010-T005`) explicitly authorizes a tiny safe fix
- [ ] Owner understands standard refusal boundary: the app is analysis-only; no generated story prose controls should appear during smoke

## 3. Local Run Instructions (T004 Placeholders)

**Do not run these commands during T003.** T004 fills in the actual values below before execution.

| Item | T004 value (fill in at execution time) |
| --- | --- |
| Backend server command | `[T004: backend command]` |
| Frontend dev server command | `[T004: frontend command]` |
| Expected backend localhost URL | `[T004: e.g. http://localhost:8000]` |
| Expected frontend localhost URL | `[T004: e.g. http://localhost:5173]` |
| Browser used | `[T004: browser name and version]` |
| Shutdown procedure | `[T004: how backend and frontend were stopped]` |
| Backend terminal errors observed | `[T004: none / describe]` |
| Frontend terminal errors observed | `[T004: none / describe]` |

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
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Fatal load failure, blank screen with no recoverable UI, or unexpected model/Ollama activity on load → **stop T004** and record blocker. |

---

### Flow B — Create blank project

| Field | Detail |
| --- | --- |
| **Flow ID** | `B` |
| **Flow name** | Create blank project |
| **Steps** | 1. From project selector/library, start blank project creation.<br>2. Enter an owner-authored title (e.g. `smoke-blank-<timestamp>`).<br>3. Confirm/create using the existing create-project path.<br>4. Observe whether the project opens or appears in the library.<br>5. Inspect project contents: scenes, notes, materials, OMI records, memory/canon files (via UI only; no manual filesystem edits during smoke). |
| **Expected result** | Owner can create a blank project from owner-entered title; project opens or appears in library; blank project does **not** contain generated story content; **no scenes, notes, materials, OMI, or memory/canon records are silently created** except minimal safe metadata already documented; project ID/path behavior appears safe. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Hidden pre-confirmation writes, generated content in new project, or unsafe path/ID behavior → **stop T004** and record blocker. |

---

### Flow C — Select existing example project

| Field | Detail |
| --- | --- |
| **Flow ID** | `C` |
| **Flow name** | Select existing example project |
| **Steps** | 1. From project selector/library, select a known existing example project with scenes.<br>2. Observe project title and status display.<br>3. Open or observe the scene list.<br>4. Select one scene and note the body text shown before any edit.<br>5. Reload or re-select the same scene without saving. |
| **Expected result** | Example project opens; title/status visible; existing scene list loads; **owner-authored body text is not modified on load**. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Scene body changed on load/reload without owner save → **stop T004** and record blocker. |

---

### Flow D — Switch projects

| Field | Detail |
| --- | --- |
| **Flow ID** | `D` |
| **Flow name** | Switch projects |
| **Steps** | 1. With an example project open, note active project title and visible content.<br>2. Switch to a different project (e.g. blank project from Flow B or another existing project).<br>3. If editor has unsaved changes, attempt switch and observe dirty-state warning.<br>4. Confirm active project title/context updates.<br>5. Open a scene/note/material in the new project and verify content belongs to that project only.<br>6. Confirm Overview becomes active when that is the documented behavior on project switch. |
| **Expected result** | Active project title/context updates; dirty editor warnings appear when applicable; **previous project scene/note/material content does not leak** into next project; Overview becomes active per documented behavior. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Cross-project content leak or missing dirty-state warning when editor is dirty → **stop T004** and record blocker. |

---

### Flow E — Scene editor smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `E` |
| **Flow name** | Scene editor smoke |
| **Steps** | 1. Select a scene with known owner-authored body text.<br>2. Confirm editor shows exact body (no metadata injected).<br>3. Make a small owner-authored edit; confirm dirty state indicator.<br>4. Save via UI control; confirm save success and dirty state clears.<br>5. Reload/re-select scene; confirm saved text persists.<br>6. Test keyboard save (e.g. Ctrl/Cmd+S) **only while editor is focused**.<br>7. Confirm scene title/metadata display remains separate from body. |
| **Expected result** | Selecting a scene loads exact owner-authored scene body; editing marks dirty state; save preserves owner-authored text; keyboard save works only in editor context; scene metadata remains separate from body. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Save corrupts body, metadata appears in body, or keyboard save fires outside editor context → **stop T004** and record blocker. |

---

### Flow F — Notes smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `F` |
| **Flow name** | Notes smoke |
| **Steps** | 1. Open a project with existing notes (or skip with NOT RUN if none exist).<br>2. Confirm notes list loads.<br>3. Select a note; confirm exact owner-authored note body loads.<br>4. Make a small edit; save; reload and confirm persistence.<br>5. Scan note UI for summary/extraction/model actions. |
| **Expected result** | Notes list loads when notes exist; selecting a note loads exact owner-authored note body; editing/saving note body works; metadata is not injected into note body; **no summary/extraction/model action** appears. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Note body corrupted on save/load or model/extraction UI appears → **stop T004** and record blocker. |

---

### Flow G — Materials smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `G` |
| **Flow name** | Materials smoke |
| **Steps** | 1. Open a project with existing materials (or skip with NOT RUN if none exist).<br>2. Confirm materials list loads.<br>3. Select a material; confirm exact owner-provided material body loads.<br>4. If current runtime supports material body editing, make a small edit, save, and confirm persistence.<br>5. Scan for import/upload/external-fetch UI unless already implemented and explicitly authorized. |
| **Expected result** | Materials list loads when materials exist; selecting a material loads exact owner-provided material body; editing/saving material body works when current runtime supports it; metadata/provenance is not injected into material body; **no import/upload/external-fetch behavior** appears unless already implemented and authorized. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Material body corrupted or unauthorized import/fetch UI appears → **stop T004** and record blocker. |

---

### Flow H — Shared editor dirty-state and discard safeguards

| Field | Detail |
| --- | --- |
| **Flow ID** | `H` |
| **Flow name** | Shared editor dirty-state and discard safeguards |
| **Steps** | 1. Open a scene, note, or material in the editor.<br>2. Make an unsaved edit.<br>3. Attempt to switch to a different document → observe warning.<br>4. Choose cancel/keep → confirm editor content retained.<br>5. Repeat unsaved edit; attempt project switch → observe warning.<br>6. Choose confirm/discard only when intentional → confirm discard behavior matches choice.<br>7. Simulate or trigger a failed save (if safely reproducible) and confirm editor text is not erased. |
| **Expected result** | Unsaved changes warn before switching document/project; cancel keeps current editor content; confirm discards only when owner chooses; failed save does not erase editor text. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Silent data loss on failed save or missing discard warning → **stop T004** and record blocker. |

---

### Flow I — Project Overview view

| Field | Detail |
| --- | --- |
| **Flow ID** | `I` |
| **Flow name** | Project Overview view |
| **Steps** | 1. Navigate to Overview workspace view.<br>2. Confirm Overview is visible and separate from editor view.<br>3. Observe project title, status, and array-derived counts (scenes, notes, materials).<br>4. Scan for generated summaries, extraction controls, Story Check auto-run, model calls, or semantic search.<br>5. Observe approved-memory snapshot area — confirm placeholder/status only. |
| **Expected result** | Overview is visible as workspace view; overview uses deterministic existing project/list/status data; **no generated summaries** appear; **no extraction, Story Check auto-run, model call, or semantic search** appears; approved-memory snapshot remains placeholder/status only. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Generated summary, model call, or Story Check auto-run on Overview → **stop T004** and record blocker. |

---

### Flow J — OMI-guided project creation staged shell

| Field | Detail |
| --- | --- |
| **Flow ID** | `J` |
| **Flow name** | OMI-guided project creation staged shell |
| **Steps** | 1. Open OMI-guided project creation entry point.<br>2. Enter owner-authored setup idea text.<br>3. Observe staged setup labels — confirm candidate/planning-only visibility.<br>4. Cancel or reset staged flow → confirm no project is created.<br>5. Restart staged flow; proceed to final confirmation using existing create-project path only.<br>6. During staged steps (before final confirmation), watch network/backend logs for staged setup storage/API calls and OMI writes.<br>7. Confirm no generated prose is created during staged steps. |
| **Expected result** | Owner can enter setup idea text; staged setup labels are visibly candidate/planning only; cancel/reset does not create a project; final confirmation uses existing create-project path; **no backend staged setup storage/API is called**; **no OMI candidate records are written before final confirmation**; no generated prose is created. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Pre-confirmation OMI write, backend staged API call, or generated prose in staged flow → **stop T004** and record blocker. |

---

### Flow K — Memory / Canon shell

| Field | Detail |
| --- | --- |
| **Flow ID** | `K` |
| **Flow name** | Memory / Canon shell |
| **Steps** | 1. Navigate to Memory / Canon workspace view (`memory-canon`).<br>2. Confirm it is separate from Overview, editor, and OMI candidate panels.<br>3. Verify all nine approved-only categories are visible with empty states:<br>&nbsp;&nbsp;• characters<br>&nbsp;&nbsp;• locations/settings<br>&nbsp;&nbsp;• timeline<br>&nbsp;&nbsp;• plot threads<br>&nbsp;&nbsp;• continuity/consistency<br>&nbsp;&nbsp;• open questions<br>&nbsp;&nbsp;• relationships<br>&nbsp;&nbsp;• organizations/groups<br>&nbsp;&nbsp;• objects/items<br>4. Confirm OMI candidates and promotion/audit records are **not** shown as approved canon.<br>5. Scan for apply-promotion button/action and memory/canon mutation UI. |
| **Expected result** | Memory / Canon is visible as separate workspace view; nine approved-only categories visible with approved-only empty states; OMI candidates and promotion/audit records are not shown as approved canon; **no apply-promotion button/action exists**; **no memory/canon mutation UI exists**. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | OMI candidates displayed as canon, apply-promotion UI, or memory/canon mutation control appears → **stop T004** and record blocker. |

---

### Flow L — Boundary and safety smoke

| Field | Detail |
| --- | --- |
| **Flow ID** | `L` |
| **Flow name** | Boundary and safety smoke |
| **Steps** | 1. Scan entire workspace UI (nav, editor, overview, OMI panel, memory/canon, project creation) for prohibited controls.<br>2. Navigate, switch projects, open/save documents, and view overview/memory-canon while watching backend logs.<br>3. Confirm no Story Check auto-run on load/switch/save.<br>4. Confirm no hidden project writes outside explicit owner actions (save, create project, etc.). |
| **Expected result** | **No generated prose controls**; no rewrite/continue/improve/polish/story-prose generation path; **no model/Ollama call** unless owner explicitly runs an existing allowed analysis path outside this checklist; no extraction UI; no semantic search UI; no Story Check auto-run on load/switch/save; no apply-promotion; no memory/canon mutation; no hidden project writes outside explicit owner actions. |
| **Result** | `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL` `[ ] NOT RUN` |
| **Evidence / observation** | |
| **Stop condition** | Any boundary violation (generated prose UI, unexpected model call, apply-promotion, silent writes) → **stop T004** and record blocker. |

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
| A | App loads and project selector/library appears | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| B | Create blank project | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| C | Select existing example project | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| D | Switch projects | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| E | Scene editor smoke | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| F | Notes smoke | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| G | Materials smoke | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| H | Shared editor dirty-state and discard safeguards | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| I | Project Overview view | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| J | OMI-guided project creation staged shell | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| K | Memory / Canon shell | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |
| L | Boundary and safety smoke | PASS / PARTIAL / FAIL / NOT RUN | | blocker / repair candidate / deferred / not-a-bug / — | yes / no | |

**T004 overall result:** `[ ] PASS` `[ ] PARTIAL` `[ ] FAIL`

**T004 execution date:** `[T004: YYYY-MM-DD]`

**Early stop triggered:** yes / no — if yes, describe:

## 7. Owner Observation Notes

Record free-form observations during T004:

| Prompt | Notes |
| --- | --- |
| Confusing UI | |
| Confusing navigation | |
| Missing labels | |
| Unsafe AI / prose-generation implication | |
| Unexpected write (describe action and observed effect) | |
| Browser console error | |
| Backend terminal error | |
| Frontend terminal error | |

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
