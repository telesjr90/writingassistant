# OMI-Guided Project Creation and Idea Capture Spec

## 1. Purpose

This specification defines `WORKSPACE-004`, the detailed planning handoff for future OMI-guided project creation and owner-authored idea capture in the pre-Dramatica Project Workspace Foundation.

This is documentation only. It does not implement backend routes, frontend UI, tests, package changes, datasets, JSONL records, training data, model calls, OMI records, project runtime files, memory/canon files, extractor logic, Dramatica-specific logic, staging, commits, or pushes.

The future implementation target is an owner-controlled OMI-guided setup flow that captures an initial project idea, organizes owner-provided material into setup candidates, prepares project metadata, optionally prepares candidate project-structure suggestions, and creates a project only after explicit owner confirmation.

The app remains analysis-only. It may store, edit, save, reload, and organize owner-authored prose and owner-authored ideas, but the AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. Current Context Observed

Current runtime state, inspected read-only for planning:

- `backend/project_manager.py` stores project data under repo-local `projects/`.
- Existing helper `_safe_path_component()` rejects empty values, absolute paths, path traversal, `"."`, and `".."`.
- Current OMI helpers can create project-local raw ideas, structured candidates, promotion audit records, and `omi/index.json` only under an existing project path.
- Current OMI blocks prose-oriented destinations such as `scene_prose`, `dialogue`, `rewrite`, `continuation`, and `final_story_text`.
- Current OMI promotion records are audit records only and do not apply durable truth.
- `backend/main.py` exposes project-scoped OMI routes, but no pre-project setup route and no project creation route.
- `frontend/src/api.js` still hard-codes `PROJECT_ID = 'example'`.
- `frontend/src/components/OMIPanel.jsx` exposes current project-local raw idea and candidate planning UI, but not OMI-guided project creation.
- WORKSPACE-002 defines blank project creation and high-level OMI-guided creation rules.
- WORKSPACE-003 defines project selector/library behavior after projects exist.

This spec plans future work. It does not change those runtime files.

## 3. OMI-Guided Creation Purpose

OMI-guided project creation should help the owner:

- Capture an initial project idea.
- Organize owner-provided idea material into candidate setup fields.
- Prepare project metadata before creation.
- Optionally prepare candidate project structure suggestions.
- Review, revise, approve, reject, or defer setup candidates.
- Preserve owner control over what initializes the project.
- Create a project only after explicit owner confirmation.
- Keep setup candidates separate from project canon and approved memory.

OMI-guided creation must not:

- Generate story prose.
- Generate scene text, chapter text, dialogue, openings, endings, blurbs, continuations, rewrites, polish, improvement text, or style imitation examples.
- Treat setup candidates as canon.
- Promote candidates silently.
- Create approved memory/canon records.
- Mutate `memory/`, `bible.json`, `storyform.json`, `scenes/`, `chapters/`, `notes/`, or `materials/` as story truth.
- Call a model unless a later guarded request path is explicitly implemented and tested.
- Create JSONL records, update `training/data/dataset_manifest.json`, write training data, or create model artifacts.

## 4. Allowed Owner-Authored Inputs

The OMI-guided setup flow may accept owner-entered fields such as:

- Raw idea.
- Working title.
- Subtitle.
- Genre or tags.
- Language.
- Owner-authored description.
- Owner-authored premise note.
- Project goals.
- Intended format.
- Notes about characters.
- Notes about locations or settings.
- Notes about themes.
- Notes about plot ideas.
- Notes about research needs.
- Owner-authored prose snippets used as source input.

Rules:

- These fields are owner-authored input.
- Saving these fields must not be blocked as AI prose generation.
- Owner-authored prose snippets can be stored as owner input, but AI must not generate, rewrite, continue, polish, improve, imitate, or extend them.
- Owner-authored idea text is not automatically approved canon.
- Owner-authored setup metadata may initialize `project.json` only when it is explicitly selected for project creation.
- Owner-authored notes about characters, locations, themes, or plot ideas remain project setup input or OMI candidates until later owner-approved promotion.
- Storing an owner-authored description or premise note in `project.json` does not make it story canon; it is project metadata.
- Raw ideas and setup notes must not be copied into `bible.json`, `storyform.json`, `memory/`, scenes, chapters, notes, or materials without a separate explicit owner action and route contract.

## 5. Candidate Setup Outputs

Future setup candidates may include these candidate classes.

| Candidate class | Purpose | Allowed initialization target |
| --- | --- | --- |
| `project_title_candidate` | Candidate display title or title variants from owner-provided text | `project.json.title` only after owner selection and confirmation |
| `project_metadata_candidate` | Candidate language, status, format, goals, or metadata fields | Specific `project.json` metadata fields only after confirmation |
| `genre_tag_candidate` | Candidate genre, format, or tag labels | `project.json.tags` or equivalent metadata only after confirmation |
| `premise_note_candidate` | Candidate owner-reviewed premise/setup note metadata | `project.json.description` or future owner note only after confirmation |
| `initial_chapter_candidate` | Candidate chapter placeholder metadata such as label/order | Future chapter metadata only if a later task allows it; not chapter prose |
| `initial_scene_placeholder_candidate` | Candidate scene placeholder metadata such as title/label/status | Future scene metadata only if a later task allows it; not scene prose |
| `character_candidate` | Candidate character setup note from owner input | OMI candidate only; future memory promotion requires later apply-promotion |
| `location_candidate` | Candidate location/setting setup note from owner input | OMI candidate only; future memory promotion requires later apply-promotion |
| `object_candidate` | Candidate object/item/setup note from owner input | OMI candidate only; future memory promotion requires later apply-promotion |
| `plot_thread_candidate` | Candidate plot thread or unresolved thread from owner input | OMI candidate only; future memory promotion requires later apply-promotion |
| `open_question_candidate` | Diagnostic project setup question for owner review | OMI candidate or review checklist only |
| `research_note_candidate` | Candidate research need or owner-supplied research note | OMI candidate or future material metadata only after explicit owner action |

Candidate rules:

- Setup candidates are not canon.
- WORKSPACE-005 defines the future chapter/scene metadata contract that any later import of `initial_chapter_candidate` or `initial_scene_placeholder_candidate` must follow.
- Candidates need owner review.
- Pending candidates must not initialize project metadata.
- Rejected candidates must not initialize project metadata.
- Approved setup fields may initialize `project.json` only after explicit final confirmation.
- Candidate approval is not apply-promotion to memory/canon.
- Candidate setup suggestions must be visibly labeled as candidates.
- Candidate setup records must include provenance linking them to owner input or manual owner edits.
- No generated story prose, dialogue, scene text, chapter prose, continuation, rewrite, polish, improvement, or style imitation is allowed.

## 6. OMI Wizard Flow

Future wizard flow:

1. Owner chooses OMI-guided project creation.
2. Owner captures raw idea as owner input.
3. Owner optionally captures title, metadata, tags, language, format, project goals, or setup notes.
4. App stores or stages raw idea safely.
5. App presents structured setup candidates.
6. Owner reviews, revises, approves, rejects, archives, or leaves candidates pending.
7. Owner chooses which approved fields initialize the project.
8. Owner confirms project creation.
9. Project is created using WORKSPACE-002 project creation rules.
10. Owner lands on Project Overview.
11. Unapproved candidates remain in OMI, not canon.

Current vs future:

- Current runtime OMI can store raw ideas and structured candidates under an existing project.
- Current runtime OMI can update owner decisions and create promotion audit records under an existing project.
- Current runtime OMI cannot create projects.
- Current runtime OMI has no pre-project setup storage.
- Current runtime OMI does not call a model path for candidate generation.
- Future OMI-guided project creation needs new routes, UI, and storage decisions.
- Future project creation still follows WORKSPACE-002 safe `project_id`, collision, `project.json`, and rollback rules.

Wizard safety:

- The owner can leave the wizard without creating a project.
- Leaving the wizard must not create a partial project unless the owner has confirmed creation.
- Setup candidates must remain visible as candidates.
- The final confirmation step must show the exact metadata fields that will initialize `project.json`.
- Project creation must fail closed if `project_id` validation or collision checks fail.

## 7. Pre-Project vs Project-Local OMI Storage

### Option A: Transient Wizard State Until Project Creation

Description:

- Keep all setup input and candidates in frontend/session wizard state until the owner confirms project creation.
- After confirmation, create the project and then write project-local OMI records if needed.

Pros:

- Simple.
- Avoids orphaned pre-project records.
- Avoids accidental project creation.
- No new pre-project storage model.

Cons:

- Less durable if the browser/app closes.
- Weaker audit trail before project creation.
- Harder to resume abandoned setup later.

### Option B: Temporary Pre-Project OMI Inbox

Description:

- Add a durable pre-project inbox outside `projects/{project_id}/`.
- Store setup IDs, raw ideas, setup candidates, and owner decisions before a project exists.

Pros:

- Durable and resumable.
- Good audit trail for abandoned setup.

Cons:

- New storage area and lifecycle.
- Orphan cleanup required.
- More path safety and privacy rules.
- More migration complexity into project-local OMI.

### Option C: Create Project First, Then Store OMI Project-Locally

Description:

- Create a minimal project early, then store setup OMI records under `projects/{project_id}/omi/`.

Pros:

- Reuses current project-local OMI model.
- Strong traceability after creation.

Cons:

- Can create accidental empty projects.
- Requires project identity before setup is complete.
- Failed or abandoned setup may leave partial projects.

### Option D: Hybrid Staged Setup Object Converted After Confirmation

Description:

- Store a bounded staged setup object for the wizard.
- The staged setup may be transient in the first implementation.
- After owner confirmation and successful project creation, convert selected setup data into `project.json` and copy raw idea/candidate records into project-local `omi/`.
- Future implementation may make staged setup durable if resumability is needed.

Pros:

- Keeps first implementation simple.
- Avoids orphaned durable OMI records.
- Avoids accidental project creation.
- Preserves traceability after confirmation.
- Supports safe rollback.
- Keeps project-local OMI as the durable post-creation model.
- Does not write training/data files.

Cons:

- First version may not resume abandoned setup after browser/app close.
- Requires careful conversion logic and source snapshots.

### Recommended First Implementation

Use Option D with transient staged setup state first.

Recommended behavior:

- Keep pre-confirmation setup in a staged setup object.
- The staged setup object is not canon.
- The staged setup object is not training data.
- The staged setup object does not create a project folder by itself.
- On final confirmation, create the project using WORKSPACE-002 rules.
- After successful project creation, write project-local OMI idea/candidate records for the raw idea and any setup candidates that should remain traceable.
- If project creation fails, do not leave a project-local OMI record.
- If OMI record import fails after project creation, mark the project as created with setup import warning rather than silently treating candidates as canon.

## 8. OMI-to-Project Creation Handoff

Approved fields that may initialize `project.json` after final confirmation:

- `title`
- `subtitle`
- `description`
- `language`
- `status`
- `creation_method: "omi_guided"`
- Tags or genre labels.
- `source.created_from: "omi_guided_setup"`
- `source.omi_setup_id`
- `source.omi_idea_id` after project-local record creation.
- `source.omi_candidate_ids` for approved metadata candidates used at creation.
- `owner_authored_fields`
- `provenance.created_by: "owner"`
- `provenance.creation_method: "omi_guided"`
- `provenance.model_call: false` unless a future guarded model path exists.
- `owner_approved_truth_policy`

Project-local OMI after creation:

- Raw idea may become an OMI idea record with `source_type: "project_setup_idea"`.
- Setup candidates may become OMI candidate records with `candidate_type` matching the setup class.
- Approved metadata candidates used to initialize `project.json` should be marked as used for setup metadata, not promoted to canon.
- Pending setup candidates should remain pending OMI candidates or be omitted if the owner chooses not to carry them forward.
- Rejected candidates should be archived, discarded, or omitted according to the owner choice and route contract.
- Every carried-forward candidate should preserve provenance linking it to the setup raw idea and project creation confirmation.

Handoff rules:

- The owner must explicitly confirm project creation.
- The owner must explicitly choose which setup fields initialize the project.
- `creation_method` must be recorded as `omi_guided`.
- Final confirmation should be captured in the setup handoff record or project provenance.
- Project creation uses WORKSPACE-002 validation, safe `project_id`, collision, folder creation, and rollback rules.
- This handoff is not apply-promotion to memory/canon.
- This handoff must not create `memory/*.json`.
- This handoff must not write `bible.json` or `storyform.json` as truth.
- This handoff must not write scene or chapter prose.

## 9. No-Prose and No-Silent-Promotion Rules

OMI-guided setup cannot generate story prose.

Prohibited controls and requests:

- Write opening.
- Write scene.
- Write chapter.
- Continue.
- Rewrite.
- Polish.
- Improve.
- Make this better.
- Draft dialogue.
- Imitate style.
- Generate sample prose.
- Insert AI text into the editor.

Boundary rules:

- Raw idea save is owner input, not an AI request.
- Setup candidates are planning metadata, not prose.
- OMI cannot write to `scenes/`.
- OMI cannot write to `memory/`.
- OMI cannot write to `bible.json` or `storyform.json` as truth.
- OMI cannot create approved canon without explicit owner promotion and future apply-promotion.
- OMI cannot call a model unless a future guarded request path is implemented and tested.
- Any future model-authored setup candidate path must run no-prose request guards before the model call and output guards after the model output.
- Pending and rejected candidates must not initialize project truth.
- Approved setup metadata can initialize only allowed project metadata fields after final owner confirmation.

If the owner asks OMI to write or rewrite prose, the standard refusal message applies.

## 10. API Planning

These routes are planning targets only. They are not implemented by this documentation task.

### `POST /api/omi/project-setups`

Purpose:

- Create a staged OMI-guided project setup from owner-authored input.

Request shape:

```json
{
  "raw_idea": "Owner-authored idea text.",
  "working_title": "Owner title",
  "subtitle": "",
  "description": "",
  "premise_note": "",
  "language": "en",
  "tags": ["novel"],
  "project_goals": [],
  "intended_format": "novel",
  "owner_notes": {}
}
```

Response shape:

```json
{
  "setup": {
    "setup_id": "setup_0001",
    "status": "draft",
    "raw_idea": "Owner-authored idea text.",
    "owner_inputs": {},
    "setup_candidates": [],
    "created_at": "2026-06-07T00:00:00Z",
    "updated_at": "2026-06-07T00:00:00Z"
  }
}
```

Validation:

- `raw_idea` or at least one owner-authored setup field is required.
- Fields must be length-limited and JSON-serializable.
- This route does not require a `project_id`.
- If a `project_id` preview is included later, it must use WORKSPACE-002 validation rules before creation.

No-prose boundary:

- Request fields are owner-authored input.
- Saving owner-authored raw idea and setup notes must not be blocked as assistant prose generation.
- The route does not call a model in the first implementation.

Candidate/canon boundary:

- Creates only staged setup state.
- Does not create a project.
- Does not create project-local OMI records yet.
- Does not create memory/canon or project truth.

Expected errors:

- 400 missing input.
- 400 invalid field shape or size.
- 413 payload too large.
- 500 unexpected storage failure if future durable staging exists.

### `GET /api/omi/project-setups/{setup_id}`

Purpose:

- Load a staged setup for review or continuation.

Response shape:

```json
{
  "setup": {
    "setup_id": "setup_0001",
    "status": "owner_review",
    "owner_inputs": {},
    "setup_candidates": [],
    "selected_initialization_fields": {},
    "provenance": {}
  }
}
```

Validation:

- `setup_id` must be a safe identifier.
- If first implementation uses transient browser state only, this route may be deferred.

No-prose boundary:

- Returns owner input and setup metadata only.
- Does not generate or summarize prose.

Candidate/canon boundary:

- Returned candidates remain candidates.
- Does not open or mutate a project.

Expected errors:

- 400 invalid `setup_id`.
- 404 setup not found.

### `PATCH /api/omi/project-setups/{setup_id}`

Purpose:

- Update owner inputs, setup candidates, owner decisions, selected initialization fields, or setup status before final creation.

Request shape:

```json
{
  "owner_inputs": {
    "working_title": "Owner title",
    "description": "Owner-authored metadata."
  },
  "candidate_decisions": [
    {
      "candidate_id": "setup_candidate_0001",
      "decision": "approve",
      "approval_confirmed": true,
      "notes": ""
    }
  ],
  "selected_initialization_fields": {
    "title": "Owner title",
    "description": "Owner-authored metadata.",
    "tags": ["novel"]
  },
  "status": "owner_review"
}
```

Response shape:

```json
{
  "setup": {
    "setup_id": "setup_0001",
    "status": "owner_review",
    "setup_candidates": [],
    "selected_initialization_fields": {}
  }
}
```

Validation:

- `setup_id` must be safe.
- Candidate decisions must use allow-listed statuses.
- Only allowed fields may be selected for initialization.
- Selected `project_id`, if present, must pass WORKSPACE-002 validation before final creation.

No-prose boundary:

- Owner-authored fields are allowed.
- Route must not rewrite owner input.
- Route must not generate prose.

Candidate/canon boundary:

- Candidate decisions affect setup state only.
- Approval here does not create memory/canon.
- Approval here does not write to bible/storyform/scenes.

Expected errors:

- 400 invalid setup ID, field, or decision.
- 404 setup not found.
- 409 stale setup version if future versioning exists.

### `POST /api/projects/from-omi`

Purpose:

- Create a project from an owner-confirmed OMI-guided setup.

Request shape:

```json
{
  "setup_id": "setup_0001",
  "project_id": "owner-project",
  "selected_initialization_fields": {
    "title": "Owner Project",
    "subtitle": "",
    "description": "Owner-authored metadata.",
    "language": "en",
    "status": "active",
    "tags": ["novel"]
  },
  "candidate_ids_to_import": ["setup_candidate_0001"],
  "final_confirmation": true
}
```

Response shape:

```json
{
  "project": {
    "project_id": "owner-project",
    "title": "Owner Project",
    "creation_method": "omi_guided",
    "default_view": "overview"
  },
  "omi_import": {
    "idea_id": "idea_0001",
    "candidate_ids": ["omi_candidate_0001"],
    "warnings": []
  }
}
```

Validation:

- Requires `final_confirmation: true`.
- `project_id` must follow WORKSPACE-002 safe path and collision rules.
- Selected fields must be allowed project metadata fields.
- Pending/rejected candidates cannot initialize project metadata.
- Candidate import must not target blocked prose destinations.

No-prose boundary:

- Does not call a model.
- Does not generate project prose.
- Does not create scene/chapter text.

Candidate/canon boundary:

- Creates project metadata and optional project-local OMI records only.
- Does not create memory/canon.
- Does not apply OMI promotion records.
- Does not write bible/storyform truth.

Expected errors:

- 400 missing confirmation.
- 400 invalid setup, selected fields, or `project_id`.
- 404 setup not found.
- 409 project ID collision.
- 422 candidate state does not permit initialization.
- 500 write failure with repair/rollback details.

### `POST /api/projects/{project_id}/omi/import-setup` Later

Purpose:

- Import a staged setup's raw idea and setup candidates into an already-created project if project creation succeeded but OMI import was deferred or retried.

Request shape:

```json
{
  "setup_id": "setup_0001",
  "candidate_ids": ["setup_candidate_0001"],
  "final_confirmation": true
}
```

Response shape:

```json
{
  "idea_id": "idea_0001",
  "candidate_ids": ["omi_candidate_0001"],
  "warnings": []
}
```

Validation:

- `project_id` must be safe.
- Project must exist and have valid `project.json`.
- Requires final confirmation.
- Setup candidates must be imported as OMI candidates only.

No-prose boundary:

- Does not generate text.
- Does not call a model.

Candidate/canon boundary:

- Imports OMI idea/candidate records only.
- Does not apply promotion.
- Does not write memory/canon, scenes, bible, or storyform truth.

Expected errors:

- 400 invalid `project_id` or setup state.
- 404 project or setup not found.
- 409 setup already imported.
- 422 candidate state invalid for import.

## 11. Frontend Planning

Future UI surfaces:

- OMI-guided creation tab.
- Raw idea capture form.
- Optional owner metadata fields.
- Candidate setup review panel.
- Approval/revision controls.
- Project ID preview.
- Project metadata preview.
- Final confirmation step.
- Safe empty states.
- Blocked-prose-request messaging.
- Link to created Project Overview.

OMI-guided creation tab:

- Lives in the future Create Project flow beside Blank Project.
- Explains candidate-only setup behavior.
- Captures owner input without calling a model by default.

Raw idea capture form:

- Accepts owner-authored idea text.
- May include title, subtitle, description, tags, language, goals, format, and setup notes.
- Does not treat owner-authored prose snippets as assistant requests.

Candidate setup review panel:

- Shows setup candidates with visible candidate labels.
- Shows source/provenance.
- Lets owner approve, reject, revise, archive, or leave pending.
- Separates metadata initialization candidates from story-knowledge candidates.

Final confirmation:

- Shows exact `project_id`.
- Shows exact metadata that will initialize `project.json`.
- Shows which candidates will be imported into project-local OMI.
- Requires explicit confirmation.
- Links to Project Overview after success.

UI prohibitions:

- No AI writing buttons.
- No generated story prose display as project content.
- No "generate project", "write my story", "write opening", "continue", "rewrite", "polish", "improve", "draft dialogue", or "imitate this style" controls.
- Candidate setup fields must be visibly labeled.
- OMI-guided setup remains idea organization and candidate review only.

## 12. Future Tests

Future implementation should add tests before or with runtime changes.

Owner input and staging tests:

- Owner raw idea can be saved or staged without no-prose overblocking.
- Owner-authored title, description, premise note, project goals, and setup notes can be saved or staged.
- Owner-authored prose snippets are stored as owner input, not generated output.
- Prose-generation requests receive the standard refusal message when routed through a future guarded request path.

Candidate tests:

- Setup candidates remain candidates.
- Pending candidates do not initialize project metadata.
- Rejected candidates do not initialize project metadata.
- Approved setup fields can initialize `project.json` only after final confirmation.
- Candidate setup fields remain visibly labeled.
- Candidate provenance links back to owner raw idea/setup.

Project creation handoff tests:

- OMI-guided project creation records `creation_method = "omi_guided"`.
- `project_id` validation and collision handling match WORKSPACE-002.
- Selected initialization fields write only allowed `project.json` metadata.
- Failed creation does not leave corrupted projects.
- Failed OMI import does not silently convert candidates to canon.
- Created project opens Project Overview.

No-prose and no-silent-promotion tests:

- No scene or chapter prose is generated.
- No scene files are written by OMI setup.
- No chapter prose files are written by OMI setup.
- No memory/canon files are written.
- No bible/storyform truth mutation occurs.
- No OMI promotion or apply-promotion occurs.
- No model/Ollama call occurs unless a future guarded path explicitly enables and tests it.
- No JSONL/training writes occur.
- No `training/data/dataset_manifest.json` update occurs.
- No AI prose-generation controls appear in the UI.

Storage tests:

- Transient staged setup does not create a project folder before final confirmation.
- Project-local OMI records are created only after successful project creation and explicit import choice.
- Pending/rejected imported candidates remain non-canon.
- Abandoned setup does not create orphaned project folders.

## 13. Deferred Decisions

These remain for implementation or later planning tasks:

- Whether first implementation keeps staged setup only in frontend state or adds a backend transient setup route.
- Whether durable pre-project setup storage is needed for resume-after-close behavior.
- Whether setup candidate generation is manual/rule-based first or later model-assisted.
- If model-assisted setup candidates are added later, what exact guarded prompt, schema, and output sanitizer are required.
- Whether initial chapter and scene placeholder candidates are imported in WORKSPACE-004 implementation or deferred until chapter/scene model specs.
- Whether rejected setup candidates are archived into project-local OMI or discarded.
- Whether pending setup candidates are imported by default or only if the owner opts in.
- Exact setup candidate status taxonomy for `draft`, `candidate`, `owner_review`, `approved`, `rejected`, `archived`, `used_for_project_metadata`, and `imported_to_project_omi`.
- Whether final confirmation text must require typing the future `project_id`.
- Whether staged setup IDs are globally unique, session-local, or project-local after conversion.
- How long abandoned staged setup data is retained if a durable pre-project inbox is later added.

## 14. Related Specifications

- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_creation_flow_spec.md`
- `docs/roadmap/project_selector_library_spec.md`
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
