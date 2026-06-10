# WORKSPACE-016: Approved Plot Threads Page Spec

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
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- WORKSPACE-019: `docs/roadmap/approved_relationships_page_spec.md`
- WORKSPACE-020: `docs/roadmap/approved_organizations_groups_page_spec.md`
- WORKSPACE-021: `docs/roadmap/approved_objects_items_page_spec.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Plot Threads page should be the future project-local destination for owner-approved plot-thread memory/canon records. It must show only plot-thread records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, and approved-but-not-applied plot-thread candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

The Approved Plot Threads page should:

- Show owner-approved plot-thread memory/canon records only when those records are present in the future `memory/plot_threads.json` file.
- Treat approved plot-thread truth as project memory/canon only after owner approval, a recorded promotion record, and a successful future apply-promotion step.
- Clearly distinguish approved plot-thread truth from OMI plot-thread candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved plot thread back to source evidence, provenance, source candidate IDs, source scene IDs, source promotion record IDs, and approval metadata.
- Show unresolved or missing plot-thread fields honestly as `Unknown`, `Not approved yet`, or `Not recorded` instead of guessing.
- Show thread status, resolution, and related open questions only when the approved record explicitly carries them.
- Show an empty state when no approved plot-thread records exist yet.
- Show a candidate backlog snapshot that links only counts and entry points to the OMI Ideas / Candidates page.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic candidate extraction.
- Avoid apply-promotion behavior.
- Avoid silent mutation of approved memory/canon or OMI records.
- Avoid Dramatica-specific plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claims in this workspace phase.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Plot Threads Page Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for plot-thread candidates.
- Source material is not approved plot-thread memory/canon by default.
- A thread mentioned in a scene is not an approved plot-thread record by itself.
- A plot summary in a note is not an approved plot-thread record by itself.
- Source material must not be copied into approved plot-thread memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions a plot thread is not an approved plot-thread record.

### OMI Plot-Thread Candidates

Definition:

- Structured `plot_thread_candidate` records that have not been applied to approved memory/canon.

Rules:

- Plot-thread candidates are not canon.
- Plot-thread candidates must not appear in the approved plot-thread list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.

### Approved-but-Not-Applied Candidates

Definition:

- `plot_thread_candidate` records the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved plot-thread memory/canon.
- Approved-but-not-applied candidates must not appear in the approved plot-thread list.
- The page may show counts and entry points only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved plot threads.
- Promotion records may be linked as provenance from a plot-thread record that an apply-promotion step actually created.

### Applied Plot-Thread Memory / Canon Records

Definition:

- Durable owner-approved `plot_thread_memory_record` entries written to the future `memory/plot_threads.json` file by a future apply-promotion step.

Rules:

- Applied plot-thread records are the only records allowed in the approved plot-thread list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, and approval metadata.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/plot_threads.json` entries.

### Thread Status and Resolution

Definition:

- Future `status`, `start_event_id`, `current_event_id`, and `resolved_event_id` references on approved plot-thread records.

Rules:

- Thread status must come from approved memory/canon records only.
- Thread status must not be inferred from scene text or notes at page load.
- Thread status conflicts (for example, `resolved` with no `resolved_event_id`) must surface as non-destructive warnings.
- Thread status must not be silently corrected, retitled, or rewritten.
- Missing status or resolution must be shown as `Unknown` or `Not Recorded`, not inferred.

### Related Open Questions

Definition:

- Future `related_open_question_ids` references between approved plot-thread records and approved open-question memory records.

Rules:

- Related open-question links must come from approved memory/canon records only.
- The first version of this page must not render an open-questions view; it must show a placeholder.
- Missing open-question links must be shown as `Unknown` or `Not Recorded`, not inferred.

### Related Continuity Warnings

Definition:

- Future `related_continuity_warning_ids` references between approved plot-thread records and approved continuity-warning memory records.

Rules:

- Related continuity-warning links must come from approved memory/canon records only.
- The first version of this page must not render a continuity view; it must show a placeholder.
- Missing continuity-warning links must be shown as `Unknown` or `Not Recorded`, not inferred.

### Future Dramatica Plot, Signpost, Driver, or Thematic Claims

Definition:

- Future Dramatica storyform-specific plot classification, signpost progression, driver/quad classification, Concern/Issue/Problem/Solution mapping, or thematic interpretation claims.

Rules:

- Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claims are deferred.
- The first version of this page must not display any Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claim.
- Generic labels such as `Main Plot`, `Subplot`, `B-story`, or `Theme` are not required and should not be inferred.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved plot-thread display.
- The first implementation of this page must not call a model.

### Insufficient Evidence

Definition:

- Plot-thread evidence/provenance is missing, weak, broken, unsafe, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting or rewriting the plot-thread record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any thread that already exists.

## 3. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Plot Thread` | Marks each applied `plot_thread_memory_record`. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Approved Candidate` | Marks approved-but-not-applied plot-thread candidates on the OMI page; this page may show counts and links only. |
| `Pending Candidate` | Marks pending OMI plot-thread candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI plot-thread candidates on the OMI page. |
| `Archived Candidate` | Marks archived OMI plot-thread candidates on the OMI page. |
| `Needs Revision` | Marks needs-revision OMI plot-thread candidates on the OMI page. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied plot-thread record. |
| `Source / Evidence` | Marks source scene, source note, source material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved thread fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Thread Status Conflict` | Marks records where the stored status is inconsistent with the stored resolution fields. |
| `Open Questions Placeholder` | Marks that the related open-questions view is not yet implemented. |
| `Continuity Warnings Placeholder` | Marks that the related continuity-warnings view is not yet implemented. |
| `Future / Not Implemented` | Marks areas such as plot-thread graph, plot-thread timeline, or Dramatica plot/thread classification that are not part of the first implementation. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved plot-thread list.
- Counts must be separated by status.
- Approved plot-thread counts must come from applied `plot_thread_memory_record` entries only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Plot Thread`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved plot-thread list.
- Thread status conflict warnings must use `Thread Status Conflict` and must not auto-repair, silently retitle, or silently correct the stored status.
- Open-questions and continuity-warnings placeholders must use their named labels and must not invent missing links.

## 4. First-Version Page Layout

First-version sections:

- Page Header.
- Plot Threads Page Boundary Banner.
- Approved Plot Thread List.
- Plot Thread Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Linked Timeline / Scene Snapshot.
- Related Characters / Locations / Objects Snapshot.
- Related Open Questions Placeholder.
- Related Continuity Warnings Placeholder.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and the Approved Plot Threads area.
- Show approved-only counts and link back to the project memory/canon index when available.

Data source:

- Active project metadata from `project.json`.
- Future `memory/index.json` and `memory/plot_threads.json` only if those files already exist.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate plot summaries, thread explanations, causal explanations, or thematic prose.

Candidate/canon boundary:

- Approved plot-thread counts must come from applied memory/canon records only.
- Candidate or promotion counts must be labeled separately and must not appear as approved counts.

Empty state:

- Show zero approved threads and a link to OMI Ideas / Candidates.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved plot-thread metadata shows a warning and avoids approved display.

### Plot Threads Page Boundary Banner

Purpose:

- State that the page is owner-approved plot-thread memory/canon only, not candidate review and not an AI writing surface.

Data source:

- Static product boundary copy.

No-prose boundary:

- Banner must include or link to the standard refusal policy.
- No write, rewrite, continue, polish, improve, imitate, expand, or generate controls.

Candidate/canon boundary:

- Banner must state that OMI plot-thread candidates, approved-but-not-applied candidates, and promotion records are not approved plot-thread memory/canon.
- Banner must state that Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claims are not part of this page.

Empty state:

- Banner remains visible even when no approved threads exist.

Error state:

- Banner remains visible even when approved plot-thread data is partially corrupt.

### Approved Plot Thread List

Purpose:

- Show applied plot-thread memory/canon records for the selected project.
- Provide a deterministic ordering and a simple local filter/search over safe text fields.

Data source:

- Future `memory/plot_threads.json` only.
- Future `memory/index.json` as derived convenience state only.

No-prose boundary:

- Display stored record fields only.
- Do not generate plot summaries, thread explanations, causal explanations, or thematic prose.
- Do not include "explain plot," "fix plot," "resolve thread," "write missing scene," "continue thread," or "generate twist" actions.

Candidate/canon boundary:

- Each row must use `Approved Plot Thread`.
- Approved counts must come from applied memory/canon records only.
- Pending/rejected/archived/approved-but-not-applied candidates must not be blended in.

Empty state:

- Show a guidance block that no approved threads exist yet and link to OMI Ideas / Candidates.

Error state:

- Corrupt thread records, duplicate IDs, thread status conflicts, unsupported schema, or stale index entries show warnings and the affected thread must not appear as a normal approved row.

### Plot Thread Detail Panel

Purpose:

- Show the selected approved thread's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, linked sources, thread status, resolution references, related open-question links, related continuity-warning links, approval metadata, and provenance summary.

Data source:

- The selected applied `plot_thread_memory_record` from `memory/plot_threads.json`.

No-prose boundary:

- Display stored fields only.
- No generated plot summary, no generated thread explanation, no generated causal or thematic prose, no style imitation.

Candidate/canon boundary:

- Use `Approved Plot Thread` labeling.
- The thread must be an applied record, not a candidate.
- Promotion records are linked as provenance, not as the thread itself.

Empty state:

- No selection should show "select an approved plot thread" guidance.

Error state:

- Broken cross-record links, missing source references, or unsupported schema must show warnings and not invent replacements.

### Evidence / Provenance Panel

Purpose:

- Show evidence, source references, source kind, source scenes, source notes/materials, source candidate IDs, source promotion record IDs, hashes if stored, confidence at promotion time, and approval timestamps.

Data source:

- Approved thread record `source_candidate_ids`, `promotion_record_ids`, `evidence_summaries`, `provenance`, `evidence_ids`, and `confidence_at_promotion`.

No-prose boundary:

- Evidence display must not generate explanatory prose beyond stored metadata and fixed UI labels.
- No generated "what this thread represents" or "why this thread matters" prose.

Candidate/canon boundary:

- Evidence supports owner review and traceability.
- Evidence does not establish truth by itself outside the apply-promotion step that created the record.

Empty state:

- Missing evidence must show `Evidence Required` or `Insufficient Evidence` where applicable, never guessed.

Error state:

- Broken source references, unsafe paths, or unsupported source kinds must show warnings and not invent replacements.

### Linked Sources Panel

Purpose:

- Show linked scenes, chapters, notes, materials, and other approved memory records that the thread is connected to.
- Show linked approved character, location, object, organization, timeline event, and plot thread records when those records are available.

Data source:

- Approved thread `introduced_scene_id`, `related_scene_ids`, `linked_chapter_ids`, `linked_timeline_event_ids`, `linked_character_ids`, `linked_location_ids`, `linked_object_ids`, and any other cross-record references that exist in future schema.

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

### Linked Timeline / Scene Snapshot

Purpose:

- Show approved thread scene and chapter usage counts and links based on `introduced_scene_id`, `related_scene_ids`, and `linked_chapter_ids`.
- Show approved thread timeline event links based on `linked_timeline_event_ids` and `start_event_id` / `current_event_id` / `resolved_event_id` when available.
- Provide a simple deterministic count without generating scene summaries.

Data source:

- Approved thread scene, chapter, and timeline event references only.

No-prose boundary:

- Counts and links only.
- No generated scene summaries, "what happens here" prose, or "thread progression" prose.

Candidate/canon boundary:

- Scene, chapter, and timeline event usage must come from approved memory/canon records only.
- Broken scene, chapter, or timeline event references must show warnings and must not be silently dropped.

Empty state:

- Show "no approved scene or timeline usage" or equivalent.

Error state:

- Broken scene, chapter, or timeline event references must show warnings and must not be invented.

### Related Characters / Locations / Objects Snapshot

Purpose:

- Show approved thread counts and labels for linked characters, locations, and objects.
- Provide a simple deterministic count and link set without generating summaries.

Data source:

- Approved thread `linked_character_ids`, `linked_location_ids`, and `linked_object_ids` only.

No-prose boundary:

- Counts, IDs, and labels only.
- No generated character or location summaries, no generated "why this thread involves this character" prose.

Candidate/canon boundary:

- Only applied memory/canon records may appear as linked entities here.
- Candidate references must route through the OMI page, not through this page.

Empty state:

- Show "no related approved characters, locations, or objects" or equivalent.

Error state:

- Broken cross-record references should show warnings and not be silently dropped.

### Related Open Questions Placeholder

Purpose:

- Reserve space for the future approved open-questions page or open-questions panel.

Data source:

- Approved thread `related_open_question_ids` only if those fields exist in the applied record.

No-prose boundary:

- No generated open-question narrative.
- No generated "this thread raises the question" prose.

Candidate/canon boundary:

- The first version must not infer open-question links from scene text, notes, or OMI candidates.
- Missing open-question links must be shown as `Unknown` or `Not Recorded`, not inferred.

Empty state:

- Show the placeholder.

Error state:

- Missing open-question links should show warnings and not auto-repair.

### Related Continuity Warnings Placeholder

Purpose:

- Reserve space for the future approved continuity/consistency page or continuity-warnings panel.

Data source:

- Approved thread `related_continuity_warning_ids` only if those fields exist in the applied record.

No-prose boundary:

- No generated continuity-warning narrative.
- No generated "this thread conflicts with" prose.

Candidate/canon boundary:

- The first version must not infer continuity-warning links from scene text, notes, or OMI candidates.
- Missing continuity-warning links must be shown as `Unknown` or `Not Recorded`, not inferred.

Empty state:

- Show the placeholder.

Error state:

- Missing continuity-warning links should show warnings and not auto-repair.

### Candidate Backlog Snapshot

Purpose:

- Show owner-visible counts and links for OMI plot-thread candidates.
- Help the owner see whether plot-thread review is needed in OMI.

Data source:

- `omi/index.json` candidate counts and lightweight candidate metadata when valid.

No-prose boundary:

- Counts and labels only.
- No generated candidate summaries or plot hints.

Candidate/canon boundary:

- Counts must be clearly labeled `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, or `Promotion Record Only` and must not appear in approved plot-thread counts.
- The page may link only to the OMI Ideas / Candidates page for review.

Empty state:

- Show no candidates and link to OMI Ideas / Candidates.

Error state:

- Corrupt OMI metadata should show a warning and avoid using its counts as truth.

### Empty State

Purpose:

- Explain what the page shows when no approved threads exist yet.

Data source:

- Static product boundary copy plus project metadata.

No-prose boundary:

- Guidance is operational, not generated story text.

Candidate/canon boundary:

- Link to OMI Ideas / Candidates for candidate review.
- State that approved threads appear only after future apply-promotion.

Empty state:

- Missing `memory/plot_threads.json`, empty `records` array, or absent `memory/` folder are valid empty states.

Error state:

- If project metadata is invalid, show recovery/help instead of empty-state guidance.

### Warning State

Purpose:

- Surface non-destructive health warnings about the approved plot-thread store.

Data source:

- Project validation.
- Memory index/category validation.
- Cross-record reference checks where safe.
- Thread status conflict detection where safe.

No-prose boundary:

- Warnings are factual status messages only.
- No generated repair text that rewrites thread truth.

Candidate/canon boundary:

- Warnings must not promote, repair, delete, merge, rewrite, retitle, or silently correct thread records.

Empty state:

- Show no warnings when clean.

Error state:

- Blocking warnings prevent approved display for the affected thread.
- Non-blocking warnings allow partial display where safe.

### Future Page Link Reference

Purpose:

- Reserve space for navigation to future approved pages.

Data source:

- Static route references.

No-prose boundary:

- Link text only.

Candidate/canon boundary:

- Future approved page links (characters, locations/settings, timeline, continuity/consistency, approved memory/canon index) must be labeled as future or as currently available depending on implementation status.

Empty state:

- Show a guidance block for future pages.

Error state:

- Disable links whose target pages are not yet implemented.

## 5. Approved Plot-Thread Display Model

Approved plot-thread records must be displayed only from applied `plot_thread_memory_record` entries. The first version of this page may display the following fields when they exist in the stored record.

| Field | Source | Display rule |
| --- | --- | --- |
| `plot_thread_id` | Applied record | Stable ID shown in small text. |
| `display_title` | `thread_label` or `canonical_name` | Primary label. |
| `thread_type` | Applied record | Show only if explicitly present; do not infer Dramatica plot, signpost, driver, or thematic type. |
| `status` | Applied record | Show only the stored status; never rewrite. Conflicts must surface `Thread Status Conflict` warnings. |
| `short_owner_approved_description` | `thread_summary` or `notes` | Show only if the owner has approved the description; otherwise show `Not approved yet` or `Not recorded`. Never display AI-generated plot summary, thread explanation, causal or thematic prose. |
| `linked_scene_ids` | `introduced_scene_id`, `related_scene_ids` | Show scene IDs and titles. |
| `linked_chapter_ids` | Applied record | Show chapter IDs and titles. |
| `linked_timeline_event_ids` | Applied record | Show approved timeline event IDs and labels when available. |
| `linked_character_ids` | Applied record | Show approved character IDs and labels when available. |
| `linked_location_ids` | Applied record | Show approved location IDs and labels when available. |
| `linked_object_ids` | Applied record | Show approved object IDs and labels when available. |
| `start_event_id` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `current_event_id` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `resolved_event_id` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `related_open_question_ids` | Applied record | Show only when the applied record explicitly carries them. |
| `related_continuity_warning_ids` | Applied record | Show only when the applied record explicitly carries them. |
| `first_seen_source` | `introduced_scene_id` plus metadata | Show source scene title and ID. |
| `evidence_summaries` | Applied record | Show stored summaries. |
| `confidence_at_promotion` | Applied record | Show as a stored label or number, not as canon certainty. |
| `created_at` | Applied record | Show ISO-8601 timestamp. |
| `updated_at` | Applied record | Show ISO-8601 timestamp. |
| `approved_at` | Applied record | Show ISO-8601 approval timestamp. |
| `approved_by` | Applied record | Show owner or reviewer identifier. |
| `source_candidate_ids` | Applied record | Show source OMI candidate IDs and link to the OMI page for each. |
| `promotion_record_ids` | Applied record | Show source promotion record IDs and link to the OMI page for each as `Promotion Record Only` until apply-promotion actually created the thread. |
| `revision_history` | Applied record | Show when present. |
| `supersedes_record_ids` | Applied record | Show when present. |
| `superseded_by_record_id` | Applied record | Show when present. |
| `notes` | Applied record | Show owner notes only. |

Display rules:

- All displayed plot-thread truth must come from applied memory/canon records.
- Unapproved candidates must not appear as truth.
- Generated plot summaries are prohibited.
- Generated thread explanations are prohibited.
- Generated causal or thematic prose is prohibited.
- Owner-approved summaries may be displayed only if explicitly approved or owner-authored.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded` and must not be guessed.
- `evidence_summaries` must not be paraphrased into prose.
- `confidence_at_promotion` must be displayed as a stored value, never as a current truth certainty.
- Thread status, resolution, and related open-question references must come from the approved record only.
- Thread status conflicts (for example, `resolved` with no `resolved_event_id`) must surface as `Thread Status Conflict` warnings, not be auto-repaired.
- Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claims must not be displayed.

## 6. Page Operations

First-version allowed operations:

- View the approved plot-thread list.
- Select a thread to view its detail panel.
- Filter and search the approved plot-thread list locally.
- Open linked source scene/note/material from the linked sources panel.
- Open linked timeline event, character, location, or object page if available.
- Open the source OMI candidate or promotion record from the provenance links.
- Open the OMI Ideas / Candidates page from the candidate backlog snapshot.
- Open the future approved open-questions placeholder.
- Open the future approved continuity-warnings placeholder.
- Open the future approved scene/usage placeholder.

First-version operations must:

- Be read-only with respect to approved memory/canon.
- Be read-only with respect to OMI records.
- Avoid model/Ollama calls during navigation, list, filter, search, or selection.
- Avoid generated summaries, generated explanations, or generated plot/timeline prose.
- Avoid any silent mutation of `memory/plot_threads.json`, `memory/index.json`, or OMI records.
- Avoid any direct apply-promotion action from this page.
- Avoid any silent retitling or silent status correction of plot-thread records.

Future-only operations (out of scope for WORKSPACE-016 first implementation):

- Editing approved plot-thread memory/canon directly.
- Merging approved plot threads.
- Splitting approved plot-thread records.
- Archiving approved plot threads.
- Restoring superseded approved plot threads.
- Creating new approved plot threads from this page.
- Apply-promotion from this page.
- Extracting plot-thread candidates from owner-authored text on this page.
- Plot-thread graph visualization.
- Plot-thread timeline visualization.
- Auto-detecting unresolved plot threads.
- Generating plot summaries or explanations.
- Dramatica plot or thread classification.

Future operations must be defined in separate future specs and require separate tests.

## 7. Local Search and Filter

First-version search and filter must be local and deterministic.

Allowed search/filter dimensions:

- `display_title` / `thread_label` / `canonical_name`.
- `thread_type` if present.
- `status` if present.
- `tags` if present.
- Approved description if the owner has approved a description.
- Linked source IDs (`introduced_scene_id`, `related_scene_ids`, `linked_chapter_ids`, `linked_timeline_event_ids`, `linked_character_ids`, `linked_location_ids`, `linked_object_ids`).
- `source_candidate_ids`.
- `promotion_record_ids`.

First-version search/filter must:

- Run locally over already-loaded data.
- Avoid semantic search.
- Avoid model/Ollama calls.
- Avoid generated summaries, descriptions, causal explanations, thematic prose, or expansions.
- Avoid any candidate extraction during search.
- Avoid any apply-promotion or OMI mutation during search.
- Label results with their status: `Approved Plot Thread`, `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, `Promotion Record Only`, or `Not Yet Applied`.

Search rules:

- No global fuzzy expansion.
- No global synonyms.
- No language model ranking.
- No AI ranking explanations.
- No hidden generated plot summaries, thread explanations, or thematic hints in result rows.

## 8. Warning and Error States

The page must surface non-destructive warnings and errors. Warnings are not allowed to auto-repair, auto-delete, silently rewrite, silently retitle, silently correct, or silently promote records.

Required warnings and errors:

- Missing `memory/` directory.
- Missing `memory/plot_threads.json`.
- Missing `memory/index.json` if a future implementation depends on it.
- Corrupt `memory/plot_threads.json`.
- Corrupt `memory/index.json` if present.
- Unsupported `memory/plot_threads.json` schema.
- Duplicate `plot_thread_id` values within `memory/plot_threads.json`.
- `plot_thread_id` that does not match a safe single path component.
- `plot_thread_id` references that fail path safety.
- Approved thread references missing source candidate.
- Approved thread references missing promotion record.
- Broken linked scene references.
- Broken linked chapter references.
- Broken linked note/material references.
- Broken cross-record references to other approved memory records.
- Broken linked character/location/object/timeline-event references.
- Thread status conflicts (for example, `resolved` with no `resolved_event_id` or `resolved_event_id` set without `status: resolved`).
- Missing or inconsistent `start_event_id` / `current_event_id` / `resolved_event_id` references.
- Plot-thread cycles or contradictory relation links if represented.
- OMI plot-thread candidates exist but no approved plot threads yet.
- Promotion records present but no applied plot-thread record.
- Related open-question links exist but the open-questions page/model is not yet implemented.
- Related continuity-warning links exist but the continuity page/model is not yet implemented.
- Plot-thread graph or timeline visualization links exist but the visualization UI is not yet implemented.
- Scene usage links exist but linked scenes are missing.
- Evidence/provenance missing where required.
- Insufficient evidence labels carried over from apply-promotion.

Warning rules:

- Warnings are non-destructive.
- No auto-repair.
- No auto-delete.
- No identity rewrite.
- No silent retitling.
- No silent status correction.
- No silent cycle breaking.
- No silent candidate promotion.
- No silent deletion of corrupt records.
- No host filesystem path leakage in UI/API errors.
- Blocking warnings should prevent approved display for the affected thread.
- Non-blocking warnings may allow partial display where safe.

Recommended severity levels:

- `blocking`: approved display is unsafe for the affected thread.
- `warning`: page can load with degraded or partial data.
- `info`: empty state, future feature, or candidate-only note.

## 9. Relationship to Other Pages

Project Memory / Canon index page (WORKSPACE-011):

- Provides the parent navigation entry and category cards.
- The Plot Threads card must show approved-only counts and link to this page.
- Candidate counts must remain on the OMI page.

Project Overview (WORKSPACE-008):

- May show approved plot-thread count only.
- May show candidate count labeled as candidate/audit.
- May link to this page and to the OMI page.

OMI Ideas / Candidates (WORKSPACE-012):

- Owns candidate review, owner decision, destination, evidence/provenance, and promotion record creation for plot-thread candidates.
- This page must not duplicate OMI review actions.

Chapters / Scenes (WORKSPACE-009) and Notes / Materials (WORKSPACE-010):

- May show plot-thread references in scene or note metadata.
- This page is the project-local approved destination for those references.

Approved Characters (WORKSPACE-013), Approved Locations / Settings (WORKSPACE-014), and Approved Timeline (WORKSPACE-015):

- Are sibling approved-only category pages.
- Cross-record references should be consistent with the Approved Characters, Approved Locations / Settings, and Approved Timeline pages' display rules.

Future approved pages (relationships, continuity/consistency, open questions, approved memory/canon index):

- Should follow the same approved-only display rules.
- Cross-record links should be consistent with this page's display rules.

## 10. API Planning

These routes are future planning only. Do not implement them in WORKSPACE-016.

Every route must validate `project_id` as a safe single path component and preserve project-local state. Plot-thread routes must reject traversal, absolute paths, unsafe IDs, unsupported schema versions, duplicate IDs, and invalid record shapes.

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/plot_threads.json` or `memory/index.json` on read.
- First-version routes must not apply promotions.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/plot-threads`

Version:

- First-version planning.

Purpose:

- Return the approved plot-thread list for the selected project.

Page dependency:

- Page Header.
- Approved Plot Thread List.
- Empty State.
- Warning State.

Validation:

- Safe `project_id`.
- Existing project.
- `memory/plot_threads.json` envelope shape when present.

No-prose boundary:

- Return stored thread records only.
- No generated summaries, thread explanations, causal explanations, or thematic prose.

Candidate/canon boundary:

- Return applied plot-thread memory/canon records only.
- Candidate records must come from OMI routes, not memory category routes.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project, treated as empty where appropriate.
- 422 corrupt `memory/plot_threads.json`, unsupported schema, duplicate IDs, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/plot-threads/{plot_thread_id}`

Version:

- First-version planning.

Purpose:

- Return a single approved plot-thread record.

Page dependency:

- Plot Thread Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.

Validation:

- Safe `project_id` and `plot_thread_id`.
- `plot_thread_id` is one of the IDs in `memory/plot_threads.json`.
- `plot_thread_id` is a safe single path component.

No-prose boundary:

- Return stored thread fields only.
- Do not generate summary, thread explanation, causal explanation, or thematic prose.

Candidate/canon boundary:

- Return applied plot-thread records only.

Expected errors:

- 400 invalid ID.
- 404 missing project or thread.
- 422 corrupt or unsupported record.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/plot-threads/{plot_thread_id}/provenance`

Version:

- First-version planning.

Purpose:

- Return provenance metadata for a single approved plot thread.

Page dependency:

- Evidence / Provenance Panel.

Validation:

- Safe `project_id` and `plot_thread_id`.

No-prose boundary:

- Return stored provenance only.
- No generated explanations.

Candidate/canon boundary:

- Provenance is audit metadata, not a thread description.

Expected errors:

- 400 invalid ID.
- 404 missing project or thread.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/plot-threads/health`

Version:

- First-version planning.

Purpose:

- Return non-destructive health warnings for the approved plot-thread store.

Page dependency:

- Warning State.

Validation:

- Safe `project_id`.
- Read-only scans only.
- Thread status conflict and inconsistent start/current/resolved event detection must be non-mutating.

No-prose boundary:

- Warnings are factual status only.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, rewrite, retitle, or silently correct thread records.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project.
- 500 sanitized partial scan failure.

### `GET /api/projects/{project_id}/memory/summary` (composed)

Version:

- Optional first-version route.

Purpose:

- Provide approved plot-thread counts alongside other approved category counts.

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

- This is the only future route group that may create applied plot-thread memory/canon from a promotion record.

Expected errors:

- Deferred.

## 11. Frontend Planning

Do not implement UI in WORKSPACE-016.

Future components:

- `ApprovedPlotThreadsPage`
- `ApprovedPlotThreadsBoundaryBanner`
- `ApprovedPlotThreadList`
- `ApprovedPlotThreadListItem`
- `ApprovedPlotThreadDetailPanel`
- `PlotThreadEvidencePanel`
- `PlotThreadSourceLinksPanel`
- `PlotThreadTimelineSceneSnapshot`
- `PlotThreadRelatedEntitiesSnapshot`
- `PlotThreadOpenQuestionsPlaceholder`
- `PlotThreadContinuityWarningsPlaceholder`
- `PlotThreadCandidateBacklogSnapshot`
- `PlotThreadSearchFilterControls`
- `PlotThreadWarningsPanel`
- `PlotThreadEmptyState`
- `PlotThreadFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No "explain plot" button.
- No "fix plot" button.
- No "resolve thread" button.
- No "write missing scene" button.
- No "continue thread" button.
- No "generate twist" button.
- No "generate plot summary" button.
- No "improve thread" button.
- No "polish thread" button.
- No style imitation controls.
- No generated summaries.
- No apply-promotion button.
- No archive/merge/split controls.
- No direct edit of approved plot-thread records from this page.
- No mutation of `memory/plot_threads.json` or `memory/index.json` on the client.
- No mutation of OMI records.
- No JSONL/training writes.
- No model/Ollama calls during navigation, list, filter, search, or selection.

UI labeling rules:

- Each approved thread must use `Approved Plot Thread` labeling.
- Candidate counts must use the candidate status labels from WORKSPACE-012.
- Promotion record counts must use `Promotion Record Only` and `Not Yet Applied` until the record actually created the thread.
- Missing fields must use `Unknown`, `Not approved yet`, or `Not recorded`.
- Thread status conflicts must use `Thread Status Conflict`.
- Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claims must not appear.

Suggested loading behavior:

- Show page shell while approved plot-thread list loads.
- Show partial sections where data is available.
- Show warnings for degraded or invalid sections.
- Use project recovery state for blocking project metadata failures.

## 12. Future Tests

Future implementation should include tests for:

- Page loads with no `memory/` directory.
- Page loads empty approved plot-thread state.
- Page loads approved plot threads from `memory/plot_threads.json`.
- Page loads with corrupt `memory/plot_threads.json` and shows warning.
- Page loads with duplicate `plot_thread_id` values and shows warning.
- Page rejects unsafe `project_id` and `plot_thread_id` values.
- Page rejects `plot_thread_id` traversal.
- Page rejects `plot_thread_id` that is not in the allowed set.
- Page loads with unsupported schema and shows warning.
- Page shows `Unknown`/`Not approved yet`/`Not recorded` for missing fields.
- Page shows `Thread Status Conflict` for inconsistent status and resolution fields.
- Page does not show `Pending Candidate` rows.
- Page does not show `Rejected Candidate` rows.
- Page does not show `Archived Candidate` rows.
- Page does not show `Approved Candidate` rows from OMI.
- Page does not show `Promotion Record Only` rows as approved threads.
- Page shows `Promotion Record Only` link only as provenance.
- Page does not call Ollama or any model during load, list, filter, search, or selection.
- Page does not generate summaries, descriptions, thread explanations, causal explanations, or thematic prose.
- Page does not create OMI records.
- Page does not modify `memory/plot_threads.json` or `memory/index.json`.
- Page does not apply promotions.
- Page does not write JSONL records.
- Page does not update `training/data/dataset_manifest.json`.
- Page does not display Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claims.
- Page exposes only allowed first-version operations.
- Page has no AI prose-generation controls.
- Local search/filter does not call a model.
- Local search/filter is deterministic and bounded to safe fields.
- Linked source scene/note/material links open correctly.
- Broken linked source references show warnings.
- Broken linked character/location/object/timeline-event references show warnings.
- Missing or inconsistent `start_event_id` / `current_event_id` / `resolved_event_id` references show warnings.
- Plot-thread cycles or contradictory relation links show warnings if represented.
- Empty state shows guidance and a link to OMI Ideas / Candidates.
- Empty state does not invent placeholder threads.
- Warning state shows non-destructive warnings only.
- Warning state does not auto-repair, auto-delete, auto-promote, auto-retitle, or auto-correct thread records.

## 13. Deferred Decisions

Deferred to future implementation tasks:

- Whether the plot-thread graph view becomes a list, a tree, or a network graph.
- Whether the plot-thread timeline view becomes a list, a sortable table, or a graph.
- Whether the first plot-thread list loads from `memory/plot_threads.json` directly, from `memory/index.json` plus category files, or from a backend summary endpoint.
- Whether approved plot-thread records support per-record files in addition to category files.
- Whether `thread_type` becomes a bounded allowed list before it appears in the UI.
- Whether `status` becomes a bounded allowed list before it appears in the UI.
- Whether `start_event_id` / `current_event_id` / `resolved_event_id` editors are owner-controlled only or also candidate-driven.
- Whether navigation summaries may mention approved plot threads in approved navigation contexts.
- Whether cross-record links include future approved open-questions, continuity-warnings, and relationships pages and what minimum fields they require.
- Whether `memory/index.json` is required before the first plot-threads page implementation or remains derived/lazy.
- Whether applied plot-thread records can ever carry a future Dramatica plot, signpost, driver, Concern, Issue, Problem, Solution, or thematic claim and under what approval/evidence conditions.
- Whether future apply-promotion is allowed to merge or split plot threads atomically.
- Whether archived/superseded plot threads are hidden by default, shown in a section, or shown with status.
- Browser design for large plot-thread lists.
- Whether the candidate backlog snapshot is hidden, collapsed, or always visible.
- Whether `revision_history` becomes a dedicated panel.
- Whether scene/usage view becomes a count, a list, or a per-scene link set.
- Whether thread status conflict resolution becomes a separate future repair flow.

## 14. Implementation Non-Goals

WORKSPACE-016 does not implement:

- The Approved Plot Threads page UI.
- Backend memory/canon routes for plot threads.
- Apply-promotion.
- Plot-thread extraction.
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
- Plot Threads page concepts and required labels.
- First-version page layout.
- Approved plot-thread display model.
- Page operations.
- Local search/filter planning.
- Warning and error states.
- Relationship to other pages.
- API planning.
- Frontend planning.
- Future tests.
- Deferred decisions.
- Implementation non-goals.

This spec does not implement runtime code, frontend UI, tests, packages, dataset files, JSONL records, training, model calls, project files, OMI records, memory/canon files, plot-thread extraction, apply-promotion, or Dramatica-specific logic.
