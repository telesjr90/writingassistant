# WORKSPACE-021: Approved Objects / Items Page Spec

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
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Objects / Items page should be the future project-local destination for owner-approved object and item memory/canon records. It must show only object/item records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, needs-revision, and approved-but-not-applied object/item candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

This page is not a Dramatica structural page. Generic objects, items, artifacts, tools, clues, possessions, documents, keys, weapons, heirlooms, or recurring props are not throughline proof and must not be presented as Influence Character status, antagonist/protagonist function, Relationship Story proof, CIPS, dynamics, thematic symbol proof, or Dramatica storyform truth.

The page should:

- Show owner-approved `object_memory_record` or `item_memory_record` entries for the selected project.
- Read approved object/item truth only from future memory files such as `memory/objects.json`, `memory/items.json`, or an equivalent approved memory store.
- Clearly distinguish approved object/item truth from OMI object/item candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved object/item back to source evidence, provenance, source candidate IDs, promotion record IDs, and approval metadata where available.
- Show unresolved, ambiguous, partial, or missing fields honestly as `Unknown`, `Not approved yet`, or `Not recorded`.
- Show an empty state when no approved object/item records exist.
- Link to the OMI Ideas / Candidates page for pending object/item candidates.
- Link to related characters, organizations/groups, relationships, locations/settings, timeline events, plot threads, open questions, continuity/consistency issues, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic object/item extraction.
- Avoid inventory tracking.
- Avoid automatic ownership, holder, location, movement, or symbolic inference.
- Avoid object graph generation.
- Avoid contradiction detection.
- Avoid apply-promotion behavior.
- Avoid generated object analysis, generated summaries, rewrite suggestions, scene suggestions, item-fix suggestions, and any controls that write or rewrite story prose.
- Avoid Dramatica-specific structural, role, or thematic claims unless later approved and evidence-backed by a separate advanced-layer task.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Object / Item Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for object/item candidates.
- Source material is not approved object/item memory/canon by default.
- A mention of an artifact, clue, possession, weapon, document, tool, vehicle, relic, or prop in a scene, note, or material is not an approved object/item record by itself.
- Source material must not be copied into approved object/item memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions an object/item is not an approved object/item record.

### OMI Object / Item Candidates

Definition:

- Structured `object_candidate`, `item_candidate`, or future equivalent object/item candidate records that have not been applied to approved memory/canon.

Rules:

- Object/item candidates are not canon.
- Object/item candidates must not appear in the approved object/item list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate object type, object status, ownership, holder, creator, location, movement, symbolic note, evidence state, related links, and certainty must not be inferred as approved truth.
- Object/item candidates are generic story-knowledge candidates. They are not Dramatica structural or thematic proof.

### Approved-but-Not-Applied Candidates

Definition:

- Object/item candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved object/item memory/canon.
- Approved-but-not-applied candidates must not appear in the approved object/item list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved objects/items.
- Promotion records may be linked as provenance from an approved object/item record that a future apply-promotion step actually created.
- Promotion records present without an approved memory record must show an audit-only warning or candidate backlog state, not an approved object/item.

### Applied Object / Item Memory Records

Definition:

- Durable owner-approved `object_memory_record` or `item_memory_record` entries written to the future approved memory store by a future apply-promotion step.

Rules:

- Applied object/item records are the only records allowed in the approved object/item list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, approval metadata, owner/holder/location links, related entity links, and revision metadata where available.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/objects.json`, `memory/items.json`, or equivalent records.

### Ownership, Holder, and Location State

Definition:

- Future stored fields that identify approved owner characters, holder characters, creator characters, origin locations, current locations, location/movement references, affected sources, and linked story knowledge.

Rules:

- Ownership, holder, creator, location, and movement state must come from approved memory/canon records only.
- An object/item may remain ambiguous, unresolved, disputed, lost, hidden, destroyed, partly unknown, or insufficiently evidenced without implying an error.
- Missing ownership, holder, creator, or location state must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- Conflicting ownership, holder, location, movement, type, or status fields must surface non-destructive warnings and must not be silently corrected.

### Symbolic or Thematic Notes

Definition:

- Optional owner-approved non-Dramatica notes about an object/item's symbolic, motif, or thematic relevance.

Rules:

- Symbolic or thematic notes may be displayed only when the approved object/item record explicitly stores an owner-approved non-Dramatica note.
- Symbolic or thematic meaning must not be inferred from candidates, source text, model output, or page context.
- Symbolic notes must not be presented as Dramatica Issue, Variation, Problem, Solution, RS, IC, CIPS, dynamics, or thematic proof.

### Future Dramatica Structural or Thematic Claims

Definition:

- Future Dramatica storyform-specific classifications such as Issue, Variation, Problem, Solution, thematic symbol proof, throughline role, protagonist/antagonist function, Influence Character status, Relationship Story proof, CIPS, dynamics, or other storyform truth.

Rules:

- Dramatica-specific object/item classification is deferred.
- The first version of this page must not display any Dramatica-specific object/item diagnosis.
- Generic object/item labels and owner-approved symbolic notes must not be treated as Dramatica proof.
- Object/item records are not Dramatica claims unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, analysis system, or future object-analysis helper.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved object/item display.
- The first implementation of this page must not call a model.
- Generated object analysis, generated summaries, generated symbolic explanations, generated fixes, rewrite suggestions, scene suggestions, and item-fix suggestions are prohibited.

### Insufficient Evidence

Definition:

- Object/item evidence/provenance is missing, weak, broken, unsafe, ambiguous, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting, rewriting, retitling, reclassifying, moving, assigning ownership, or resolving the object/item record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any object/item that already exists.

## 3. Approved Object / Item Display Model

Approved object/item records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `object_id` | Stable approved object/item ID; reject unsafe IDs and show duplicate warnings. |
| `display_title` | Owner-approved display label; do not generate or retitle. |
| `object_type` | Stored type such as object, item, artifact, tool, clue, weapon, document, vehicle, relic, possession, resource, or unknown. Do not infer from source text or candidates. |
| `object_status` | Stored status such as active, lost, hidden, destroyed, transferred, disputed, unknown, not recorded, superseded, or archived. |
| `object_scope` | Stored scope such as project, chapter, scene, plot thread, relationship, character, organization, location, or unknown. |
| `short_owner_approved_description` | Stored owner-approved description only; no generated summaries. |
| `alias_names` | Stored aliases, alternate names, nicknames, or labels. |
| `owner_character_ids` | Stored approved owner character links; missing ownership is allowed. |
| `holder_character_ids` | Stored approved current/past holder character links; broken links warn only. |
| `creator_character_ids` | Stored approved creator/maker/originator character links; broken links warn only. |
| `related_character_ids` | Stored approved character links that are not necessarily owners, holders, or creators. |
| `linked_organization_ids` | Stored approved organization/group links. |
| `linked_relationship_ids` | Stored approved relationship links. |
| `linked_location_ids` | Stored approved location/setting links. |
| `origin_location_ids` | Stored approved origin/source location links. |
| `current_location_ids` | Stored approved current location links. |
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
| `symbolic_or_thematic_note if owner-approved and non-Dramatica` | Stored owner-approved non-Dramatica note only; do not infer symbolic meaning. |
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
| `notes` | Stored notes, ambiguity notes, uncertainty notes, or implementation notes. |

Display rules:

- Unapproved candidates must not appear as truth.
- Generated object analysis, generated summaries, symbolic interpretations, rewrite suggestions, scene suggestions, and item-fix suggestions are prohibited.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- An object/item may remain ambiguous, unresolved, disputed, ownerless, unlocated, partly unknown, symbolically unapproved, or insufficiently evidenced without implying an error.
- Owner-approved descriptions, symbolic notes, and owner notes may be displayed only as stored approved fields.
- Object/item records must not be presented as Dramatica Issue, Variation, Problem, Solution, Relationship Story, Influence Character, CIPS, dynamics, thematic proof, or storyform truth.
- If a future storage schema represents items as `object_type` values inside `memory/objects.json`, the page may display them without requiring a separate `memory/items.json`.

## 4. First-Version Page Sections

Each section must define purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

### Page Header

Purpose:

- Identify the active project and Approved Objects / Items area.
- Show approved object/item count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved object/item records from `memory/objects.json`, `memory/items.json`, or equivalent approved memory store if present.

Candidate/canon boundary:

- Header approved count must come from applied memory/canon records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, object summaries, symbolic explanations, fixes, scenes, or rewrite suggestions.

Empty state:

- Show that no approved objects/items exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Objects / Items Boundary Banner

Purpose:

- Explain that the page shows approved memory/canon object/item records only.
- Point pending object/item candidates to OMI.
- State that the page is not a prose-writing, inventory-tracking, fix-suggestion, graph-generation, symbolic-interpretation, or Dramatica proof surface.

Data source:

- Static page copy.
- Optional lightweight OMI object/item candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not canon.
- State that approved objects/items require future apply-promotion into memory/canon.
- State that object/item records are not Dramatica structural or thematic proof.

No-prose boundary:

- Prohibit generated object analysis, generated summaries, symbolic explanations, scene suggestions, rewrite suggestions, item fixes, and prose-patching controls.

Empty state:

- Banner remains visible even when no approved records exist.

Error state:

- Banner remains visible even when optional OMI counts cannot load.

### Approved Object List

Purpose:

- List approved object/item memory records for selection and local filtering.

Data source:

- Applied records from approved memory store only.
- `memory/index.json` may support navigation but must not override category files.

Candidate/canon boundary:

- Rows must be applied approved memory/canon records only.
- Candidate rows must not be included.

No-prose boundary:

- List shows stored labels, types, statuses, tags, and warning badges only.
- No generated descriptions, plot relevance summaries, symbolic interpretations, or fixes.

Empty state:

- Show no approved objects/items and link to OMI Ideas / Candidates for candidate review.

Error state:

- Duplicate IDs, unsafe IDs, corrupt category envelope, unsupported schema, or unreadable records show warnings and block unsafe display for affected records.

### Object Detail Panel

Purpose:

- Show selected approved object/item details and related approved links.

Data source:

- Selected applied object/item memory record.
- Lightweight linked approved records, source documents, and OMI audit links where available.

Candidate/canon boundary:

- Detail fields are approved truth only when stored in the approved record.
- Source candidate and promotion links are provenance, not candidate truth display.

No-prose boundary:

- Do not generate object descriptions, importance analysis, symbolic explanations, continuity fixes, or scene suggestions.
- Owner-approved descriptions and notes may be displayed exactly as stored.

Empty state:

- No selection shows choose-an-object guidance.

Error state:

- Broken linked records show warnings while preserving the stored object/item record.

### Evidence / Provenance Panel

Purpose:

- Show compact source evidence/provenance, approval metadata, source candidate IDs, promotion record IDs, confidence/certainty labels, and evidence warnings.

Data source:

- Approved object/item record evidence/provenance fields.
- OMI candidate and promotion audit metadata only by link.

Candidate/canon boundary:

- Evidence supports owner review and traceability; it must not be treated as automatic proof beyond the approved stored record.
- Candidate evidence must not be promoted by display.

No-prose boundary:

- No generated evidence summaries, symbolic explanations, or fix text.
- Avoid long source excerpts; show compact locators and stored summaries.

Empty state:

- Missing evidence shows `Evidence Required`, `Insufficient Evidence`, `Unknown`, or `Not recorded` as appropriate.

Error state:

- Broken source candidate, promotion, evidence, or provenance references show warnings and do not auto-repair.

### Linked Sources Panel

Purpose:

- Show source scenes, chapters, notes, and materials linked to the approved object/item record.

Data source:

- `affected_scene_ids`, `affected_chapter_ids`, `linked_note_ids`, `linked_material_ids`, `first_seen_source`, and `latest_seen_source` stored on approved records.

Candidate/canon boundary:

- Source documents are evidence/provenance, not canon by default.
- Source text does not create approved object/item fields unless the approved record stores them.

No-prose boundary:

- Links use stored titles/IDs/status only.
- Do not summarize source content or suggest source edits.

Empty state:

- Show no linked sources recorded.

Error state:

- Broken source links show warnings and do not remove or rewrite references.

### Ownership / Holder Snapshot

Purpose:

- Show stored owner, holder, creator, and related character links for selected object/item records.

Data source:

- `owner_character_ids`, `holder_character_ids`, `creator_character_ids`, and `related_character_ids` from approved records.
- Approved character records for display labels where available.

Candidate/canon boundary:

- Ownership, holder, creator, and related-character state must come from approved object/item memory only.
- Candidate ownership or holder claims remain in OMI.

No-prose boundary:

- No generated ownership explanations, scene fixes, or item transfer suggestions.

Empty state:

- Show ownership/holder/creator as `Unknown`, `Not approved yet`, or `Not recorded`.

Error state:

- Broken owner/holder/creator links and ownership/holder conflicts show warnings without inferring replacements.

### Location / Movement Snapshot

Purpose:

- Show stored origin/current/linked locations and movement-related timeline or source references where approved.

Data source:

- `origin_location_ids`, `current_location_ids`, `linked_location_ids`, `linked_timeline_event_ids`, `affected_scene_ids`, and stored status/location fields.

Candidate/canon boundary:

- Location and movement state must come from approved object/item records.
- The first version does not infer movement paths or inventory state.

No-prose boundary:

- No generated travel summaries, clue trails, continuity fixes, or scene suggestions.

Empty state:

- Show origin/current location as `Unknown`, `Not approved yet`, or `Not recorded`.

Error state:

- Broken location links, location/movement conflicts, or missing affected source references show warnings only.

### Linked Story Knowledge Snapshot

Purpose:

- Show stored links from the object/item record to approved characters, organizations/groups, relationships, locations/settings, and related object/item records if represented later.

Data source:

- Approved object/item link fields and approved linked-memory records.

Candidate/canon boundary:

- Linked story knowledge must be approved records only.
- Pending candidates may be counted separately but not shown as linked truth.

No-prose boundary:

- Do not generate link explanations, relationship analysis, symbolic meaning, or graph descriptions.

Empty state:

- Show no approved linked story knowledge.

Error state:

- Broken or cyclic related-object links, if represented, show warnings without repair.

### Related Plot / Timeline Snapshot

Purpose:

- Show stored links to timeline events and plot threads that involve the object/item.

Data source:

- `linked_timeline_event_ids` and `linked_plot_thread_ids` from approved records.

Candidate/canon boundary:

- Plot/timeline links must come from approved records only.
- Do not infer importance, clue status, payoff, causality, or sequence from candidates or source text.

No-prose boundary:

- No generated plot analysis, causal explanations, event summaries, or scene suggestions.

Empty state:

- Show no approved plot/timeline links.

Error state:

- Broken timeline or plot-thread links show warnings.

### Related Open Questions / Continuity Snapshot

Purpose:

- Show stored links to approved open questions and continuity/consistency issues involving the object/item.

Data source:

- `linked_open_question_ids` and `linked_continuity_issue_ids` from approved records.

Candidate/canon boundary:

- Related questions/issues must be approved records only.
- Candidate continuity/object issue output remains in OMI.

No-prose boundary:

- No generated answers, fixes, rewrite suggestions, symbolic explanations, or object-continuity patches.

Empty state:

- Show no related approved open questions or continuity issues.

Error state:

- Broken open-question or continuity links show warnings only.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for pending object/item candidates outside the approved list.

Data source:

- OMI candidate metadata and promotion records where available.

Candidate/canon boundary:

- Counts and links only; candidate contents must remain in OMI.
- Approved-but-not-applied candidates and promotion records must be labeled `Not Yet Applied` and `Promotion Record Only`.

No-prose boundary:

- No candidate summaries generated for this page.

Empty state:

- Show no object/item candidates in OMI.

Error state:

- Corrupt OMI metadata shows degraded counts and warnings.

### Empty State

Purpose:

- Explain the valid state where no approved object/item records exist yet.

Data source:

- Approved memory counts and optional OMI counts.

Candidate/canon boundary:

- State that pending candidates, approved candidates, and promotion records are not approved memory/canon.

No-prose boundary:

- Empty-state guidance is operational only.
- Do not suggest generating objects/items, clues, scenes, or fixes.

Empty state:

- Missing `memory/`, missing `memory/objects.json`, missing `memory/items.json`, or zero records all show a valid empty approved state.

Error state:

- If memory metadata is corrupt, show warning state instead of a clean empty state.

### Warning State

Purpose:

- Surface non-destructive memory, link, evidence, schema, and candidate/canon warnings.

Data source:

- Project validation, memory category validation, OMI audit link validation, approved record cross-link validation, and source-link validation.

Candidate/canon boundary:

- Warnings must not repair, promote, delete, merge, split, retitle, reclassify, move, assign ownership, infer holders, infer locations, infer symbolic meaning, or rewrite records.

No-prose boundary:

- Warning copy is factual status text only.
- No generated fixes or replacement prose.

Empty state:

- No warnings when clean.

Error state:

- Blocking warnings prevent approved display for affected unsafe data; non-blocking warnings allow partial display where safe.

### Future Page Link Reference

Purpose:

- Document future navigation links to adjacent approved-only and source pages.

Data source:

- Static route planning and linked IDs where available.

Candidate/canon boundary:

- Links to approved pages must represent approved records only.
- Links to OMI represent candidate review, not canon.

No-prose boundary:

- Navigation links must not launch writing, rewriting, generation, symbolic explanation, graph generation, or fix actions.

Empty state:

- Related page links may show `Related Page Not Implemented`.

Error state:

- Missing adjacent routes show future-only/placeholder labels.

## 5. Candidate / Canon Separation

Approved records:

- Approved records are read from future memory files such as `memory/objects.json`, `memory/items.json`, or an equivalent approved memory store.
- Approved records are durable project truth only when a future apply-promotion flow has created or updated the approved memory record.
- Approved records should preserve source candidate IDs, promotion record IDs, evidence/provenance, approval metadata, uncertainty, and revision metadata where available.

OMI candidates:

- OMI object/item candidates remain in OMI candidates.
- Pending, rejected, archived, needs-revision, duplicate, uncertain, and approved-but-not-applied candidates do not appear as approved objects/items.
- Candidate backlog may show counts and links only.
- Source candidate and promotion audit links may be shown as provenance from applied records.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved object/item memory.
- Promotion records present without approved memory records must not count as approved objects/items.

Inference limits:

- Object type, object status, ownership, holder, creator, origin/current location, movement, symbolic note, evidence state, related links, and certainty must not be inferred as truth from candidate output.
- Object/item records are not Dramatica structural or thematic claims unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.

## 6. First-Version Operations

Allowed first-version operations:

- View approved object/item list.
- View object/item details.
- Filter/search approved objects/items locally.
- Open linked source scene, note, or material.
- Open linked character, organization/group, relationship, location, timeline event, plot-thread, open-question, or continuity/consistency page if available.
- Open related OMI candidate or promotion record.
- Show ownership/holder snapshot.
- Show location/movement snapshot.
- Show linked story-knowledge snapshot.

Future-only operations:

- Edit approved object/item memory.
- Merge/split approved objects/items.
- Archive/restore approved objects/items.
- Mark object/item resolved/changed.
- Apply-promotion.
- Extract object/item candidates.
- Infer ownership/holder/location automatically.
- Generate object graph visualization.
- Suggest object/item fixes.
- Rewrite dialogue or scene to alter item continuity.
- Contradiction detection.
- Dramatica thematic/structural classification.
- Issue/Variation/Problem/Solution/CIPS/dynamics classification.

## 7. Local Search / Filter Planning

First-version local search/filter may operate over approved-record data only:

- `display_title`
- `object_type`
- `object_status`
- `object_scope`
- `alias_names`
- `owner_character_ids`
- `holder_character_ids`
- `creator_character_ids`
- `related_character_ids`
- `linked_organization_ids`
- `linked_relationship_ids`
- `linked_location_ids`
- `origin_location_ids`
- `current_location_ids`
- `tags` if available
- Approved description if available
- Linked source IDs
- Affected scene/chapter IDs
- Linked timeline/plot-thread/open-question/continuity IDs
- `source_candidate_ids`
- `promotion_record_ids`

Rules:

- Search is local and deterministic.
- Search labels results as approved-only.
- No semantic search in the first version.
- No model/Ollama calls.
- No generated summaries.
- No generated object analysis.
- No symbolic interpretation during search.
- No extraction during search.
- No contradiction detection during search.
- No Dramatica classification during search.
- Search must not create OMI records, promotion records, memory/canon records, JSONL records, or training data.
- Search must not mutate project files.

## 8. Warning and Invalid-State Behavior

Warnings are non-destructive. They must not auto-repair, auto-delete, rewrite identity, retitle, infer owners, infer holders, infer locations, infer symbolic meaning, correct roles/status, resolve object continuity, promote candidates, or leak host filesystem paths.

Required warning/invalid states:

- Missing `memory/`.
- Missing/corrupt `memory/objects.json`.
- Missing/corrupt `memory/items.json` if used.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Broken owner, holder, creator, or character references.
- Broken organization, relationship, or location references.
- Broken scene, note, or material references.
- Broken timeline, plot-thread, open-question, or continuity references.
- Duplicate object IDs.
- Unsafe IDs.
- Object type/status conflicts.
- Ownership/holder conflicts.
- Location/movement conflicts.
- Affected source references missing.
- Related object links broken/cyclic if represented.
- Promotion records present but no approved memory record.
- OMI object/item candidates exist but no approved objects/items yet.
- Related pages/entities not implemented yet.
- Missing or insufficient evidence.
- Corrupt `memory/index.json`.

Behavior:

- Missing memory folders and missing category files are valid empty states when no approved records exist.
- Corrupt memory files block approved display for the affected category and show a warning.
- Unsupported schema versions should show read-only or needs-migration warnings.
- Duplicate or unsafe IDs should fail closed for detail routing.
- Broken links should show target type and stored ID without exposing host paths.
- Conflict warnings should preserve stored ambiguity rather than forcing a correction.
- Candidate backlog warnings must link to OMI and not display candidate content as truth.

## 9. API Planning

This section documents future route planning only. Do not implement routes in this task.

Objects/items may be represented as `object_type` values inside `memory/objects.json`, or by parallel item endpoints in a later decision. A future project memory/canon summary endpoint may also compose these responses instead of dedicated route groups.

Every route must validate `project_id` as a safe single path component. Object routes must validate `object_id` as a safe record ID. Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose. Routes must not call Ollama or any model in the first implementation. Routes must not create OMI records, create memory files on read, apply promotions, write JSONL/training records, or update dataset manifests.

### `GET /api/projects/{project_id}/memory/objects`

Purpose:

- Return approved object/item list payload and warning summary.

Request shape:

- Path parameter: `project_id`.
- Optional local filter/search query parameters if implemented.

Response shape:

- Project ID.
- Approved object/item records or compact list rows.
- Candidate backlog counts by status if included, labeled candidate-only.
- Warnings.

Validation:

- Safe project ID.
- Existing project.
- Optional existing memory folder read-only.
- `memory/objects.json` envelope is valid if present.
- Record IDs are unique and safe.

Path safety:

- Read only inside selected project.
- Do not expose absolute paths.

Candidate/canon boundary:

- Return applied memory/canon records only.
- Candidate records must remain OMI links/counts only.

No-prose boundary:

- Return stored fields only.
- No generated summaries, symbolic interpretations, or fixes.

Expected errors:

- 400 invalid project ID or filters.
- 404 missing project.
- 422 corrupt memory metadata, unsupported schema, duplicate IDs, unsafe IDs, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/objects/{object_id}`

Purpose:

- Return one approved object/item detail payload.

Request shape:

- Path parameters: `project_id`, `object_id`.

Response shape:

- Approved object/item detail record.
- Linked source/reference status.
- Linked approved story-knowledge status.
- Warnings.

Validation:

- Safe project ID and object ID.
- Record exists in approved memory store.
- Linked IDs are safe before lookup.

Path safety:

- No traversal, absolute paths, or host path leakage.

Candidate/canon boundary:

- Detail is approved memory only.
- Source candidate and promotion links are provenance only.

No-prose boundary:

- Return stored owner-approved descriptions/notes only.
- No generated object analysis or symbolic explanations.

Expected errors:

- 400 invalid ID.
- 404 missing project, missing category file where not treated as list empty, or missing object.
- 422 corrupt category file, duplicate IDs, unsafe links, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/objects/{object_id}/provenance`

Purpose:

- Return compact evidence/provenance, source candidate, promotion record, and source-link data for one approved object/item.

Request shape:

- Path parameters: `project_id`, `object_id`.

Response shape:

- Evidence/provenance summary.
- Source candidate IDs and status.
- Promotion record IDs and audit status.
- First/latest source locators.
- Warnings.

Validation:

- Safe IDs.
- Evidence/provenance objects are bounded JSON objects/arrays.
- Source links remain project-relative where applicable.

Path safety:

- Do not expose raw host filesystem paths.
- Do not read long source bodies.

Candidate/canon boundary:

- Provenance explains how the approved record was created; it does not display candidates as approved truth.

No-prose boundary:

- No generated evidence narratives or source summaries.

Expected errors:

- Invalid IDs.
- Missing approved object/item.
- Broken source candidate or promotion references.
- Corrupt provenance.
- Sanitized partial read failure.

### `GET /api/projects/{project_id}/memory/objects/health`

Purpose:

- Return non-destructive health warnings for object/item memory state.

Request shape:

- Path parameter only, with optional validation depth in a later design.

Response shape:

- Health status.
- Warning list with code, severity, target type, target ID, and sanitized message.

Validation:

- Safe project ID.
- Read-only scans only.

Path safety:

- Scan only approved project-local memory/OMI references.
- Sanitize paths.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, split, retitle, or infer truth.

No-prose boundary:

- Warnings are factual status only.

Expected errors:

- 400 invalid project ID.
- 404 missing project.
- 500 sanitized partial scan failure.

## 10. Frontend Planning

Do not implement UI in this task. Future components:

- `ApprovedObjectsItemsPage`
- `ObjectsItemsBoundaryBanner`
- `ApprovedObjectList`
- `ApprovedObjectListItem`
- `ObjectDetailPanel`
- `ObjectEvidencePanel`
- `ObjectSourceLinksPanel`
- `ObjectOwnershipHolderSnapshot`
- `ObjectLocationMovementSnapshot`
- `ObjectLinkedStoryKnowledgeSnapshot`
- `ObjectRelatedPlotTimelineSnapshot`
- `ObjectRelatedQuestionsContinuitySnapshot`
- `ObjectCandidateBacklogSnapshot`
- `ObjectSearchFilterControls`
- `ObjectWarningsPanel`
- `ObjectEmptyState`
- `ObjectFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No generated object analysis button.
- No generated graph button in the first version.
- No controls like generate item, fix object continuity, rewrite scene, generate clue, explain symbolism, classify thematic role, prove Issue, prove Variation, or classify Dramatica role.
- Labels must distinguish approved objects/items, OMI candidates, promotion records, source/evidence, and future/not implemented states.
- Missing fields must show `Unknown`, `Not approved yet`, or `Not recorded`.
- Opening the page must not trigger analysis, extraction, model calls, OMI record creation, promotion, memory/canon mutation, or project-file writes.

## 11. Future Tests

Future implementation tests should cover:

- No memory directory / no approved records.
- Load approved object/item records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt memory file warning.
- Duplicate object IDs warning.
- Unsafe IDs rejected.
- Broken owner/holder/source/entity links warning.
- Ownership/holder conflicts warning.
- Location/movement conflicts warning.
- Object type/status conflicts warning.
- Related object broken/cyclic warning if represented.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- No AI prose-generation controls.
- No generated object analysis/fixes/rewrites/summaries/symbolic explanations.
- No Dramatica Issue/Variation/Problem/Solution/CIPS/dynamics claims.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 12. Deferred Decisions

Deferred to later tasks:

- Whether items are represented as `object_type` values inside `memory/objects.json` or by a parallel `memory/items.json` file.
- Exact object/item type enum.
- Exact object/item status enum.
- Whether owner/holder history is first-class or derived from approved timeline/source links later.
- Whether location/movement history becomes a separate approved event model.
- Whether related object links are represented and how cycles are warned.
- Exact evidence locator strategy for object/item source mentions.
- Whether symbolic/thematic notes are allowed in the first implementation or displayed only after a later owner-approved note workflow.
- Whether approved object/item records may be edited directly or only through future OMI/apply-promotion revisions.
- Merge/split/archive/restore/supersede UI timing.
- Browser/manual acceptance checklist for implemented Approved Objects / Items page.

## 13. Implementation Non-Goals

WORKSPACE-021 does not implement:

- Approved Objects / Items UI.
- Backend memory/canon routes.
- Apply-promotion.
- Object/item extraction.
- Inventory tracking.
- Graph visualization.
- Contradiction detection.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
- Tests.
