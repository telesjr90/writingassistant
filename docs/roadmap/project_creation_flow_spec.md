# Project Creation Flow Spec

## 1. Purpose

This specification defines `WORKSPACE-002`, the detailed planning handoff for future project creation in the pre-Dramatica Project Workspace Foundation.

This is documentation only. It does not implement backend routes, frontend UI, tests, package changes, datasets, JSONL records, training data, model calls, OMI records, project runtime files, memory/canon files, extractor logic, Dramatica-specific logic, staging, commits, or pushes.

The future implementation target is safe local project creation before Dramatica-specific analysis, advanced extractors, RunPod work, Books 4-5, or fine-tuning.

The app remains analysis-only. It may store, edit, save, reload, and organize owner-authored prose, but the AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. Current Context Observed

Current runtime state, inspected read-only for planning:

- `backend/project_manager.py` stores project data under repo-local `projects/`.
- Existing helper `_safe_path_component()` rejects empty values, absolute paths, path traversal, `"."`, and `".."`.
- Existing scene operations use `projects/{project_name}/scenes/{scene_id}.md`.
- Existing OMI helpers can create project-local ideas, candidates, promotion audit records, and `omi/index.json` under an existing project path through owner actions.
- Existing OMI blocks prose-oriented destinations such as `scene_prose`, `dialogue`, `rewrite`, `continuation`, and `final_story_text`.
- `backend/main.py` exposes project-scoped scene, bible, storyform, Story Check, and OMI routes, but no project library or create-project route yet.
- `frontend/src/api.js` still hard-codes `PROJECT_ID = 'example'`.
- `frontend/src/components/ProjectNav.jsx` renders scene navigation for the current hard-coded project.
- `frontend/src/components/OMIPanel.jsx` displays candidate-only boundary copy and has no prose-generation controls.

This spec plans future work. It does not change those runtime files.

## 3. Project Creation Principles

Project creation must follow these principles:

- Local-first: project metadata and owner material live under repo-local `projects/{project_id}/`.
- Safe identity: `project_id` is a filesystem-safe identifier and a single path component.
- Display title is separate from `project_id`.
- Project creation must never call Ollama, qwen3, or any other live model.
- Project creation must never generate story prose.
- Owner-authored title, subtitle, description, premise note, setup note, tags, and idea text may be stored as owner input.
- Any future OMI setup suggestions are candidates only.
- No candidate becomes canon without explicit owner approval, destination, provenance/evidence where applicable, final confirmation, and a future apply-promotion action.
- Blank projects and OMI-guided projects produce the same safe project storage foundation.
- Dramatica/storyform data is optional and deferred; it must not be required to create a writing workspace project.
- Project creation must not create JSONL records, update `training/data/dataset_manifest.json`, write training data, or create model artifacts.

## 4. Blank Project Creation Flow

Blank project creation is the first implementation path.

### Step-by-Step Flow

1. Owner clicks **Create Project**.
2. Owner chooses **Blank Project**.
3. Owner enters required project title.
4. Owner may enter optional owner-authored metadata:
   - Subtitle.
   - Short owner note.
   - Description.
   - Genre or format tags.
   - Language.
   - Status.
5. App derives a proposed `project_id` from the title.
6. App shows the proposed `project_id` in an advanced/editable field or review step.
7. Owner accepts or edits the `project_id`.
8. App validates title and `project_id`.
9. App checks for project ID collision.
10. App creates the minimal safe project structure.
11. App writes `project.json`.
12. App creates initial folders or defers them according to the chosen folder strategy.
13. App opens the new Project Overview.
14. App shows next-step UI guidance such as "Create a chapter" or "Add a note".

Next-step prompts are UI guidance only. They are not AI output and must not generate premise prose, scene text, dialogue, chapter text, continuation, rewrite, polish, or style imitation.

### Required Validation

Project title:

- Required.
- Must be a string after trimming.
- Should have a practical maximum length, recommended 160 characters.
- May contain human-readable Unicode characters because it is JSON data, not a path.
- Must be safely serialized in `project.json`.

Project ID:

- Required, either derived or owner-provided.
- Must be one filesystem-safe path component.
- Must not be empty.
- Must not be `"."` or `".."`.
- Must not be an absolute path.
- Must not contain path separators.
- Must not contain path traversal.
- Must not contain control characters.
- Must not collide with an existing project unless the owner chooses a different ID.
- Must not be a reserved name.
- Must be stable after creation unless a future explicit rename/migration task updates all references.

Collision handling:

- First implementation should fail closed when the final `project_id` already exists.
- UI may propose suffixes such as `my-project-2`, but creation should proceed only after owner confirmation.
- The backend should never silently overwrite an existing project folder or `project.json`.

Write behavior:

- Project creation should be atomic where practical.
- If project creation fails after creating a folder, the backend should clean up only the files/folders it created in that transaction.
- If cleanup is unsafe or ambiguous, the operation should fail with a repair-needed state rather than deleting existing data.
- `project.json` writes should use the same atomic temp-file pattern already used for OMI record writes where practical.

## 5. OMI-Guided Project Creation Flow

OMI-guided project creation is a future guided setup path. It helps organize owner-provided ideas into setup candidates. It must not author story prose.

Detailed WORKSPACE-004 planning lives in `docs/roadmap/omi_guided_project_creation_spec.md`. This section remains the high-level creation-flow bridge; the dedicated spec defines owner-authored setup inputs, setup candidate classes, wizard flow, staged setup storage, OMI-to-project handoff, API/UI planning, no-prose/no-silent-promotion rules, and future tests.

### Current vs Future

Current OMI:

- Can store owner-authored raw ideas under a project.
- Can store structured candidates under a project.
- Can update owner decisions, statuses, and destinations.
- Can create promotion audit records only after gates pass.
- Does not apply promotions to durable truth.
- Does not call a model path for OMI.
- Does not generate story prose.

Future OMI-guided project creation:

- Is not implemented yet.
- Needs a pre-project wizard state or future pre-project idea inbox because no `project_id` exists before confirmation.
- Must reuse OMI no-prose, candidate-first, no-silent-promotion, provenance, and owner-control rules.

### Step-by-Step Flow

1. Owner clicks **Create Project**.
2. Owner chooses **OMI-Guided Setup**.
3. Owner enters an owner-authored raw idea.
4. App stores or stages the raw idea as owner input, not assistant output.
5. OMI may organize the idea into setup candidates only if a future rule/model path is explicitly allowed.
6. Setup candidates are shown with visible candidate labels.
7. Owner reviews, revises, approves, rejects, or leaves setup candidates pending.
8. Owner confirms the project title and `project_id`.
9. App creates the project only after explicit owner confirmation.
10. Approved setup fields may initialize `project.json`.
11. Pending or rejected setup candidates remain non-canon.
12. App opens the new Project Overview.
13. If durable OMI records are created, they live under the new project after confirmation.

### Allowed Setup Candidate Types

Future setup candidates may include:

- Project title candidate.
- Subtitle candidate.
- Genre or format tag candidate.
- Language candidate.
- Status candidate.
- Premise note candidate as owner-reviewed metadata, not story prose.
- Initial chapter or scene placeholder metadata, such as titles or labels only.
- Character candidate.
- Location or setting candidate.
- Object, organization, or faction candidate.
- Open question candidate.
- Diagnostic setup question.

### Prohibited OMI-Guided Outputs

OMI-guided creation must not generate:

- Story prose.
- Scene text.
- Chapter text.
- Dialogue.
- Opening pages.
- Endings.
- Blurbs written as story prose.
- Continuations.
- Rewrites.
- Polish/improvement text.
- Style imitation examples.
- AI text inserted into any editor field.

If the owner asks OMI to write or rewrite prose, the standard refusal message applies.

### Candidate and Canon Boundary

- Raw idea text is owner input.
- Setup suggestions are candidates.
- Candidate approval is not durable canon by itself.
- A project creation confirmation may write approved setup metadata to `project.json`.
- `project.json` metadata is not story canon.
- Rejected or pending setup candidates must not initialize approved memory/canon files.
- OMI promotion records are audit records only.
- Future apply-promotion remains separate and fail-closed.

## 6. Project ID Strategy

### Options Considered

1. **Slug derived from title**
   - Pros: simple, predictable, low friction.
   - Cons: title changes do not change ID; collisions need handling; non-ASCII titles need normalization.

2. **Owner-provided `project_id`**
   - Pros: explicit owner control.
   - Cons: higher friction; more validation errors.

3. **Generated ID independent from title**
   - Pros: avoids title collisions and rename concerns.
   - Cons: less readable in the filesystem.

4. **Hybrid derived slug with owner-editable advanced field**
   - Pros: readable by default, owner-correctable, low friction.
   - Cons: requires UI validation and preview.

### Recommended First Implementation

Use the hybrid strategy:

- Derive a lowercase ASCII slug from the title by default.
- Allow the owner to edit it before creation through an advanced field.
- Validate the final `project_id` server-side.
- On collision, fail closed and return suggested alternatives; require owner confirmation before retry.

### Recommended Normalization Rules

For the default derived slug:

- Trim whitespace.
- Lowercase.
- Normalize accented characters to closest ASCII where practical.
- Replace any run of non-allowed characters with `-`.
- Collapse repeated `-`.
- Trim leading and trailing `-`.
- Limit to 64 characters after trimming.
- If empty after normalization, use `project` plus a suffix suggestion.

Recommended allowed final `project_id` characters:

- `a-z`
- `0-9`
- `-`
- `_`

Recommended constraints:

- Maximum length: 64 characters for first implementation.
- Minimum length: 1 character after normalization.
- Must match a single component pattern equivalent to `^[a-z0-9][a-z0-9_-]{0,63}$`.
- Should not end with a path separator or contain `.` as a path component.
- Prefer not to allow `.` at all in first implementation to avoid hidden-file and extension ambiguity.

Reserved names for first implementation:

- `.`
- `..`
- `index`
- `new`
- `create`
- `api`
- `projects`
- `project`
- `memory`
- `omi`
- `scenes`
- `chapters`
- `notes`
- `materials`
- Windows device names: `con`, `prn`, `aux`, `nul`, `com1` through `com9`, `lpt1` through `lpt9`.

Examples:

| Title | Derived `project_id` |
| --- | --- |
| `The Long Road` | `the-long-road` |
| `Mara's Second Draft` | `mara-s-second-draft` |
| `Project: Night City` | `project-night-city` |
| `  Test   Project  ` | `test-project` |
| `!!!` | `project` plus collision-safe suffix suggestion |

### Collision Behavior

If `projects/{project_id}/` already exists:

- Do not overwrite.
- Return a 409-style conflict in API planning.
- Return safe alternatives such as `my-project-2` and `my-project-3`.
- Let the owner choose or edit before retry.

### Migration Concern for `example`

The current frontend hard-codes `PROJECT_ID = 'example'`. The first implementation may keep `example` as an existing legacy project during transition. A later library/selector implementation should:

- Add or derive `projects/example/project.json` only through a separate runtime task.
- Keep `example` stable until project selection replaces the hard-coded frontend ID.
- Avoid changing existing `bible.json`, `storyform.json`, scenes, OMI records, or fixture files as part of this documentation task.

## 7. Minimal `project.json` Schema

`project.json` stores durable project metadata. It is not story prose, not approved story canon, not raw model output, and not an OMI candidate store.

Recommended first schema:

```json
{
  "schema_version": "0.1.0",
  "project_id": "the-long-road",
  "title": "The Long Road",
  "subtitle": "",
  "description": "",
  "language": "en",
  "status": "active",
  "creation_method": "blank",
  "source": {
    "created_by": "owner",
    "created_from": "blank_project_form",
    "omi_idea_id": null,
    "omi_candidate_ids": []
  },
  "owner_authored_fields": [
    "title",
    "subtitle",
    "description"
  ],
  "default_view": "overview",
  "counts": {
    "chapters": 0,
    "scenes": 0,
    "notes": 0,
    "materials": 0,
    "omi_ideas": 0,
    "omi_candidates": 0,
    "approved_memory_records": 0
  },
  "capabilities": {
    "workspace": true,
    "omi": true,
    "story_check": false,
    "dramatica_analysis": false,
    "candidate_extraction": false,
    "apply_promotion": false
  },
  "owner_approved_truth_policy": {
    "durable_truth_requires_owner_approval": true,
    "candidate_outputs_do_not_promote_automatically": true,
    "ai_prose_generation_prohibited": true,
    "standard_refusal_message": "I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose."
  },
  "provenance": {
    "created_at": "2026-06-07T00:00:00Z",
    "updated_at": "2026-06-07T00:00:00Z",
    "created_by": "owner",
    "creation_method": "blank",
    "model": null,
    "model_call": false
  },
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z"
}
```

Required first fields:

- `schema_version`
- `project_id`
- `title`
- `status`
- `creation_method`
- `created_at`
- `updated_at`
- `owner_approved_truth_policy`
- `provenance`

Recommended optional fields:

- `subtitle`
- `description`
- `language`
- `source`
- `owner_authored_fields`
- `default_view`
- `counts`
- `capabilities`

Rules:

- `creation_method` should be `blank`, `omi_guided`, `imported`, or `legacy`.
- Owner-authored metadata fields may be stored directly.
- OMI-guided setup fields may enter `project.json` only after owner review and project-creation confirmation.
- `project.json` must not contain AI-generated story prose.
- `project.json` must not contain scene text, chapter prose, dialogue, raw model output, OMI candidate content, training records, or raw external source text.
- Counts may be omitted, computed on read, or stored as derived metadata. Counts are not project truth.
- `capabilities` are feature availability hints, not proof that runtime logic exists.

## 8. Initial Folder and File Creation Strategy

### Options Considered

1. **Lazy creation**
   - Create only `project.json`.
   - Create folders on first use.
   - Pros: fewer empty folders, clean diffs.
   - Cons: more empty-state branching and more first-use errors.

2. **Eager creation**
   - Create `project.json` and every future folder immediately.
   - Pros: predictable layout and simpler directory checks.
   - Cons: more empty clutter; may imply memory/canon exists before approval.

3. **Hybrid creation**
   - Create `project.json` and core workspace folders.
   - Defer memory/canon folders until apply-promotion or approved memory shell implementation.
   - Create OMI folders only when OMI setup/candidate flows are used, or create a clearly empty OMI index if the OMI page requires it.
   - Pros: supports first workspace use without implying canon.
   - Cons: still requires clear rules for deferred folders.

### Recommended First Implementation

Use hybrid creation:

```text
projects/{project_id}/
  project.json
  chapters/
  scenes/
  scene_metadata/
  notes/
  note_metadata/
  materials/
  material_metadata/
```

For blank projects:

- Create the core workspace folders above.
- Defer `omi/` until the OMI page creates the first idea/candidate, unless the UI needs an empty OMI index for display.
- Defer `memory/` until the future approved-memory/canon page or apply-promotion task explicitly creates approved records.
- Do not create `bible.json` or `storyform.json` unless a later compatibility task decides current Story Check requires them for a newly created workspace project.

For OMI-guided projects:

- Create the same core workspace folders.
- If setup records must persist after confirmation, create:

```text
projects/{project_id}/
  omi/
    ideas/
    candidates/
    promotions/
    index.json
```

- Store owner raw idea and setup candidates only after project confirmation unless a pre-project inbox is separately implemented.
- Do not create `memory/` from setup candidates.

Rollback:

- Project creation should track every new folder/file it creates.
- On failure, remove only transaction-created empty folders/files.
- Never remove an existing project folder on collision.

## 9. Project Library and Index Strategy

Project library behavior is specified in `WORKSPACE-003` at `docs/roadmap/project_selector_library_spec.md`, but project creation must support it.

### Recommended First Implementation

Scan `projects/` for folders that contain a valid `project.json`.

Reasons:

- Avoids index consistency bugs during initial project creation.
- Keeps project creation atomic around one metadata file.
- Lets the library recover if `projects/index.json` is missing or stale.
- Avoids treating a derived index as story truth.

### Listing Rules

Future project listing should:

- Read only lightweight metadata from `project.json` and maybe small derived counts.
- Avoid reading full scene/note/material content.
- Validate every project folder name as a safe path component before including it.
- Require `project.json` to be a JSON object.
- Handle missing/corrupt metadata with a repair/import-needed state.
- Never auto-delete corrupt projects.
- Sort by `updated_at` descending by default, with title sort available later.
- Show `project_id`, title, status, updated date, creation method, and basic counts.

### Optional Future `projects/index.json`

`projects/index.json` may be added later as a derived navigation cache:

- It should be rebuildable from project folders.
- It is not story truth.
- It must not contain story prose, raw model output, OMI candidate content, approved memory/canon records, JSONL records, or raw source text.
- It should be updated after project create/update only if the implementation can keep it consistent.

## 10. Future API Planning

These routes are planning targets only.

### `GET /api/projects`

Purpose:

- List local projects for the project library.

Response shape:

```json
{
  "projects": [
    {
      "project_id": "the-long-road",
      "title": "The Long Road",
      "status": "active",
      "creation_method": "blank",
      "updated_at": "2026-06-07T00:00:00Z",
      "counts": {
        "chapters": 0,
        "scenes": 0,
        "notes": 0,
        "materials": 0,
        "omi_candidates": 0,
        "approved_memory_records": 0
      },
      "metadata_status": "valid"
    }
  ],
  "errors": []
}
```

Validation and boundaries:

- Does not call a model.
- Does not read full prose content.
- Does not write files.
- Does not treat pending candidates as canon.
- Returns corrupt/missing metadata as an error row or `metadata_status`, not a crash.

Expected errors:

- 500 only for unexpected application failures.
- Corrupt project metadata should be represented in response data where practical.

### `POST /api/projects`

Purpose:

- Create a blank project.

Request shape:

```json
{
  "title": "The Long Road",
  "project_id": "the-long-road",
  "subtitle": "",
  "description": "",
  "language": "en",
  "tags": ["novel"],
  "status": "active"
}
```

Response shape:

```json
{
  "project": {
    "project_id": "the-long-road",
    "title": "The Long Road",
    "status": "active",
    "creation_method": "blank",
    "default_view": "overview",
    "created_at": "2026-06-07T00:00:00Z",
    "updated_at": "2026-06-07T00:00:00Z"
  },
  "created_paths": [
    "project.json",
    "chapters/",
    "scenes/",
    "scene_metadata/",
    "notes/",
    "note_metadata/",
    "materials/",
    "material_metadata/"
  ]
}
```

Validation:

- Title required.
- `project_id` required or derived before backend call.
- `project_id` must pass safe component and stricter slug rules.
- Collision returns conflict.
- Optional metadata must be JSON-serializable and length-limited.

No-prose boundary:

- Request fields are owner-authored metadata, not assistant request intent.
- No freeform model request is accepted.
- No model call is made.
- No AI text is generated.

Candidate/canon boundary:

- No OMI candidate is created.
- No memory/canon file is created.
- No bible/storyform truth is inferred.

Expected errors:

- 400 invalid title or metadata.
- 400 invalid `project_id`.
- 409 project already exists.
- 500 write failure with repair/rollback details.

### `GET /api/projects/{project_id}`

Purpose:

- Load project metadata for the selected project.

Response shape:

```json
{
  "project": {
    "project_id": "the-long-road",
    "title": "The Long Road",
    "status": "active",
    "creation_method": "blank",
    "updated_at": "2026-06-07T00:00:00Z"
  }
}
```

Validation and boundaries:

- `project_id` must be a safe path component.
- Reads `project.json` only.
- Does not read full prose content.
- Does not call a model.
- Does not promote candidates.

Expected errors:

- 400 invalid `project_id`.
- 404 project or `project.json` not found.
- 400 corrupt `project.json`.

### `PATCH /api/projects/{project_id}`

Purpose:

- Update owner-authored project metadata.

Request shape:

```json
{
  "title": "The Long Road",
  "subtitle": "",
  "description": "",
  "language": "en",
  "status": "active"
}
```

Validation and boundaries:

- `project_id` path does not change through this route.
- Owner-authored metadata saves are allowed and should not be blocked as assistant prose requests.
- Does not call a model.
- Does not generate prose.
- Does not mutate scenes, OMI candidates, promotion records, memory/canon, bible, or storyform.

Expected errors:

- 400 invalid `project_id`, invalid metadata, or invalid status.
- 404 project not found.
- 409 if a future update conflicts with another write.

### `POST /api/projects/from-omi`

Purpose:

- Future OMI-guided project creation after owner confirmation.

Request shape:

```json
{
  "raw_idea": "Owner-authored setup idea.",
  "approved_setup": {
    "title": "The Long Road",
    "project_id": "the-long-road",
    "subtitle": "",
    "description": "",
    "language": "en",
    "tags": ["novel"]
  },
  "setup_candidate_decisions": [
    {
      "candidate_id": "temporary-or-existing-id",
      "decision": "approve"
    }
  ],
  "final_confirmation": true
}
```

Validation and boundaries:

- Requires final confirmation.
- Requires a safe `project_id`.
- Raw idea is owner input.
- Setup candidates remain candidates unless approved for metadata initialization.
- Does not write story prose.
- Does not call a model unless a future separately approved setup-candidate generation path exists.
- Does not create memory/canon files.
- Does not apply OMI promotion records.

Expected errors:

- 400 missing confirmation.
- 400 invalid setup fields.
- 400 invalid `project_id`.
- 409 project collision.
- 500 write failure with repair/rollback details.

### `GET /api/projects/{project_id}/summary`

Purpose:

- Future lightweight Project Overview data.

Response shape:

```json
{
  "project": {},
  "counts": {},
  "recent": {
    "chapters": [],
    "scenes": [],
    "notes": []
  },
  "omi_status": {
    "pending_candidates": 0,
    "approved_candidates": 0,
    "promotion_records": 0
  },
  "approved_memory_status": {
    "available": false,
    "record_count": 0
  }
}
```

Boundaries:

- Reads lightweight metadata and counts.
- Does not present pending candidates as canon.
- Does not generate summaries with AI.
- Does not call a model.

## 11. Future Frontend Planning

Future UI surfaces:

- Project Library screen.
- Project switcher or selector in the app shell.
- Create Project modal or page.
- Blank Project tab.
- OMI-Guided Project tab.
- Project ID preview and advanced edit field.
- Collision/error display.
- Project Overview after creation.
- Safe empty-state copy for first chapter/scene/note creation.
- OMI Ideas and Candidates entry point for guided setup.

UI rules:

- UI copy may guide the owner through workflow steps.
- UI copy must not generate story prose.
- No AI writing buttons.
- No controls named or behaving like "write my story", "continue", "rewrite", "polish", "improve", "make this better", "draft dialogue", or "imitate this style".
- OMI-guided setup is idea organization and candidate review only.
- Owner-authored fields must be clearly distinct from assistant output.
- Candidate setup fields must carry candidate labels until approved.
- Project creation success should open Project Overview for the selected project.
- Frontend state should replace the hard-coded `PROJECT_ID = 'example'` only in a future implementation task after the project selector/library plan is ready.

Safe empty-state copy examples:

- "Create a chapter."
- "Add a scene."
- "Add an owner-authored note."
- "Capture an idea in OMI."

Unsafe copy/control examples:

- "Write my opening."
- "Continue this chapter."
- "Rewrite this scene."
- "Polish this prose."
- "Generate dialogue."

## 12. Future Tests

Future implementation should add tests before or with runtime changes.

Project creation tests:

- Create blank project with valid title.
- Derive `project_id` slug from title.
- Accept owner-edited `project_id`.
- Reject invalid `project_id`.
- Reject path traversal.
- Reject absolute paths.
- Reject empty/dot/dot-dot IDs.
- Reject reserved names.
- Handle collision without overwrite.
- Create `project.json` with expected schema.
- Create expected initial folders according to the selected hybrid strategy.
- Roll back partial creation on simulated write failure where practical.

Project library tests:

- Created project appears in `GET /api/projects`.
- Missing `project.json` is represented safely.
- Corrupt `project.json` is represented safely.
- Listing does not read full scene/note prose content.
- Listing does not auto-delete corrupt project folders.

No-prose and safety tests:

- Owner-authored title, description, and setup notes are not blocked by no-prose guard.
- Owner-authored raw OMI idea is not blocked as assistant request intent.
- No AI prose-generation fields/buttons are present in project creation UI.
- Project creation does not call Ollama/qwen3/live models.
- Project creation does not create or modify JSONL files.
- Project creation does not update `training/data/dataset_manifest.json`.
- Project creation does not create model artifacts or training reports.
- Project creation does not mutate `bible.json`, `storyform.json`, scenes, memory/canon, or OMI promotion records unless explicitly part of the creation route contract.

OMI-guided creation tests:

- Raw idea is stored or staged as owner input.
- Setup candidates remain candidates.
- Approved setup metadata can initialize `project.json` only after final confirmation.
- Rejected/pending setup candidates do not enter `project.json` or canon.
- No story prose, scene text, dialogue, continuation, rewrite, polish, or style imitation is generated.

Frontend tests:

- Project Library empty state renders.
- Create Project form validates title.
- Project ID preview is visible.
- Collision/invalid ID errors are visible.
- Successful creation selects the new project.
- No unsafe generation controls appear.

## 13. Deferred Decisions

These remain for implementation or later planning tasks:

- Whether `project_id` collision suffixes are generated server-side, client-side, or both.
- Exact `project_id` maximum length after implementation constraints are known.
- Whether Unicode transliteration for slugs uses a dependency-free standard-library approach or a small local helper.
- Whether `projects/index.json` is introduced in WORKSPACE-003 or deferred until after scanning works.
- Whether OMI-guided setup uses temporary wizard state, session-local storage, or a durable pre-project inbox.
- WORKSPACE-004 recommends staged setup state for the first implementation, converted into project-local OMI records only after owner confirmation and successful project creation.
- Whether a blank project should create `omi/index.json` immediately for UI convenience.
- Whether a blank project should create compatibility `bible.json` and `storyform.json` or defer those until Story Check is used.
- Whether `description` is enough for a first owner-authored premise note or whether a separate `notes/` record should be created after confirmation.
- Whether project deletion/archive is planned before or after the project selector implementation.
- Whether project renaming can change title only or also supports future `project_id` migration.
- Exact browser/manual acceptance checklist for the first create-project implementation.

## 14. Related Specifications

- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_selector_library_spec.md`
- `docs/roadmap/omi_guided_project_creation_spec.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/mvp_completion_test_matrix.md`
- `docs/master_plan.md`
- `docs/plan.md`
