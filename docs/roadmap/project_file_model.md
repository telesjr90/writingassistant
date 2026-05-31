# App MVP Project File Model

## 1. Executive Summary

This specification defines the target local project file model for the Dramatica-Informed Writing Assistant MVP. Its purpose is to make project storage explicit before implementation work starts, so future backend and frontend changes preserve the product boundary: the app analyzes structure, but it does not write or rewrite story prose.

What exists now:

- Runtime project files live under `projects/{project_name}/`.
- Scenes are Markdown files in `scenes/{scene_id}.md`.
- `bible.json` stores current project bible data.
- `storyform.json` stores current NCP/storyform context.
- The frontend hard-codes the project ID `example`.
- Story Check output is transient frontend state and is not saved as an artifact.

MVP target:

- Add an explicit project metadata model with `project.json`.
- Keep owner-approved truth in separate durable files.
- Keep Story Check and model outputs as candidate analysis artifacts.
- Keep OMI raw ideas and OMI candidates separate from project truth.
- Require owner approval, destination, provenance, and status before any candidate can be promoted.

Must remain candidate-only until explicit owner approval:

- Raw model output.
- Normalized Story Check diagnostics.
- OMI output and OMI candidates.
- NotebookLM output.
- External dataset or reference-derived material.
- Retrieved Dramatica/NCP definitions.

Immediate next task after this spec: App-3 NCP compatibility subset, with OMI-001 schema/lifecycle and sample project alignment following closely.

## 2. Current Implemented Storage Inventory

Current project root:

```text
projects/{project_name}/
```

Current scenes path:

```text
projects/{project_name}/scenes/{scene_id}.md
```

Current bible path:

```text
projects/{project_name}/bible.json
```

Current storyform path:

```text
projects/{project_name}/storyform.json
```

Current backend behavior:

- `backend/project_manager.py` uses repo-local `projects/`.
- `project_name` and `scene_id` must be non-empty single path components.
- Absolute paths, path traversal, `"."`, and `".."` are rejected.
- `load_bible()` requires `bible.json` to contain a JSON object.
- `save_bible()` writes JSON and creates the project directory.
- `load_scene()` reads UTF-8 scene Markdown.
- `save_scene()` writes UTF-8 scene Markdown and creates `scenes/`.
- `list_scenes()` returns sorted Markdown stems from `scenes/`.

Current API behavior:

- `GET /api/projects/{project_name}/scenes`
- `GET /api/projects/{project_name}/scenes/{scene_id}`
- `PUT /api/projects/{project_name}/scenes/{scene_id}`
- `GET /api/projects/{project_name}/bible`
- `POST /api/projects/{project_name}/story-check/{scene_id}`
- `GET /api/projects/{project_name}/storyform-context`

Current frontend behavior:

- `frontend/src/api.js` hard-codes `PROJECT_ID = 'example'`.
- The app loads scenes and storyform context for `example` on startup.
- The selected scene is loaded, edited, saved, and analyzed through that hard-coded project path.

Current sample mismatch:

- `projects/example/bible.json` and `projects/example/scenes/scene_001.md` use Elena/Whispering Woods material.
- `projects/example/storyform.json` uses Quest for the Ember Crown/Mara/Calen material.
- This mismatch must be fixed separately before Story Check quality is evaluated.

## 3. Project File Model Goals

- Local-first: project data remains usable without cloud services.
- Human-readable where practical: JSON for structured metadata and Markdown/plain text for scene drafts.
- Safe path handling: project IDs and scene IDs remain single path components.
- Durable owner-approved truth separated from generated or candidate outputs.
- OMI candidate planning separated from project truth.
- Analysis artifacts separated from story truth.
- Migration-friendly: current `bible.json`, `storyform.json`, and `scenes/` remain valid during transition.
- Compatible with `ANALYSIS_MODE=mock`, `ANALYSIS_MODE=ollama_baseline` using `qwen3:8b`, and future `dramatica-analyst:8b` after model gates pass.
- Conservative Dramatica/NCP claims: schema-valid does not mean verified story truth.

## 4. Proposed MVP Project Structure

Target folder shape:

```text
projects/
  {project_id}/
    project.json                         # MVP-required after migration
    bible.json                           # MVP-required
    storyform.json                       # MVP-required for Story Check with storyform context
    owner_memory.json                    # MVP-optional or deferred
    scenes/
      {scene_id}.md                      # MVP-required for editable scenes
    scene_metadata/
      {scene_id}.json                    # MVP-optional
    analysis/
      {scene_id}.{timestamp}.story_check.json  # MVP-optional; required only if saving analysis history
    omi/
      ideas/
        {idea_id}.json                   # MVP-required when OMI is implemented
      candidates/
        {candidate_id}.json              # MVP-required when OMI is implemented
    exports/
      ...                                # future-only
```

MVP-required now or at first project-model implementation:

- `project.json`
- `bible.json`
- `storyform.json`
- `scenes/{scene_id}.md`

MVP-optional:

- `owner_memory.json`
- `scene_metadata/{scene_id}.json`
- `analysis/{scene_id}.{timestamp}.story_check.json`

MVP-required only when OMI implementation begins:

- `omi/ideas/{idea_id}.json`
- `omi/candidates/{candidate_id}.json`

Future-only:

- `exports/`
- global idea inbox
- model-specific caches
- collaboration/sync metadata

No project file may contain secrets, raw book/source text, packet evidence, SFT records, model artifacts, or training runs.

## 5. `project.json` Specification

Purpose: `project.json` stores project identity and project-level metadata. It is not story truth and must not hold raw model output or OMI candidate content.

Proposed fields:

```json
{
  "schema_version": "0.1.0",
  "project_id": "example",
  "title": "Example Project",
  "description": "",
  "status": "active",
  "created_at": "2026-05-31T00:00:00Z",
  "updated_at": "2026-05-31T00:00:00Z",
  "default_scene_id": "scene_001",
  "analysis_mode_default": "ollama_baseline",
  "app_metadata": {
    "product_name": "Dramatica-Informed Writing Assistant"
  },
  "owner_approved_truth_policy": {
    "durable_truth_requires_owner_approval": true,
    "candidate_outputs_do_not_promote_automatically": true,
    "standard_refusal_message": "I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose."
  },
  "provenance_summary": {
    "created_by": "owner",
    "source_material_status": "owner_managed",
    "notes": []
  }
}
```

Field notes:

- `project_id`: filesystem-safe ID and directory name.
- `title`: display title, may differ from `project_id`.
- `schema_version`: version of this project file model, not the NCP schema.
- `default_scene_id`: initial scene to select when no user preference exists.
- `status`: recommended values include `active`, `archived`, and `template`.
- `analysis_mode_default`: project preference only; runtime implementation must still validate supported modes.
- `owner_approved_truth_policy`: explicit reminder that candidate outputs are not durable truth.
- `provenance_summary`: high-level project origin summary, not a replacement for per-artifact provenance.

Do not put in `project.json`:

- Scene prose.
- Raw model output.
- OMI candidates.
- NotebookLM output.
- Full bible/storyform data.
- Secrets or local machine credentials.
- Raw book/source text.
- SFT records or training data.

## 6. `bible.json` Role and Boundary

`bible.json` is durable owner-approved project/story bible data.

Allowed role:

- Owner-approved characters, places, objects, relationships, rules, continuity facts, and project facts.
- Human-edited corrections and decisions.
- Stable context used by Story Check.

Boundary:

- Not raw model output.
- Not transient Story Check output.
- Not OMI candidate output unless explicitly owner-approved and promoted.
- Not NotebookLM output unless owner-approved and promoted with provenance.
- Not retrieved Dramatica/NCP definitions.

Future metadata:

- Each major bible entry should eventually have provenance/status metadata either inline or in an adjacent metadata file.
- Recommended statuses: `approved`, `needs_review`, `superseded`, `rejected`.
- Promotion into `bible.json` requires owner confirmation and a destination.

## 7. `storyform.json` Role and Boundary

`storyform.json` is durable owner-approved NCP/storyform context.

Allowed role:

- Owner-approved storyform/NCP structural context.
- Approved OS/MC/IC/RS separation.
- Approved dynamics, story points, throughlines, concerns, issues, problems, and related fields when evidence supports them.

Boundary:

- Not inferred automatically from Story Check.
- Not filled from NotebookLM or book/master packets without owner approval.
- Not filled from OMI candidates without explicit owner approval and destination selection.
- Not a full Dramatica verifier.

Conservative claim rules:

- Positive OS/MC/IC/RS/CIPS/dynamics claims require evidence and owner approval.
- Generic relationship conflict is not Relationship Story proof.
- Generic theme language is not Dramatica Issue/Variation proof.
- Unsupported, unknown, or deferred fields should remain unresolved, not guessed.

## 8. `owner_memory.json` Role and Boundary

`owner_memory.json` is durable owner-approved project memory. It may be deferred until after basic Story Check and OMI flows if the MVP can preserve boundaries without it.

Purpose:

- Store owner-approved preferences, recurring decisions, unresolved questions, and durable project notes that are not cleanly part of bible/storyform/scenes.

Recommended categories:

- `facts`
- `preferences`
- `decisions`
- `unresolved_items`
- `rejected_candidates`

Boundary:

- Must distinguish facts, preferences, decisions, and unresolved items.
- Must not silently absorb raw model output.
- Must not silently absorb Story Check diagnostics.
- Must not silently absorb OMI candidates.
- Must record provenance and owner decision status for promoted material.

## 9. `scenes/` and Scene Metadata

Scene text files:

- `scenes/{scene_id}.md` stores owner-authored scene text.
- Markdown is acceptable for MVP because the current editor stores and loads Markdown-like plain text.
- Scene text is owner-authored durable project material, not model-generated content.

Plain text vs Markdown:

- MVP can continue using Markdown files.
- The app should avoid treating formatting conversions as structural truth.
- Future rich text storage should preserve plain text extraction for analysis.

Empty scene behavior:

- Empty scene files should load as editable drafts where practical.
- Story Check should treat empty scenes as insufficient evidence and should not call the model unnecessarily once runtime guardrails exist.
- Current backend returns 404 for empty scene content; changing this is a future implementation task.

Scene ID rules:

- Non-empty single path component.
- No absolute paths.
- No traversal.
- Stable across rename unless an explicit migration updates references.
- Recommended format: `scene_001`, `scene_002`, or slug-like IDs such as `opening_watchtower`.

Scene metadata:

```json
{
  "scene_id": "scene_001",
  "title": "Scene 001",
  "status": "draft",
  "order": 1,
  "created_at": "2026-05-31T00:00:00Z",
  "updated_at": "2026-05-31T00:00:00Z",
  "owner_review_status": "owner_authored",
  "provenance": {
    "source": "owner"
  }
}
```

Dirty-state/save implications:

- Frontend should track whether the editor content differs from the saved scene.
- Scene switching should warn or save explicitly when dirty.
- Save/reload testing should verify no content loss.

Safe write rules:

- Write only inside `projects/{project_id}/scenes/`.
- Use UTF-8.
- Validate path components before writing.
- Prefer atomic write or backup strategy once save operations expand.

## 10. `analysis/` Artifacts

Story Check outputs are candidate diagnostics, not project truth.

Purpose:

- Preserve optional analysis history.
- Support owner review of model observations.
- Support evaluation of mock, qwen3 baseline, and future `dramatica-analyst:8b` behavior.

Suggested artifact fields:

```json
{
  "task": "story_check",
  "scene_id": "scene_001",
  "created_at": "2026-05-31T00:00:00Z",
  "analysis_mode": "ollama_baseline",
  "model_name": "qwen3:8b",
  "input_context_hash": "sha256:...",
  "provenance": {
    "scene_ref": "scenes/scene_001.md",
    "bible_ref": "bible.json",
    "storyform_ref": "storyform.json"
  },
  "normalized_report": {},
  "raw_diagnostics": {},
  "schema_valid": false,
  "owner_review_status": "candidate"
}
```

Rules:

- Analysis artifacts must not mutate `bible.json`.
- Analysis artifacts must not mutate `storyform.json`.
- Analysis artifacts must not mutate `owner_memory.json`.
- Analysis artifacts must not rewrite scenes.
- Owner must explicitly promote a specific finding to a specific destination before it can become durable truth.

## 11. OMI Project File Model

OMI storage is a design target for MVP implementation. This task does not create OMI files, endpoints, or frontend components.

Proposed OMI folders:

```text
omi/
  ideas/
    {idea_id}.json
  candidates/
    {candidate_id}.json
```

Required OMI fields:

- `raw_idea`
- `candidates`
- `owner_decision`
- `destination`
- `provenance`
- `status`

Suggested idea file:

```json
{
  "idea_id": "idea_001",
  "raw_idea": "Owner-provided idea text or note.",
  "created_at": "2026-05-31T00:00:00Z",
  "updated_at": "2026-05-31T00:00:00Z",
  "provenance": {
    "source": "owner",
    "source_detail": "manual_entry"
  },
  "status": "draft"
}
```

Suggested candidate file:

```json
{
  "candidate_id": "omi_candidate_001",
  "idea_id": "idea_001",
  "raw_idea": "Owner-provided idea text or note.",
  "candidates": [
    {
      "candidate_type": "planning_note",
      "content": {},
      "no_prose_generated": true
    }
  ],
  "owner_decision": {
    "decision": "pending",
    "decided_at": null,
    "notes": ""
  },
  "destination": "planning_notes",
  "provenance": {
    "source": "omi",
    "analysis_mode": "mock",
    "model_name": null
  },
  "status": "candidate"
}
```

Suggested OMI statuses:

- `draft`
- `candidate`
- `owner_review`
- `approved`
- `rejected`
- `promoted`
- `archived`

Suggested OMI destinations:

- `planning_notes`
- `project_bible_candidate`
- `storyform_context_candidate`
- `scene_prompt_context_candidate`
- `template_starter_candidate`
- `discard`

Required OMI boundaries:

- No prose generation.
- OMI cannot write scenes, chapters, dialogue, paragraphs, endings, or story continuations.
- OMI cannot rewrite, improve, polish, imitate, or extend prose.
- OMI candidates cannot mutate `bible.json`, `storyform.json`, `owner_memory.json`, `scenes/`, or planning notes without explicit owner approval.
- OMI promotion requires destination, provenance, status, and owner confirmation.
- OMI output remains candidate planning material until explicitly approved and promoted.

## 12. Candidate vs Owner-Approved Lifecycle

Shared lifecycle:

1. `draft`: owner-entered material or incomplete candidate material.
2. `candidate`: generated or structured material available for review.
3. `owner_review`: owner is actively reviewing the candidate.
4. `approved`: owner approved the candidate for a specific destination.
5. `rejected`: owner rejected the candidate.
6. `promoted`: approved candidate was written to its destination.
7. `archived`: retained for history but not active.

Truth rules:

- `draft` cannot feed durable truth automatically.
- `candidate` cannot feed durable truth automatically.
- `owner_review` cannot feed durable truth automatically.
- `approved` may feed durable truth only when destination and provenance are present.
- `promoted` is the only state that confirms a candidate was incorporated.
- `rejected` and `archived` cannot feed durable truth.

Durable truth destinations:

- `bible.json`
- `storyform.json`
- `owner_memory.json`
- future planning notes, if owner-approved

Scenes remain owner-authored. OMI and Story Check may provide diagnostic questions or structured planning candidates, but they must not generate scene prose.

## 13. Provenance Requirements

Every candidate, promotion, and durable-memory update should record provenance.

Source types and what they can establish:

| Source | Can establish | Cannot establish |
| --- | --- | --- |
| Human-created owner input | Owner intent and owner-approved facts when marked approved | Dramatica/NCP proof without supporting evidence where required |
| Manual owner edits | Durable truth after save/approval | Automated provenance unless recorded |
| OMI candidate output | Candidate planning material | Story prose, durable truth, automatic bible/storyform changes |
| Story Check model output | Candidate diagnostics and questions | Durable story truth or automatic storyform updates |
| NotebookLM candidate output | Candidate aggregation or review support | Training truth or durable project truth without owner review |
| External dataset/reference output | Task scaffolding or reference context after rights review | Positive Dramatica truth for the owner's project |
| Retrieved Dramatica/NCP definitions | Reference definitions | Story-specific proof, CIPS proof, IC/RS proof, or dynamics proof |

Promotion provenance should include:

- Source type.
- Source file or route reference.
- Created timestamp.
- Model name and analysis mode when applicable.
- Owner decision timestamp.
- Destination.
- Status before and after promotion.

## 14. Safe Path and File-Write Rules

Rules:

- IDs must be single path components.
- No absolute paths.
- No `.` or `..`.
- No path traversal.
- UTF-8 for text and JSON files.
- JSON files must contain JSON objects unless a specific schema says otherwise.
- Validate `project_id`, `scene_id`, `idea_id`, `candidate_id`, and artifact IDs before reading or writing.
- Do not write to raw book/source folders.
- Do not write to packet evidence, SFT JSONL, model artifacts, training runs, venvs, caches, or `node_modules`.

Write recommendations:

- Use atomic writes for structured JSON once implementation expands.
- Keep backup or migration notes before destructive schema migrations.
- Prefer append/create of candidate artifacts over mutation of owner-approved truth.
- Require explicit owner confirmation for destructive operations.

## 15. Migration Plan From Current Project Structure

No migration is executed in this task.

Migration notes:

- Current `projects/{project_name}/bible.json`, `storyform.json`, and `scenes/` remain valid.
- `project.json` can be introduced later with default values derived from the folder name and scene list.
- `scene_metadata/` can be introduced later without changing scene text files.
- `analysis/` can be introduced later when analysis history is implemented.
- `omi/` can be introduced later when OMI storage/API/UI work begins.
- `owner_memory.json` can be introduced later or deferred if not needed for immediate MVP safety.
- The `projects/example` Elena/Ember Crown mismatch must be fixed as a separate sample alignment task.

Suggested migration order:

1. Add read/default behavior for missing `project.json`.
2. Add optional `project.json` creation for new projects.
3. Add scene metadata defaults.
4. Add analysis artifact save/list behavior.
5. Add OMI idea/candidate storage.
6. Add owner-approved promotion behavior.

## 16. API Implications for Future Implementation

Design targets only; not implemented in this task:

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `PUT /api/projects/{project_id}`
- `GET /api/projects/{project_id}/scenes`
- `POST /api/projects/{project_id}/scenes`
- `GET /api/projects/{project_id}/scenes/{scene_id}`
- `PUT /api/projects/{project_id}/scenes/{scene_id}`
- `GET /api/projects/{project_id}/bible`
- `PUT /api/projects/{project_id}/bible`
- `GET /api/projects/{project_id}/storyform`
- `PUT /api/projects/{project_id}/storyform`
- `GET /api/projects/{project_id}/analysis`
- `POST /api/projects/{project_id}/analysis/story-check/{scene_id}`
- `GET /api/projects/{project_id}/omi/ideas`
- `POST /api/projects/{project_id}/omi/ideas`
- `GET /api/projects/{project_id}/omi/candidates`
- `POST /api/projects/{project_id}/omi/candidates`
- `PUT /api/projects/{project_id}/omi/candidates/{candidate_id}`
- `POST /api/projects/{project_id}/omi/candidates/{candidate_id}/approve`
- `POST /api/projects/{project_id}/omi/candidates/{candidate_id}/reject`
- `POST /api/projects/{project_id}/omi/candidates/{candidate_id}/promote`

All future write endpoints must enforce path safety, JSON validation, provenance/status requirements, and no-prose guardrails where model output is involved.

## 17. Frontend Implications for Future Implementation

Future frontend design targets:

- Project selector or configurable project ID instead of hard-coded `example`.
- Project metadata display from `project.json`.
- Scene metadata display and editing.
- Dirty-state handling before scene switches.
- Save/reload status that proves scene content is durable.
- Storyform and bible ownership labels.
- Clear labels for owner-approved truth vs candidate material.
- Analysis artifact history.
- Mode visibility for mock, qwen3 baseline, and future model modes.
- OMI UI for raw idea, candidates, status, provenance, and destination.
- Promotion UI requiring owner confirmation.

No frontend implementation is performed in this task.

## 18. Test Implications

Future tests needed:

- Project path safety for project, scene, analysis, and OMI IDs.
- `project.json` load/default behavior.
- `project.json` write validation.
- Scene metadata load/save.
- Empty scene handling.
- Save/reload behavior for scene text.
- Analysis artifact save/list behavior.
- Analysis artifact cannot mutate bible/storyform/owner memory.
- OMI candidate cannot mutate truth without approval.
- Provenance/status required for promotion.
- Rejected/archived candidates cannot promote.
- No-prose guard applies to OMI routes when implemented.
- No-prose guard applies before Story Check model calls when relevant.
- No-prose guard applies after model output parsing.

## 19. App-2 Acceptance Checklist

- [x] Defines current implemented storage.
- [x] Defines target MVP project folder shape.
- [x] Separates owner-approved truth from candidate analysis.
- [x] Separates OMI candidate planning from project truth.
- [x] Defines `project.json` target fields.
- [x] Defines `bible.json` and `storyform.json` boundaries.
- [x] Defines `owner_memory.json` role and deferral option.
- [x] Defines scenes and scene metadata.
- [x] Defines analysis artifact boundaries.
- [x] Defines OMI storage/lifecycle design without implementing it.
- [x] Defines candidate vs owner-approved lifecycle.
- [x] Defines provenance requirements.
- [x] Defines safe path/write rules.
- [x] Includes migration notes without executing migration.
- [x] Lists future API/frontend/test implications.
- [x] Lists owner questions separately from engineering tasks.

## 20. Recommended Next Tasks

1. App-3 NCP compatibility subset.
2. App-3a / OMI-001 OMI MVP schema and lifecycle, using this project model as storage context.
3. Sample project alignment decision.
4. Phase 2 backend guardrails/schema foundation.

## 21. Owner Questions

- Should `project_id` remain filesystem-oriented, with display title fully separate from `project_id`?
- Should `owner_memory.json` be included in MVP, or deferred until after Story Check and OMI basics?
- Should analysis artifacts be saved automatically after every Story Check, or only when the owner chooses to save them?
- Should OMI candidates live inside each project, or can there be a global idea inbox later?
- For the aligned sample project, should we use owner-created material or public-domain material?
