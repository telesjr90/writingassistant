# PHASE7-IMPL-010 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-010`
- Canonical title: `Workspace Validation / Browser and Manual Smoke`
- Type: validation parent
- Status: `active_next` in `docs/roadmap/roadmap_index.yaml`
- Depends on: `PHASE7-IMPL-004`, `PHASE7-IMPL-005`, `PHASE7-IMPL-006`, `PHASE7-IMPL-007`, `PHASE7-IMPL-008`, `PHASE7-IMPL-009`

Registered roadmap boundary tags:

- `validation`
- `manual_smoke`
- `no_runtime_feature_scope`

Additional boundary concepts preserved in prose:

- validate completed workspace functionality, not new features
- source-level and automated regression confirmation
- browser/manual smoke checklist and execution
- owner-observed UI smoke notes
- validation repair triage only when explicitly needed
- no generated prose, model calls, extraction, apply-promotion, or memory/canon mutation
- no feature expansion during validation

## Validation Scope

`PHASE7-IMPL-010` validates completed workspace functionality from `PHASE7-IMPL-004` through `PHASE7-IMPL-009`. It does not add new product features.

| Area | Completed parent | Validation focus |
| --- | --- | --- |
| Chapter/scene metadata compatibility | `PHASE7-IMPL-004` | Legacy `scenes/{scene_id}.md` compatibility, metadata-shaped scene records, route contracts, frontend display compatibility |
| Notes/materials storage | `PHASE7-IMPL-005` | Separate body/metadata storage, route compatibility, path safety, minimal navigation/display shell |
| Shared owner-authored editor | `PHASE7-IMPL-006` | Scene/note/material body-only load/save, dirty state, keyboard-save safeguards, project-switch guards, document-switch guards |
| Project Overview shell | `PHASE7-IMPL-007` | Deterministic overview view, array-derived counts, overview/editor separation, no backend overview dependency |
| OMI-guided staged creation shell | `PHASE7-IMPL-008` | Frontend-transient staged setup, visible setup/candidate labels, explicit final confirmation, blank project compatibility, no hidden pre-confirmation writes |
| Memory / Canon shell | `PHASE7-IMPL-009` | Read-only `memory-canon` workspace view, approved-only empty states, OMI candidate exclusion, no memory file creation on load |
| Project creation and selection | `PHASE7-IMPL-001` through `PHASE7-IMPL-003` | Blank project creation, library listing, project switching, unsaved-change protection |
| Safety boundaries | all prior phases | No generated prose controls, no model/Ollama calls during storage/search/navigation, no apply-promotion, no memory/canon mutation, candidate/canon label separation |

## Validation Types

Planned validation types for this parent:

1. **Source-level regression confirmation** — `tests/test_frontend_project_workspace_source.py` and related source-contract phrases remain aligned with roadmap boundaries.
2. **Backend pytest regression confirmation** — `tests/test_project_manager.py`, `tests/test_scene_routes.py`, `tests/test_note_material_routes.py`, and related OMI boundary tests.
3. **Frontend source-contract test confirmation** — focused frontend source tests that lock no-prose, candidate/canon, editor, overview, staged creation, and memory/canon shell contracts.
4. **Browser/manual smoke checklist** — explicit owner-observable flows, expected outcomes, and stop conditions prepared in a later child.
5. **Owner-observed UI smoke notes** — recorded observations from local app execution without turning validation into feature expansion.
6. **Roadmap/status closeout** — parent completion, validator pass, and frontier move only after validation/repair children finish.

`PHASE7-IMPL-010-T001` performs docs/status planning only. It does not run browser/manual validation, app servers, pytest, or frontend builds.

## Completed Workspace Surfaces To Validate

### Project creation and selection

- Blank project creation via existing `POST /api/projects`.
- Project library listing and selection.
- Project switching with unsaved-change safeguards.
- OMI-guided staged creation shell with explicit final confirmation and blank-project compatibility.

### Workspace views

- Project Overview (`overview` workspace view).
- Shared owner-authored editor (`editor` workspace view) for scene/note/material documents.
- Memory / Canon shell (`memory-canon` workspace view) with approved-only empty states.
- OMI panel candidate/audit separation from approved canon.

### Storage and editing behavior

- Scene/chapter metadata compatibility without rewriting owner-authored scene bodies.
- Notes/materials body and metadata separation.
- Shared editor exact body load/save for scene/note/material documents.
- Dirty-state, keyboard-save, project-switch, and document-switch guards.

### Boundaries to confirm absent

- Generated prose, summaries, extraction, semantic search.
- Story Check auto-runs during navigation/storage/overview/memory-canon viewing.
- Model calls and Ollama calls during routine workspace flows.
- Apply-promotion and memory/canon mutation.
- Backend approved-memory routes/helpers.
- Frontend approved-memory API helpers.
- Metadata editing UI.
- Note/material create/import/upload UI.

## Existing Test Surfaces

- `tests/test_frontend_project_workspace_source.py` — primary frontend source-contract and regression surface for workspace views, editor, overview, staged creation, and memory/canon shell boundaries.
- `tests/test_project_manager.py` — project creation, metadata compatibility, notes/materials helpers, OMI lifecycle, and safety helpers.
- `tests/test_scene_routes.py` — scene route compatibility and metadata behavior.
- `tests/test_note_material_routes.py` — note/material route compatibility and path safety.
- `tests/test_omi_boundaries.py` and `tests/test_omi_routes.py` — OMI no-prose and candidate/audit boundaries.

Browser/manual smoke remains unexecuted until `PHASE7-IMPL-010-T004` or another explicitly scoped validation child.

## Boundaries

`PHASE7-IMPL-010` must NOT add:

- Generated prose, AI-written content, summaries, extraction, or semantic search.
- Story Check auto-runs, model calls, or Ollama calls as part of validation setup.
- Apply-promotion, memory/canon mutation, or OMI candidate promotion.
- Backend approved-memory routes/helpers or frontend approved-memory API helpers.
- Metadata editing UI, note/material create/import/upload UI, or new runtime features unless a later validation repair task explicitly authorizes a tiny safe bug fix.
- Training data, JSONL records, dataset artifacts, or `training/data/dataset_manifest.json` updates.
- Feature expansion disguised as validation cleanup.

Validation repair (`PHASE7-IMPL-010-T005`) is conditional. It exists only if smoke or regression finds issues. Repairs must be classified as blocker, deferred, or not-a-bug before any tiny runtime change is attempted.

## Risks

- Browser smoke may reveal UI-only bugs that source-level tests do not catch.
- Validation may require tiny repair tasks; repairs must stay minimal and explicitly authorized.
- Validation must not become feature expansion or a pretext for new product scope.
- App server and browser execution steps must remain separated from docs planning (`T001`, `T003` prep).
- Runtime project files under `projects/` should remain untouched during `T001`.
- Raw git or LeanCTX hook behavior should not block docs planning; record hook skips honestly when they occur.
- Prior deferred browser/manual validation language attached to `PHASE7-IMPL-004` through `PHASE7-IMPL-009` must be treated as numbering drift if found; correct references under `PHASE7-IMPL-010`, not by renumbering parents.

## Recommended Child Sequence

1. `PHASE7-IMPL-010-T001` — Workspace Validation / Browser and Manual Smoke inventory and child-task plan. Docs/status only.
2. `PHASE7-IMPL-010-T002` — Automated regression validation pass. Run existing backend/source regression suites and record results.
3. `PHASE7-IMPL-010-T003` — Browser smoke checklist preparation. Define exact flows, expected outcomes, and stop conditions; no browser execution unless explicitly scoped.
4. `PHASE7-IMPL-010-T004` — Browser/manual smoke execution. Run app locally and execute checklist; record observed results.
5. `PHASE7-IMPL-010-T005` — Validation repair triage. Only if smoke finds issues; classify blocker/deferred/not-a-bug; tiny repair only if explicitly necessary and safe.
6. `PHASE7-IMPL-010-T006` — Final validation regression pass. Rerun validators and relevant automated tests after any repairs; confirm no boundary drift.
7. `PHASE7-IMPL-010-T007` — Roadmap/status closeout. Close validation parent and move active frontier to the next roadmap-authorized task.

## Recommended Next Child

`PHASE7-IMPL-010-T002` — Automated regression validation pass.

Likely scope:

- Run `tests/test_frontend_project_workspace_source.py`, `tests/test_project_manager.py`, `tests/test_scene_routes.py`, `tests/test_note_material_routes.py`, and any other roadmap-named regression suites.
- Record pass/fail results in validation docs.
- Make no runtime changes unless a tiny validation repair is explicitly needed and separately authorized.
