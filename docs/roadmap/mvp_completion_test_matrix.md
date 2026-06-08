# MVP Completion Test Matrix

## Purpose

This matrix defines the formal MVP exit gate for the local Dramatica-informed writing assistant. It is a planning artifact only. It does not create tests, scripts, runtime routes, frontend UI, model calls, OMI promotion behavior, training data, or model artifacts.

Product pivot note: this MVP foundation remains valuable and should still be completed/recorded. After MVP foundation acceptance, the next product milestone is the pre-Dramatica Project Workspace Foundation, then Writer Assistant Core. Dramatica-specific work, advanced extractors, RunPod, Books 4-5, and fine-tuning remain deferred. Live qwen3/Dramatica baseline checks remain optional/manual and are not central to the new workspace/core direction.

The MVP exit gate verifies the current product boundary:

- The app is analysis-only.
- It supports local project loading, scene editing/saving, bible/storyform read/write, Story Check, rich diagnostics, mock mode, qwen3/Ollama baseline mode, no-prose guardrails, and bounded OMI candidate planning.
- It does not write, rewrite, continue, imitate, polish, improve, or extend story prose.

The next Product Workspace Foundation milestone should add its own acceptance checklist later for project creation/library, chapters/scenes/notes/materials, owner-authored prose save/reload, OMI-guided project creation, extraction trigger strategy, owner approval, no silent promotion, no AI prose generation, and project-local memory/canon visibility. Those future workspace checks do not invalidate the current MVP safety/workflow foundation.

## MVP Exit Criteria

The MVP is not considered complete until each matrix row has a recorded pass, an accepted owner-approved exception, or a documented blocker.

Pass/fail recording should use the format in the final section of this document.

## Test Matrix

| Area | Required Validation | Command or Method | Pass Criteria |
| --- | --- | --- | --- |
| Repo safety tests | Confirm no unexpected tracked/ignored unsafe files are staged for release | `git status --short --branch`; `git status --ignored --short` | Only expected tracked changes; ignored reports/build/cache files remain unstaged |
| Full backend automated tests | Run all backend pytest coverage | `.venv-unsloth-clean/bin/python -m pytest tests -q` | All tests pass |
| Focused backend test groups | Run high-risk route, guard, normalizer, OMI, and evaluation groups | Focused pytest files for story check, context routes, scene routes, guardrails, OMI routes, project manager, evaluation fixtures, baseline harness | All focused groups pass |
| Frontend build tests | Verify production frontend build | `cd frontend && npm run build` | Build succeeds; known warnings recorded |
| Backend server smoke | Start backend locally | Backend run command from current project setup | Server starts, health-critical API routes respond, no crash on load |
| Frontend app smoke | Start frontend locally | `cd frontend && npm run dev` | App loads, project UI renders, no console-blocking runtime error |
| Story Check mock mode | Run Story Check with deterministic mock mode | `ANALYSIS_MODE=mock` local route/manual smoke and tests | Normalized rich Story Check appears; no live Ollama call; no project truth mutation |
| Story Check qwen3 baseline mode | Run optional baseline against local Ollama only when available | `ANALYSIS_MODE=ollama_baseline` with explicit `OLLAMA_BASE_URL` and `OLLAMA_MODEL=qwen3:8b` | JSON response normalizes safely; no unsupported Dramatica truth claims; no prose output |
| No-prose request guard tests | Verify prohibited request classes refuse safely | Guardrail and request-path pytest groups | Standard refusal message appears where expected; owner-authored saves are not overblocked |
| Output guard tests | Verify model-authored unsafe text is sanitized | Output guard pytest groups | Unsafe warnings/suggestions/diagnostics are removed or replaced; evidence spans preserved |
| Bible/storyform context tests | Verify owner-controlled read/write behavior | Context route and project manager tests | Valid saves work; invalid storyform saves preserve files; candidate analysis does not overwrite truth |
| OMI MVP tests | Verify raw idea, candidate, decision, destination, promotion-record, and boundary behavior | Project manager, OMI route, and OMI boundary tests | OMI records stay under `omi/`; no promotion application; no durable truth mutation; no prose-generation destination/type path |
| Evaluation harness tests | Verify App-12/App-13 fixtures and offline harness | Evaluation fixture and baseline harness pytest groups; optional offline sample report | Fixtures load; fallback/refusal/guard behavior tracked; no training data or manifest writes |
| Full end-to-end MVP manual acceptance test | Exercise the app as a local writer | Manual checklist below | Owner can load project, edit/save scene, edit/save context, run Story Check, view diagnostics, create/review OMI candidates, create promotion records only, and confirm no prose generation path exists |

## Automated Backend Tests

Minimum backend suite for MVP exit:

- Full test suite.
- Story Check route tests.
- Analysis normalizer tests.
- Analysis engine tests with mocked model paths.
- Request guard tests.
- Output guard tests.
- Scene route tests.
- Context route tests.
- Project manager tests.
- OMI route tests.
- OMI boundary tests.
- Evaluation fixture tests.
- Baseline harness tests.

No automated backend test may require live Ollama unless explicitly marked as a manual or optional baseline smoke.

## Frontend Build Tests

Minimum frontend validation:

- `npm run build` passes.
- Known bundle-size warnings are recorded but do not block unless they indicate a new failure.
- No new dependency install is required during MVP exit validation unless explicitly documented.

## Manual Local Smoke Tests

Manual smoke should confirm:

- Backend starts.
- Frontend starts.
- Project navigation renders.
- Existing scene loads.
- Scene edit/save/reload works.
- Empty scene behavior remains intentional and safe.
- Bible/storyform panels load.
- Bible/storyform owner saves work with valid JSON.
- Storyform invalid JSON or invalid schema errors preserve existing files.
- Story Check button returns bounded structured diagnostics.
- OMI panel loads and shows candidate-only boundary copy.

## Story Check Mock Mode Tests

Mock mode must confirm:

- No Ollama request is made.
- Deterministic fixture output appears.
- Rich diagnostics render.
- Insufficient evidence remains visible.
- No generated story prose appears.
- No project truth file is mutated.

## Story Check qwen3 Baseline Tests

qwen3/Ollama baseline mode is optional for normal automated validation and required only for a final local baseline smoke when Ollama is available.

Baseline smoke must confirm:

- Explicit mode and endpoint are used.
- Returned JSON normalizes through the existing Story Check normalizer.
- Output guard runs after normalization.
- Unsafe prose-generation content is not exposed.
- Missing MC/IC/RS/CIPS/dynamics remain unresolved or insufficient evidence unless supported.
- No durable project truth is mutated.

## No-Prose Request Guard Tests

Request guard validation must cover:

- Write/draft/continue/rewrite/imitate/polish/improve/extend story prose requests.
- Standard refusal message.
- Allowed structural analysis and diagnostic question requests.
- Owner-authored scene, bible, storyform, raw idea, candidate content, decision notes, and promotion metadata are not treated as assistant request intent when saved.

## Output Guard Tests

Output guard validation must cover:

- Unsafe model-authored warnings.
- Unsafe suggestions.
- Unsafe reasons/concerns.
- Unsafe diagnostics.
- Severe multi-field leakage fallback.
- Exact owner-authored evidence span preservation.
- Analysis-only suggestions preserved.
- Insufficient-evidence fields preserved.

## Bible/Storyform Context Tests

Project context validation must cover:

- Read bible.
- Save bible as owner-authored JSON.
- Read storyform.
- Save valid storyform JSON.
- Reject invalid storyform without overwriting existing file.
- Story Check and OMI candidate outputs do not automatically overwrite context files.

## OMI Workflow Tests

OMI MVP validation must cover:

- Create/list/load raw idea.
- Create/list/load structured candidate.
- Owner decision update.
- Candidate destination update.
- Approval confirmation requirement.
- Promotion readiness blockers.
- Promotion record creation for approved confirmed candidates.
- Promotion record status remains record-only, not `promoted`.
- No apply-promotion route exists.
- No writes to `bible.json`, `storyform.json`, `scenes/`, `project.json`, `owner_memory.json`, planning notes, `training/data`, or `dataset_manifest.json`.
- No prose-generation candidate type or destination is accepted.
- Owner-authored raw ideas, candidate content, decision notes, and promotion metadata are not treated as assistant request intent when saved.
- UI boundary copy remains present and no generation/rewrite/continue/polish/improve controls appear.

## Evaluation Harness Tests

Evaluation validation must cover:

- App-level fixtures are outside `training/data`.
- Fixture README marks fixtures as not training data.
- Valid, minimal, malformed, refusal, insufficient-evidence, and unsafe-output fixtures are represented.
- Offline baseline harness reads fixtures and writes report JSON only.
- Live Ollama mode is explicit opt-in only.
- Report includes raw counts for tiny samples.

## Full End-to-End MVP Acceptance Checklist

- [ ] Repo status reviewed.
- [ ] Backend full tests pass.
- [ ] Focused backend tests pass.
- [ ] Frontend build passes.
- [ ] Backend starts locally.
- [ ] Frontend starts locally.
- [ ] Project loads.
- [ ] Scene edit/save/reload works.
- [ ] Bible/storyform read/write works.
- [ ] Story Check mock mode works.
- [ ] Story Check qwen3 baseline smoke passes when Ollama is available.
- [ ] Rich analysis sidebar renders bounded diagnostics.
- [ ] No-prose request guard behavior verified.
- [ ] Output guard behavior verified.
- [ ] OMI raw idea and candidate creation works.
- [ ] OMI owner decision/destination workflow works.
- [ ] OMI promotion records can be created only through gates.
- [ ] No durable project truth mutation occurs from Story Check or OMI candidate/promotion records.
- [ ] No generated story prose is created.
- [ ] No training data, SFT records, dataset manifest updates, model artifacts, or raw source text changes are created by MVP validation.

## Future Project Workspace Foundation Acceptance Areas

These are not part of the current MVP exit gate. They define the next milestone after MVP foundation acceptance:

`WORKSPACE-001` defines the detailed first usable workspace acceptance checklist in `docs/roadmap/project_workspace_foundation_spec.md`.
`WORKSPACE-002` defines project creation planning in `docs/roadmap/project_creation_flow_spec.md`, including blank creation, OMI-guided setup, safe `project_id` behavior, `project.json`, initial folder strategy, API/UI surfaces, and future project-creation tests.
`WORKSPACE-003` defines selector/library planning in `docs/roadmap/project_selector_library_spec.md`, including scan-first discovery, metadata cards/lists, sorting/filtering/search, opening/switching behavior, invalid/corrupt handling, archive/delete planning, API/UI surfaces, path safety, and future selector tests.
`WORKSPACE-004` defines OMI-guided creation planning in `docs/roadmap/omi_guided_project_creation_spec.md`, including owner-authored setup inputs, setup candidates, wizard/storage model, OMI-to-project handoff, no-prose/no-silent-promotion rules, API/UI surfaces, and future guided-creation tests.
`WORKSPACE-005` defines chapter/scene data model planning in `docs/roadmap/chapter_scene_data_model_spec.md`, including chapter records, scene Markdown compatibility, separate scene metadata, ID/order/movement rules, save/reload behavior, API/UI surfaces, future extraction provenance, and future chapter/scene tests.
`WORKSPACE-006` defines notes/materials data model planning in `docs/roadmap/notes_materials_data_model_spec.md`, including note/material body files, separate metadata, ID/linking rules, save/reload behavior, local search/filter, reference/license boundaries, API/UI surfaces, future extraction provenance, and future notes/materials tests.
`WORKSPACE-007` defines shared user-authored document editor workflow planning in `docs/roadmap/user_authored_document_editor_workflow_spec.md`, including scene/note/material document types, editor state, save/reload behavior, unsaved-change protections, conflict detection, no-prose UI safety, analysis/extraction separation, API/UI surfaces, and future editor workflow tests.
`WORKSPACE-008` defines Project Overview page planning in `docs/roadmap/project_overview_page_spec.md`, including safe overview content, sections, quick actions, recent document metadata, OMI status, approved memory/canon snapshot, health warnings, API/UI surfaces, and future overview tests.
`WORKSPACE-009` defines Chapters / Scenes page planning in `docs/roadmap/chapters_scenes_page_spec.md`, including page layout, chapter/scene operations, editor integration, ordering/consistency behavior, local search/filter, candidate-only analysis placeholder, API/UI surfaces, and future page tests.
`WORKSPACE-010` defines Notes / Materials page planning in `docs/roadmap/notes_materials_page_spec.md`, including page layout, note/material operations, editor integration, organization/linking behavior, local search/filter, provenance/license warnings, candidate-only extraction placeholder, API/UI surfaces, and future page tests.

- Project creation from scratch.
- Project selector/library.
- OMI-guided project creation and idea capture.
- Chapter/scene/note/material organization.
- User-authored prose editor save/reload without no-prose overblocking.
- Project Overview, Chapters/Scenes, Notes/Materials, OMI Ideas/Candidates, and Approved Memory/Canon pages.
- Candidate extraction from owner-authored material with evidence/provenance.
- Owner approval workflow for approve/reject/revise/archive/merge/split/mark-uncertain/request-more-evidence.
- Tests for no AI prose generation.
- Tests for no silent promotion.
- Tests proving pending/rejected candidates are not treated as canon.
- Tests proving approved memory/canon is project-local.

## Pass/Fail Recording Format

Use one row per validation item:

| Date | Area | Command or Method | Result | Evidence | Notes | Owner Exception |
| --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | Full backend automated tests | `.venv-unsloth-clean/bin/python -m pytest tests -q` | pass/fail/blocked | output summary or report path | Known warnings or blockers | none/owner-approved exception |
