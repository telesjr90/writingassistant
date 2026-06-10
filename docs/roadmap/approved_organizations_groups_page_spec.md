# WORKSPACE-020: Approved Organizations / Groups Page Spec

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
- WORKSPACE-019: `docs/roadmap/approved_relationships_page_spec.md`
- WORKSPACE-020: `docs/roadmap/approved_organizations_groups_page_spec.md`
- WORKSPACE-021: `docs/roadmap/approved_objects_items_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Organizations / Groups page should be the future project-local destination for owner-approved organization and group memory/canon records. It must show only organization/group records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, needs-revision, and approved-but-not-applied organization/group candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

This page is not a Dramatica structural page. Generic organizations, groups, factions, teams, institutions, families, governments, companies, or informal groups are not throughline proof and must not be presented as protagonist/antagonist function, Influence Character status, Relationship Story proof, CIPS, dynamics, or Dramatica storyform truth.

The page should:

- Show owner-approved `organization_memory_record` or `group_memory_record` entries for the selected project.
- Read approved organization/group truth only from future memory files such as `memory/organizations.json`, `memory/groups.json`, or an equivalent approved memory store.
- Clearly distinguish approved organization/group truth from OMI organization/group candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved organization/group back to source evidence, provenance, source candidate IDs, promotion record IDs, and approval metadata where available.
- Show unresolved, ambiguous, partial, or missing fields honestly as `Unknown`, `Not approved yet`, or `Not recorded`.
- Show an empty state when no approved organization/group records exist.
- Link to the OMI Ideas / Candidates page for pending organization/group candidates.
- Link to related characters, relationships, locations, objects/items, timeline events, plot threads, open questions, continuity/consistency issues, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic organization extraction.
- Avoid organization graph generation.
- Avoid contradiction detection.
- Avoid apply-promotion behavior.
- Avoid generated organization analysis, generated summaries, rewrite suggestions, scene suggestions, faction-fix suggestions, and any controls that write or rewrite story prose.
- Avoid Dramatica-specific structural claims unless later approved and evidence-backed by a separate advanced-layer task.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Organization / Group Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for organization/group candidates.
- Source material is not approved organization/group memory/canon by default.
- A mention of a faction, team, company, government, family, institution, informal group, alliance, opposition, membership, leadership, hierarchy, or group purpose is not an approved organization/group record by itself.
- Source material must not be copied into approved organization/group memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions an organization/group is not an approved organization/group record.

### OMI Organization / Group Candidates

Definition:

- Structured `organization_candidate`, `group_candidate`, or future equivalent organization/group candidate records that have not been applied to approved memory/canon.

Rules:

- Organization/group candidates are not canon.
- Organization/group candidates must not appear in the approved organization/group list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate organization type, status, hierarchy, membership, leadership, relationships, evidence state, related links, and certainty must not be inferred as approved truth.
- Organization/group candidates are generic story-knowledge candidates. They are not Dramatica structural proof.

### Approved-but-Not-Applied Candidates

Definition:

- Organization/group candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved organization/group memory/canon.
- Approved-but-not-applied candidates must not appear in the approved organization/group list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved organizations/groups.
- Promotion records may be linked as provenance from an approved organization/group record that a future apply-promotion step actually created.
- Promotion records present without an approved memory record must show an audit-only warning or candidate backlog state, not an approved organization/group.

### Applied Organization / Group Memory Records

Definition:

- Durable owner-approved `organization_memory_record` or `group_memory_record` entries written to the future approved memory store by a future apply-promotion step.

Rules:

- Applied organization/group records are the only records allowed in the approved organization/group list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, approval metadata, member/leader links, related entity links, and revision metadata where available.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/organizations.json`, `memory/groups.json`, or equivalent records.

### Future Dramatica Structural Claims

Definition:

- Future Dramatica storyform-specific classifications such as throughline role, protagonist/antagonist function, Influence Character status, Relationship Story proof, CIPS, dynamics, or other storyform truth.

Rules:

- Dramatica-specific organization/group classification is deferred.
- The first version of this page must not display any Dramatica-specific organization/group diagnosis.
- Generic group labels must not be treated as Dramatica proof.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved organization/group display.
- The first implementation of this page must not call a model.

Required labels:

| Label | Use |
| --- | --- |
| `Approved Organization / Group` | Marks each applied approved memory/canon record. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Candidate` | Marks OMI organization/group candidates outside the approved list. |
| `Pending Candidate` | Marks pending OMI organization/group candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied organization/group candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI organization/group candidates. |
| `Needs Revision` | Marks OMI organization/group candidates needing revision. |
| `Archived Candidate` | Marks archived OMI organization/group candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied memory record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved organization/group fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Ambiguous Organization / Group` | Marks organizations/groups whose approved record intentionally preserves ambiguity. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Not Dramatica Structural Proof` | Marks the page and relevant records as generic story knowledge, not Dramatica proof. |
| `Future / Not Implemented` | Marks editing, merge/split, graph visualization, extraction, contradiction detection, apply-promotion, and Dramatica structural classification. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved organization/group list.
- Counts must be separated by status.
- Approved organization/group counts must come from applied memory/canon records only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Organization / Group`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, needs-revision, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved organization/group list.
- Organization/group records must carry an explicit non-Dramatica boundary wherever Dramatica confusion is likely.

## 3. Approved Organization / Group Display Model

Future approved organization/group records may evolve, but the first-version page should plan to display these fields when stored:

| Field | Display rule |
| --- | --- |
| `organization_id` | Stable approved record ID; reject unsafe IDs and show duplicate warnings. |
| `display_title` | Owner-approved display label; do not generate or retitle. |
| `organization_type` | Stored type such as faction, family, team, institution, company, government, alliance, or group; show `Unknown` when missing. |
| `organization_status` | Stored status such as active, inactive, destroyed, hidden, dissolved, disputed, or unknown; do not infer from candidates. |
| `organization_scope` | Stored scope such as local, regional, global, informal, formal, scene-local, or unknown. |
| `short_owner_approved_description` | Stored owner-approved description only; no generated summaries. |
| `alias_names` | Stored aliases or alternate group names. |
| `member_character_ids` | Stored approved member character links; broken links warn only. |
| `leader_character_ids` | Stored approved leader character links; broken links warn only. |
| `related_character_ids` | Stored approved character links that are not necessarily members/leaders. |
| `parent_organization_ids` | Stored parent/supergroup links; cycles warn only. |
| `child_organization_ids` | Stored child/subgroup links; cycles warn only. |
| `allied_organization_ids` | Stored alliance links; broken/cyclic links warn only. |
| `opposed_organization_ids` | Stored opposition/rival links; broken/cyclic links warn only. |
| `linked_relationship_ids` | Stored approved relationship links. |
| `linked_location_ids` | Stored approved location/setting links. |
| `linked_object_ids` | Stored approved object/item links. |
| `linked_timeline_event_ids` | Stored approved timeline event links. |
| `linked_plot_thread_ids` | Stored approved plot-thread links. |
| `linked_open_question_ids` | Stored approved open-question links. |
| `linked_continuity_issue_ids` | Stored approved continuity/consistency links. |
| `affected_scene_ids` | Stored affected source scene links. |
| `affected_chapter_ids` | Stored affected source chapter links. |
| `linked_note_ids` | Stored note links. |
| `linked_material_ids` | Stored material links. |
| `first_seen_source` | Stored first source locator if approved. |
| `latest_seen_source` | Stored latest source locator if approved. |
| `evidence/provenance summary` | Stored evidence/provenance metadata only. |
| `confidence/certainty label if stored` | Stored confidence/certainty at approval, not objective truth. |
| `owner_notes` | Stored owner notes only. |
| `created_at` | Stored creation timestamp. |
| `updated_at` | Stored update timestamp. |
| `approved_at` | Stored approval timestamp. |
| `approved_by` | Stored owner/reviewer identifier. |
| `source_candidate_ids` | Candidate IDs that led to the approved record; provenance only. |
| `promotion_record_ids` | Promotion audit record IDs; provenance only. |
| `revision_history` | Stored revision metadata. |
| `supersedes_record_ids` | Older approved records replaced by this one. |
| `superseded_by_record_id` | Newer approved record replacing this one. |
| `tags` | Stored approved tags. |
| `notes` | Stored notes or implementation notes. |

Display rules:

- Unapproved candidates must not appear as truth.
- Generated organization analysis, generated summaries, rewrite suggestions, scene suggestions, and faction-fix suggestions are prohibited.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- An organization/group may remain ambiguous, unresolved, informal, partly unknown, or insufficiently evidenced without implying an error.
- Owner-approved descriptions and owner notes may be displayed only as stored approved fields.
- Organization/group records must not be presented as Dramatica throughline, antagonist/protagonist, IC, RS, CIPS, or dynamics proof.
- If a future storage schema represents groups as `organization_type` values inside `memory/organizations.json`, the page may display them in this page without creating a separate `memory/groups.json` requirement.

## 4. First-Version Page Sections

Each section must define purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

### Page Header

Purpose:

- Identify the active project and Approved Organizations / Groups area.
- Show approved organization/group count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved organization/group records from `memory/organizations.json`, `memory/groups.json`, or equivalent approved memory store if present.

Candidate/canon boundary:

- Header approved count must come from applied memory/canon records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, organization summaries, explanations, fixes, scenes, or rewrite suggestions.

Empty state:

- Show that no approved organizations/groups exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Organizations / Groups Boundary Banner

Purpose:

- Explain that the page shows approved memory/canon organization/group records only.
- Point pending organization/group candidates to OMI.
- State that the page is not a prose-writing, faction-fix, graph-generation, or Dramatica structural proof surface.

Data source:

- Static page copy.
- Optional lightweight OMI organization/group candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not canon.
- State that approved organizations/groups require future apply-promotion into memory/canon.
- State that generic organization/group records are not Dramatica structural proof.

No-prose boundary:

- Prohibit generated organization analysis, generated summaries, scene suggestions, rewrite suggestions, faction fixes, and prose-patching controls.

Empty state:

- Banner remains visible even when no records exist.

Error state:

- Banner remains visible when approved-memory load partially fails.

### Approved Organization List

Purpose:

- List approved organization/group records for the selected project.
- Support local filter/search over approved organization/group metadata.

Data source:

- Applied `organization_memory_record` or `group_memory_record` entries.
- Optional derived `memory/index.json` for navigation, with category files remaining source of truth.

Candidate/canon boundary:

- Exclude all OMI candidates, promotion records without applied memory, and source-only material.
- Candidate backlog may be represented only as separate counts/links.
- Each row must use `Approved Organization / Group`.

No-prose boundary:

- Do not generate organization summaries, explanations, fixes, scene suggestions, or faction arcs.
- List item descriptions must come from approved stored fields only.

Empty state:

- "No approved organizations/groups yet" with link to OMI candidate review if candidate counts exist.

Error state:

- Corrupt memory file, unsupported schema, duplicate IDs, unsafe IDs, invalid records, membership/leadership conflicts, hierarchy cycles, or type/status conflicts should show warnings and omit unsafe/invalid records from normal detail display.

### Organization Detail Panel

Purpose:

- Show the selected approved organization's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, affected sources, members/leaders, hierarchy links, linked story knowledge, approval metadata, revision history, and notes.

Data source:

- Selected approved organization/group memory record.

Candidate/canon boundary:

- Detail panel must not hydrate missing fields from OMI candidates.
- Source candidate and promotion links are provenance only.
- Generic organization/group detail must not imply Dramatica structural classification.

No-prose boundary:

- Do not generate organization analysis, faction arc explanation, scene rewrite, dialogue, group conflict, group fix, or Dramatica proof.

Empty state:

- Prompt the owner to select an approved organization/group.

Error state:

- Invalid selected ID, missing record, unsafe ID, unsupported schema, membership/leadership conflicts, hierarchy cycles, type/status conflicts, or broken links show non-destructive warnings.

### Evidence / Provenance Panel

Purpose:

- Show the evidence/provenance trail behind the approved organization/group.
- Identify first/latest sources, evidence IDs, source candidate IDs, promotion record IDs, approval data, and confidence/certainty labels where stored.

Data source:

- Approved memory record evidence/provenance fields.
- Linked OMI candidate/promotion metadata for audit links only.

Candidate/canon boundary:

- Candidate/promotion data is provenance, not approved truth.
- If evidence is missing or insufficient, show `Evidence Required` or `Insufficient Evidence`.
- Provenance links must not imply candidate organization/group analysis is approved truth.

No-prose boundary:

- Evidence summaries must be stored metadata only.
- Avoid long source copies and generated explanations.
- Do not generate organization interpretations or Dramatica proof.

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
- Do not summarize, rewrite, continue, or suggest organization/faction fixes from source material.

Empty state:

- Show `Not Recorded` when no source links exist.

Error state:

- Broken scene, chapter, note, material, or unsafe reference shows non-destructive warning without host filesystem path leakage.

### Members / Leadership Snapshot

Purpose:

- Show approved member, leader, and related character links.
- Help the owner see stored membership/leadership state without inferring missing roles.

Data source:

- Approved organization/group `member_character_ids`, `leader_character_ids`, `related_character_ids`, and equivalent approved record fields.
- Future approved character memory files where implemented.

Candidate/canon boundary:

- Only approved memory/canon character links may be shown as organization/group truth.
- Candidate member/leader suggestions may be linked only as OMI provenance/audit context.
- Missing members, leaders, or roles must remain missing until owner-approved.

No-prose boundary:

- Do not generate member bios, leadership explanations, faction dynamics, dialogue, or scenes.

Empty state:

- Show `Not Recorded` or `No linked approved members/leaders`.

Error state:

- Broken member, leader, character, or source references show warnings and do not auto-repair.

### Organization Hierarchy Snapshot

Purpose:

- Show approved parent, child, allied, and opposed organization/group links.
- Surface hierarchy cycles or broken organization/group links as warnings.

Data source:

- Approved `parent_organization_ids`, `child_organization_ids`, `allied_organization_ids`, `opposed_organization_ids`, and equivalent approved record fields.
- Future approved organization/group memory files where implemented.

Candidate/canon boundary:

- Only approved memory/canon organization/group links may be shown as hierarchy/alliance/opposition truth.
- Candidate hierarchy suggestions may be linked only as provenance/audit context.
- The page must not infer hierarchy from names, source text, or candidate output.

No-prose boundary:

- Do not generate organization graphs, faction histories, alliance explanations, conflict arcs, fixes, or scenes.

Empty state:

- Show `Not Recorded` or `No approved hierarchy/alliance links`.

Error state:

- Broken parent/child/allied/opposed links and hierarchy cycles show non-destructive warnings and do not auto-repair.

### Linked Story Knowledge Snapshot

Purpose:

- Show linked approved characters, relationships, locations, objects/items, and related organizations/groups when those records are available.
- Help the owner navigate across approved memory pages.

Data source:

- Approved organization/group record link fields.
- Future approved memory files for linked records where implemented.

Candidate/canon boundary:

- Only approved memory/canon links may be shown as story knowledge truth.
- Missing pages/entities must be labeled as future/not implemented or broken links.
- Related organization/group links must not be used to infer an unapproved organization graph.

No-prose boundary:

- Do not generate entity summaries, organization explanations, faction arcs, or Dramatica proof.

Empty state:

- Show `Not Recorded` or `No linked approved story knowledge`.

Error state:

- Broken character/relationship/location/object/organization links show warnings and do not auto-repair.

### Related Relationship / Plot / Timeline Snapshot

Purpose:

- Show linked approved relationships, plot threads, and timeline events when approved links exist.
- Help the owner see whether the organization/group is tied to approved relationship, plot, or event records without creating a graph, causal explanation, or fix.

Data source:

- Approved organization/group `linked_relationship_ids`, `linked_plot_thread_ids`, and `linked_timeline_event_ids`.
- Future approved relationship, plot-thread, and timeline memory files where implemented.

Candidate/canon boundary:

- Related relationship, plot thread, and timeline links must come from approved memory/canon records only.
- OMI candidates and promotion records may be linked only as provenance/audit context, not as approved related records.

No-prose boundary:

- Do not generate plot fixes, timeline explanations, organization arcs, causal explanations, dialogue, or rewrite suggestions.

Empty state:

- Show `Not Recorded` or `No approved relationship, plot-thread, or timeline links`.

Error state:

- Broken relationship, plot-thread, or timeline links show non-destructive warnings and do not auto-repair.

### Related Open Questions / Continuity Snapshot

Purpose:

- Show linked approved open questions and continuity/consistency issues when approved links exist.
- Help the owner navigate unresolved organization/group-related knowledge without generating answers or fixes.

Data source:

- Approved organization/group `linked_open_question_ids` and `linked_continuity_issue_ids`.
- Future approved open-question and continuity/consistency memory files where implemented.

Candidate/canon boundary:

- Related open-question and continuity links must come from approved memory/canon records only.
- Candidate links and promotion records are provenance/audit context only.

No-prose boundary:

- Do not generate answers, fixes, organization repairs, hierarchy repairs, dialogue rewrites, continuity patches, or explanations.

Empty state:

- Show `Not Recorded` or `No approved open-question or continuity links`.

Error state:

- Broken open-question or continuity links show non-destructive warnings and do not auto-repair.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for OMI organization/group candidates by status.
- Help the owner navigate to OMI without blending candidate records into approved truth.

Data source:

- OMI index/candidate metadata where available.

Candidate/canon boundary:

- Candidate backlog may show counts and links only.
- Candidate organization type, status, hierarchy, membership, leadership, proposed links, proposed certainty, and proposed descriptions must not be shown as approved truth.

No-prose boundary:

- Do not generate candidate summaries, organization analyses, explanations, or fixes.

Empty state:

- Show `No pending organization/group candidates`.

Error state:

- Corrupt OMI index/candidate metadata shows an OMI warning without blocking approved organization/group display.

### Empty State

Purpose:

- Provide safe guidance when no approved organization/group records exist.

Data source:

- Approved memory file presence and record count.
- Optional OMI organization/group candidate counts.

Candidate/canon boundary:

- Empty approved state remains empty even if candidates exist.
- If candidates exist, link to OMI with candidate labels only.
- Missing `memory/`, `memory/organizations.json`, or `memory/groups.json` is a valid empty state.

No-prose boundary:

- Empty-state guidance must not ask the AI to invent organizations, generate organization analysis, fix factions, draft dialogue, or write missing story material.

Empty state:

- "No approved organizations/groups have been applied yet."

Error state:

- If memory load fails, use Warning State instead of empty state.

### Warning State

Purpose:

- Surface invalid, missing, corrupt, unsafe, unsupported, duplicate, broken-link, membership-conflict, leadership-conflict, type/status-conflict, hierarchy-cycle, related-link-cycle, or insufficient-evidence states.

Data source:

- Project validation.
- Memory file validation.
- OMI candidate/promotion metadata validation when candidate counts are shown.

Candidate/canon boundary:

- Warnings are diagnostics, not approved story truth.
- Warnings must not promote, resolve, retitle, reclassify, infer members, infer leaders, correct roles/status, repair hierarchy, or repair records.

No-prose boundary:

- Warning copy is factual status text only.
- Do not generate organization fixes, faction fixes, scene suggestions, dialogue suggestions, rewrite suggestions, or explanatory story prose.

Empty state:

- Show "No organization/group warnings detected in approved memory metadata" only when validation ran and found no warnings.

Error state:

- Partial validation failure should show partial warnings and preserve read-only page behavior.

### Future Page Link Reference

Purpose:

- Link to related approved pages and future page placeholders.
- Clarify implementation status for OMI, Project Memory / Canon, characters, relationships, locations/settings, objects/items, timeline, plot threads, open questions, continuity/consistency, chapters, scenes, notes, and materials.

Data source:

- Route/page availability metadata.
- Static planning copy.

Candidate/canon boundary:

- Links to approved pages must use approved-memory labels.
- Links to OMI must use candidate/audit labels.
- Future graph visualization must be labeled future-only.

No-prose boundary:

- Navigation only; no generated page summaries, answers, fixes, organization analysis, faction arcs, or hierarchy explanations.

Empty state:

- Show future/not implemented labels for unavailable pages.

Error state:

- Broken route/page availability state shows a non-blocking navigation warning.

## 5. Candidate / Canon Separation

Approved records:

- Approved organization/group records are read from future memory files such as `memory/organizations.json`, `memory/groups.json`, or an equivalent approved memory store.
- Approved organization/group truth exists only after owner approval, promotion record creation, and successful future apply-promotion into approved memory/canon.
- Approved records are project-local and must not leak across projects.
- Approved records are generic story-knowledge records unless a later Dramatica-specific approved memory record explicitly says otherwise.

OMI candidates:

- OMI organization/group candidates remain in OMI candidates.
- Pending, rejected, archived, duplicate, uncertain, and needs-revision candidates do not appear as approved organizations/groups.
- Approved-but-not-applied candidates do not appear as approved organizations/groups.
- Candidate backlog may show counts and links only.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved organization/group memory.
- Source candidate and promotion audit links may be shown as provenance from approved records.
- Promotion records present but no approved memory record must show `Promotion Record Only` or `Not Yet Applied`, not an approved organization/group.

Inference restrictions:

- Organization type, status, hierarchy, membership, leadership, relationships, evidence state, related links, and certainty must not be inferred as truth from candidate output.
- Missing approved fields must remain missing and be displayed honestly.
- No model, extractor, NotebookLM output, source material, raw idea, raw analysis artifact, or organization graph candidate may directly become approved organization/group truth.
- Organization/group records are not Dramatica structural claims unless a later Dramatica-specific approved memory record explicitly says so.

## 6. First-Version Operations

Allowed first-version operations:

- View approved organization/group list.
- View organization/group details.
- Filter/search approved organizations/groups locally.
- Open linked source scene/note/material.
- Open linked character, relationship, location, object/item, timeline event, plot-thread, open-question, or continuity/consistency page if available.
- Open related OMI candidate or promotion record as provenance/audit context.
- Show members/leadership snapshot.
- Show hierarchy snapshot.
- Show linked story-knowledge snapshot.

First-version operations must:

- Be read-only with respect to approved memory/canon.
- Be read-only with respect to OMI records.
- Avoid model/Ollama calls during navigation, list, filter, search, or selection.
- Avoid generated organization summaries, generated analysis, generated explanations, generated fixes, scene suggestions, dialogue suggestions, faction arcs, or rewrite suggestions.
- Avoid any silent mutation of `memory/organizations.json`, `memory/groups.json`, `memory/index.json`, or OMI records.
- Avoid any direct apply-promotion action from this page.
- Avoid any organization graph generation.
- Avoid any Dramatica structural role classification.

Future-only operations:

- Edit approved organization/group memory.
- Merge/split approved organizations/groups.
- Archive/restore.
- Mark organization/group resolved/changed.
- Apply-promotion.
- Extract organization/group candidates.
- Generate organization graph visualization.
- Suggest organization/faction fixes.
- Rewrite dialogue or scene to alter group dynamics.
- Contradiction detection.
- Dramatica structural role classification.
- Protagonist/antagonist/IC/RS/CIPS/dynamics classification.

## 7. Local Search and Filter Planning

First-version search/filter should be local and deterministic over approved records only.

Search/filter fields:

- `display_title`
- `organization_type`
- `organization_status`
- `organization_scope`
- `alias_names`
- `member_character_ids`
- `leader_character_ids`
- `related_character_ids`
- `parent_organization_ids`
- `child_organization_ids`
- `tags` if available
- approved description if available
- linked source IDs
- affected scene/chapter IDs
- linked relationship/location/object/timeline/plot-thread/open-question/continuity IDs
- `source_candidate_ids`
- `promotion_record_ids`

Rules:

- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No generated organization analysis.
- No extraction during search.
- No contradiction detection during search.
- No Dramatica classification during search.
- Approved-only labels must remain visible in search results.
- Candidate counts/links may be separately filtered by status only if the UI makes them clearly non-canon.
- Search results must not infer organization type, status, membership, leadership, hierarchy, certainty, or Dramatica meaning.

## 8. Warning and Invalid-State Behavior

The page should warn for these states:

- Missing `memory/`.
- Missing or corrupt `memory/organizations.json`.
- Missing or corrupt `memory/groups.json` if used.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Broken member/leader/character references.
- Broken parent/child organization references.
- Parent/child hierarchy cycles.
- Broken ally/opponent organization references.
- Broken relationship/location/object references.
- Broken scene/note/material references.
- Broken timeline/plot-thread/open-question/continuity references.
- Duplicate organization IDs.
- Unsafe IDs.
- Organization type/status conflicts.
- Membership/leadership conflicts.
- Affected source references missing.
- Related organization links broken/cyclic if represented.
- Promotion records present but no approved memory record.
- OMI organization/group candidates exist but no approved organizations/groups yet.
- Related pages/entities not implemented yet.
- Missing or insufficient evidence.
- Corrupt `memory/index.json`.

Warning rules:

- Warnings are non-destructive.
- Warnings must not auto-repair records.
- Warnings must not auto-delete records.
- Warnings must not rewrite identity.
- Warnings must not retitle organizations/groups.
- Warnings must not infer members.
- Warnings must not infer leaders.
- Warnings must not correct roles/status.
- Warnings must not correct organization type or status.
- Warnings must not resolve hierarchy.
- Warnings must not promote candidates.
- Warnings must not generate fixes, dialogue, summaries, explanations, scene suggestions, faction arcs, or rewrite suggestions.
- Warnings must not leak host filesystem paths.
- Warnings should use project-relative identifiers where needed.

## 9. Future API Planning

These routes are future planning only. Do not implement them in WORKSPACE-020. These route groups may be implemented directly or composed from a future project memory/canon summary endpoint.

Route group:

```text
GET /api/projects/{project_id}/memory/organizations
GET /api/projects/{project_id}/memory/organizations/{organization_id}
GET /api/projects/{project_id}/memory/organizations/{organization_id}/provenance
GET /api/projects/{project_id}/memory/organizations/health
```

Groups may be represented as `organization_type` values inside `memory/organizations.json`, or by parallel group endpoints in a later decision.

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/organizations.json`, `memory/groups.json`, or `memory/index.json` on read.
- First-version routes must not apply promotions.
- First-version routes must not generate organization graphs, organization analysis, faction fixes, summaries, scene suggestions, dialogue suggestions, or Dramatica classifications.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/organizations`

Purpose:

- List approved organizations/groups for one project.
- Optionally include approved-only counts and lightweight warning metadata.

Request shape:

- Path parameter `project_id`.
- Optional query parameters for local filter/sort/search over approved organization/group fields.
- No body.

Response shape:

- Project ID.
- Approved organization/group list or compact organization/group summaries.
- Approved count.
- Optional warning list.
- Optional candidate backlog counts labeled separately if included.

Validation:

- `project_id` must be a safe single path component.
- Load approved memory store read-only.
- Validate envelope/schema before displaying records.
- Reject unsafe record IDs.
- Validate organization IDs, member/leader references, hierarchy/alliance/opposition links, affected source references, and approved link fields where safe.

Path safety:

- Use project path helpers.
- Reject absolute paths, traversal, empty IDs, `"."`, and `".."`.
- Return project-relative source references only.

Candidate/canon boundary:

- Return applied memory/canon records only.
- Do not include candidate bodies as approved records.
- Candidate backlog counts, if included, must be labeled candidate-only.

No-prose boundary:

- Do not generate organization descriptions, analyses, explanations, summaries, fixes, scene suggestions, rewrites, faction arcs, or Dramatica proof.

Expected errors:

- Project not found.
- Missing memory store, treated as empty if project is valid.
- Corrupt memory file.
- Unsupported schema.
- Unsafe ID.
- Duplicate organization ID.
- Broken index warning.

### `GET /api/projects/{project_id}/memory/organizations/{organization_id}`

Purpose:

- Load one approved organization/group detail.

Request shape:

- Path parameters `project_id` and `organization_id`.
- No body.

Response shape:

- Approved organization/group detail record.
- Approved display fields.
- Warnings for missing linked records, unsupported optional fields, hierarchy cycles, membership/leadership conflicts, or type/status conflicts.

Validation:

- `project_id` and `organization_id` must be safe IDs.
- Record must exist in approved memory store.
- Record type must be supported.
- Member/leader references, organization links, and linked approved entity references should be validated where safe.

Path safety:

- No filesystem paths from request values.
- No host-path leakage in errors.

Candidate/canon boundary:

- Candidate and promotion links are IDs/provenance only.
- Do not hydrate missing approved fields from OMI candidates.
- Do not infer members, leaders, hierarchy, organization status, certainty, or Dramatica meaning.

No-prose boundary:

- Return stored fields only.
- No generated organization analysis, fix, rewrite, dialogue suggestion, faction scene, hierarchy explanation, group conflict resolution, organization arc explanation, or Dramatica proof.

Expected errors:

- Project not found.
- Approved memory missing.
- Record not found.
- Duplicate record ID.
- Unsafe ID.
- Unsupported schema.
- Broken member/leader/hierarchy or linked-record references.

### `GET /api/projects/{project_id}/memory/organizations/{organization_id}/provenance`

Purpose:

- Return evidence/provenance metadata for one approved organization/group.
- Support audit links to source candidate IDs and promotion record IDs.

Request shape:

- Path parameters `project_id` and `organization_id`.
- No body.

Response shape:

- Evidence IDs.
- Provenance metadata.
- First/latest source locators if stored.
- Source candidate IDs.
- Promotion record IDs.
- Missing/broken reference warnings.

Validation:

- Same ID safety as organization/group detail.
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
- Do not generate summaries, explanations, organization analysis, fixes, or Dramatica classifications.

Expected errors:

- Project not found.
- Record not found.
- Corrupt provenance metadata.
- Broken source candidate reference.
- Broken promotion record reference.
- Unsafe source locator.

### `GET /api/projects/{project_id}/memory/organizations/health`

Purpose:

- Validate organization/group memory health without mutation.
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
- Validate memory envelope, IDs, schema version, duplicate IDs, member/leader links, hierarchy links, linked sources, linked approved entities, related organization links, type/status conflicts, membership/leadership conflicts, hierarchy cycles, and evidence presence.

Path safety:

- Do not expose host filesystem paths.
- Use project-relative IDs and safe labels.

Candidate/canon boundary:

- Health warnings are diagnostics, not approved story truth.
- Candidate counts remain candidate-only.
- Health must not infer approved truth from OMI records or promotion records.

No-prose boundary:

- Warnings are factual status messages only.
- Do not propose fixes, rewrites, faction repairs, hierarchy repairs, dialogue, scenes, or story prose.

Expected errors:

- Project not found.
- Corrupt memory file.
- Corrupt memory index.
- Unsupported schema.
- Unsafe ID.
- Partial validation failure.

## 10. Future Frontend Planning

These components are future planning only. Do not implement UI in WORKSPACE-020.

Future components:

- `ApprovedOrganizationsGroupsPage`
- `OrganizationsGroupsBoundaryBanner`
- `ApprovedOrganizationList`
- `ApprovedOrganizationListItem`
- `OrganizationDetailPanel`
- `OrganizationEvidencePanel`
- `OrganizationSourceLinksPanel`
- `OrganizationMembersLeadershipSnapshot`
- `OrganizationHierarchySnapshot`
- `OrganizationLinkedStoryKnowledgeSnapshot`
- `OrganizationRelatedRelationshipPlotTimelineSnapshot`
- `OrganizationRelatedQuestionsContinuitySnapshot`
- `OrganizationCandidateBacklogSnapshot`
- `OrganizationSearchFilterControls`
- `OrganizationWarningsPanel`
- `OrganizationEmptyState`
- `OrganizationFuturePagesReference`

Component rules:

- No AI writing buttons.
- No generated organization analysis button.
- No generated graph button in the first version.
- No controls named or behaving like `generate faction`, `fix organization`, `rewrite scene`, `generate group conflict`, `resolve hierarchy`, `explain faction arc`, `classify antagonist group`, `prove RS`, or `classify Dramatica role`.
- No controls that write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Search/filter controls must be local and deterministic.
- Candidate backlog controls must route to OMI and remain labeled as candidate/audit state.
- Detail panels must display stored approved fields only.
- Warning panels must be non-destructive.
- Missing fields must use `Unknown`, `Not approved yet`, or `Not recorded`.
- Generic organization/group records must use or link to `Not Dramatica Structural Proof` boundary copy.

## 11. Future Tests

Future tests should cover:

- No memory directory / no approved records.
- Load approved organization/group records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt memory file warning.
- Duplicate organization IDs warning.
- Unsafe IDs rejected.
- Broken member/leader/source/entity links warning.
- Parent/child hierarchy cycle warning.
- Organization type/status conflicts warning.
- Membership/leadership conflicts warning.
- Related organization broken/cyclic warning if represented.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- No AI prose-generation controls.
- No generated organization analysis/fixes/rewrites/summaries/explanations.
- No generated graph visualization in the first version.
- No Dramatica throughline/antagonist/protagonist/IC/RS/CIPS/dynamics claims.
- No JSONL/training writes.
- Missing/corrupt `memory/groups.json` warnings if a separate groups file is used.
- Broken ally/opponent organization links warning.
- Broken relationship/location/object/timeline/plot-thread/open-question/continuity links warning.
- Warning paths do not leak host filesystem paths.

## 12. Deferred Decisions

Deferred:

- Whether groups remain `organization_type` values inside `memory/organizations.json` or later receive parallel `memory/groups.json` and route groups.
- Exact organization/group schema names, envelope version, and enum values.
- Exact project navigation route names and how unavailable approved pages are represented.
- Whether hierarchy/alliance/opposition links are displayed as simple lists only or later as graph data.
- Whether organization/group edit, merge/split, archive/restore, or apply-promotion flows live on this page or in a separate owner-controlled memory management surface.
- How future Dramatica-specific organization/group classifications, if ever approved, are stored without blending into generic story-knowledge records.

## 13. Safety Boundaries

WORKSPACE-020 is documentation-only.

This spec does not implement:

- Backend runtime code.
- Frontend runtime code.
- Tests.
- Package/dependency changes.
- Dataset files.
- JSONL/training records.
- `training/data/dataset_manifest.json` changes.
- Training or fine-tuning.
- Ollama/live model calls.
- Package installs.
- Organizations / Groups page UI.
- Backend memory/canon routes.
- Apply-promotion.
- Organization extraction.
- Graph visualization.
- Contradiction detection.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- Git staging, commits, or pushes.
