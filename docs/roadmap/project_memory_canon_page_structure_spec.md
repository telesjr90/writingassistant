# WORKSPACE-011: Project Memory / Canon Page Structure Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-002: `docs/roadmap/project_creation_flow_spec.md`
- WORKSPACE-003: `docs/roadmap/project_selector_library_spec.md`
- WORKSPACE-004: `docs/roadmap/omi_guided_project_creation_spec.md`
- WORKSPACE-005: `docs/roadmap/chapter_scene_data_model_spec.md`
- WORKSPACE-006: `docs/roadmap/notes_materials_data_model_spec.md`
- WORKSPACE-007: `docs/roadmap/user_authored_document_editor_workflow_spec.md`
- WORKSPACE-008: `docs/roadmap/project_overview_page_spec.md`
- WORKSPACE-009: `docs/roadmap/chapters_scenes_page_spec.md`
- WORKSPACE-010: `docs/roadmap/notes_materials_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Project Memory / Canon area should be the future approved-story-knowledge entry point for a project. It should show only owner-approved memory/canon records that have been explicitly applied by a future apply-promotion flow, while clearly separating pending candidates, rejected candidates, archived candidates, approved-but-not-applied candidates, and promotion records.

The page should:

- Show approved project truth only when explicitly promoted by the owner and applied by a future apply-promotion flow.
- Clearly separate approved memory/canon from pending candidates, rejected candidates, archived candidates, approved candidates that are not applied, and promotion records.
- Provide category-specific navigation to approved characters, locations/settings, objects/items, organizations/groups, timeline events, relationships, plot threads, open questions, annotations, and continuity warnings.
- Show empty states before apply-promotion exists.
- Avoid implying that OMI candidates are canon.
- Avoid creating or editing story truth automatically.
- Avoid model/Ollama calls in the first implementation.
- Avoid Dramatica-specific requirements in this workspace phase.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Memory / Canon Concepts

The page must make the following concepts visually and textually distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and owner-entered OMI ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for candidates.
- Source material is not approved memory/canon by default.
- Notes/materials are not canon by default.
- Source material must not be copied into memory/canon by opening the page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth by themselves.
- Raw ideas may link to candidates but must remain separate from approved memory/canon.

### Pending OMI Candidates

Definition:

- Structured planning or story-knowledge candidate records that have not been owner-approved.

Rules:

- Pending candidates are not canon.
- Pending candidates may be counted only in candidate-labeled areas.
- Pending candidates must not appear in approved memory/canon category lists.

### Approved OMI Candidates

Definition:

- Candidate records the owner has approved as eligible for a destination or later promotion.

Rules:

- Approved candidates are not durable memory/canon until future apply-promotion exists and runs explicitly.
- Approved candidates may show as "Approved Candidate" or "Needs Apply-Promotion" only outside approved canon lists.
- Approval status alone must not create memory files or approved category records.

### Promotion Records

Definition:

- Audit records that capture owner-approved intent, selected destination, evidence/provenance, source snapshot, and final confirmation data for future target mutation.

Rules:

- Promotion records are audit records, not canon by themselves.
- Promotion records may be shown in a snapshot panel with "Promotion Record Only" and "Not Yet Applied" labels.
- Promotion records must not be converted automatically into `memory/*.json`.

### Applied Memory / Canon Records

Definition:

- Durable owner-approved project truth records created by a future successful apply-promotion step into `memory/*.json`.

Rules:

- Applied memory/canon records are the only records allowed in approved memory/canon category lists.
- They should reference source candidate IDs, promotion record IDs, evidence, and provenance.
- They must remain project-local.

### Bible / Storyform Context

Definition:

- Existing or future owner-approved project context in `bible.json` and `storyform.json`.

Rules:

- `bible.json` and `storyform.json` remain separate stores unless a future explicit bridge is designed.
- This page must not mutate bible/storyform context.
- Mismatch warnings may be future health checks only, not Dramatica claims or automatic repair.

### Future Dramatica-Specific Truth

Definition:

- Future Dramatica/storyform-specific truth claims such as throughlines, story points, dynamics, or Relationship Story assertions.

Rules:

- Dramatica-specific truth is deferred.
- Relationship memory records are generic story-knowledge records, not Dramatica Relationship Story proof.
- No Dramatica-specific page requirement exists in this workspace phase.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved memory/canon display.
- The first implementation of this page must not call a model.

## 3. First-Version Page Structure

First-version sections:

- Page Header.
- Canon Status Banner.
- Approved Memory / Canon Category Cards.
- Candidate vs Canon Explanation.
- Promotion Records Snapshot.
- Empty-State Guidance.
- Health / Warning Area.
- Links to OMI Ideas/Candidates.
- Links to Project Overview.
- Future Apply-Promotion Placeholder.

### Page Header

Purpose:

- Identify the active project and the Project Memory / Canon area.
- Show high-level approved-memory status and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Future memory summary/index from `memory/index.json` and `memory/*.json` only if those files already exist.
- Lightweight OMI promotion/candidate counts only if needed for labeled non-canon badges.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, canon summaries, character descriptions, plot summaries, or story prose.

Candidate/canon boundary:

- Approved memory counts must come from applied memory/canon records only.
- Candidate or promotion counts must be labeled separately.

Empty state:

- Show that no approved memory/canon has been applied yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt memory metadata should show a warning and avoid approved display.

### Canon Status Banner

Purpose:

- Make the current canon state unambiguous.
- Tell the owner whether applied memory/canon exists, whether promotion records exist, and whether apply-promotion is unavailable.

Data source:

- `memory/index.json` and category files if present.
- OMI promotion summaries from `omi/promotions/` if present.
- OMI candidate status counts where cheap and clearly labeled.

No-prose boundary:

- Banner text is factual status copy only.
- No generated summaries or recommendations.

Candidate/canon boundary:

- Must label "No approved memory/canon records yet" before applied records exist.
- Must label promotion records as audit-only.
- Must label approved-but-not-applied candidates separately.

Empty state:

- Show placeholder state before apply-promotion exists.

Error state:

- If memory status cannot be computed safely, show degraded warning and do not display inferred approved counts.

### Approved Memory / Canon Category Cards

Purpose:

- Provide category-specific navigation to approved memory/canon areas.
- Show approved-only counts and category health warnings.

Data source:

- Future `memory/*.json` category files.
- Future `memory/index.json` as derived navigation metadata only.
- OMI candidate counts may appear only as clearly separated candidate badges.

No-prose boundary:

- Cards show stored labels, counts, statuses, and warnings.
- Do not generate category summaries or story descriptions.

Candidate/canon boundary:

- Approved count is applied memory/canon records only.
- Pending/rejected/archived candidates must not be blended into the approved count.
- Promotion-record-only counts must appear separately.

Empty state:

- Cards may show zero approved records and a link to OMI review.

Error state:

- Corrupt category file, duplicate record IDs, unsupported schema, or stale index should show category warning.

### Candidate vs Canon Explanation

Purpose:

- Explain the separation between source material, OMI candidates, promotion records, and applied memory/canon.

Data source:

- Static page copy based on roadmap policy.

No-prose boundary:

- Copy is operational safety guidance, not story content.

Candidate/canon boundary:

- Must state that pending/rejected/archived candidates are not canon.
- Must state that promotion records are audit records, not canon.
- Must state that approved candidates are not durable memory/canon until applied.

Empty state:

- Always available as guidance.

Error state:

- Not applicable beyond normal page rendering failure.

### Promotion Records Snapshot

Purpose:

- Show OMI promotion records as audit-only records.
- Help the owner understand which promotions are recorded but not applied.

Data source:

- `omi/promotions/{promotion_id}.json`.
- `omi/index.json` promotion IDs, treated as derived convenience state.

No-prose boundary:

- Snapshot displays stored promotion metadata only.
- Do not generate promotion summaries or story truth.

Candidate/canon boundary:

- Promotion records must use "Promotion Record Only" and "Not Yet Applied" labels unless future apply-promotion result links exist.
- Promotion records must not appear in approved category lists.

Empty state:

- Show no promotion records.
- Link to OMI Ideas/Candidates page for candidate review.

Error state:

- Corrupt or missing promotion records show warnings and must not be treated as applied memory.

### Empty-State Guidance

Purpose:

- Guide the owner when no applied memory/canon exists.

Data source:

- Memory counts.
- OMI counts.
- Page availability.

No-prose boundary:

- Guidance is operational only.
- Do not suggest "generate canon", "write memory", or "summarize story".

Candidate/canon boundary:

- Link to OMI review for candidates.
- State that approved memory/canon appears only after future apply-promotion.

Empty state:

- Missing `memory/` directory.
- Empty category files.
- No applied records.

Error state:

- If project metadata is invalid, show recovery/help instead of candidate/canon guidance.

### Health / Warning Area

Purpose:

- Surface non-destructive health warnings about memory, OMI links, evidence, and project state.

Data source:

- Project validation.
- Memory index/category validation.
- OMI promotion/candidate validation.
- Evidence/source link checks where safe.

No-prose boundary:

- Warnings are factual status messages only.
- Do not generate repair text that rewrites story material.

Candidate/canon boundary:

- Warnings must not promote, repair, merge, or delete candidate/canon state.

Empty state:

- No warnings when clean.

Error state:

- Blocking errors prevent approved display.
- Non-blocking errors show degraded state.

### Links to OMI Ideas/Candidates

Purpose:

- Route pending, rejected, archived, approved-but-not-applied, and promotion-record-only review back to the candidate review area.

Data source:

- Static route definitions.
- Optional OMI candidate/promotion counts.

No-prose boundary:

- Link labels are workflow labels only.

Candidate/canon boundary:

- OMI links must be labeled candidates/review, not canon.

Empty state:

- Show link even when no OMI records exist.

Error state:

- If OMI metadata is corrupt, show warning and avoid using its counts as truth.

### Links to Project Overview

Purpose:

- Return the owner to the project-level landing page and its status snapshot.

Data source:

- Static route definitions.

No-prose boundary:

- Link text only.

Candidate/canon boundary:

- Overview link should not imply candidates are approved memory.

Empty state:

- Always available when project is valid.

Error state:

- Disable or replace with recovery state if project identity is invalid.

### Future Apply-Promotion Placeholder

Purpose:

- Reserve space for future apply-promotion status without exposing an unsafe action.

Data source:

- None in first implementation.
- Future apply-promotion capability state after separate design.

No-prose boundary:

- No generate/write/rewrite controls.

Candidate/canon boundary:

- Must say apply-promotion is future/not implemented until the separate flow exists.
- No automatic conversion from promotion records to memory/canon.

Empty state:

- Show disabled or informational placeholder only.

Error state:

- If future capability discovery fails, keep apply-promotion unavailable.

## 4. Category Cards and Subpages

Category cards should link to future dedicated approved pages where applicable. In WORKSPACE-011 they define structure only; they do not implement routes or UI.

Shared category card rules:

- Display approved-only counts from applied memory/canon records.
- If pending-candidate counts are shown, they must be clearly labeled and visually separate.
- Show source/evidence/provenance availability.
- Link to OMI review for candidate work.
- Link to future dedicated category page where applicable.
- Show empty state when no applied records exist.
- Show warning state for corrupt files, unsupported schema, duplicate IDs, or broken evidence/source references.
- Never display pending, rejected, archived, or promotion-record-only items as approved records.

### Characters

Expected record type:

- `character_memory_record` from `memory/characters.json`.

Approved-only display rule:

- Show only applied character memory records.

Evidence/provenance expectation:

- Show source candidate IDs, promotion record IDs, first seen scene, evidence/provenance status, and uncertainty warnings where retained.

Future page:

- Approved Characters page, planned by WORKSPACE-012.

Empty state:

- "No approved character records yet" or equivalent.

Warning state:

- Duplicate character record IDs, broken related character/location/plot links, missing evidence/provenance, or corrupt category file.

### Locations / Settings

Expected record type:

- `location_memory_record` from `memory/locations.json`.

Approved-only display rule:

- Show only applied location/setting records.

Evidence/provenance expectation:

- Show source candidate IDs, promotion record IDs, first seen scene, mentioned scene IDs, and provenance status.

Future page:

- Approved Locations / Settings page, planned by WORKSPACE-013.

Empty state:

- "No approved location/setting records yet" or equivalent.

Warning state:

- Duplicate location IDs, broken connected character/event links, missing evidence/provenance, or corrupt category file.

### Objects / Items

Expected record type:

- `object_memory_record` from `memory/objects.json`.

Approved-only display rule:

- Show only applied object/item records.

Evidence/provenance expectation:

- Show source candidate IDs, promotion record IDs, holder/owner uncertainty, first seen scene, and provenance status.

Future page:

- Future approved objects/items page if later scheduled.

Empty state:

- "No approved object/item records yet" or equivalent.

Warning state:

- Duplicate object IDs, broken holder links, missing evidence/provenance, or corrupt category file.

### Organizations / Groups

Expected record type:

- `organization_memory_record` from `memory/organizations.json`.

Approved-only display rule:

- Show only applied organization/group records.

Evidence/provenance expectation:

- Show source candidate IDs, promotion record IDs, member link status, and provenance status.

Future page:

- Future approved organizations/groups page if later scheduled.

Empty state:

- "No approved organization/group records yet" or equivalent.

Warning state:

- Duplicate organization IDs, broken member/location/plot links, missing evidence/provenance, or corrupt category file.

### Timeline Events

Expected record type:

- `timeline_event_memory_record` from `memory/timeline.json`.

Approved-only display rule:

- Show only applied timeline event records.

Evidence/provenance expectation:

- Show source scene, sequence position, time references, involved records, uncertainty notes, and provenance status.

Future page:

- Approved Timeline page, planned by WORKSPACE-014.

Empty state:

- "No approved timeline events yet" or equivalent.

Warning state:

- Duplicate event IDs, invalid sequence positions, broken involved record links, missing evidence/provenance, or corrupt category file.

### Relationships

Expected record type:

- `relationship_memory_record` from `memory/relationships.json`.

Approved-only display rule:

- Show only applied relationship records.

Evidence/provenance expectation:

- Show subject/object records, relationship type, direction/status, evidence scene IDs, uncertainty notes, and provenance status.

Future page:

- Future approved relationships page or relationship graph page if later scheduled.

Empty state:

- "No approved relationship records yet" or equivalent.

Warning state:

- Duplicate relationship IDs, broken subject/object links, missing evidence/provenance, or corrupt category file.

Boundary:

- Relationship memory records are generic story-knowledge records. They are not Dramatica Relationship Story proof.

### Plot Threads

Expected record type:

- `plot_thread_memory_record` from `memory/plot_threads.json`.

Approved-only display rule:

- Show only applied plot-thread records.

Evidence/provenance expectation:

- Show introduced scene, related scenes, related characters, thread status, unresolved questions, and provenance status.

Future page:

- Approved Plot Threads page, planned by WORKSPACE-015.

Empty state:

- "No approved plot threads yet" or equivalent.

Warning state:

- Duplicate plot-thread IDs, broken related scene/character links, missing evidence/provenance, or corrupt category file.

### Open Questions

Expected record type:

- `open_question_memory_record` from `memory/open_questions.json`.

Approved-only display rule:

- Show only applied open-question records.

Evidence/provenance expectation:

- Show source scene, related records, question type, status, why-it-matters field, and provenance status.

Future page:

- Future approved open questions page or part of Continuity / Consistency if later scheduled.

Empty state:

- "No approved open questions yet" or equivalent.

Warning state:

- Duplicate question IDs, broken related record links, missing evidence/provenance, or corrupt category file.

### Annotations

Expected record type:

- `annotation_memory_record` from `memory/annotations.json`.

Approved-only display rule:

- Show only applied annotation records.

Evidence/provenance expectation:

- Show target type, target ID, source scene, visibility status, evidence, and provenance status.

Future page:

- Future annotations page or annotation sidebar if later scheduled.

Empty state:

- "No approved annotations yet" or equivalent.

Warning state:

- Duplicate annotation IDs, broken target links, missing evidence/provenance, or corrupt category file.

Boundary:

- Annotation text is analysis/metadata only, not generated story prose.

### Continuity Warnings

Expected record type:

- `continuity_warning_memory_record` from `memory/continuity_warnings.json`.

Approved-only display rule:

- Show only applied continuity warning records.

Evidence/provenance expectation:

- Show warning type, severity, conflicting sources, affected records, review status, `no_rewrite_provided`, and provenance status.

Future page:

- Continuity / Consistency page, planned by WORKSPACE-016.

Empty state:

- "No approved continuity warnings yet" or equivalent.

Warning state:

- Duplicate warning IDs, missing `no_rewrite_provided`, broken conflicting source links, missing evidence/provenance, or corrupt category file.

Boundary:

- Continuity warnings may ask diagnostic questions but must not provide replacement prose.

### Future Dramatica / Storyform Truth Placeholder

Expected record type:

- None for this workspace phase.

Approved-only display rule:

- Placeholder only. Do not display Dramatica-specific truth as project memory/canon.

Evidence/provenance expectation:

- Future Dramatica work must define separate evidence, owner approval, and truth boundaries.

Future page:

- Future advanced Dramatica/storyform page only after workspace and owner-approved memory flows are implemented.

Empty state:

- "Future / Not Implemented" or equivalent.

Warning state:

- If storyform context exists, label it as separate context, not memory/canon.

## 5. Approved vs Candidate Labeling

Required labels:

- `Approved Canon`
- `Approved Memory`
- `Pending Candidate`
- `Rejected Candidate`
- `Archived Candidate`
- `Promotion Record Only`
- `Not Yet Applied`
- `Needs Owner Review`
- `Evidence Required`
- `Insufficient Evidence`
- `Future / Not Implemented`

Labeling rules:

- Labels must appear in UI copy and route/page specs where those states are represented.
- Labels must prevent owner confusion between candidate review and approved truth.
- No candidate should be visually blended into canon lists.
- Counts must be separated by status.
- Approved memory/canon counts must be applied-record counts only.
- Approved-candidate counts must be labeled "Approved Candidate" or "Not Yet Applied", not approved canon.
- Promotion-record counts must be labeled "Promotion Record Only" or "Audit Only".
- Pending, rejected, archived, duplicate, uncertain, and insufficient-evidence candidates must remain outside approved memory/canon lists.

Recommended count grouping:

```json
{
  "approved_memory_count": 0,
  "pending_candidate_count": 0,
  "approved_candidate_not_applied_count": 0,
  "promotion_record_only_count": 0,
  "rejected_candidate_count": 0,
  "archived_candidate_count": 0
}
```

## 6. Behavior Before Apply-Promotion Exists

First implementation may show:

- Empty approved memory/canon placeholders.
- Category cards with zero approved counts.
- OMI promotion-record snapshots labeled audit-only.
- Links to OMI Ideas/Candidates for candidate review.
- Health warnings for missing memory directory or existing corrupt memory files.
- Future apply-promotion placeholder.

First implementation must not:

- Create `memory/` or `memory/*.json` by opening the page.
- Create `memory/index.json` by opening the page.
- Create OMI records.
- Create promotion records.
- Expose an apply-promotion button unless a future explicit flow exists.
- Convert promotion records to memory/canon.
- Run hidden extraction.
- Run hidden Dramatica analysis.
- Call Ollama, qwen3, or any model.
- Generate summaries.
- Mutate project files.
- Write JSONL/training records.
- Update `training/data/dataset_manifest.json`.

If promotion records exist before apply-promotion exists:

- Show them as "Promotion Record Only".
- Show "Not Yet Applied".
- Do not add them to approved memory/canon counts.

If approved candidates exist before apply-promotion exists:

- Show them as "Approved Candidate" or "Needs Apply-Promotion".
- Do not add them to approved memory/canon counts.

## 7. Future Apply-Promotion Dependency

Future apply-promotion must be separately designed and tested before this page can show real applied memory/canon beyond existing manually present files.

Future apply-promotion must require:

- Approved candidate.
- Explicit destination.
- Attached evidence/provenance.
- Promotion record.
- Final owner confirmation.
- Safe target type.
- Valid memory record shape.
- Atomic write or rollback-safe behavior.
- Audit trail.
- Failure handling.
- No prose generation.
- No bible/storyform mutation unless destination is explicitly designed and approved.

Apply-promotion must fail closed when requirements are missing.

Future apply-promotion output should:

- Write approved memory/canon records into the correct `memory/*.json` category file.
- Update `memory/index.json` only as derived navigation metadata.
- Preserve source candidate IDs and promotion record IDs.
- Preserve evidence/provenance.
- Preserve uncertainty where applicable.
- Record revision history where practical.
- Leave scenes, notes, materials, OMI candidates, and promotion records unchanged except for explicit status updates designed by that future flow.

Future apply-promotion must not:

- Write generated story prose.
- Mutate scene/chapter prose.
- Mutate notes/materials body content.
- Treat model output as truth by default.
- Mutate `bible.json` or `storyform.json` unless separately designed and owner-approved.
- Write training data.
- Call a model to fill missing fields.

## 8. API Planning

These route groups are future planning only. Do not implement them during WORKSPACE-011.

Every route must validate `project_id` as a safe single path component and preserve project-local state. Memory routes must reject traversal, absolute paths, unsafe category names, unsupported schema versions, and invalid record IDs.

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create memory files on read.
- First-version routes must not apply promotions.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory`

Version:

- First-version planning.

Purpose:

- Return a lightweight approved-memory/canon page payload.

Page dependency:

- Page Header.
- Canon Status Banner.
- Approved Memory / Canon Category Cards.
- Empty-State Guidance.

Validation:

- Safe `project_id`.
- Existing project.
- Optional existing memory folder is read-only.

No-prose boundary:

- Return counts and stored metadata only.
- No generated summaries.

Candidate/canon boundary:

- Approved counts only from applied memory files.
- Candidate and promotion counts labeled separately.

Expected errors:

- 400 invalid project ID.
- 404 missing project.
- 422 corrupt memory metadata or unsupported schema.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/index`

Version:

- First-version planning if an index exists; optional.

Purpose:

- Load derived memory index metadata.

Page dependency:

- Category cards.
- Future search/navigation.

Validation:

- Safe `project_id`.
- `memory/index.json` must be JSON object if present.
- Index entries must not be treated as authoritative over category files.

No-prose boundary:

- No generated summaries.

Candidate/canon boundary:

- Index may list applied records only.
- Missing/stale index must not make candidates canon.

Expected errors:

- 404 no index, treated as valid empty/degraded state where appropriate.
- 422 corrupt or stale index.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/{category}`

Version:

- First-version planning.

Purpose:

- Load approved records for one memory category.

Page dependency:

- Category cards.
- Future dedicated approved category pages.

Validation:

- Safe `project_id`.
- Category allow-list only: `characters`, `locations`, `objects`, `organizations`, `timeline`, `relationships`, `plot_threads`, `open_questions`, `annotations`, `continuity_warnings`, and future allowed categories.
- Category file envelope and record type match expected category.
- Record IDs unique.

No-prose boundary:

- Return stored approved records only.
- Do not generate descriptions, summaries, or fixes.

Candidate/canon boundary:

- Return applied memory/canon records only.
- Candidate records must come from OMI routes, not memory category routes.

Expected errors:

- 400 invalid project/category.
- 404 missing category file, treated as empty where appropriate.
- 422 corrupt category file, unsupported schema, duplicate IDs, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/health`

Version:

- First-version planning.

Purpose:

- Return non-destructive health warnings for memory/canon state.

Page dependency:

- Health / Warning Area.
- Canon Status Banner.

Validation:

- Safe `project_id`.
- Read-only scans only.

No-prose boundary:

- Warnings are factual status only.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, or rewrite records.

Expected errors:

- 400 invalid project ID.
- 404 missing project.
- 500 sanitized partial scan failure.

### `GET /api/projects/{project_id}/omi/promotions`

Version:

- Existing OMI-adjacent route group; page dependency planning only.

Purpose:

- Return OMI promotion records for audit-only snapshot.

Page dependency:

- Promotion Records Snapshot.
- Canon Status Banner.

Validation:

- Safe `project_id`.
- Promotion IDs safe.
- Promotion records JSON object only.

No-prose boundary:

- Return stored promotion metadata only.

Candidate/canon boundary:

- Promotion records are not memory/canon.
- Page must label them "Promotion Record Only" and "Not Yet Applied" unless future applied result links exist.

Expected errors:

- 400 invalid project ID.
- 404 missing project or missing OMI folder, treated as empty where appropriate.
- 422 corrupt promotion record.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/summary`

Version:

- Optional first-version route if it simplifies the frontend.

Purpose:

- Return compact approved memory counts, candidate/promotion audit counts, and warning summaries.

Page dependency:

- Header.
- Status banner.
- Category grid.

Validation:

- Safe `project_id`.
- Read-only.
- Must not trust stale derived indexes as authoritative.

No-prose boundary:

- Counts and labels only.
- No generated summaries.

Candidate/canon boundary:

- Separate approved records, approved-but-not-applied candidates, pending candidates, rejected candidates, archived candidates, and promotion records.

Expected errors:

- Invalid project ID.
- Missing project.
- Corrupt memory/OMI metadata.
- Partial read failure.

### `POST /api/projects/{project_id}/memory/apply-promotion`

Version:

- Future-only. Do not implement in first Project Memory / Canon page implementation.

Purpose:

- Apply an owner-approved promotion record into a memory/canon category file.

Page dependency:

- Future apply-promotion flow only after separate design.

Validation:

- Safe `project_id`.
- Safe `promotion_id`.
- Approved candidate.
- Explicit destination.
- Evidence/provenance.
- Final owner confirmation.
- Safe target type/category.
- Valid memory record shape.
- Atomic write/rollback.

No-prose boundary:

- Must not generate missing fields or prose.

Candidate/canon boundary:

- Must write applied memory/canon only after all gates pass.
- Must preserve audit trail.

Expected errors:

- 400 invalid ID or unsafe target.
- 404 missing project/candidate/promotion.
- 409 conflict or stale promotion.
- 422 missing approval/evidence/provenance/final confirmation/valid memory shape.
- 500 rollback-safe write failure.

## 9. Frontend Planning

Do not implement UI in WORKSPACE-011.

Future components:

- `ProjectMemoryCanonPage`.
- `CanonStatusBanner`.
- `MemoryCategoryGrid`.
- `MemoryCategoryCard`.
- `CandidateCanonExplanation`.
- `PromotionRecordsSnapshot`.
- `MemoryHealthWarning`.
- `EmptyCanonState`.
- `FutureApplyPromotionPlaceholder`.
- `EvidenceProvenanceSummary`.
- `LinkToOMIReview`.

Frontend responsibilities:

- Track active project.
- Load memory/canon summary without creating files.
- Load OMI promotion snapshots only as audit-only data.
- Separate approved memory counts from candidate and promotion counts.
- Render empty states before apply-promotion exists.
- Render health warnings non-destructively.
- Link to OMI Ideas/Candidates for candidate review.
- Link to Project Overview for project status.
- Avoid rendering automatic promotion controls.
- Avoid rendering AI writing buttons.
- Keep analysis/candidate panels separate from approved-memory lists.

UI labeling rules:

- Owner-authored source material should be labeled source/evidence/provenance, not canon by default.
- OMI candidates should be labeled by candidate status.
- Promotion records should be labeled audit-only.
- Applied memory/canon should be labeled approved memory or approved canon.
- Future/not implemented states must be explicit.

Prohibited UI controls:

- Write.
- Continue.
- Rewrite.
- Polish.
- Improve.
- Expand.
- Imitate style.
- Generate canon.
- Generate memory.
- Auto-promote.
- Apply promotion, until a future explicit flow is designed and implemented.
- Repair canon automatically.
- Summarize story with AI.

## 10. Health and Warning States

Warnings to support:

- Memory directory missing.
- Memory index missing.
- Memory files corrupt.
- Unsupported memory schema version.
- Promotion records exist but no applied memory exists.
- Candidates approved but not applied.
- Pending candidates shown elsewhere.
- Evidence/provenance missing.
- Duplicate memory record IDs.
- Broken source references.
- Broken candidate references.
- Broken promotion record references.
- Broken cross-record links.
- Stale or inconsistent `memory/index.json`.
- Category file record type mismatch.
- Continuity warning missing `no_rewrite_provided`.
- Relationship memory displayed without non-Dramatica label.
- Bible/storyform mismatch if a future route surfaces it, without Dramatica assumptions.

Warning rules:

- Warnings are non-destructive.
- No auto-repair unless a future owner-approved repair flow exists.
- No auto-delete.
- No silent canon rewrite.
- No silent link repair.
- No hidden apply-promotion.
- No host filesystem path leakage in UI/API errors.
- Blocking warnings should prevent approved display for invalid files.
- Non-blocking warnings may allow partial category display where safe.

Recommended severity levels:

- `blocking`: approved display is unsafe for the affected area.
- `warning`: page can load with degraded/partial data.
- `info`: empty state, future feature, or candidate-only note.

## 11. Future Tests

Future implementation should include tests for:

- Page loads with no memory directory.
- Page loads empty canon state.
- Page displays approved memory counts only when memory files exist.
- Page separates pending candidates from approved canon.
- Page separates rejected candidates from approved canon.
- Page separates archived candidates from approved canon.
- Promotion records shown as audit-only.
- Approved-but-not-applied state is labeled.
- Opening page does not create memory files.
- Opening page does not create `memory/index.json`.
- Opening page does not mutate project files.
- Opening page does not create OMI records.
- Opening page does not create promotion records.
- Opening page does not promote candidates.
- Opening page does not mutate `bible.json` or `storyform.json`.
- No model/Ollama call.
- No generated summaries.
- No hidden extraction.
- No Dramatica analysis.
- No AI prose-generation controls.
- Corrupt memory files show warnings.
- Unsupported memory schema shows warning.
- Duplicate memory record IDs show warnings.
- Broken evidence/source links show warnings.
- Broken candidate/promotion links show warnings.
- Pending/rejected/archived candidates never appear in approved category lists.
- Promotion-record-only items never appear in approved category lists.
- Relationship memory records are not labeled as Dramatica Relationship Story proof.
- Path traversal rejected.
- Unsafe category rejected.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 12. Deferred Decisions

Deferred to future implementation tasks:

- Exact first category card/subpage depth versus index-only page.
- Whether `memory/index.json` is required before category files or remains derived/lazy.
- Whether category files are loaded directly, through summary endpoint, or through frontend composition.
- Exact approved/candidate count strategy.
- Whether approved-but-not-applied gets its own count and filter.
- Memory health validation depth for first implementation.
- Evidence locator strategy.
- Broken-source repair flow.
- Duplicate memory record handling.
- Apply-promotion flow design.
- Atomic write/rollback model and tests.
- Apply-promotion failure handling.
- Future route/component naming.
- Whether `/memory/summary` is needed.
- Archive/delete/supersede behavior for applied memory records.
- Whether `bible.json` can ever mirror a subset of approved memory.
- Whether `storyform.json` can ever mirror a subset of approved memory.
- Future Dramatica/storyform truth boundary once Dramatica work resumes.
- Browser/manual acceptance checklist for implemented Project Memory / Canon page.

## 13. Implementation Non-Goals

WORKSPACE-011 does not implement:

- Project Memory / Canon UI.
- Backend memory/canon routes.
- Apply-promotion.
- Candidate extraction.
- Project creation.
- Project selector/library.
- Editor changes.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
