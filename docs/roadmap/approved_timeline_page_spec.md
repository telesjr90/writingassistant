# WORKSPACE-015: Approved Timeline Page Spec

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
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Timeline page should be the future project-local destination for owner-approved timeline event memory/canon records. It must show only timeline event records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, and approved-but-not-applied timeline/event candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

The Approved Timeline page should:

- Show owner-approved timeline event memory/canon records only when those records are present in the future `memory/timeline.json` file.
- Treat approved timeline event truth as project memory/canon only after owner approval, a recorded promotion record, and a successful future apply-promotion step.
- Clearly distinguish approved timeline event truth from OMI timeline/event candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved timeline event back to source evidence, provenance, source candidate IDs, source scene IDs, source promotion record IDs, and approval metadata.
- Show absolute dates, relative times, sequence indices, and order groups only when the approved record explicitly carries them.
- Show unresolved or missing event fields honestly as `Unknown`, `Not approved yet`, or `Not recorded` instead of guessing.
- Show ambiguous or undecidable order as `Ambiguous Order` or `Order Not Approved` rather than forcing a false sequence.
- Show cause/effect links only when they are explicitly approved.
- Show an empty state when no approved timeline event records exist yet.
- Show a candidate backlog snapshot that links only counts and entry points to the OMI Ideas / Candidates page.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic candidate extraction.
- Avoid apply-promotion behavior.
- Avoid silent mutation of approved memory/canon or OMI records.
- Avoid Dramatica-specific sequence, signpost, driver, or causality claims in this workspace phase.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Timeline Page Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for timeline event candidates.
- Source material is not approved timeline event memory/canon by default.
- An event mentioned in a scene is not an approved timeline event record by itself.
- A date or sequence note in a material is not an approved timeline event record by itself.
- Source material must not be copied into approved timeline memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions an event is not an approved timeline event record.

### OMI Timeline / Event Candidates

Definition:

- Structured `timeline_event_candidate` records that have not been applied to approved memory/canon.

Rules:

- Timeline/event candidates are not canon.
- Timeline/event candidates must not appear in the approved timeline event list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.

### Approved-but-Not-Applied Candidates

Definition:

- `timeline_event_candidate` records the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved timeline event memory/canon.
- Approved-but-not-applied candidates must not appear in the approved timeline event list.
- The page may show counts and entry points only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved timeline events.
- Promotion records may be linked as provenance from a timeline event record that an apply-promotion step actually created.

### Applied Timeline Event Memory / Canon Records

Definition:

- Durable owner-approved `timeline_event_memory_record` entries written to the future `memory/timeline.json` file by a future apply-promotion step.

Rules:

- Applied timeline event records are the only records allowed in the approved timeline event list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, and approval metadata.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/timeline.json` entries.

### Chronology and Sequence

Definition:

- Future `absolute_date`, `relative_time`, `sequence_index`, `order_group`, and `chronology_label` fields on approved timeline event records.

Rules:

- Chronology and sequence must come from approved memory/canon records only.
- Chronology must not be inferred from scene text or notes at page load.
- Sequence collisions and chronology conflicts must surface as non-destructive warnings.
- The first version of this page must not render a sorted timeline; it must show a placeholder plus a deterministic ordering warning.
- Ambiguous order must be shown as `Ambiguous Order` or `Order Not Approved`, not as a forced sequence.

### Cause / Effect Links

Definition:

- Future `cause_event_ids` and `effect_event_ids` references between approved timeline event records.

Rules:

- Cause/effect links must come from approved memory/canon records only.
- Cause/effect links must not be inferred from scene text, notes, or OMI candidates.
- Cycles in the cause/effect graph must surface as non-destructive `Cause / Effect Cycle` warnings.
- The first version of this page must not render a causality graph; it must show a placeholder.
- Missing or unapproved cause/effect links must be shown as `Unknown` or `Not Recorded`, not inferred.

### Scene Usage

Definition:

- Future `linked_scene_ids` and `linked_chapter_ids` references between approved timeline event records and scene or chapter files.

Rules:

- Scene usage must come from approved memory/canon records only.
- Broken scene references must show warnings and must not invent replacements.
- Scene usage counts are derived from approved records; they are not generated summaries.

### Future Dramatica Sequence, Signpost, Driver, or Causality Claims

Definition:

- Future Dramatica storyform-specific signpost progression, driver/quad classification, or causality grid claims.

Rules:

- Dramatica sequence, signpost, driver, or causality claims are deferred.
- The first version of this page must not display any Dramatica sequence, signpost, driver, or causality claim.
- Generic labels such as `Signpost 1` or `Driver` are not required and should not be inferred.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved timeline event display.
- The first implementation of this page must not call a model.

### Insufficient Evidence

Definition:

- Timeline event evidence/provenance is missing, weak, broken, unsafe, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting or rewriting the timeline event record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any event that already exists.

## 3. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Timeline Event` | Marks each applied `timeline_event_memory_record`. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Approved Candidate` | Marks approved-but-not-applied timeline/event candidates on the OMI page; this page may show counts and links only. |
| `Pending Candidate` | Marks pending OMI timeline/event candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI timeline/event candidates on the OMI page. |
| `Archived Candidate` | Marks archived OMI timeline/event candidates on the OMI page. |
| `Needs Revision` | Marks needs-revision OMI timeline/event candidates on the OMI page. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied timeline event record. |
| `Source / Evidence` | Marks source scene, source note, source material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved event fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Ambiguous Order` | Marks records where the owner has not approved a definite sequence position. |
| `Order Not Approved` | Marks records where the sequence or chronology has not been approved. |
| `Chronology Placeholder` | Marks that the chronology/ordering view is not yet implemented. |
| `Cause / Effect Placeholder` | Marks that the cause/effect view is not yet implemented. |
| `Scene Usage Placeholder` | Marks that the scene usage view is not yet implemented. |
| `Chronology Conflict` | Marks two or more approved events whose stored order labels conflict. |
| `Sequence Collision` | Marks two or more approved events that share the same `sequence_index`. |
| `Cause / Effect Cycle` | Marks a cycle in the approved cause/effect graph. |
| `Future / Not Implemented` | Marks areas such as timeline visualization, causality graph, or Dramatica signpost/driver claims that are not part of the first implementation. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved timeline event list.
- Counts must be separated by status.
- Approved timeline event counts must come from applied `timeline_event_memory_record` entries only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Timeline Event`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved timeline event list.
- Chronology conflict, sequence collision, and cause/effect cycle warnings must use their named labels and must not auto-repair, silently reorder, or silently break cycles.
- Chronology, cause/effect, and scene usage placeholders must use their named labels and must not invent missing links.

## 4. First-Version Page Layout

First-version sections:

- Page Header.
- Timeline Page Boundary Banner.
- Approved Timeline Event List.
- Timeline Event Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Chronology / Ordering Placeholder.
- Cause / Effect Links Placeholder.
- Scene Usage Snapshot.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and the Approved Timeline area.
- Show approved-only counts and link back to the project memory/canon index when available.

Data source:

- Active project metadata from `project.json`.
- Future `memory/index.json` and `memory/timeline.json` only if those files already exist.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate event summaries, causal explanations, plot summaries, or story prose.

Candidate/canon boundary:

- Approved timeline event counts must come from applied memory/canon records only.
- Candidate or promotion counts must be labeled separately and must not appear as approved counts.

Empty state:

- Show zero approved events and a link to OMI Ideas / Candidates.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved timeline event metadata shows a warning and avoids approved display.

### Timeline Page Boundary Banner

Purpose:

- State that the page is owner-approved timeline event memory/canon only, not candidate review and not an AI writing surface.

Data source:

- Static product boundary copy.

No-prose boundary:

- Banner must include or link to the standard refusal policy.
- No write, rewrite, continue, polish, improve, imitate, expand, or generate controls.

Candidate/canon boundary:

- Banner must state that OMI timeline/event candidates, approved-but-not-applied candidates, and promotion records are not approved timeline event memory/canon.
- Banner must state that Dramatica signpost, driver, or causality claims are not part of this page.

Empty state:

- Banner remains visible even when no approved events exist.

Error state:

- Banner remains visible even when approved timeline event data is partially corrupt.

### Approved Timeline Event List

Purpose:

- Show applied timeline event memory/canon records for the selected project.
- Provide a deterministic ordering and a simple local filter/search over safe text fields.

Data source:

- Future `memory/timeline.json` only.
- Future `memory/index.json` as derived convenience state only.

No-prose boundary:

- Display stored record fields only.
- Do not generate event summaries, causal explanations, plot summaries, or story prose.
- Do not include "explain causality," "generate timeline," "fix chronology," "write missing event," or "create scene from event" actions.

Candidate/canon boundary:

- Each row must use `Approved Timeline Event`.
- Approved counts must come from applied memory/canon records only.
- Pending/rejected/archived/approved-but-not-applied candidates must not be blended in.
- The list may use the stored `sequence_index` or `order_group` for deterministic ordering, but it must not invent ordering where the owner has not approved it.

Empty state:

- Show a guidance block that no approved events exist yet and link to OMI Ideas / Candidates.

Error state:

- Corrupt event records, duplicate IDs, sequence collisions, chronology conflicts, unsupported schema, or stale index entries show warnings and the affected event must not appear as a normal approved row.

### Timeline Event Detail Panel

Purpose:

- Show the selected approved event's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, linked sources, chronology, cause/effect links, scene usage links, approval metadata, and provenance summary.

Data source:

- The selected applied `timeline_event_memory_record` from `memory/timeline.json`.

No-prose boundary:

- Display stored fields only.
- No generated summary, no generated causal explanation, no generated plot summary, no style imitation.

Candidate/canon boundary:

- Use `Approved Timeline Event` labeling.
- The event must be an applied record, not a candidate.
- Promotion records are linked as provenance, not as the event itself.

Empty state:

- No selection should show "select an approved timeline event" guidance.

Error state:

- Broken cross-record links, missing source references, or unsupported schema must show warnings and not invent replacements.

### Evidence / Provenance Panel

Purpose:

- Show evidence, source references, source kind, source scenes, source notes/materials, source candidate IDs, source promotion record IDs, hashes if stored, confidence at promotion time, and approval timestamps.

Data source:

- Approved event record `source_candidate_ids`, `promotion_record_ids`, `evidence_summaries`, `provenance`, `evidence_ids`, and `confidence_at_promotion`.

No-prose boundary:

- Evidence display must not generate explanatory prose beyond stored metadata and fixed UI labels.
- No generated "what this event represents" or "why this event matters" prose.

Candidate/canon boundary:

- Evidence supports owner review and traceability.
- Evidence does not establish truth by itself outside the apply-promotion step that created the record.

Empty state:

- Missing evidence must show `Evidence Required` or `Insufficient Evidence` where applicable, never guessed.

Error state:

- Broken source references, unsafe paths, or unsupported source kinds must show warnings and not invent replacements.

### Linked Sources Panel

Purpose:

- Show linked scenes, chapters, notes, materials, and other approved memory records that the event is connected to.
- Show linked approved character, location, object, organization, plot thread, and continuity warning records when those records are available.

Data source:

- Approved event `linked_scene_ids`, `linked_chapter_ids`, `involved_character_ids`, `location_id`, `involved_object_ids`, `related_plot_thread_ids`, and any other cross-record references that exist in future schema.

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

### Chronology / Ordering Placeholder

Purpose:

- Reserve space for the future approved chronology/ordering view.

Data source:

- Approved event `absolute_date`, `relative_time`, `sequence_index`, `order_group`, and `chronology_label` only if those fields exist in the applied record.

No-prose boundary:

- No generated chronology narrative.
- No generated "this event happened before" prose.

Candidate/canon boundary:

- Chronology must be built from approved memory/canon records only.
- The first version must not infer chronology from scene text, notes, or OMI candidates.
- Sequence collisions and chronology conflicts must surface as non-destructive `Sequence Collision` or `Chronology Conflict` warnings.
- Ambiguous order must surface as `Ambiguous Order` or `Order Not Approved`.

Empty state:

- Show the placeholder.

Error state:

- Sequence collisions, chronology conflicts, or unresolved sequence/chronology fields must show warnings and not auto-repair.

### Cause / Effect Links Placeholder

Purpose:

- Reserve space for the future approved cause/effect view.

Data source:

- Approved event `cause_event_ids` and `effect_event_ids` only if those fields exist in the applied record.

No-prose boundary:

- No generated causal narrative.
- No generated "this event caused" prose.

Candidate/canon boundary:

- Cause/effect must be built from approved memory/canon records only.
- The first version must not infer cause/effect from scene text, notes, or OMI candidates.
- Cycles in the cause/effect graph must surface as non-destructive `Cause / Effect Cycle` warnings.

Empty state:

- Show the placeholder.

Error state:

- Cycle detection or unresolved cause/effect references must show warnings and not auto-repair.

### Scene Usage Snapshot

Purpose:

- Show approved event scene and chapter usage counts and links based on `linked_scene_ids` and `linked_chapter_ids`.
- Provide a simple deterministic count without generating scene summaries.

Data source:

- Approved event scene and chapter references only.

No-prose boundary:

- Counts and links only.
- No generated scene summaries or "what happens here" prose.

Candidate/canon boundary:

- Scene usage must come from approved memory/canon records only.
- Broken scene or chapter references must show warnings and must not be silently dropped.

Empty state:

- Show "no approved scene usage" or equivalent.

Error state:

- Broken scene or chapter references must show warnings and must not be invented.

### Candidate Backlog Snapshot

Purpose:

- Show owner-visible counts and links for OMI timeline/event candidates.
- Help the owner see whether timeline/event review is needed in OMI.

Data source:

- `omi/index.json` candidate counts and lightweight candidate metadata when valid.

No-prose boundary:

- Counts and labels only.
- No generated candidate summaries or plot hints.

Candidate/canon boundary:

- Counts must be clearly labeled `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, or `Promotion Record Only` and must not appear in approved timeline event counts.
- The page may link only to the OMI Ideas / Candidates page for review.

Empty state:

- Show no candidates and link to OMI Ideas / Candidates.

Error state:

- Corrupt OMI metadata should show a warning and avoid using its counts as truth.

### Empty State

Purpose:

- Explain what the page shows when no approved events exist yet.

Data source:

- Static product boundary copy plus project metadata.

No-prose boundary:

- Guidance is operational, not generated story text.

Candidate/canon boundary:

- Link to OMI Ideas / Candidates for candidate review.
- State that approved events appear only after future apply-promotion.

Empty state:

- Missing `memory/timeline.json`, empty `records` array, or absent `memory/` folder are valid empty states.

Error state:

- If project metadata is invalid, show recovery/help instead of empty-state guidance.

### Warning State

Purpose:

- Surface non-destructive health warnings about the approved timeline store.

Data source:

- Project validation.
- Memory index/category validation.
- Cross-record reference checks where safe.
- Sequence collision and chronology conflict detection where safe.
- Cause/effect cycle detection where safe.

No-prose boundary:

- Warnings are factual status messages only.
- No generated repair text that rewrites event truth.

Candidate/canon boundary:

- Warnings must not promote, repair, delete, merge, rewrite, reorder, or break cycle records.

Empty state:

- Show no warnings when clean.

Error state:

- Blocking warnings prevent approved display for the affected event.
- Non-blocking warnings allow partial display where safe.

### Future Page Link Reference

Purpose:

- Reserve space for navigation to future approved pages.

Data source:

- Static route references.

No-prose boundary:

- Link text only.

Candidate/canon boundary:

- Future approved page links (characters, locations/settings, plot threads, continuity/consistency, approved memory/canon index) must be labeled as future or as currently available depending on implementation status.

Empty state:

- Show a guidance block for future pages.

Error state:

- Disable links whose target pages are not yet implemented.

## 5. Approved Timeline / Event Display Model

Approved timeline event records must be displayed only from applied `timeline_event_memory_record` entries. The first version of this page may display the following fields when they exist in the stored record.

| Field | Source | Display rule |
| --- | --- | --- |
| `timeline_event_id` | Applied record | Stable ID shown in small text. |
| `display_title` | `event_label` or `canonical_name` | Primary label. |
| `event_type` | Applied record | Show only if explicitly present; do not infer Dramatica signpost, driver, or causality type. |
| `status` | Applied record | Show `active`, `needs_review`, `superseded`, `archived`, or `deleted_by_owner` if present. |
| `chronology_label` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `absolute_date` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `relative_time` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `sequence_index` | Applied record | Show only when the applied record explicitly carries it. Collisions must surface `Sequence Collision` warnings. |
| `order_group` | Applied record | Show only when the applied record explicitly carries it. If undefined, show `Not Recorded`. |
| `short_owner_approved_description` | `event_summary` or `notes` | Show only if the owner has approved the description; otherwise show `Not approved yet` or `Not recorded`. Never display AI-generated event summary, causal explanation, or plot prose. |
| `linked_scene_ids` | Applied record | Show scene IDs and titles. |
| `linked_chapter_ids` | Applied record | Show chapter IDs and titles. |
| `linked_character_ids` | `involved_character_ids` | Show approved character IDs and labels when available. |
| `linked_location_ids` | `location_id` | Show approved location IDs and labels when available. |
| `linked_object_ids` | `involved_object_ids` | Show approved object IDs and labels when available. |
| `linked_plot_thread_ids` | `related_plot_thread_ids` | Show approved plot thread IDs and labels when available. |
| `cause_event_ids` | Applied record | Show only when the applied record explicitly carries them. Cycles must surface `Cause / Effect Cycle` warnings. |
| `effect_event_ids` | Applied record | Show only when the applied record explicitly carries them. Cycles must surface `Cause / Effect Cycle` warnings. |
| `first_seen_source` | `scene_id` plus metadata | Show source scene title and ID. |
| `evidence_summaries` | Applied record | Show stored summaries. |
| `confidence_at_promotion` | Applied record | Show as a stored label or number, not as canon certainty. |
| `created_at` | Applied record | Show ISO-8601 timestamp. |
| `updated_at` | Applied record | Show ISO-8601 timestamp. |
| `approved_at` | Applied record | Show ISO-8601 approval timestamp. |
| `approved_by` | Applied record | Show owner or reviewer identifier. |
| `source_candidate_ids` | Applied record | Show source OMI candidate IDs and link to the OMI page for each. |
| `promotion_record_ids` | Applied record | Show source promotion record IDs and link to the OMI page for each as `Promotion Record Only` until apply-promotion actually created the event. |
| `revision_history` | Applied record | Show when present. |
| `supersedes_record_ids` | Applied record | Show when present. |
| `superseded_by_record_id` | Applied record | Show when present. |
| `notes` | Applied record | Show owner notes only. |

Display rules:

- All displayed timeline truth must come from applied memory/canon records.
- Unapproved candidates must not appear as truth.
- Generated event summaries are prohibited.
- Generated causal explanations are prohibited.
- Generated plot/timeline prose is prohibited.
- Owner-approved summaries may be displayed only if explicitly approved or owner-authored.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded` and must not be guessed.
- `evidence_summaries` must not be paraphrased into prose.
- `confidence_at_promotion` must be displayed as a stored value, never as a current truth certainty.
- Ambiguous order must surface as `Ambiguous Order` or `Order Not Approved`; the page must not silently assign a sequence position.
- Cause/effect links must come from approved records only; cycles must surface as warnings, not be auto-repaired.
- Dramatica signpost, driver, or causality claims must not be displayed.

## 6. Page Operations

First-version allowed operations:

- View the approved timeline event list.
- Select an event to view its detail panel.
- Filter and search the approved timeline event list locally.
- Open linked source scene/note/material from the linked sources panel.
- Open the source OMI candidate or promotion record from the provenance links.
- Open the OMI Ideas / Candidates page from the candidate backlog snapshot.
- Open the future approved chronology/ordering placeholder.
- Open the future approved cause/effect placeholder.
- Open the future approved scene usage placeholder.

First-version operations must:

- Be read-only with respect to approved memory/canon.
- Be read-only with respect to OMI records.
- Avoid model/Ollama calls during navigation, list, filter, search, or selection.
- Avoid generated summaries, generated causal explanations, or generated plot/timeline prose.
- Avoid any silent mutation of `memory/timeline.json`, `memory/index.json`, or OMI records.
- Avoid any direct apply-promotion action from this page.
- Avoid any silent reordering of timeline events.

Future-only operations (out of scope for WORKSPACE-015 first implementation):

- Editing approved timeline event memory/canon directly.
- Merging approved timeline events.
- Splitting approved timeline event records.
- Archiving approved timeline events.
- Restoring superseded approved timeline events.
- Creating new approved timeline events from this page.
- Apply-promotion from this page.
- Extracting timeline/event candidates from owner-authored text on this page.
- Timeline visualization.
- Causality graph visualization.
- Auto-ordering of ambiguous events.
- Generated event summaries or causal explanations.
- Dramatica signpost or driver classification.

Future operations must be defined in separate future specs and require separate tests.

## 7. Local Search and Filter

First-version search and filter must be local and deterministic.

Allowed search/filter dimensions:

- `display_title` / `event_label` / `canonical_name`.
- `event_type` if present.
- `status` if present.
- `chronology_label` if present.
- `relative_time` if present.
- `tags` if present.
- Approved description if the owner has approved a description.
- Linked source IDs (`linked_scene_ids`, `linked_chapter_ids`, `involved_*` IDs, `related_*` IDs).
- `source_candidate_ids`.
- `promotion_record_ids`.

First-version search/filter must:

- Run locally over already-loaded data.
- Avoid semantic search.
- Avoid model/Ollama calls.
- Avoid generated summaries, descriptions, causal explanations, or expansions.
- Avoid any candidate extraction during search.
- Avoid any apply-promotion or OMI mutation during search.
- Label results with their status: `Approved Timeline Event`, `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, `Archived Candidate`, `Promotion Record Only`, or `Not Yet Applied`.

Search rules:

- No global fuzzy expansion.
- No global synonyms.
- No language model ranking.
- No AI ranking explanations.
- No hidden generated event summaries, causal explanations, or plot hints in result rows.

## 8. Warning and Error States

The page must surface non-destructive warnings and errors. Warnings are not allowed to auto-repair, auto-delete, silently rewrite, silently reorder, silently break cycles, or silently promote records.

Required warnings and errors:

- Missing `memory/` directory.
- Missing `memory/timeline.json`.
- Missing `memory/index.json` if a future implementation depends on it.
- Corrupt `memory/timeline.json`.
- Corrupt `memory/index.json` if present.
- Unsupported `memory/timeline.json` schema.
- Duplicate `timeline_event_id` values within `memory/timeline.json`.
- `timeline_event_id` that does not match a safe single path component.
- `timeline_event_id` references that fail path safety.
- Approved event references missing source candidate.
- Approved event references missing promotion record.
- Broken linked scene references.
- Broken linked chapter references.
- Broken linked note/material references.
- Broken cross-record references to other approved memory records.
- Broken linked character/location/object/plot-thread references.
- Chronology conflicts between two or more approved events.
- Sequence index collisions between two or more approved events.
- Cause/effect cycles in the approved event graph.
- Impossible or contradictory order labels (`Chronology Conflict`).
- OMI timeline/event candidates exist but no approved timeline events yet.
- Promotion records present but no applied timeline event record.
- Timeline visualization links exist but visualization UI is not yet implemented.
- Cause/effect view links exist but cause/effect UI is not yet implemented.
- Scene usage links exist but linked scenes are missing.
- Evidence/provenance missing where required.
- Insufficient evidence labels carried over from apply-promotion.

Warning rules:

- Warnings are non-destructive.
- No auto-repair.
- No auto-delete.
- No identity rewrite.
- No silent reordering.
- No silent cycle breaking.
- No silent candidate promotion.
- No silent deletion of corrupt records.
- No host filesystem path leakage in UI/API errors.
- Blocking warnings should prevent approved display for the affected event.
- Non-blocking warnings may allow partial display where safe.

Recommended severity levels:

- `blocking`: approved display is unsafe for the affected event.
- `warning`: page can load with degraded or partial data.
- `info`: empty state, future feature, or candidate-only note.

## 9. Relationship to Other Pages

Project Memory / Canon index page (WORKSPACE-011):

- Provides the parent navigation entry and category cards.
- The Timeline card must show approved-only counts and link to this page.
- Candidate counts must remain on the OMI page.

Project Overview (WORKSPACE-008):

- May show approved timeline event count only.
- May show candidate count labeled as candidate/audit.
- May link to this page and to the OMI page.

OMI Ideas / Candidates (WORKSPACE-012):

- Owns candidate review, owner decision, destination, evidence/provenance, and promotion record creation for timeline/event candidates.
- This page must not duplicate OMI review actions.

Chapters / Scenes (WORKSPACE-009) and Notes / Materials (WORKSPACE-010):

- May show timeline event references in scene or note metadata.
- This page is the project-local approved destination for those references.

Approved Characters (WORKSPACE-013) and Approved Locations / Settings (WORKSPACE-014):

- Are sibling approved-only category pages.
- Cross-record references should be consistent with the Approved Characters and Approved Locations / Settings pages' display rules.

Future approved pages (plot threads, relationships, continuity/consistency, approved memory/canon index):

- Should follow the same approved-only display rules.
- Cross-record links should be consistent with this page's display rules.

## 10. API Planning

These routes are future planning only. Do not implement them in WORKSPACE-015.

Every route must validate `project_id` as a safe single path component and preserve project-local state. Timeline routes must reject traversal, absolute paths, unsafe IDs, unsupported schema versions, duplicate IDs, and invalid record shapes.

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/timeline.json` or `memory/index.json` on read.
- First-version routes must not apply promotions.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/timeline`

Version:

- First-version planning.

Purpose:

- Return the approved timeline event list for the selected project.

Page dependency:

- Page Header.
- Approved Timeline Event List.
- Empty State.
- Warning State.

Validation:

- Safe `project_id`.
- Existing project.
- `memory/timeline.json` envelope shape when present.

No-prose boundary:

- Return stored event records only.
- No generated summaries, causal explanations, or plot/timeline prose.

Candidate/canon boundary:

- Return applied timeline event memory/canon records only.
- Candidate records must come from OMI routes, not memory category routes.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project, treated as empty where appropriate.
- 422 corrupt `memory/timeline.json`, unsupported schema, duplicate IDs, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/timeline/{timeline_event_id}`

Version:

- First-version planning.

Purpose:

- Return a single approved timeline event record.

Page dependency:

- Timeline Event Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.

Validation:

- Safe `project_id` and `timeline_event_id`.
- `timeline_event_id` is one of the IDs in `memory/timeline.json`.
- `timeline_event_id` is a safe single path component.

No-prose boundary:

- Return stored event fields only.
- Do not generate summary, causal explanation, or plot/timeline prose.

Candidate/canon boundary:

- Return applied timeline event records only.

Expected errors:

- 400 invalid ID.
- 404 missing project or event.
- 422 corrupt or unsupported record.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/timeline/{timeline_event_id}/provenance`

Version:

- First-version planning.

Purpose:

- Return provenance metadata for a single approved timeline event.

Page dependency:

- Evidence / Provenance Panel.

Validation:

- Safe `project_id` and `timeline_event_id`.

No-prose boundary:

- Return stored provenance only.
- No generated explanations.

Candidate/canon boundary:

- Provenance is audit metadata, not an event description.

Expected errors:

- 400 invalid ID.
- 404 missing project or event.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/timeline/health`

Version:

- First-version planning.

Purpose:

- Return non-destructive health warnings for the approved timeline store.

Page dependency:

- Warning State.

Validation:

- Safe `project_id`.
- Read-only scans only.
- Sequence collision, chronology conflict, and cause/effect cycle detection must be non-mutating.

No-prose boundary:

- Warnings are factual status only.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, rewrite, reorder, or break cycle records.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project.
- 500 sanitized partial scan failure.

### `GET /api/projects/{project_id}/memory/summary` (composed)

Version:

- Optional first-version route.

Purpose:

- Provide approved timeline event counts alongside other approved category counts.

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

- This is the only future route group that may create applied timeline event memory/canon from a promotion record.

Expected errors:

- Deferred.

## 11. Frontend Planning

Do not implement UI in WORKSPACE-015.

Future components:

- `ApprovedTimelinePage`
- `ApprovedTimelineBoundaryBanner`
- `ApprovedTimelineEventList`
- `ApprovedTimelineEventListItem`
- `ApprovedTimelineEventDetailPanel`
- `TimelineEvidencePanel`
- `TimelineSourceLinksPanel`
- `TimelineChronologyPlaceholder`
- `TimelineCauseEffectPlaceholder`
- `TimelineSceneUsageSnapshot`
- `TimelineCandidateBacklogSnapshot`
- `TimelineSearchFilterControls`
- `TimelineWarningsPanel`
- `TimelineEmptyState`
- `TimelineFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No "explain causality" button.
- No "generate timeline" button.
- No "fix chronology" button.
- No "write missing event" button.
- No "create scene from event" button.
- No "generate event summary" button.
- No "improve event" button.
- No "polish event" button.
- No style imitation controls.
- No generated summaries.
- No apply-promotion button.
- No archive/merge/split controls.
- No direct edit of approved timeline event records from this page.
- No mutation of `memory/timeline.json` or `memory/index.json` on the client.
- No mutation of OMI records.
- No JSONL/training writes.
- No model/Ollama calls during navigation, list, filter, search, or selection.

UI labeling rules:

- Each approved event must use `Approved Timeline Event` labeling.
- Candidate counts must use the candidate status labels from WORKSPACE-012.
- Promotion record counts must use `Promotion Record Only` and `Not Yet Applied` until the record actually created the event.
- Missing fields must use `Unknown`, `Not approved yet`, or `Not recorded`.
- Ambiguous order must use `Ambiguous Order` or `Order Not Approved`.
- Sequence collisions must use `Sequence Collision`.
- Chronology conflicts must use `Chronology Conflict`.
- Cause/effect cycles must use `Cause / Effect Cycle`.
- Dramatica signpost, driver, or causality claims must not appear.

Suggested loading behavior:

- Show page shell while approved timeline event list loads.
- Show partial sections where data is available.
- Show warnings for degraded or invalid sections.
- Use project recovery state for blocking project metadata failures.

## 12. Future Tests

Future implementation should include tests for:

- Page loads with no `memory/` directory.
- Page loads empty approved timeline event state.
- Page loads approved timeline events from `memory/timeline.json`.
- Page loads with corrupt `memory/timeline.json` and shows warning.
- Page loads with duplicate `timeline_event_id` values and shows warning.
- Page rejects unsafe `project_id` and `timeline_event_id` values.
- Page rejects `timeline_event_id` traversal.
- Page rejects `timeline_event_id` that is not in the allowed set.
- Page loads with unsupported schema and shows warning.
- Page shows `Unknown`/`Not approved yet`/`Not recorded` for missing fields.
- Page shows `Ambiguous Order` or `Order Not Approved` for events without approved order.
- Page does not show `Pending Candidate` rows.
- Page does not show `Rejected Candidate` rows.
- Page does not show `Archived Candidate` rows.
- Page does not show `Approved Candidate` rows from OMI.
- Page does not show `Promotion Record Only` rows as approved events.
- Page shows `Promotion Record Only` link only as provenance.
- Page does not call Ollama or any model during load, list, filter, search, or selection.
- Page does not generate summaries, descriptions, causal explanations, or plot/timeline prose.
- Page does not create OMI records.
- Page does not modify `memory/timeline.json` or `memory/index.json`.
- Page does not apply promotions.
- Page does not write JSONL records.
- Page does not update `training/data/dataset_manifest.json`.
- Page does not display Dramatica signpost, driver, or causality claims.
- Page exposes only allowed first-version operations.
- Page has no AI prose-generation controls.
- Local search/filter does not call a model.
- Local search/filter is deterministic and bounded to safe fields.
- Linked source scene/note/material links open correctly.
- Broken linked source references show warnings.
- Broken linked character/location/object/plot-thread references show warnings.
- Chronology conflicts show `Chronology Conflict` warnings.
- Sequence collisions show `Sequence Collision` warnings.
- Cause/effect cycles show `Cause / Effect Cycle` warnings.
- Chronology, sequence, and cause/effect warnings are non-destructive.
- Empty state shows guidance and a link to OMI Ideas / Candidates.
- Empty state does not invent placeholder events.
- Warning state shows non-destructive warnings only.
- Warning state does not auto-repair, auto-delete, auto-promote, or auto-reorder.

## 13. Deferred Decisions

Deferred to future implementation tasks:

- Whether the chronology view becomes a list, a sortable table, or a graph.
- Whether the cause/effect view becomes a list, a graph, or a matrix.
- Whether the first timeline list loads from `memory/timeline.json` directly, from `memory/index.json` plus category files, or from a backend summary endpoint.
- Whether approved timeline event records support per-record files in addition to category files.
- Whether `event_type` becomes a bounded allowed list before it appears in the UI.
- Whether `chronology_label` and `order_group` editors are owner-controlled only or also candidate-driven.
- Whether navigation summaries may mention approved timeline events in approved navigation contexts.
- Whether cross-record links include a future approved plot threads page and what minimum fields it requires.
- Whether `memory/index.json` is required before the first timeline page implementation or remains derived/lazy.
- Whether applied timeline event records can ever carry a future Dramatica signpost, driver, or causality claim and under what approval/evidence conditions.
- Whether future apply-promotion is allowed to merge or split events atomically.
- Whether archived/superseded events are hidden by default, shown in a section, or shown with status.
- Browser design for large timeline event lists.
- Whether the candidate backlog snapshot is hidden, collapsed, or always visible.
- Whether `revision_history` becomes a dedicated panel.
- Whether scene usage view becomes a count, a list, or a per-scene link set.
- Whether chronology, sequence, and cause/effect cycle resolution becomes a separate future repair flow.

## 14. Implementation Non-Goals

WORKSPACE-015 does not implement:

- The Approved Timeline page UI.
- Backend memory/canon routes for timeline events.
- Apply-promotion.
- Timeline/event extraction.
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
- Timeline page concepts and required labels.
- First-version page layout.
- Approved timeline/event display model.
- Page operations.
- Local search/filter planning.
- Warning and error states.
- Relationship to other pages.
- API planning.
- Frontend planning.
- Future tests.
- Deferred decisions.
- Implementation non-goals.

This spec does not implement runtime code, frontend UI, tests, packages, dataset files, JSONL records, training, model calls, project files, OMI records, memory/canon files, timeline/event extraction, apply-promotion, or Dramatica-specific logic.
