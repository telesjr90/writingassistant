# WORKSPACE-013: Approved Characters Page Spec

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
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Characters page should be the future project-local destination for owner-approved character memory/canon records. It must show only character records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, and approved-but-not-applied character candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

The Approved Characters page should:

- Show owner-approved character memory/canon records only when those records are present in the future `memory/characters.json` file.
- Treat approved character truth as project memory/canon only after owner approval, a recorded promotion record, and a successful future apply-promotion step.
- Clearly distinguish approved character truth from OMI character candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved character back to source evidence, provenance, source candidate IDs, source scene IDs, source promotion record IDs, and approval metadata.
- Show aliases/nicknames only when the approved character record explicitly carries them.
- Show unresolved or missing character fields honestly as `Unknown`, `Not approved yet`, or `Not recorded` instead of guessing.
- Show an empty state when no approved character records exist yet.
- Show a candidate backlog snapshot that links only counts and entry points to the OMI Ideas / Candidates page.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic candidate extraction.
- Avoid apply-promotion behavior.
- Avoid silent mutation of approved memory/canon or OMI records.
- Avoid Dramatica-specific character role claims (Protagonist, Antagonist, Sidekick, etc.) in this workspace phase.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Character Page Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for character candidates.
- Source material is not approved character memory/canon by default.
- A character mentioned in a scene is not an approved character record by itself.
- A character shown in a note is not an approved character record by itself.
- Source material must not be copied into approved character memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions a character is not an approved character record.

### OMI Character Candidates

Definition:

- Structured `character_candidate` records that have not been applied to approved memory/canon.

Rules:

- Character candidates are not canon.
- Character candidates must not appear in the approved character list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.

### Approved-but-Not-Applied Candidates

Definition:

- `character_candidate` records the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved character memory/canon.
- Approved-but-not-applied candidates must not appear in the approved character list.
- The page may show counts and entry points only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved character records.
- Promotion records may be linked as provenance from a character record that an apply-promotion step actually created.

### Applied Character Memory / Canon Records

Definition:

- Durable owner-approved `character_memory_record` entries written to the future `memory/characters.json` file by a future apply-promotion step.

Rules:

- Applied character records are the only records allowed in the approved character list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, and approval metadata.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/characters.json` entries.

### Future Dramatica Character Role Claims

Definition:

- Future Dramatica storyform-specific role claims such as Protagonist, Antagonist, Sidekick, Skeptic, or Reason role mappings.

Rules:

- Dramatica character role claims are deferred.
- The first version of this page must not display any Dramatica character role claim.
- Generic role labels such as `Protagonist` or `Antagonist` are not required and should not be inferred.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved character display.
- The first implementation of this page must not call a model.

### Insufficient Evidence

Definition:

- Character evidence/provenance is missing, weak, broken, unsafe, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting or rewriting the character record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any character that already exists.

## 3. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Character` | Marks each applied `character_memory_record`. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Approved Candidate` | Marks approved-but-not-applied character candidates on the OMI page; this page may show counts and links only. |
| `Pending Candidate` | Marks pending OMI character candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI character candidates on the OMI page. |
| `Archived Candidate` | Marks archived OMI character candidates on the OMI page. |
| `Needs Revision` | Marks needs-revision OMI character candidates on the OMI page. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied character record. |
| `Source / Evidence` | Marks source scene, source note, source material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved character fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Future / Not Implemented` | Marks areas such as relationships, timeline, or Dramatica character roles that are not part of the first implementation. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved character list.
- Counts must be separated by status.
- Approved character counts must come from applied `character_memory_record` entries only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Character`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved character list.

## 4. First-Version Page Layout

First-version sections:

- Page Header.
- Character Page Boundary Banner.
- Approved Character List.
- Character Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Relationships Snapshot Placeholder.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and the Approved Characters area.
- Show approved-only counts and link back to the project memory/canon index when available.

Data source:

- Active project metadata from `project.json`.
- Future `memory/index.json` and `memory/characters.json` only if those files already exist.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate character summaries, biographies, motivation prose, or story descriptions.

Candidate/canon boundary:

- Approved character counts must come from applied memory/canon records only.
- Candidate or promotion counts must be labeled separately and must not appear as approved counts.

Empty state:

- Show zero approved characters and a link to OMI Ideas / Candidates.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved character metadata shows a warning and avoids approved display.

### Character Page Boundary Banner

Purpose:

- State that the page is owner-approved character memory/canon only, not candidate review and not an AI writing surface.

Data source:

- Static product boundary copy.

No-prose boundary:

- Banner must include or link to the standard refusal policy.
- No write, rewrite, continue, polish, improve, imitate, expand, or generate controls.

Candidate/canon boundary:

- Banner must state that OMI character candidates, approved-but-not-applied candidates, and promotion records are not approved character memory/canon.
- Banner must state that Dramatica character role claims are not part of this page.

Empty state:

- Banner remains visible even when no approved characters exist.

Error state:

- Banner remains visible even when approved character data is partially corrupt.

### Approved Character List

Purpose:

- Show applied character memory/canon records for the selected project.
- Provide a deterministic ordering and a simple local filter/search over safe text fields.

Data source:

- Future `memory/characters.json` only.
- Future `memory/index.json` as derived convenience state only.

No-prose boundary:

- Display stored record fields only.
- Do not generate character descriptions, summaries, motivation prose, or backstory.
- Do not include "make character better," "rewrite character," "expand character," or "generate backstory" actions.

Candidate/canon boundary:

- Each row must use `Approved Character`.
- Approved counts must come from applied memory/canon records only.
- Pending/rejected/archived/approved-but-not-applied candidates must not be blended in.

Empty state:

- Show a guidance block that no approved characters exist yet and link to OMI Ideas / Candidates.

Error state:

- Corrupt character records, duplicate IDs, unsupported schema, or stale index entries show warnings and the affected character must not appear as a normal approved row.

### Character Detail Panel

Purpose:

- Show the selected approved character's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, linked sources, approval metadata, and provenance summary.

Data source:

- The selected applied `character_memory_record` from `memory/characters.json`.

No-prose boundary:

- Display stored fields only.
- No generated biography, no generated description, no generated summary, no generated motivation prose, no generated character arc, no generated dialogue, no style imitation.

Candidate/canon boundary:

- Use `Approved Character` labeling.
- The character must be an applied record, not a candidate.
- Promotion records are linked as provenance, not as the character itself.

Empty state:

- No selection should show "select an approved character" guidance.

Error state:

- Broken cross-record links, missing source references, or unsupported schema must show warnings and not invent replacements.

### Evidence / Provenance Panel

Purpose:

- Show evidence, source references, source kind, source scenes, source notes/materials, source candidate IDs, source promotion record IDs, hashes if stored, confidence at promotion time, and approval timestamps.

Data source:

- Approved character record `source_candidate_ids`, `promotion_record_ids`, `evidence_summaries`, `provenance`, `evidence_ids`, and `confidence_at_promotion`.

No-prose boundary:

- Evidence display must not generate explanatory prose beyond stored metadata and fixed UI labels.
- No generated "what this character represents" or "why this matters" prose.

Candidate/canon boundary:

- Evidence supports owner review and traceability.
- Evidence does not establish truth by itself outside the apply-promotion step that created the record.

Empty state:

- Missing evidence must show `Evidence Required` or `Insufficient Evidence` where applicable, never guessed.

Error state:

- Broken source references, unsafe paths, or unsupported source kinds must show warnings and not invent replacements.

### Linked Sources Panel

Purpose:

- Show linked scenes, chapters, notes, materials, and other approved memory records that the character is connected to.
- Show linked approved location, object, organization, timeline, relationship, plot thread, and continuity warning records when those records are available.

Data source:

- Approved character `first_seen_scene_id`, `mentioned_in_scene_ids`, `related_location_ids`, `related_object_ids`, `related_plot_thread_ids`, and any other cross-record references that exist in future schema.

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

### Relationships Snapshot Placeholder

Purpose:

- Reserve space for the future approved relationships page or relationship graph page.

Data source:

- None in the first implementation.

No-prose boundary:

- No generated relationship narrative.

Candidate/canon boundary:

- Future relationship memory records are not Dramatica Relationship Story proof.
- Placeholder should say "future approved relationships page" only.

Empty state:

- Show the placeholder.

Error state:

- Not applicable beyond normal page rendering failure.

### Candidate Backlog Snapshot

Purpose:

- Show owner-visible counts and links for OMI character candidates.
- Help the owner see whether character review is needed in OMI.

Data source:

- `omi/index.json` candidate counts and lightweight candidate metadata when valid.

No-prose boundary:

- Counts and labels only.
- No generated candidate summaries or story hints.

Candidate/canon boundary:

- Counts must be clearly labeled `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, or `Promotion Record Only` and must not appear in approved character counts.
- The page may link only to the OMI Ideas / Candidates page for review.

Empty state:

- Show no candidates and link to OMI Ideas / Candidates.

Error state:

- Corrupt OMI metadata should show a warning and avoid using its counts as truth.

### Empty State

Purpose:

- Explain what the page shows when no approved characters exist yet.

Data source:

- Static product boundary copy plus project metadata.

No-prose boundary:

- Guidance is operational, not generated story text.

Candidate/canon boundary:

- Link to OMI Ideas / Candidates for candidate review.
- State that approved characters appear only after future apply-promotion.

Empty state:

- Missing `memory/characters.json`, empty `records` array, or absent `memory/` folder are valid empty states.

Error state:

- If project metadata is invalid, show recovery/help instead of empty-state guidance.

### Warning State

Purpose:

- Surface non-destructive health warnings about the approved character store.

Data source:

- Project validation.
- Memory index/category validation.
- Cross-record reference checks where safe.

No-prose boundary:

- Warnings are factual status messages only.
- No generated repair text that rewrites character truth.

Candidate/canon boundary:

- Warnings must not promote, repair, delete, merge, or rewrite character records.

Empty state:

- Show no warnings when clean.

Error state:

- Blocking warnings prevent approved display for the affected character.
- Non-blocking warnings allow partial display where safe.

### Future Page Link Reference

Purpose:

- Reserve space for navigation to future approved pages.

Data source:

- Static route references.

No-prose boundary:

- Link text only.

Candidate/canon boundary:

- Future approved page links (locations/settings, timeline, plot threads, continuity/consistency, approved memory/canon index) must be labeled as future or as currently available depending on implementation status.

Empty state:

- Show a guidance block for future pages.

Error state:

- Disable links whose target pages are not yet implemented.

## 5. Approved Character Display Model

Approved character records must be displayed only from applied `character_memory_record` entries. The first version of this page may display the following fields when they exist in the stored record.

| Field | Source | Display rule |
| --- | --- | --- |
| `character_id` | Applied record | Stable ID shown in small text. |
| `display_name` | `canonical_name` | Primary label. |
| `aliases` | Applied record | Show only when present; do not infer or guess. |
| `role_label` | Optional future field | Show only when explicitly present; do not infer Dramatica role claims. |
| `status` | Applied record | Show `active`, `needs_review`, `superseded`, `archived`, or `deleted_by_owner` if present. |
| `short_owner_approved_description` | `description_notes` or `notes` | Show only if the owner has approved the description; otherwise show `Not approved yet` or `Not recorded`. Never display AI-generated biography. |
| `traits` | Applied record | Show approved owner-authored trait labels only. |
| `goals` | Applied record | Show approved owner-authored goal labels only. |
| `conflicts` | Applied record | Show approved owner-authored conflict labels only. |
| `relationships_count` | Derived from `related_*` fields or future `memory/relationships.json` | Show as a number plus a `Future Approved Relationships` placeholder when relationships are not yet approved. |
| `linked_location_ids` | Applied record | Show as approved location IDs and labels when available. |
| `linked_object_ids` | Applied record | Show as approved object IDs and labels when available. |
| `linked_scene_ids` | `first_seen_scene_id`, `mentioned_in_scene_ids` | Show scene IDs and titles. |
| `first_seen_source` | `first_seen_scene_id` plus metadata | Show source scene title and ID. |
| `evidence_summaries` | Applied record | Show stored summaries. |
| `confidence_at_promotion` | Applied record | Show as a stored label or number, not as canon certainty. |
| `created_at` | Applied record | Show ISO-8601 timestamp. |
| `updated_at` | Applied record | Show ISO-8601 timestamp. |
| `approved_at` | Applied record | Show ISO-8601 approval timestamp. |
| `approved_by` | Applied record | Show owner or reviewer identifier. |
| `source_candidate_ids` | Applied record | Show source OMI candidate IDs and link to the OMI page for each. |
| `promotion_record_ids` | Applied record | Show source promotion record IDs and link to the OMI page for each as `Promotion Record Only` until apply-promotion actually created the character. |
| `revision_history` | Applied record | Show when present. |
| `supersedes_record_ids` | Applied record | Show when present. |
| `superseded_by_record_id` | Applied record | Show when present. |
| `notes` | Applied record | Show owner notes only. |

Display rules:

- All displayed character truth must come from applied memory/canon records.
- Unapproved candidates must not appear as truth.
- Generated biographical prose is prohibited.
- Owner-approved summaries may be displayed only if explicitly approved or owner-authored.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded` and must not be guessed.
- `evidence_summaries` must not be paraphrased into prose.
- `confidence_at_promotion` must be displayed as a stored value, never as a current truth certainty.
- `aliases` and `nicknames` must come from the approved record only.
- Dramatica role claims must not be displayed.

## 6. Page Operations

First-version allowed operations:

- View the approved character list.
- Select a character to view its detail panel.
- Filter and search the approved character list locally.
- Open linked source scene/note/material from the linked sources panel.
- Open the source OMI candidate or promotion record from the provenance links.
- Open the OMI Ideas / Candidates page from the candidate backlog snapshot.
- Open the future approved relationships placeholder.

First-version operations must:

- Be read-only with respect to approved memory/canon.
- Be read-only with respect to OMI records.
- Avoid model/Ollama calls during navigation, list, filter, search, or selection.
- Avoid generated summaries, generated descriptions, or generated character biographies.
- Avoid any silent mutation of `memory/characters.json`, `memory/index.json`, or OMI records.
- Avoid any direct apply-promotion action from this page.

Future-only operations (out of scope for WORKSPACE-013 first implementation):

- Editing approved character memory/canon directly.
- Merging approved characters.
- Splitting approved character records.
- Archiving approved characters.
- Restoring superseded approved characters.
- Creating new approved characters from this page.
- Apply-promotion from this page.
- Extracting character candidates from owner-authored text on this page.
- Graph/relationship visualization.
- Dramatica character role assignment.

Future operations must be defined in separate future specs and require separate tests.

## 7. Local Search and Filter

First-version search and filter must be local and deterministic.

Allowed search/filter dimensions:

- `display_name` / `canonical_name`.
- `aliases` if present.
- `status` if present.
- `role_label` if present.
- `tags` if present.
- `approved description` if the owner has approved a description.
- `linked source IDs` (`first_seen_scene_id`, `mentioned_in_scene_ids`, `related_*` IDs).
- `source_candidate_ids`.
- `promotion_record_ids`.

First-version search/filter must:

- Run locally over already-loaded data.
- Avoid semantic search.
- Avoid model/Ollama calls.
- Avoid generated summaries, descriptions, or expansions.
- Avoid any candidate extraction during search.
- Avoid any apply-promotion or OMI mutation during search.
- Label results with their status: `Approved Character`, `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, `Promotion Record Only`, or `Not Yet Applied`.

Search rules:

- No global fuzzy expansion.
- No global synonyms.
- No language model ranking.
- No AI ranking explanations.
- No hidden generated character summaries in result rows.

## 8. Warning and Error States

The page must surface non-destructive warnings and errors. Warnings are not allowed to auto-repair, auto-delete, silently rewrite, or silently promote records.

Required warnings and errors:

- Missing `memory/` directory.
- Missing `memory/characters.json`.
- Missing `memory/index.json` if a future implementation depends on it.
- Corrupt `memory/characters.json`.
- Corrupt `memory/index.json` if present.
- Unsupported `memory/characters.json` schema.
- Duplicate `character_id` values within `memory/characters.json`.
- `character_id` that does not match a safe single path component.
- `character_id` references that fail path safety.
- Approved character references missing source candidate.
- Approved character references missing promotion record.
- Broken linked scene references.
- Broken linked note/material references.
- Broken cross-record references to other approved memory records.
- OMI character candidates exist but no approved characters yet.
- Promotion records present but no applied character record.
- Relationship links exist but the relationship page/model is not implemented yet.
- Evidence/provenance missing where required.
- Insufficient evidence labels carried over from apply-promotion.

Warning rules:

- Warnings are non-destructive.
- No auto-repair.
- No auto-delete.
- No identity rewrite.
- No silent candidate promotion.
- No silent deletion of corrupt records.
- No host filesystem path leakage in UI/API errors.
- Blocking warnings should prevent approved display for the affected character.
- Non-blocking warnings may allow partial display where safe.

Recommended severity levels:

- `blocking`: approved display is unsafe for the affected character.
- `warning`: page can load with degraded or partial data.
- `info`: empty state, future feature, or candidate-only note.

## 9. Relationship to Other Pages

Project Memory / Canon index page (WORKSPACE-011):

- Provides the parent navigation entry and category cards.
- The Characters card must show approved-only counts and link to this page.
- Candidate counts must remain on the OMI page.

Project Overview (WORKSPACE-008):

- May show approved character count only.
- May show candidate count labeled as candidate/audit.
- May link to this page and to the OMI page.

OMI Ideas / Candidates (WORKSPACE-012):

- Owns candidate review, owner decision, destination, evidence/provenance, and promotion record creation for character candidates.
- This page must not duplicate OMI review actions.

Chapters / Scenes (WORKSPACE-009) and Notes / Materials (WORKSPACE-010):

- May show character references in scene or note metadata.
- This page is the project-local approved destination for those references.

Future approved pages (locations/settings, timeline, plot threads, relationships, continuity/consistency, approved memory/canon index):

- Should follow the same approved-only display rules.
- Cross-record links should be consistent with this page's display rules.

## 10. API Planning

These routes are future planning only. Do not implement them in WORKSPACE-013.

Every route must validate `project_id` as a safe single path component and preserve project-local state. Character routes must reject traversal, absolute paths, unsafe IDs, unsupported schema versions, duplicate IDs, and invalid record shapes.

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/characters.json` or `memory/index.json` on read.
- First-version routes must not apply promotions.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/characters`

Version:

- First-version planning.

Purpose:

- Return the approved character list for the selected project.

Page dependency:

- Page Header.
- Approved Character List.
- Empty State.
- Warning State.

Validation:

- Safe `project_id`.
- Existing project.
- `memory/characters.json` envelope shape when present.

No-prose boundary:

- Return stored character records only.
- No generated descriptions, summaries, biographies, or traits.

Candidate/canon boundary:

- Return applied character memory/canon records only.
- Candidate records must come from OMI routes, not memory category routes.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project, treated as empty where appropriate.
- 422 corrupt `memory/characters.json`, unsupported schema, duplicate IDs, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/characters/{character_id}`

Version:

- First-version planning.

Purpose:

- Return a single approved character record.

Page dependency:

- Character Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.

Validation:

- Safe `project_id` and `character_id`.
- `character_id` is one of the IDs in `memory/characters.json`.
- `character_id` is a safe single path component.

No-prose boundary:

- Return stored character fields only.
- Do not generate biography, description, summary, motivation, or style imitation.

Candidate/canon boundary:

- Return applied character records only.

Expected errors:

- 400 invalid ID.
- 404 missing project or character.
- 422 corrupt or unsupported record.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/characters/{character_id}/provenance`

Version:

- First-version planning.

Purpose:

- Return provenance metadata for a single approved character.

Page dependency:

- Evidence / Provenance Panel.

Validation:

- Safe `project_id` and `character_id`.

No-prose boundary:

- Return stored provenance only.
- No generated explanations.

Candidate/canon boundary:

- Provenance is audit metadata, not a character description.

Expected errors:

- 400 invalid ID.
- 404 missing project or character.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/characters/health`

Version:

- First-version planning.

Purpose:

- Return non-destructive health warnings for the approved character store.

Page dependency:

- Warning State.

Validation:

- Safe `project_id`.
- Read-only scans only.

No-prose boundary:

- Warnings are factual status only.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, or rewrite character records.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project.
- 500 sanitized partial scan failure.

### `GET /api/projects/{project_id}/memory/summary` (composed)

Version:

- Optional first-version route.

Purpose:

- Provide approved character counts alongside other approved category counts.

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

- This is the only future route group that may create applied character memory/canon from a promotion record.

Expected errors:

- Deferred.

## 11. Frontend Planning

Do not implement UI in WORKSPACE-013.

Future components:

- `ApprovedCharactersPage`
- `ApprovedCharactersBoundaryBanner`
- `ApprovedCharacterList`
- `ApprovedCharacterListItem`
- `ApprovedCharacterDetailPanel`
- `CharacterEvidencePanel`
- `CharacterSourceLinksPanel`
- `CharacterRelationshipsSnapshot`
- `CharacterCandidateBacklogSnapshot`
- `CharacterSearchFilterControls`
- `CharacterWarningsPanel`
- `CharacterEmptyState`
- `CharacterFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No "rewrite character" button.
- No "make character better" button.
- No "expand character" button.
- No "generate backstory" button.
- No "generate character description" button.
- No "improve character" button.
- No "polish character" button.
- No style imitation controls.
- No generated summaries.
- No apply-promotion button.
- No archive/merge/split controls.
- No direct edit of approved character records from this page.
- No mutation of `memory/characters.json` or `memory/index.json` on the client.
- No mutation of OMI records.
- No JSONL/training writes.
- No model/Ollama calls during navigation, list, filter, search, or selection.

UI labeling rules:

- Each approved character must use `Approved Character` labeling.
- Candidate counts must use the candidate status labels from WORKSPACE-012.
- Promotion record counts must use `Promotion Record Only` and `Not Yet Applied` until the record actually created the character.
- Missing fields must use `Unknown`, `Not approved yet`, or `Not recorded`.
- Dramatica role claims must not appear.

Suggested loading behavior:

- Show page shell while approved character list loads.
- Show partial sections where data is available.
- Show warnings for degraded or invalid sections.
- Use project recovery state for blocking project metadata failures.

## 12. Future Tests

Future implementation should include tests for:

- Page loads with no `memory/` directory.
- Page loads empty approved character state.
- Page loads approved characters from `memory/characters.json`.
- Page loads with corrupt `memory/characters.json` and shows warning.
- Page loads with duplicate `character_id` values and shows warning.
- Page rejects unsafe `project_id` and `character_id` values.
- Page rejects `character_id` traversal.
- Page rejects `character_id` that is not in the allowed set.
- Page loads with unsupported schema and shows warning.
- Page shows `Unknown`/`Not approved yet`/`Not recorded` for missing fields.
- Page does not show `Pending Candidate` rows.
- Page does not show `Rejected Candidate` rows.
- Page does not show `Archived Candidate` rows.
- Page does not show `Approved Candidate` rows from OMI.
- Page does not show `Promotion Record Only` rows as approved characters.
- Page shows `Promotion Record Only` link only as provenance.
- Page does not call Ollama or any model during load, list, filter, search, or selection.
- Page does not generate summaries, descriptions, or biographies.
- Page does not create OMI records.
- Page does not modify `memory/characters.json` or `memory/index.json`.
- Page does not apply promotions.
- Page does not write JSONL records.
- Page does not update `training/data/dataset_manifest.json`.
- Page does not display Dramatica character role claims.
- Page exposes only allowed first-version operations.
- Page has no AI prose-generation controls.
- Local search/filter does not call a model.
- Local search/filter is deterministic and bounded to safe fields.
- Linked source scene/note/material links open correctly.
- Broken linked source references show warnings.
- Empty state shows guidance and a link to OMI Ideas / Candidates.
- Empty state does not invent placeholder characters.
- Warning state shows non-destructive warnings only.
- Warning state does not auto-repair, auto-delete, or auto-promote.

## 13. Deferred Decisions

Deferred to future implementation tasks:

- Whether relationships are first-class on the characters page, on a separate approved relationships page, or both.
- Whether the first character list loads from `memory/characters.json` directly, from `memory/index.json` plus category files, or from a backend summary endpoint.
- Whether approved character records support per-record files in addition to category files.
- Whether `role_label` becomes a bounded allowed list before it appears in the UI.
- Whether `aliases` editor is owner-controlled only or also candidate-driven.
- Whether navigation summaries may mention approved characters in approved navigation contexts.
- Whether cross-record links include a future approved relationships page and what minimum fields it requires.
- Whether `memory/index.json` is required before the first character page implementation or remains derived/lazy.
- Whether applied character records can ever carry a future Dramatica character role claim and under what approval/evidence conditions.
- Whether future apply-promotion is allowed to merge or split characters atomically.
- Whether archived/superseded characters are hidden by default, shown in a section, or shown with status.
- Browser design for large character lists.
- Whether the candidate backlog snapshot is hidden, collapsed, or always visible.
- Whether `revision_history` becomes a dedicated panel.

## 14. Implementation Non-Goals

WORKSPACE-013 does not implement:

- The Approved Characters page UI.
- Backend memory/canon routes for characters.
- Apply-promotion.
- Character extraction.
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
- Character page concepts and required labels.
- First-version page layout.
- Approved character display model.
- Page operations.
- Local search/filter planning.
- Warning and error states.
- Relationship to other pages.
- API planning.
- Frontend planning.
- Future tests.
- Deferred decisions.
- Implementation non-goals.

This spec does not implement runtime code, frontend UI, tests, packages, dataset files, JSONL records, training, model calls, project files, OMI records, memory/canon files, character extraction, apply-promotion, or Dramatica-specific logic.
