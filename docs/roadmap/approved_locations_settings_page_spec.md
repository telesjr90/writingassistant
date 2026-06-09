# WORKSPACE-014: Approved Locations / Settings Page Spec

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
- WORKSPACE-011: `docs/roadmap/project_memory_canon_page_structure_spec.md`
- WORKSPACE-012: `docs/roadmap/omi_ideas_candidates_page_spec.md`
- WORKSPACE-013: `docs/roadmap/approved_characters_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- WORKSPACE-016: `docs/roadmap/approved_plot_threads_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Locations / Settings page should be the future project-local destination for owner-approved location and setting memory/canon records. It must show only location/setting records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, and approved-but-not-applied location candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

The Approved Locations / Settings page should:

- Show owner-approved location/setting memory/canon records only when those records are present in the future `memory/locations.json` file.
- Treat approved location/setting truth as project memory/canon only after owner approval, a recorded promotion record, and a successful future apply-promotion step.
- Clearly distinguish approved location/setting truth from OMI location candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved location/setting back to source evidence, provenance, source candidate IDs, source scene IDs, source promotion record IDs, and approval metadata.
- Show aliases, alternate names, regions, or nested places only when the approved record explicitly carries them.
- Show unresolved or missing location/setting fields honestly as `Unknown`, `Not approved yet`, or `Not recorded` instead of guessing.
- Show an empty state when no approved location/setting records exist yet.
- Show a candidate backlog snapshot that links only counts and entry points to the OMI Ideas / Candidates page.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic candidate extraction.
- Avoid apply-promotion behavior.
- Avoid silent mutation of approved memory/canon or OMI records.
- Avoid Dramatica-specific setting/world claims in this workspace phase.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Locations / Settings Page Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for location candidates.
- Source material is not approved location/setting memory/canon by default.
- A location mentioned in a scene is not an approved location record by itself.
- A setting described in a note is not an approved setting record by itself.
- Source material must not be copied into approved location memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions a location is not an approved location record.

### OMI Location Candidates

Definition:

- Structured `location_candidate` records that have not been applied to approved memory/canon.

Rules:

- Location candidates are not canon.
- Location candidates must not appear in the approved location list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.

### Approved-but-Not-Applied Candidates

Definition:

- `location_candidate` records the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved location memory/canon.
- Approved-but-not-applied candidates must not appear in the approved location list.
- The page may show counts and entry points only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved location records.
- Promotion records may be linked as provenance from a location record that an apply-promotion step actually created.

### Applied Location / Setting Memory / Canon Records

Definition:

- Durable owner-approved `location_memory_record` entries written to the future `memory/locations.json` file by a future apply-promotion step.

Rules:

- Applied location/setting records are the only records allowed in the approved location list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, and approval metadata.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/locations.json` entries.

### Place Hierarchy

Definition:

- Future `parent_location_id` and `child_location_ids` references between approved location records.

Rules:

- Place hierarchy must come from approved memory/canon records only.
- Place hierarchy must not be derived from scene text or notes at page load.
- Cycles in the parent/child chain must surface as non-destructive warnings.
- The first version of this page must not render a hierarchy tree; it must show a placeholder.
- Missing parent/child links must be shown as `Unknown` or `Not recorded`, not inferred.

### Scene Usage

Definition:

- Future `first_seen_scene_id` and `mentioned_in_scene_ids` references between approved location records and scene files.

Rules:

- Scene usage must come from approved memory/canon records only.
- Broken scene references must show warnings and must not invent replacements.
- Scene usage counts are derived from approved records; they are not generated summaries.

### Future Dramatica Setting / World Claims

Definition:

- Future Dramatica storyform-specific setting or world claims such as story world, genre universe, or setting-element mappings.

Rules:

- Dramatica setting/world claims are deferred.
- The first version of this page must not display any Dramatica setting or world claim.
- Generic labels such as `Story World` or `Setting Type` are not required and should not be inferred.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved location display.
- The first implementation of this page must not call a model.

### Insufficient Evidence

Definition:

- Location evidence/provenance is missing, weak, broken, unsafe, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting or rewriting the location record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any location that already exists.

## 3. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Location` | Marks each applied `location_memory_record`. |
| `Approved Setting` | Equivalent label when the owner has used `Approved Setting` for a record; default to `Approved Location` for storage uniformity. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Approved Candidate` | Marks approved-but-not-applied location candidates on the OMI page; this page may show counts and links only. |
| `Pending Candidate` | Marks pending OMI location candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI location candidates on the OMI page. |
| `Archived Candidate` | Marks archived OMI location candidates on the OMI page. |
| `Needs Revision` | Marks needs-revision OMI location candidates on the OMI page. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied location record. |
| `Source / Evidence` | Marks source scene, source note, source material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved location fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Hierarchy Placeholder` | Marks that the place hierarchy view is not yet implemented. |
| `Scene Usage Placeholder` | Marks that the scene usage view is not yet implemented. |
| `Cycle Detected` | Marks parent/child location references that form a cycle. |
| `Future / Not Implemented` | Marks areas such as map/graph visualization, hierarchy tree, or Dramatica setting claims that are not part of the first implementation. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved location list.
- Counts must be separated by status.
- Approved location counts must come from applied `location_memory_record` entries only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Location`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved location list.
- Cycle warnings must use `Cycle Detected` and must not auto-repair.
- Hierarchy and scene usage placeholders must use `Hierarchy Placeholder` and `Scene Usage Placeholder` and must not invent missing links.

## 4. First-Version Page Layout

First-version sections:

- Page Header.
- Location Page Boundary Banner.
- Approved Location / Setting List.
- Location Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Place Hierarchy Placeholder.
- Scene Usage Snapshot.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and the Approved Locations / Settings area.
- Show approved-only counts and link back to the project memory/canon index when available.

Data source:

- Active project metadata from `project.json`.
- Future `memory/index.json` and `memory/locations.json` only if those files already exist.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate location descriptions, worldbuilding prose, atmosphere prose, or setting summaries.

Candidate/canon boundary:

- Approved location counts must come from applied memory/canon records only.
- Candidate or promotion counts must be labeled separately and must not appear as approved counts.

Empty state:

- Show zero approved locations and a link to OMI Ideas / Candidates.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved location metadata shows a warning and avoids approved display.

### Location Page Boundary Banner

Purpose:

- State that the page is owner-approved location/setting memory/canon only, not candidate review and not an AI writing surface.

Data source:

- Static product boundary copy.

No-prose boundary:

- Banner must include or link to the standard refusal policy.
- No write, rewrite, continue, polish, improve, imitate, expand, or generate controls.

Candidate/canon boundary:

- Banner must state that OMI location candidates, approved-but-not-applied candidates, and promotion records are not approved location memory/canon.
- Banner must state that Dramatica setting/world claims are not part of this page.

Empty state:

- Banner remains visible even when no approved locations exist.

Error state:

- Banner remains visible even when approved location data is partially corrupt.

### Approved Location / Setting List

Purpose:

- Show applied location/setting memory/canon records for the selected project.
- Provide a deterministic ordering and a simple local filter/search over safe text fields.

Data source:

- Future `memory/locations.json` only.
- Future `memory/index.json` as derived convenience state only.

No-prose boundary:

- Display stored record fields only.
- Do not generate location descriptions, worldbuilding summaries, atmosphere prose, mood prose, or backstory.
- Do not include "describe this place," "expand setting," "rewrite location," or "generate lore" actions.

Candidate/canon boundary:

- Each row must use `Approved Location` (or `Approved Setting` if the owner has explicitly used that label for the record).
- Approved counts must come from applied memory/canon records only.
- Pending/rejected/archived/approved-but-not-applied candidates must not be blended in.

Empty state:

- Show a guidance block that no approved locations exist yet and link to OMI Ideas / Candidates.

Error state:

- Corrupt location records, duplicate IDs, unsupported schema, or stale index entries show warnings and the affected location must not appear as a normal approved row.

### Location Detail Panel

Purpose:

- Show the selected approved location's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, linked sources, parent/child references, scene usage links, approval metadata, and provenance summary.

Data source:

- The selected applied `location_memory_record` from `memory/locations.json`.

No-prose boundary:

- Display stored fields only.
- No generated description, no generated atmosphere prose, no generated worldbuilding summary, no generated history, no style imitation.

Candidate/canon boundary:

- Use `Approved Location` labeling.
- The location must be an applied record, not a candidate.
- Promotion records are linked as provenance, not as the location itself.

Empty state:

- No selection should show "select an approved location" guidance.

Error state:

- Broken cross-record links, missing source references, or unsupported schema must show warnings and not invent replacements.

### Evidence / Provenance Panel

Purpose:

- Show evidence, source references, source kind, source scenes, source notes/materials, source candidate IDs, source promotion record IDs, hashes if stored, confidence at promotion time, and approval timestamps.

Data source:

- Approved location record `source_candidate_ids`, `promotion_record_ids`, `evidence_summaries`, `provenance`, `evidence_ids`, and `confidence_at_promotion`.

No-prose boundary:

- Evidence display must not generate explanatory prose beyond stored metadata and fixed UI labels.
- No generated "what this location represents" or "why this location matters" prose.

Candidate/canon boundary:

- Evidence supports owner review and traceability.
- Evidence does not establish truth by itself outside the apply-promotion step that created the record.

Empty state:

- Missing evidence must show `Evidence Required` or `Insufficient Evidence` where applicable, never guessed.

Error state:

- Broken source references, unsafe paths, or unsupported source kinds must show warnings and not invent replacements.

### Linked Sources Panel

Purpose:

- Show linked scenes, chapters, notes, materials, and other approved memory records that the location is connected to.
- Show linked approved character, object, organization, timeline, plot thread, and continuity warning records when those records are available.

Data source:

- Approved location `first_seen_scene_id`, `mentioned_in_scene_ids`, `connected_character_ids`, `connected_event_ids`, and any other cross-record references that exist in future schema.

No-prose boundary:

- Show source title, ID, and link.
- Do not summarize or rewrite source body text.

Candidate/canon boundary:

- Only applied memory/canon records may appear as linked sources here.
- Candidate references must route through the OMI page, not through this page.

Empty state:

- Missing or empty link arrays should show "no linked approved sources" or equivalent.

Error state:

- Broken cross-record links should show warnings and not be silently dropped.

### Place Hierarchy Placeholder

Purpose:

- Reserve space for the future approved place hierarchy view.

Data source:

- Approved location `parent_location_id` and `child_location_ids` only if those fields exist in the applied record.

No-prose boundary:

- No generated hierarchy narrative.
- No generated "this place contains" prose.

Candidate/canon boundary:

- Hierarchy must be built from approved memory/canon records only.
- The first version must not infer hierarchy from scene text, notes, or OMI candidates.
- Cycle warnings must surface as non-destructive `Cycle Detected` warnings.

Empty state:

- Show the placeholder.

Error state:

- Cycle detection or unresolved parent/child references must show warnings and not auto-repair.

### Scene Usage Snapshot

Purpose:

- Show approved location scene usage counts and links based on `first_seen_scene_id` and `mentioned_in_scene_ids`.
- Provide a simple deterministic count without generating scene summaries.

Data source:

- Approved location scene references only.

No-prose boundary:

- Counts and links only.
- No generated scene summaries, atmosphere prose, or "what happens here" prose.

Candidate/canon boundary:

- Scene usage must come from approved memory/canon records only.
- Broken scene references must show warnings and must not be silently dropped.

Empty state:

- Show "no approved scene usage" or equivalent.

Error state:

- Broken scene references must show warnings and must not be invented.

### Candidate Backlog Snapshot

Purpose:

- Show owner-visible counts and links for OMI location candidates.
- Help the owner see whether location review is needed in OMI.

Data source:

- `omi/index.json` candidate counts and lightweight candidate metadata when valid.

No-prose boundary:

- Counts and labels only.
- No generated candidate summaries or worldbuilding hints.

Candidate/canon boundary:

- Counts must be clearly labeled `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, or `Promotion Record Only` and must not appear in approved location counts.
- The page may link only to the OMI Ideas / Candidates page for review.

Empty state:

- Show no candidates and link to OMI Ideas / Candidates.

Error state:

- Corrupt OMI metadata should show a warning and avoid using its counts as truth.

### Empty State

Purpose:

- Explain what the page shows when no approved locations exist yet.

Data source:

- Static product boundary copy plus project metadata.

No-prose boundary:

- Guidance is operational, not generated story text.

Candidate/canon boundary:

- Link to OMI Ideas / Candidates for candidate review.
- State that approved locations appear only after future apply-promotion.

Empty state:

- Missing `memory/locations.json`, empty `records` array, or absent `memory/` folder are valid empty states.

Error state:

- If project metadata is invalid, show recovery/help instead of empty-state guidance.

### Warning State

Purpose:

- Surface non-destructive health warnings about the approved location store.

Data source:

- Project validation.
- Memory index/category validation.
- Cross-record reference checks where safe.
- Parent/child cycle detection where safe.

No-prose boundary:

- Warnings are factual status messages only.
- No generated repair text that rewrites location truth.

Candidate/canon boundary:

- Warnings must not promote, repair, delete, merge, or rewrite location records.

Empty state:

- Show no warnings when clean.

Error state:

- Blocking warnings prevent approved display for the affected location.
- Non-blocking warnings allow partial display where safe.

### Future Page Link Reference

Purpose:

- Reserve space for navigation to future approved pages.

Data source:

- Static route references.

No-prose boundary:

- Link text only.

Candidate/canon boundary:

- Future approved page links (characters, timeline, plot threads, continuity/consistency, approved memory/canon index) must be labeled as future or as currently available depending on implementation status.

Empty state:

- Show a guidance block for future pages.

Error state:

- Disable links whose target pages are not yet implemented.

## 5. Approved Location / Setting Display Model

Approved location/setting records must be displayed only from applied `location_memory_record` entries. The first version of this page may display the following fields when they exist in the stored record.

| Field | Source | Display rule |
| --- | --- | --- |
| `location_id` | Applied record | Stable ID shown in small text. |
| `display_name` | `canonical_name` | Primary label. |
| `alternate_names` | Applied record | Show only when present; do not infer or guess. |
| `location_type` | Applied record | Show only if explicitly present; do not infer Dramatica setting or world type. |
| `status` | Applied record | Show `active`, `needs_review`, `superseded`, `archived`, or `deleted_by_owner` if present. |
| `short_owner_approved_description` | `description_notes` or `notes` | Show only if the owner has approved the description; otherwise show `Not approved yet` or `Not recorded`. Never display AI-generated worldbuilding or setting description. |
| `parent_location_id` | Applied record | Show only when the applied record explicitly carries it. Cycle detection must surface a `Cycle Detected` warning. |
| `child_location_ids` | Applied record | Show only when the applied record explicitly carries it. Cycle detection must surface a `Cycle Detected` warning. |
| `linked_scene_ids` | `first_seen_scene_id`, `mentioned_in_scene_ids` | Show scene IDs and titles. |
| `linked_character_ids` | `connected_character_ids` | Show approved character IDs and labels when available. |
| `linked_object_ids` | Applied record | Show approved object IDs and labels when available. |
| `linked_timeline_event_ids` | `connected_event_ids` | Show approved timeline event IDs and labels when available. |
| `first_seen_source` | `first_seen_scene_id` plus metadata | Show source scene title and ID. |
| `evidence_summaries` | Applied record | Show stored summaries. |
| `confidence_at_promotion` | Applied record | Show as a stored label or number, not as canon certainty. |
| `created_at` | Applied record | Show ISO-8601 timestamp. |
| `updated_at` | Applied record | Show ISO-8601 timestamp. |
| `approved_at` | Applied record | Show ISO-8601 approval timestamp. |
| `approved_by` | Applied record | Show owner or reviewer identifier. |
| `source_candidate_ids` | Applied record | Show source OMI candidate IDs and link to the OMI page for each. |
| `promotion_record_ids` | Applied record | Show source promotion record IDs and link to the OMI page for each as `Promotion Record Only` until apply-promotion actually created the location. |
| `revision_history` | Applied record | Show when present. |
| `supersedes_record_ids` | Applied record | Show when present. |
| `superseded_by_record_id` | Applied record | Show when present. |
| `notes` | Applied record | Show owner notes only. |

Display rules:

- All displayed location/setting truth must come from applied memory/canon records.
- Unapproved candidates must not appear as truth.
- Generated worldbuilding prose is prohibited.
- Generated location descriptions are prohibited.
- Generated atmosphere, mood, or "this place feels like" prose is prohibited.
- Owner-approved summaries may be displayed only if explicitly approved or owner-authored.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded` and must not be guessed.
- `evidence_summaries` must not be paraphrased into prose.
- `confidence_at_promotion` must be displayed as a stored value, never as a current truth certainty.
- `alternate_names` and region labels must come from the approved record only.
- Dramatica setting/world claims must not be displayed.
- Parent/child hierarchy must come from approved records only; cycles must surface as warnings, not be auto-repaired.

## 6. Page Operations

First-version allowed operations:

- View the approved location/setting list.
- Select a location to view its detail panel.
- Filter and search the approved location/setting list locally.
- Open linked source scene/note/material from the linked sources panel.
- Open the source OMI candidate or promotion record from the provenance links.
- Open the OMI Ideas / Candidates page from the candidate backlog snapshot.
- Open the future approved place hierarchy placeholder.
- Open the future approved scene usage placeholder.

First-version operations must:

- Be read-only with respect to approved memory/canon.
- Be read-only with respect to OMI records.
- Avoid model/Ollama calls during navigation, list, filter, search, or selection.
- Avoid generated summaries, generated descriptions, or generated worldbuilding.
- Avoid any silent mutation of `memory/locations.json`, `memory/index.json`, or OMI records.
- Avoid any direct apply-promotion action from this page.

Future-only operations (out of scope for WORKSPACE-014 first implementation):

- Editing approved location memory/canon directly.
- Merging approved locations.
- Splitting approved location records.
- Archiving approved locations.
- Restoring superseded approved locations.
- Creating new approved locations from this page.
- Apply-promotion from this page.
- Extracting location candidates from owner-authored text on this page.
- Map/graph visualization.
- Timeline/location visualization.
- Worldbuilding expansion or generated descriptions.

Future operations must be defined in separate future specs and require separate tests.

## 7. Local Search and Filter

First-version search and filter must be local and deterministic.

Allowed search/filter dimensions:

- `display_name` / `canonical_name`.
- `alternate_names` if present.
- `location_type` if present.
- `status` if present.
- `tags` if present.
- Approved description if the owner has approved a description.
- Linked source IDs (`first_seen_scene_id`, `mentioned_in_scene_ids`, `connected_*` IDs).
- Parent/child location IDs if present.
- `source_candidate_ids`.
- `promotion_record_ids`.

First-version search/filter must:

- Run locally over already-loaded data.
- Avoid semantic search.
- Avoid model/Ollama calls.
- Avoid generated summaries, descriptions, or expansions.
- Avoid any candidate extraction during search.
- Avoid any apply-promotion or OMI mutation during search.
- Label results with their status: `Approved Location`, `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, `Promotion Record Only`, or `Not Yet Applied`.

Search rules:

- No global fuzzy expansion.
- No global synonyms.
- No language model ranking.
- No AI ranking explanations.
- No hidden generated location descriptions or worldbuilding in result rows.

## 8. Warning and Error States

The page must surface non-destructive warnings and errors. Warnings are not allowed to auto-repair, auto-delete, silently rewrite, or silently promote records.

Required warnings and errors:

- Missing `memory/` directory.
- Missing `memory/locations.json`.
- Missing `memory/index.json` if a future implementation depends on it.
- Corrupt `memory/locations.json`.
- Corrupt `memory/index.json` if present.
- Unsupported `memory/locations.json` schema.
- Duplicate `location_id` values within `memory/locations.json`.
- `location_id` that does not match a safe single path component.
- `location_id` references that fail path safety.
- Approved location references missing source candidate.
- Approved location references missing promotion record.
- Broken linked scene references.
- Broken linked note/material references.
- Broken cross-record references to other approved memory records.
- Broken linked character/object/timeline references.
- Parent/child location cycles (`Cycle Detected`).
- OMI location candidates exist but no approved locations yet.
- Promotion records present but no applied location record.
- Hierarchy links exist but the hierarchy view is not implemented yet.
- Scene usage links exist but linked scenes are missing.
- Evidence/provenance missing where required.
- Insufficient evidence labels carried over from apply-promotion.

Warning rules:

- Warnings are non-destructive.
- No auto-repair.
- No auto-delete.
- No identity rewrite.
- No silent candidate promotion.
- No silent deletion of corrupt records.
- No silent reparenting of cycle records.
- No host filesystem path leakage in UI/API errors.
- Blocking warnings should prevent approved display for the affected location.
- Non-blocking warnings may allow partial display where safe.

Recommended severity levels:

- `blocking`: approved display is unsafe for the affected location.
- `warning`: page can load with degraded or partial data.
- `info`: empty state, future feature, or candidate-only note.

## 9. Relationship to Other Pages

Project Memory / Canon index page (WORKSPACE-011):

- Provides the parent navigation entry and category cards.
- The Locations / Settings card must show approved-only counts and link to this page.
- Candidate counts must remain on the OMI page.

Project Overview (WORKSPACE-008):

- May show approved location count only.
- May show candidate count labeled as candidate/audit.
- May link to this page and to the OMI page.

OMI Ideas / Candidates (WORKSPACE-012):

- Owns candidate review, owner decision, destination, evidence/provenance, and promotion record creation for location candidates.
- This page must not duplicate OMI review actions.

Chapters / Scenes (WORKSPACE-009) and Notes / Materials (WORKSPACE-010):

- May show location references in scene or note metadata.
- This page is the project-local approved destination for those references.

Approved Characters (WORKSPACE-013):

- Is a sibling approved-only category page.
- Cross-record references should be consistent with the Approved Characters page's display rules.

Future approved pages (timeline, plot threads, relationships, continuity/consistency, approved memory/canon index):

- Should follow the same approved-only display rules.
- Cross-record links should be consistent with this page's display rules.

## 10. API Planning

These routes are future planning only. Do not implement them in WORKSPACE-014.

Every route must validate `project_id` as a safe single path component and preserve project-local state. Location routes must reject traversal, absolute paths, unsafe IDs, unsupported schema versions, duplicate IDs, and invalid record shapes.

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/locations.json` or `memory/index.json` on read.
- First-version routes must not apply promotions.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/locations`

Version:

- First-version planning.

Purpose:

- Return the approved location/setting list for the selected project.

Page dependency:

- Page Header.
- Approved Location / Setting List.
- Empty State.
- Warning State.

Validation:

- Safe `project_id`.
- Existing project.
- `memory/locations.json` envelope shape when present.

No-prose boundary:

- Return stored location records only.
- No generated descriptions, summaries, worldbuilding, or atmosphere prose.

Candidate/canon boundary:

- Return applied location memory/canon records only.
- Candidate records must come from OMI routes, not memory category routes.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project, treated as empty where appropriate.
- 422 corrupt `memory/locations.json`, unsupported schema, duplicate IDs, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/locations/{location_id}`

Version:

- First-version planning.

Purpose:

- Return a single approved location record.

Page dependency:

- Location Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.

Validation:

- Safe `project_id` and `location_id`.
- `location_id` is one of the IDs in `memory/locations.json`.
- `location_id` is a safe single path component.

No-prose boundary:

- Return stored location fields only.
- Do not generate description, atmosphere, worldbuilding, or style imitation.

Candidate/canon boundary:

- Return applied location records only.

Expected errors:

- 400 invalid ID.
- 404 missing project or location.
- 422 corrupt or unsupported record.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/locations/{location_id}/provenance`

Version:

- First-version planning.

Purpose:

- Return provenance metadata for a single approved location.

Page dependency:

- Evidence / Provenance Panel.

Validation:

- Safe `project_id` and `location_id`.

No-prose boundary:

- Return stored provenance only.
- No generated explanations.

Candidate/canon boundary:

- Provenance is audit metadata, not a location description.

Expected errors:

- 400 invalid ID.
- 404 missing project or location.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/locations/health`

Version:

- First-version planning.

Purpose:

- Return non-destructive health warnings for the approved location store.

Page dependency:

- Warning State.

Validation:

- Safe `project_id`.
- Read-only scans only.
- Cycle detection must be non-mutating.

No-prose boundary:

- Warnings are factual status only.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, or rewrite location records.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project.
- 500 sanitized partial scan failure.

### `GET /api/projects/{project_id}/memory/summary` (composed)

Version:

- Optional first-version route.

Purpose:

- Provide approved location counts alongside other approved category counts.

Page dependency:

- Page Header.

Validation:

- Safe `project_id`.
- Read-only.

No-prose boundary:

- Counts and labels only.

Candidate/canon boundary:

- Counts must be applied record counts only.
- Candidate and promotion counts must be labeled separately.

Expected errors:

- Invalid `project_id`.
- Missing project.
- Corrupt memory metadata.

### `POST /api/projects/{project_id}/memory/apply-promotion` (future-only)

Version:

- Future-only.

Purpose:

- Apply a promotion record into durable memory/canon in a later explicit task.

Page dependency:

- Not a first implementation dependency for this page.

Validation:

- Future apply-promotion design must define atomic writes, target mapping, evidence/provenance, revision history, rollback/fail-closed behavior, and owner confirmation.

No-prose boundary:

- Must not write generated story prose.

Candidate/canon boundary:

- This is the only future route group that may create applied location memory/canon from a promotion record.

Expected errors:

- Deferred.

## 11. Frontend Planning

Do not implement UI in WORKSPACE-014.

Future components:

- `ApprovedLocationsSettingsPage`
- `ApprovedLocationsBoundaryBanner`
- `ApprovedLocationList`
- `ApprovedLocationListItem`
- `ApprovedLocationDetailPanel`
- `LocationEvidencePanel`
- `LocationSourceLinksPanel`
- `LocationHierarchyPlaceholder`
- `LocationSceneUsageSnapshot`
- `LocationCandidateBacklogSnapshot`
- `LocationSearchFilterControls`
- `LocationWarningsPanel`
- `LocationEmptyState`
- `LocationFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No "describe this place" button.
- No "expand setting" button.
- No "rewrite location" button.
- No "generate lore" button.
- No "generate worldbuilding" button.
- No "improve location" button.
- No "polish location" button.
- No style imitation controls.
- No generated summaries.
- No apply-promotion button.
- No archive/merge/split controls.
- No direct edit of approved location records from this page.
- No mutation of `memory/locations.json` or `memory/index.json` on the client.
- No mutation of OMI records.
- No JSONL/training writes.
- No model/Ollama calls during navigation, list, filter, search, or selection.

UI labeling rules:

- Each approved location must use `Approved Location` labeling (or `Approved Setting` only when the owner has explicitly used that label for the record).
- Candidate counts must use the candidate status labels from WORKSPACE-012.
- Promotion record counts must use `Promotion Record Only` and `Not Yet Applied` until the record actually created the location.
- Missing fields must use `Unknown`, `Not approved yet`, or `Not recorded`.
- Parent/child cycles must use `Cycle Detected`.
- Dramatica setting/world claims must not appear.

Suggested loading behavior:

- Show page shell while approved location list loads.
- Show partial sections where data is available.
- Show warnings for degraded or invalid sections.
- Use project recovery state for blocking project metadata failures.

## 12. Future Tests

Future implementation should include tests for:

- Page loads with no `memory/` directory.
- Page loads empty approved location state.
- Page loads approved locations from `memory/locations.json`.
- Page loads with corrupt `memory/locations.json` and shows warning.
- Page loads with duplicate `location_id` values and shows warning.
- Page rejects unsafe `project_id` and `location_id` values.
- Page rejects `location_id` traversal.
- Page rejects `location_id` that is not in the allowed set.
- Page loads with unsupported schema and shows warning.
- Page shows `Unknown`/`Not approved yet`/`Not recorded` for missing fields.
- Page does not show `Pending Candidate` rows.
- Page does not show `Rejected Candidate` rows.
- Page does not show `Archived Candidate` rows.
- Page does not show `Approved Candidate` rows from OMI.
- Page does not show `Promotion Record Only` rows as approved locations.
- Page shows `Promotion Record Only` link only as provenance.
- Page does not call Ollama or any model during load, list, filter, search, or selection.
- Page does not generate summaries, descriptions, atmosphere, mood, or worldbuilding prose.
- Page does not create OMI records.
- Page does not modify `memory/locations.json` or `memory/index.json`.
- Page does not apply promotions.
- Page does not write JSONL records.
- Page does not update `training/data/dataset_manifest.json`.
- Page does not display Dramatica setting/world claims.
- Page exposes only allowed first-version operations.
- Page has no AI prose-generation controls.
- Local search/filter does not call a model.
- Local search/filter is deterministic and bounded to safe fields.
- Linked source scene/note/material links open correctly.
- Broken linked source references show warnings.
- Broken linked character/object/timeline references show warnings.
- Parent/child cycles show `Cycle Detected` warnings.
- Parent/child cycle warnings are non-destructive.
- Empty state shows guidance and a link to OMI Ideas / Candidates.
- Empty state does not invent placeholder locations.
- Warning state shows non-destructive warnings only.
- Warning state does not auto-repair, auto-delete, or auto-promote.

## 13. Deferred Decisions

Deferred to future implementation tasks:

- Whether the place hierarchy view becomes a tree, a graph, or a flat list of children.
- Whether the first location list loads from `memory/locations.json` directly, from `memory/index.json` plus category files, or from a backend summary endpoint.
- Whether approved location records support per-record files in addition to category files.
- Whether `location_type` becomes a bounded allowed list before it appears in the UI.
- Whether `alternate_names` editor is owner-controlled only or also candidate-driven.
- Whether navigation summaries may mention approved locations in approved navigation contexts.
- Whether cross-record links include a future approved timeline page and what minimum fields it requires.
- Whether `memory/index.json` is required before the first locations page implementation or remains derived/lazy.
- Whether applied location records can ever carry a future Dramatica setting/world claim and under what approval/evidence conditions.
- Whether future apply-promotion is allowed to merge or split locations atomically.
- Whether archived/superseded locations are hidden by default, shown in a section, or shown with status.
- Browser design for large location lists.
- Whether the candidate backlog snapshot is hidden, collapsed, or always visible.
- Whether `revision_history` becomes a dedicated panel.
- Whether scene usage view becomes a timeline, a list, or a count.
- Whether parent/child cycle resolution becomes a separate future repair flow.

## 14. Implementation Non-Goals

WORKSPACE-014 does not implement:

- The Approved Locations / Settings page UI.
- Backend memory/canon routes for locations.
- Apply-promotion.
- Location extraction.
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

## 15. Acceptance Checklist

This planning spec is complete when it documents:

- Page purpose.
- Locations / Settings page concepts and required labels.
- First-version page layout.
- Approved location/setting display model.
- Page operations.
- Local search/filter planning.
- Warning and error states.
- Relationship to other pages.
- API planning.
- Frontend planning.
- Future tests.
- Deferred decisions.
- Implementation non-goals.

This spec does not implement runtime code, frontend UI, tests, packages, dataset files, JSONL records, training, model calls, project files, OMI records, memory/canon files, location extraction, apply-promotion, or Dramatica-specific logic.
