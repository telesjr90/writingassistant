# WORKSPACE-019: Approved Relationships Page Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-008: `docs/roadmap/project_overview_page_spec.md`
- WORKSPACE-009: `docs/roadmap/chapters_scenes_page_spec.md`
- WORKSPACE-010: `docs/roadmap/notes_materials_page_spec.md`
- WORKSPACE-011: `docs/roadmap/project_memory_canon_page_structure_spec.md`
- WORKSPACE-012: `docs/roadmap/omi_ideas_candidates_page_spec.md`
- WORKSPACE-013: `docs/roadmap/approved_characters_page_spec.md`
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- WORKSPACE-016: `docs/roadmap/approved_plot_threads_page_spec.md`
- WORKSPACE-017: `docs/roadmap/continuity_consistency_page_spec.md`
- WORKSPACE-018: `docs/roadmap/approved_open_questions_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Relationships page should be the future project-local destination for owner-approved relationship memory/canon records. It must show only relationship records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, needs-revision, and approved-but-not-applied relationship candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

This page is not a Dramatica Relationship Story page. Generic character or story-knowledge relationships are not Relationship Story proof and must not be presented as RS throughline classification, IC/RS structure, CIPS, dynamics, or Dramatica storyform truth.

The page should:

- Show owner-approved `relationship_memory_record` entries for the selected project.
- Read approved relationship truth only from future memory files such as `memory/relationships.json` or an equivalent approved memory store.
- Clearly distinguish approved relationship truth from OMI relationship candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved relationship back to source evidence, provenance, source candidate IDs, promotion record IDs, and approval metadata where available.
- Show unresolved, ambiguous, partial, or missing fields honestly as `Unknown`, `Not approved yet`, or `Not recorded`.
- Show an empty state when no approved relationship records exist.
- Link to the OMI Ideas / Candidates page for pending relationship candidates.
- Link to related characters, organizations/groups, locations, objects, timeline events, plot threads, open questions, continuity/consistency issues, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic relationship extraction.
- Avoid relationship graph generation.
- Avoid contradiction detection.
- Avoid apply-promotion behavior.
- Avoid generated relationship analysis, generated summaries, rewrite suggestions, dialogue suggestions, relationship-fix suggestions, and any controls that write or rewrite story prose.
- Avoid Dramatica-specific Relationship Story, IC/RS, CIPS, dynamics, or structural claims unless later approved and evidence-backed by a separate advanced-layer task.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Relationship Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for relationship candidates.
- Source material is not approved relationship memory/canon by default.
- An interaction, reference, proximity, conflict, alliance, family tie, organizational tie, or emotional state mentioned in a scene, note, or material is not an approved relationship record by itself.
- Source material must not be copied into approved relationship memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions a relationship is not an approved relationship record.

### OMI Relationship Candidates

Definition:

- Structured `relationship_candidate` records or future equivalent relationship candidates that have not been applied to approved memory/canon.

Rules:

- Relationship candidates are not canon.
- Relationship candidates must not appear in the approved relationship list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate relationship type, status, participant roles, evidence state, related links, and certainty must not be inferred as approved truth.
- Relationship candidates are generic story-knowledge candidates. They are not Dramatica Relationship Story proof.

### Approved-but-Not-Applied Candidates

Definition:

- Relationship candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved relationship memory/canon.
- Approved-but-not-applied candidates must not appear in the approved relationship list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved relationship records.
- Promotion records may be linked as provenance from an approved relationship record that a future apply-promotion step actually created or updated.
- Promotion records present without an approved memory record must show an audit-only warning or candidate backlog state, not an approved relationship.

### Applied Relationship Memory Records

Definition:

- Durable owner-approved `relationship_memory_record` entries written to the future approved memory store by a future apply-promotion step.

Rules:

- Applied relationship records are the only records allowed in the approved relationship list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, approval metadata, participant references, relationship state, and related record links where available.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/relationships.json` entries or equivalent records.

### Participant and Relationship State

Definition:

- Future stored fields that identify relationship participants, participant roles, relationship type, relationship status, relationship scope, affected sources, and linked story knowledge.

Rules:

- Participant identities, participant roles, relationship type, relationship status, relationship scope, and related links must come from approved memory/canon records only.
- A relationship may remain ambiguous, unresolved, one-sided, partly unknown, or insufficiently evidenced without implying an error.
- Missing participant roles or relationship state must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- Conflicting type/status/role fields must surface non-destructive warnings and must not be silently corrected.

### Future Dramatica Relationship Story Claims

Definition:

- Future Dramatica storyform-specific relationship claims, such as Relationship Story throughline proof, IC/RS structural classification, Relationship Story signpost/issue/problem/solution claims, CIPS, dynamics, or other Dramatica storyform truth.

Rules:

- Dramatica-specific relationship classification is deferred.
- The first version of this page must not display any Dramatica-specific Relationship Story diagnosis.
- Generic relationship labels must not be treated as Dramatica proof.
- Relationship records are not Dramatica RS claims unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, analysis system, or future relationship-analysis helper.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved relationship display.
- The first implementation of this page must not call a model.
- Generated relationship analysis, generated summaries, generated explanations, generated fixes, dialogue suggestions, and relationship-fix suggestions are prohibited.

### Insufficient Evidence

Definition:

- Relationship evidence/provenance is missing, weak, broken, unsafe, one-sided, ambiguous, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting, rewriting, retitling, reclassifying, or resolving the relationship record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any relationship that already exists.

## 3. Approved Relationship Display Model

Approved relationship records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `relationship_id` | Stable approved relationship ID; required for detail routing. |
| `display_title` | Owner-approved title/label. Missing title shows `Unknown`. |
| `relationship_type` | Stored type only. Do not infer from candidates, source text, or model output. |
| `relationship_status` | Stored status only, such as active, unresolved, changed, ended, ambiguous, needs owner review, superseded, archived, or not recorded. |
| `relationship_scope` | Stored scope only, such as project, chapter, scene, timeline event, plot thread, character pair, group, or object relationship. |
| `short_owner_approved_description` | Owner-approved description only. Do not generate relationship analysis, explanation, arc summary, or fix text. |
| `participant_ids` | Approved participant record IDs only; broken references show warnings. |
| `participant_roles` | Stored participant roles only. Missing roles show `Unknown`, `Not approved yet`, or `Not recorded`. |
| `primary_character_ids` | Approved character links only; unresolved links show warnings. |
| `secondary_character_ids` | Approved character links only; unresolved links show warnings. |
| `linked_organization_ids` | Approved organization/group links only; unresolved links show warnings. |
| `linked_location_ids` | Approved location links only; unresolved links show warnings. |
| `linked_object_ids` | Approved object/item links only; unresolved links show warnings. |
| `linked_timeline_event_ids` | Approved timeline event links only; unresolved links show warnings. |
| `linked_plot_thread_ids` | Approved plot-thread links only; unresolved links show warnings. |
| `linked_open_question_ids` | Approved open-question links only; unresolved links show warnings. |
| `linked_continuity_issue_ids` | Approved continuity/consistency links only; unresolved links show warnings. |
| `affected_scene_ids` | Approved source references only; broken references show warnings. |
| `affected_chapter_ids` | Approved source references only; broken references show warnings. |
| `linked_note_ids` | Approved source/reference links only; broken references show warnings. |
| `linked_material_ids` | Approved source/reference links only; broken references show warnings. |
| `first_seen_source` | First approved source/provenance locator if stored. |
| `latest_seen_source` | Latest approved source/provenance locator if stored. |
| `evidence` / `provenance` summary | Compact evidence/provenance metadata only; avoid long source copies and generated summaries. |
| `confidence` / `certainty` label | Stored confidence/certainty label only; it is owner-review metadata, not objective proof. |
| `owner_notes` | Owner-approved notes only. No generated relationship analysis or fix text. |
| `created_at` | Stored timestamp. |
| `updated_at` | Stored timestamp. |
| `approved_at` | Stored owner approval timestamp. |
| `approved_by` | Stored owner/reviewer identifier. |
| `source_candidate_ids` | OMI candidate provenance links only. |
| `promotion_record_ids` | Promotion audit links only. |
| `revision_history` | Stored revision trail if available. |
| `supersedes_record_ids` | Stored supersession links if available. |
| `superseded_by_record_id` | Stored replacement link if available. |
| `tags` | Stored owner-approved tags only. |
| `notes` | Owner notes, ambiguity notes, uncertainty notes, or implementation notes. No generated prose fixes. |

Display clarifications:

- Unapproved candidates must not appear as truth.
- Generated relationship analysis, generated summaries, rewrite suggestions, dialogue suggestions, and relationship-fix suggestions are prohibited.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- A relationship may remain ambiguous, unresolved, one-sided, partly unknown, or insufficiently evidenced without implying an error.
- Owner-approved descriptions and owner notes may be displayed only as stored approved fields.
- Generic relationship records must not be presented as Dramatica Relationship Story proof.
- If a future storage schema uses `subject_record_id` and `object_record_id`, the page may map those into `participant_ids` for display without inferring roles, direction, or RS meaning.

## 4. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Relationship` | Marks each applied approved memory/canon record. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Candidate` | Marks OMI relationship candidates outside the approved list. |
| `Pending Candidate` | Marks pending OMI relationship candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied relationship candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI relationship candidates. |
| `Needs Revision` | Marks OMI relationship candidates needing revision. |
| `Archived Candidate` | Marks archived OMI relationship candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied memory record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved relationship fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Ambiguous Relationship` | Marks relationships whose approved record intentionally preserves ambiguity. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Not Dramatica Relationship Story Proof` | Marks the page and relevant records as generic story knowledge, not RS proof. |
| `Future / Not Implemented` | Marks editing, merge/split, graph visualization, extraction, contradiction detection, apply-promotion, and Dramatica structural classification. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved relationship list.
- Counts must be separated by status.
- Approved relationship counts must come from applied memory/canon records only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Relationship`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, needs-revision, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved relationship list.
- Relationship records must carry an explicit non-Dramatica boundary wherever Dramatica confusion is likely.

## 5. First-Version Page Sections

First-version sections:

- Page Header.
- Relationships Boundary Banner.
- Approved Relationship List.
- Relationship Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Participant Snapshot.
- Linked Story Knowledge Snapshot.
- Related Plot Thread / Timeline Snapshot.
- Related Open Questions / Continuity Snapshot.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and Approved Relationships area.
- Show approved relationship count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved relationship records from `memory/relationships.json` or equivalent approved memory store if present.

Candidate/canon boundary:

- Header approved count must come from applied memory/canon records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, relationship summaries, explanations, fixes, dialogue, or rewrite suggestions.

Empty state:

- Show that no approved relationships exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Relationships Boundary Banner

Purpose:

- Explain that the page shows approved memory/canon relationship records only.
- Point pending relationship candidates to OMI.
- State that the page is not a prose-writing, relationship-fix, or Dramatica Relationship Story proof surface.

Data source:

- Static page copy.
- Optional lightweight OMI relationship candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not canon.
- State that approved relationships require future apply-promotion into memory/canon.
- State that generic relationship records are not Dramatica Relationship Story proof.

No-prose boundary:

- Prohibit generated relationship analysis, generated summaries, dialogue suggestions, rewrite suggestions, relationship fixes, and prose-patching controls.

Empty state:

- Banner remains visible even when no records exist.

Error state:

- Banner remains visible when approved-memory load partially fails.

### Approved Relationship List

Purpose:

- List approved relationship records for the selected project.
- Support local filter/search over approved relationship metadata.

Data source:

- Applied `relationship_memory_record` entries.
- Optional derived `memory/index.json` for navigation, with category files remaining source of truth.

Candidate/canon boundary:

- Exclude all OMI candidates, promotion records without applied memory, and source-only material.
- Candidate backlog may be represented only as separate counts/links.
- Each row must use `Approved Relationship`.

No-prose boundary:

- Do not generate relationship summaries, explanations, fixes, dialogue suggestions, or scene rewrite suggestions.
- List item descriptions must come from approved stored fields only.

Empty state:

- "No approved relationships yet" with link to OMI candidate review if candidate counts exist.

Error state:

- Corrupt memory file, unsupported schema, duplicate IDs, unsafe IDs, invalid records, participant conflicts, or type/status conflicts should show warnings and omit unsafe/invalid records from normal detail display.

### Relationship Detail Panel

Purpose:

- Show the selected approved relationship's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, affected sources, participants, linked story knowledge, approval metadata, revision history, and notes.

Data source:

- Selected approved relationship memory record.

Candidate/canon boundary:

- Detail panel must not hydrate missing fields from OMI candidates.
- Source candidate and promotion links are provenance only.
- Generic relationship detail must not imply Dramatica Relationship Story classification.

No-prose boundary:

- Do not generate relationship analysis, explanation, fix, rewritten dialogue, bonding scene, bridge scene, conflict resolution, or relationship arc prose.

Empty state:

- Prompt the owner to select an approved relationship.

Error state:

- Invalid selected ID, missing record, unsafe ID, unsupported schema, participant conflicts, type/status conflicts, or broken relation links show non-destructive warnings.

### Evidence / Provenance Panel

Purpose:

- Show the evidence/provenance trail behind the approved relationship.
- Identify first/latest sources, evidence IDs, source candidate IDs, promotion record IDs, approval data, and confidence/certainty labels where stored.

Data source:

- Approved memory record evidence/provenance fields.
- Linked OMI candidate/promotion metadata for audit links only.

Candidate/canon boundary:

- Candidate/promotion data is provenance, not approved truth.
- If evidence is missing or insufficient, show `Evidence Required` or `Insufficient Evidence`.
- Provenance links must not imply candidate relationship analysis is approved truth.

No-prose boundary:

- Evidence summaries must be stored metadata only.
- Avoid long source copies and generated explanations.
- Do not generate relationship interpretations or RS proof.

Empty state:

- Show `Not Recorded` when no evidence/provenance is stored.

Error state:

- Missing source candidate, missing promotion record, unsafe source path, or broken evidence reference shows a warning.

### Linked Sources Panel

Purpose:

- Show project-local source links such as affected scenes, chapters, notes, materials, and source locators.
- Let the owner open linked source scene/note/material if available.

Data source:

- Approved record source fields and evidence/provenance source locators.
- Project metadata for link validation.

Candidate/canon boundary:

- Linked sources are evidence/context, not canon by default.
- Broken source references must not be replaced from candidates or search results.

No-prose boundary:

- Opening a source displays stored owner-authored/source material only.
- Do not summarize, rewrite, continue, or suggest relationship fixes from source material.

Empty state:

- Show `Not Recorded` when no source links exist.

Error state:

- Broken scene, chapter, note, material, or unsafe reference shows non-destructive warning without host filesystem path leakage.

### Participant Snapshot

Purpose:

- Show approved participant IDs, labels, participant roles, primary/secondary character links, organization/group links, and unresolved participant references.
- Help the owner understand who or what the approved relationship connects without inferring missing roles.

Data source:

- Approved relationship `participant_ids`, `participant_roles`, `primary_character_ids`, `secondary_character_ids`, `linked_organization_ids`, and equivalent approved record fields.
- Future approved memory files for linked participants where implemented.

Candidate/canon boundary:

- Only approved memory/canon participant links may be shown as relationship truth.
- Candidate participant suggestions may be linked only as OMI provenance/audit context.
- Missing participants or roles must remain missing until owner-approved.

No-prose boundary:

- Do not generate participant summaries, relationship arc explanations, emotional-state prose, or dialogue.

Empty state:

- Show `Not Recorded` or `No linked approved participants`.

Error state:

- Broken participant, character, organization/group, object, or source references show warnings and do not auto-repair.

### Linked Story Knowledge Snapshot

Purpose:

- Show linked approved characters, organizations/groups, locations, objects, and related relationships when those records are available.
- Help the owner navigate across approved memory pages.

Data source:

- Approved relationship record link fields.
- Future approved memory files for linked records where implemented.

Candidate/canon boundary:

- Only approved memory/canon links may be shown as story knowledge truth.
- Missing pages/entities must be labeled as future/not implemented or broken links.
- Related relationship links, if represented, must not be used to infer an unapproved relationship graph.

No-prose boundary:

- Do not generate entity summaries, relationship explanations, RS proof, or "why this matters" prose.

Empty state:

- Show `Not Recorded` or `No linked approved story knowledge`.

Error state:

- Broken character/organization/location/object/relationship links show warnings and do not auto-repair.

### Related Plot Thread / Timeline Snapshot

Purpose:

- Show linked approved plot threads and timeline events when approved links exist.
- Help the owner see whether the relationship is tied to approved plot or event records without creating a relationship graph, causal explanation, or fix.

Data source:

- Approved relationship `linked_plot_thread_ids` and `linked_timeline_event_ids`.
- Future approved plot-thread and timeline memory files where implemented.

Candidate/canon boundary:

- Related plot thread and timeline links must come from approved memory/canon records only.
- OMI candidates and promotion records may be linked only as provenance/audit context, not as approved related records.

No-prose boundary:

- Do not generate plot fixes, timeline explanations, relationship arcs, causal explanations, dialogue, or rewrite suggestions.

Empty state:

- Show `Not Recorded` or `No approved plot-thread or timeline links`.

Error state:

- Broken plot-thread or timeline links show non-destructive warnings and do not auto-repair.

### Related Open Questions / Continuity Snapshot

Purpose:

- Show linked approved open questions and continuity/consistency issues when approved links exist.
- Help the owner navigate unresolved relationship-related knowledge without generating answers or fixes.

Data source:

- Approved relationship `linked_open_question_ids` and `linked_continuity_issue_ids`.
- Future approved open-question and continuity/consistency memory files where implemented.

Candidate/canon boundary:

- Related open-question and continuity links must come from approved memory/canon records only.
- Candidate links and promotion records are provenance/audit context only.

No-prose boundary:

- Do not generate answers, fixes, relationship repairs, dialogue rewrites, continuity patches, or explanations.

Empty state:

- Show `Not Recorded` or `No approved open-question or continuity links`.

Error state:

- Broken open-question or continuity links show non-destructive warnings and do not auto-repair.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for OMI relationship candidates by status.
- Help the owner navigate to OMI without blending candidate records into approved truth.

Data source:

- OMI index/candidate metadata where available.

Candidate/canon boundary:

- Candidate backlog may show counts and links only.
- Candidate relationship type, status, participant roles, proposed links, proposed certainty, and proposed descriptions must not be shown as approved truth.

No-prose boundary:

- Do not generate candidate summaries, relationship analyses, explanations, or fixes.

Empty state:

- Show `No pending relationship candidates`.

Error state:

- Corrupt OMI index/candidate metadata shows an OMI warning without blocking approved relationship display.

### Empty State

Purpose:

- Provide safe guidance when no approved relationship records exist.

Data source:

- Approved memory file presence and record count.
- Optional OMI relationship candidate counts.

Candidate/canon boundary:

- Empty approved state remains empty even if candidates exist.
- If candidates exist, link to OMI with candidate labels only.
- Missing `memory/` or `memory/relationships.json` is a valid empty state.

No-prose boundary:

- Empty-state guidance must not ask the AI to invent relationships, generate relationship analysis, fix relationships, draft dialogue, or write missing story material.

Empty state:

- "No approved relationships have been applied yet."

Error state:

- If memory load fails, use Warning State instead of empty state.

### Warning State

Purpose:

- Surface invalid, missing, corrupt, unsafe, unsupported, duplicate, broken-link, participant-conflict, type/status-conflict, cyclic-link, or insufficient-evidence states.

Data source:

- Project validation.
- Memory file validation.
- OMI candidate/promotion metadata validation when candidate counts are shown.

Candidate/canon boundary:

- Warnings are diagnostics, not approved story truth.
- Warnings must not promote, resolve, retitle, reclassify, infer participants, correct roles/status, or repair records.

No-prose boundary:

- Warning copy is factual status text only.
- Do not generate relationship fixes, dialogue suggestions, rewrite suggestions, or explanatory story prose.

Empty state:

- Show "No relationship warnings detected in approved memory metadata" only when validation ran and found no warnings.

Error state:

- Partial validation failure should show partial warnings and preserve read-only page behavior.

### Future Page Link Reference

Purpose:

- Link to related approved pages and future page placeholders.
- Clarify implementation status for OMI, Project Memory / Canon, characters, organizations/groups, locations/settings, objects/items, timeline, plot threads, open questions, continuity/consistency, chapters, scenes, notes, and materials.

Data source:

- Route/page availability metadata.
- Static planning copy.

Candidate/canon boundary:

- Links to approved pages must use approved-memory labels.
- Links to OMI must use candidate/audit labels.
- Future graph visualization must be labeled future-only.

No-prose boundary:

- Navigation only; no generated page summaries, answers, fixes, or relationship analysis.

Empty state:

- Show future/not implemented labels for unavailable pages.

Error state:

- Broken route/page availability state shows a non-blocking navigation warning.

## 6. Candidate / Canon Separation

Approved records:

- Approved relationship records are read from future memory files such as `memory/relationships.json` or an equivalent approved memory store.
- Approved relationship truth exists only after owner approval, promotion record creation, and successful future apply-promotion into approved memory/canon.
- Approved records are project-local and must not leak across projects.
- Approved records are generic story-knowledge relationships unless a later Dramatica-specific approved memory record explicitly says otherwise.

OMI candidates:

- OMI relationship candidates remain in OMI candidates.
- Pending, rejected, archived, duplicate, uncertain, and needs-revision candidates do not appear as approved relationships.
- Approved-but-not-applied candidates do not appear as approved relationships.
- Candidate backlog may show counts and links only.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved relationship memory.
- Source candidate and promotion audit links may be shown as provenance from approved records.
- Promotion records present but no approved memory record must show `Promotion Record Only` or `Not Yet Applied`, not an approved relationship.

Inference restrictions:

- Relationship type, status, participant roles, evidence state, related links, and certainty must not be inferred as truth from candidate output.
- Missing approved fields must remain missing and be displayed honestly.
- No model, extractor, NotebookLM output, source material, raw idea, raw analysis artifact, or relationship graph candidate may directly become approved relationship truth.
- Generic relationship records must not be presented as Dramatica Relationship Story proof.

## 7. First-Version Operations

Allowed first-version operations:

- View approved relationship list.
- View relationship details.
- Filter/search approved relationships locally.
- Open linked source scene/note/material.
- Open linked character, organization, location, object, timeline event, plot-thread, open-question, or continuity/consistency page if available.
- Open related OMI candidate or promotion record as provenance/audit context.
- Show participant snapshot.
- Show linked story-knowledge snapshot.

First-version operations must:

- Be read-only with respect to approved memory/canon.
- Be read-only with respect to OMI records.
- Avoid model/Ollama calls during navigation, list, filter, search, or selection.
- Avoid generated relationship summaries, generated analysis, generated explanations, generated fixes, dialogue suggestions, or rewrite suggestions.
- Avoid any silent mutation of `memory/relationships.json`, `memory/index.json`, or OMI records.
- Avoid any direct apply-promotion action from this page.
- Avoid any relationship graph generation.
- Avoid any Dramatica Relationship Story classification.

Future-only operations:

- Edit approved relationship memory.
- Merge/split approved relationships.
- Archive/restore.
- Mark relationship resolved/changed.
- Apply-promotion.
- Extract relationship candidates.
- Generate relationship graph visualization.
- Suggest relationship fixes.
- Rewrite dialogue or scene to change relationship.
- Contradiction detection.
- Dramatica Relationship Story classification.
- IC/RS structural classification.
- CIPS/dynamics classification.

## 8. Local Search and Filter Planning

First-version search/filter should be local and deterministic over approved records only.

Search/filter fields:

- `display_title`
- `relationship_type`
- `relationship_status`
- `relationship_scope`
- participant IDs
- participant roles
- `tags` if available
- approved description if available
- linked source IDs
- affected scene/chapter IDs
- linked character/organization/location/object/timeline/plot-thread/open-question/continuity IDs
- `source_candidate_ids`
- `promotion_record_ids`

Rules:

- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No generated relationship analysis.
- No extraction during search.
- No contradiction detection during search.
- No Dramatica classification during search.
- Approved-only labels must remain visible in search results.
- Candidate counts/links may be separately filtered by status only if the UI makes them clearly non-canon.
- Search results must not infer relationship status, roles, certainty, or RS meaning.

## 9. Warning and Invalid-State Behavior

The page should warn for these states:

- Missing `memory/`.
- Missing or corrupt `memory/relationships.json`.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Broken participant references.
- Broken character/organization/location/object references.
- Broken scene/note/material references.
- Broken timeline/plot-thread/open-question/continuity references.
- Duplicate relationship IDs.
- Unsafe IDs.
- Relationship type/status conflicts.
- Participant role conflicts.
- Affected source references missing.
- Related relationship links broken/cyclic if represented.
- Promotion records present but no approved memory record.
- OMI relationship candidates exist but no approved relationships yet.
- Related pages/entities not implemented yet.
- Missing or insufficient evidence.
- Corrupt `memory/index.json`.

Warning rules:

- Warnings are non-destructive.
- Warnings must not auto-repair records.
- Warnings must not auto-delete records.
- Warnings must not rewrite identity.
- Warnings must not retitle relationships.
- Warnings must not infer participants.
- Warnings must not correct participant roles.
- Warnings must not correct relationship type or status.
- Warnings must not resolve relationships.
- Warnings must not promote candidates.
- Warnings must not generate fixes, dialogue, summaries, or explanations.
- Warnings must not leak host filesystem paths.
- Warnings should use project-relative identifiers where needed.

## 10. Future API Planning

These routes are future planning only. Do not implement them in WORKSPACE-019. These route groups may be implemented directly or composed from a future project memory/canon summary endpoint.

Route group:

```text
GET /api/projects/{project_id}/memory/relationships
GET /api/projects/{project_id}/memory/relationships/{relationship_id}
GET /api/projects/{project_id}/memory/relationships/{relationship_id}/provenance
GET /api/projects/{project_id}/memory/relationships/health
```

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/relationships.json` or `memory/index.json` on read.
- First-version routes must not apply promotions.
- First-version routes must not generate relationship graphs, relationship analysis, fixes, summaries, dialogue suggestions, or Dramatica classifications.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/relationships`

Purpose:

- List approved relationships for one project.
- Optionally include approved-only counts and lightweight warning metadata.

Request shape:

- Path parameter `project_id`.
- Optional query parameters for local filter/sort/search over approved relationship fields.
- No body.

Response shape:

- Project ID.
- Approved relationship list or compact relationship summaries.
- Approved count.
- Optional warning list.
- Optional candidate backlog counts labeled separately if included.

Validation:

- `project_id` must be a safe single path component.
- Load approved memory store read-only.
- Validate envelope/schema before displaying records.
- Reject unsafe record IDs.
- Validate relationship IDs, participant references, affected source references, and approved link fields where safe.

Path safety:

- Use project path helpers.
- Reject absolute paths, traversal, empty IDs, `"."`, and `".."`.
- Return project-relative source references only.

Candidate/canon boundary:

- Return applied memory/canon records only.
- Do not include candidate bodies as approved records.
- Candidate backlog counts, if included, must be labeled candidate-only.

No-prose boundary:

- Do not generate relationship descriptions, analyses, explanations, summaries, fixes, dialogue suggestions, rewrites, or RS proof.

Expected errors:

- Project not found.
- Missing memory store, treated as empty if project is valid.
- Corrupt memory file.
- Unsupported schema.
- Unsafe ID.
- Duplicate relationship ID.
- Broken index warning.

### `GET /api/projects/{project_id}/memory/relationships/{relationship_id}`

Purpose:

- Load one approved relationship detail.

Request shape:

- Path parameters `project_id` and `relationship_id`.
- No body.

Response shape:

- Approved relationship detail record.
- Approved display fields.
- Warnings for missing linked records, unsupported optional fields, participant conflicts, or type/status conflicts.

Validation:

- `project_id` and `relationship_id` must be safe IDs.
- Record must exist in approved memory store.
- Record type must be supported.
- Participant references and linked approved entity references should be validated where safe.

Path safety:

- No filesystem paths from request values.
- No host-path leakage in errors.

Candidate/canon boundary:

- Candidate and promotion links are IDs/provenance only.
- Do not hydrate missing approved fields from OMI candidates.
- Do not infer participant roles, relationship status, certainty, or Dramatica RS meaning.

No-prose boundary:

- Return stored fields only.
- No generated relationship analysis, fix, rewrite, dialogue suggestion, bonding scene, conflict resolution, relationship arc explanation, or Dramatica proof.

Expected errors:

- Project not found.
- Approved memory missing.
- Record not found.
- Duplicate record ID.
- Unsafe ID.
- Unsupported schema.
- Broken participant or linked-record references.

### `GET /api/projects/{project_id}/memory/relationships/{relationship_id}/provenance`

Purpose:

- Return evidence/provenance metadata for one approved relationship.
- Support audit links to source candidate IDs and promotion record IDs.

Request shape:

- Path parameters `project_id` and `relationship_id`.
- No body.

Response shape:

- Evidence IDs.
- Provenance metadata.
- First/latest source locators if stored.
- Source candidate IDs.
- Promotion record IDs.
- Missing/broken reference warnings.

Validation:

- Same ID safety as relationship detail.
- Validate evidence/provenance shape.
- Treat missing candidate/promotion links as warnings.

Path safety:

- Source paths must be project-relative.
- Unsafe paths must be redacted and warned.

Candidate/canon boundary:

- Candidate and promotion data is audit context only.
- Provenance endpoint must not imply candidate output is approved truth.

No-prose boundary:

- Return stored evidence/provenance metadata only.
- Do not generate summaries, explanations, relationship analysis, fixes, or Dramatica classifications.

Expected errors:

- Project not found.
- Record not found.
- Corrupt provenance metadata.
- Broken source candidate reference.
- Broken promotion record reference.
- Unsafe source locator.

### `GET /api/projects/{project_id}/memory/relationships/health`

Purpose:

- Validate relationship memory health without mutation.
- Report missing/corrupt/unsupported/duplicate/broken-link/conflict/cyclic-link states.

Request shape:

- Path parameter `project_id`.
- Optional query for validation scope if later needed.
- No body.

Response shape:

- Health status.
- Warning list.
- Approved record count.
- Candidate backlog count if included, labeled separately.
- No repair actions.

Validation:

- Validate project ID.
- Validate memory envelope, IDs, schema version, duplicate IDs, participant links, linked sources, linked approved entities, related relationship links, type/status conflicts, participant role conflicts, and evidence presence.

Path safety:

- Do not expose host filesystem paths.
- Use project-relative IDs and safe labels.

Candidate/canon boundary:

- Health warnings are diagnostics, not approved story truth.
- Candidate counts remain candidate-only.
- Health must not infer approved truth from OMI records or promotion records.

No-prose boundary:

- Warnings are factual status messages only.
- Do not propose fixes, rewrites, relationship repairs, dialogue, or story prose.

Expected errors:

- Project not found.
- Corrupt memory file.
- Corrupt memory index.
- Unsupported schema.
- Unsafe ID.
- Partial validation failure.

## 11. Future Frontend Planning

These components are future planning only. Do not implement UI in WORKSPACE-019.

Future components:

- `ApprovedRelationshipsPage`
- `RelationshipsBoundaryBanner`
- `ApprovedRelationshipList`
- `ApprovedRelationshipListItem`
- `RelationshipDetailPanel`
- `RelationshipEvidencePanel`
- `RelationshipSourceLinksPanel`
- `RelationshipParticipantSnapshot`
- `RelationshipLinkedStoryKnowledgeSnapshot`
- `RelationshipRelatedPlotTimelineSnapshot`
- `RelationshipRelatedQuestionsContinuitySnapshot`
- `RelationshipCandidateBacklogSnapshot`
- `RelationshipSearchFilterControls`
- `RelationshipWarningsPanel`
- `RelationshipEmptyState`
- `RelationshipFuturePagesReference`

Component rules:

- No AI writing buttons.
- No generated relationship analysis button.
- No generated graph button in the first version.
- No controls named or behaving like `answer this relationship`, `fix relationship`, `rewrite dialogue`, `generate bonding scene`, `resolve conflict`, `explain relationship arc`, `prove RS`, or `classify Relationship Story`.
- No controls that write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Search/filter controls must be local and deterministic.
- Candidate backlog controls must route to OMI and remain labeled as candidate/audit state.
- Detail panels must display stored approved fields only.
- Warning panels must be non-destructive.
- Missing fields must use `Unknown`, `Not approved yet`, or `Not recorded`.
- Generic relationship records must use or link to `Not Dramatica Relationship Story Proof` boundary copy.

## 12. Future Tests

Future tests should cover:

- No memory directory / no approved records.
- Load approved relationship records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt memory file warning.
- Duplicate relationship IDs warning.
- Unsafe IDs rejected.
- Broken participant/source/entity links warning.
- Relationship type/status conflicts warning.
- Participant role conflicts warning.
- Related relationship broken/cyclic warning if represented.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- No AI prose-generation controls.
- No generated relationship analysis/fixes/rewrites/summaries/explanations.
- No generated dialogue suggestions or relationship-fix suggestions.
- No relationship graph generation in the first version.
- No Dramatica RS/IC/RS/CIPS/dynamics claims.
- Relationship records are labeled as generic story knowledge, not Relationship Story proof.
- No JSONL/training writes.

## 13. Page Relationships

Relationship to Project Memory / Canon:

- The Approved Relationships page is an approved-memory category page.
- It reads approved records only and should be reachable from the future Project Memory / Canon category cards.

Relationship to OMI:

- OMI is the review workspace for relationship candidates.
- The page may link to OMI candidate filters/counts but must not display candidates as approved relationships.

Relationship to Approved Characters:

- Approved character records may link to approved relationships only when those links exist on applied character memory records or approved relationship records.
- This page may link back to approved characters only when approved relationship records explicitly carry character IDs.
- Character-pair links are generic story-knowledge links, not Dramatica Relationship Story proof.

Relationship to Approved Locations / Settings, Objects, and Organizations:

- Linked entities are approved-memory navigation only.
- Missing future pages should show `Related Page Not Implemented`.

Relationship to Approved Timeline and Plot Threads:

- Approved timeline events and plot threads may link to relationships only when approved records explicitly carry relationship IDs.
- This page may link back only from approved relationship link fields.

Relationship to Approved Open Questions and Continuity / Consistency:

- Approved open questions and continuity/consistency records may link to relationships only when approved records explicitly carry relationship IDs.
- This page may link back only from approved relationship link fields.

Relationship to chapters, scenes, notes, and materials:

- Linked source pages show owner-authored/source material only.
- Source links are evidence/context, not approved relationship truth by themselves.

Relationship to Dramatica:

- This page is general relationship story-knowledge support.
- Dramatica-specific Relationship Story classification is deferred.

## 14. Deferred Decisions

Deferred to later tasks:

- Exact runtime schema for `relationship_memory_record` versus a richer future participant/role relation object.
- Whether first implementation reads directly from `memory/relationships.json`, a memory summary endpoint, or both.
- Exact allowed values for `relationship_type`, `relationship_status`, `relationship_scope`, and `participant_roles`.
- Exact memory envelope version and migration behavior.
- Exact source/evidence locator format for scene, chapter, note, material, and memory-record links.
- Whether relationship participants use `subject_record_id` / `object_record_id`, `participant_ids`, or both.
- Whether related relationship links use `related_relationship_ids` or a separate relation object.
- Exact OMI filter for relationship candidates.
- Exact apply-promotion behavior, rollback, record supersession, and relationship duplicate detection mechanics.
- Whether and when owner-controlled edit, merge/split, archive/restore, or resolved/changed workflows are added.
- Whether future visualization uses a list, table, relationship graph, timeline overlay, or side-by-side evidence view.
- Whether future Dramatica-specific relationship claims live in a separate approved memory category, separate advanced page, or future storyform bridge.
- Any future Dramatica Relationship Story taxonomy, IC/RS structure, CIPS, or dynamics classification.

## 15. Non-Goals for WORKSPACE-019

WORKSPACE-019 does not implement:

- Backend runtime code.
- Frontend runtime code.
- Tests.
- Package/dependency changes.
- Dataset files.
- JSONL records.
- `training/data/dataset_manifest.json` updates.
- Training or fine-tuning.
- Ollama/live model calls.
- Package installs.
- Approved Relationships page UI.
- Backend memory/canon routes.
- Apply-promotion.
- Relationship extraction.
- Relationship graph visualization.
- Contradiction detection.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- Staging, commits, or pushes.
