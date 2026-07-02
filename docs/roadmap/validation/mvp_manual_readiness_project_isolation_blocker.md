# MVP Manual Readiness — Project Isolation Blocker

## Result

- Task: `MVP-READINESS-BROWSER-EVIDENCE-001-C`
- Scope: docs/governance record only; no product fix attempted.
- Browser evidence result: **FAIL-with-evidence** (exit code `1`).
- MVP manual readiness status: **BLOCKED** until project isolation passes.
- This is not tooling blocked: Playwright imported, browser ran, app loaded, workflow completed, screenshots and workflow log were captured.

## Evidence Artifacts

| Artifact | Path |
| --- | --- |
| Evidence script | `scripts/mvp-project-isolation-browser-smoke.mjs` |
| Evidence directory | `artifacts/mvp-readiness/project-isolation` |
| Evidence report | `artifacts/mvp-readiness/project-isolation/evidence-report.md` |
| Workflow log | `artifacts/mvp-readiness/project-isolation/workflow-log.json` |
| Screenshot — initial load | `artifacts/mvp-readiness/project-isolation/screenshots/01-initial-load.png` |
| Screenshot — review before create | `artifacts/mvp-readiness/project-isolation/screenshots/02-review-before-create.png` |
| Screenshot — after project creation | `artifacts/mvp-readiness/project-isolation/screenshots/03-after-project-creation.png` |
| Screenshot — scenes workspace | `artifacts/mvp-readiness/project-isolation/screenshots/04-scenes-workspace.png` |
| Screenshot — OMI or memory/canon | `artifacts/mvp-readiness/project-isolation/screenshots/05-omi-or-memory-canon.png` |

## Run Summary

- App base URL: `http://localhost:5173`
- Browser tool: Playwright Chromium (imported from `frontend/node_modules`)
- Unique project created and activated: `MVP Isolation Test 1782963719999` (`mvp-isolation-test-1782963719999`)
- Started: `2026-07-02T03:41:59.039Z`
- Finished: `2026-07-02T03:42:04.336Z`
- Workflow log records `toolingBlocked: false` and `toolingError: null`.

### Passed Checks (context)

- OMI-guided setup fields filled; review-before-create showed the unique project title.
- Post-create active project header, selector value, and overview project id matched the new project (not `example`).
- Scenes workspace did not show example scene body content.
- Memory/Canon shell approved-only boundary copy was present.

### Blockers Captured

| Blocker label | Assertion | Details |
| --- | --- | --- |
| `hardcoded_scene_route` | `scenes_nav_no_scene_001_leak` | Scenes navigation still exposes example-project scene routing (`scene_001`) while viewing the new project. |
| `hardcoded_scene_route` | `new_project_scene_list_has_no_example_scene_items` | New project scene list still includes example-scene nav items (`sceneButtonCount: 1`). |
| `omi_cross_project_data_leakage` | `omi_memory_view_no_princess_and_pea` | Memory/Canon or OMI view shows example project title/data (`The Princess and the Pea`) for the new project context. |
| `omi_cross_project_data_leakage` | `omi_memory_view_no_scene_001` | Memory/Canon or OMI view shows example scene identifier (`scene_001`) for the new project context. |
| `candidate_setup_not_visible` | `setup_candidate_not_labeled_approved_memory_or_canon` | Setup candidate from guided project creation is not visibly labeled as candidate/planning state and must not appear as approved memory or canon. |

## MVP Readiness Decision

Owner manual readiness browser evidence **reproduced project isolation and routing leakage** in the live frontend after OMI-guided project creation.

**MVP manual readiness is blocked** until:

1. New project creation updates and activates the correct active project state (partial pass observed for header/selector/overview id; scenes and OMI/Memory views still leak).
2. Project selector selects the new project after creation or makes activation explicit (header/selector activation passed in this run; downstream views did not fully respect it).
3. Scenes navigation is project-scoped (failed — example `scene_001` leak).
4. OMI/Memory/Canon navigation is project-scoped (failed — example project strings leaked).
5. Setup candidate remains candidate/planning only and is not presented as approved memory or canon (failed visibility/labeling check).
6. Example project data never leaks into newly created project views (failed in scenes nav and OMI/Memory views).

This blocker does **not** mark MVP complete and does **not** claim end-to-end usability has passed.

## Relationship to PHASE8-IMPL-022

- `PHASE8-IMPL-022` closeout remains valid as **smoke-harness closeout** (deterministic in-memory MVP usability validation parent complete/PASS).
- `PHASE8-IMPL-022` closeout does **not** equal owner MVP acceptance or production browser/manual readiness.
- Browser evidence is a separate owner manual readiness gate that revealed runtime project isolation gaps not covered by the in-memory harness alone.

## Full Manual MVP Testing Scope

Full manual MVP testing should run Ollama, backend, frontend, and browser/manual checks together.

This specific evidence script:

- Required backend and frontend already running at `http://localhost:5173`.
- Did **not** call Ollama or live models directly.
- Did **not** execute BookNLP/spaCy, NCP/Subtxt/dramatica-flow, or training paths.
- Wrote only under `MVP_EVIDENCE_DIR` (`artifacts/mvp-readiness/project-isolation`).

## Expected Repair Direction (documentation only)

Future implementation tasks should address:

- New project creation must update active project state consistently across all workspace views.
- Project selector must select the new project after creation or make activation explicit.
- Scenes navigation must load scene lists and routes from the active `project_id` only.
- OMI/Memory/Canon navigation must load OMI and approved-memory surfaces from the active `project_id` only.
- Setup candidate from guided creation must remain visibly candidate/planning until owner review and explicit apply-promotion.
- Example project fixtures must never appear in newly created project views.

## Safety Notes

- Evidence-only script; no product fix attempted in this task.
- No Ollama/model calls.
- No BookNLP/spaCy execution.
- No NCP/Subtxt/dramatica-flow execution.
- Writes limited to `MVP_EVIDENCE_DIR`.
- Generated prose/prose-production remains permanently forbidden.

## Manual Re-run Command

```bash
# From repo root, with backend + frontend already running:
node scripts/mvp-project-isolation-browser-smoke.mjs

# Alternative module resolution:
NODE_PATH=frontend/node_modules node scripts/mvp-project-isolation-browser-smoke.mjs
```

## Recommended Next Step

Implement a scoped product fix task for project-scoped scenes and OMI/Memory/Canon navigation, then re-run the browser evidence script until exit code `0` before claiming MVP manual readiness.
