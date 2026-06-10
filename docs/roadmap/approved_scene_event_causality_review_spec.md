# WORKSPACE-024: Approved Scene / Event / Causality Review Spec

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
- WORKSPACE-022: `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
- WORKSPACE-023: `docs/roadmap/approved_contradictions_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Scene / Event / Causality Review page should be the future project-local destination for owner-approved scene-level review records, event/action records, and causality notes. It must show only records that have been explicitly applied by a future apply-promotion step or equivalent owner-approved approved-memory process. Pending, rejected, archived, needs-revision, and approved-but-not-applied scene/event/action/causality candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

This page is not a scene summary generator, not a timeline visualizer, not an automatic causal inference engine, not a generated fix page, not a rewrite page, not a semantic-search page, and not a Dramatica structural proof page. It must not generate scene summaries, rewrite scenes, infer causal chains from candidates, generate explanations, generate fixes, classify Dramatica structure, or prove storyform claims.

The page should:

- Show owner-approved `scene_review_memory_record`, `event_action_memory_record`, `causality_note_memory_record`, or equivalent approved records for the selected project.
- Read approved scene/event/causality review truth only from future memory files such as `memory/scene_reviews.json`, `memory/events.json`, `memory/actions.json`, `memory/causality.json`, or an equivalent approved memory/audit store.
- Clearly distinguish approved event/action/causality truth from OMI event/action/causality candidates.
- Distinguish this review page from the Chapters / Scenes page, which owns owner-authored prose storage, editing, save/reload, navigation, and ordering.
- Distinguish this review page from the Approved Timeline page, which owns chronology/order-focused `timeline_event_memory_record` display.
- Link approved event/action/causality records to evidence/provenance where available.
- Link records to project-local source scenes, chapters, notes, and materials where available.
- Link records to approved memory/canon records and source candidates where available.
- Show unresolved, missing, broken, uncertain, partial, or unsupported fields honestly.
- Show an empty state when no approved scene/event/causality records exist.
- Link to OMI Ideas / Candidates for pending event/action/causality candidates.
- Link to related characters, locations/settings, objects/items, organizations/groups, relationships, plot threads, open questions, continuity/consistency issues, contradictions, annotations/evidence/provenance, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic extraction.
- Avoid causal inference.
- Avoid generated summaries.
- Avoid generated explanations.
- Avoid generated fixes.
- Avoid scene rewrites.
- Avoid semantic search.
- Avoid apply-promotion behavior.
- Avoid Dramatica-specific structural/thematic claims unless later approved and evidence-backed by a separate advanced-layer task.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for scene/event/action/causality candidates or approved records.
- Source material is not approved scene/event/causality memory/canon by default.
- A scene containing an action, event, or apparent cause/effect relation is not an approved event/action/causality record by itself.
- Source material must not be copied, summarized, rewritten, re-anchored, or converted into approved memory/canon by opening this page.

### OMI Scene / Event / Action / Causality Candidates

Definition:

- Structured `timeline_event_candidate`, future `event_action_candidate`, future `scene_review_candidate`, future `causality_note_candidate`, or equivalent records that have not been applied to approved memory/canon.

Rules:

- Candidates are not canon.
- Candidates must not appear in the approved scene/event/causality list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate event type, action type, causal relation, status, source locator, linked records, evidence state, and certainty must not be inferred as approved truth.

### Approved-but-Not-Applied Candidates

Definition:

- Scene/event/action/causality candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to approved memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved scene/event/causality memory/canon.
- Approved-but-not-applied candidates must not appear in the approved record list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are audit-only unless future apply-promotion has created or updated approved scene/event/causality memory.
- Promotion records present without an approved memory record must show `Promotion Record Only` or `Not Yet Applied`, not approved truth.
- Source candidate and promotion audit links may be shown as provenance/audit context only.

### Applied Scene / Event / Causality Records

Definition:

- Durable owner-approved `scene_review_memory_record`, `event_action_memory_record`, `causality_note_memory_record`, or equivalent approved records written to the future approved memory store by a future apply-promotion step or another explicitly designed owner-approved process.

Rules:

- Applied records are the only records allowed in the approved record list.
- They should preserve source candidate IDs, promotion record IDs, evidence/provenance, source locators, linked approved-memory IDs, approval metadata, uncertainty, resolution metadata, revision metadata, and source-safety state where available.
- They remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/scene_reviews.json`, `memory/events.json`, `memory/actions.json`, `memory/causality.json`, or equivalent records.

### Scene Review Versus Scene Authoring

Definition:

- Scene review records describe owner-approved review metadata about source scenes, events/actions in scenes, or approved causal notes. They do not own or edit the scene body.

Rules:

- Chapters / Scenes remains the owner-authored prose authoring and organization page.
- This page may link to source scenes but must not edit or rewrite scene prose.
- Scene review records may remain partial, unresolved, uncertain, or not recorded without implying the source scene is invalid.
- Approved review text must be owner-approved navigation/review metadata, not generated replacement prose.

### Event / Action Versus Timeline

Definition:

- Event/action records may describe source-located events, actions, decisions, beats, or state changes without requiring approved chronology fields.

Rules:

- Approved Timeline owns chronology/order-focused `timeline_event_memory_record` display.
- This page owns source-located scene review, event/action, and cause/effect review records where owner-approved.
- `related_timeline_event_ids` may link to Approved Timeline, but this page must not duplicate timeline visualization, ordering, chronology conflict resolution, or date/sequence ownership.
- Missing or ambiguous chronology must be shown as `Unknown`, `Not approved yet`, or `Not recorded`, not inferred.

### Causality Notes

Definition:

- Causality notes record owner-approved cause/effect links, causal uncertainty, causal questions, or causal review metadata.

Rules:

- Causal links must come from approved records only.
- Causal links must not be inferred from scene text, notes, OMI candidates, or timeline proximity.
- Causal links may remain unresolved, uncertain, partly unknown, cyclic, broken, or under-evidenced without automatic repair.
- The first implementation must not render a causality graph.

### Source Locator and Excerpt State

Definition:

- Future stored fields identify source type, source ID, source locator type, source locator value, optional line/paragraph/span offsets, optional source hash, and optional owner-approved short excerpt.

Rules:

- Source locators must come from approved records only.
- Broken, missing, unsupported, out-of-range, or hash-mismatched locators must surface non-destructive warnings.
- Source excerpts must be limited, owner-approved, copyright-safe, and used only for locator/context display.
- The page must not generate, expand, rewrite, summarize, or invent excerpts.
- The page must not re-anchor source text automatically.

### Future Dramatica Structural or Thematic Claims

Definition:

- Future Dramatica storyform-specific claims such as Issue, Variation, Problem, Solution, Relationship Story, Influence Character, CIPS, dynamics, Driver, Limit, Outcome, Judgment, Signpost, Concern, or storyform proof.

Rules:

- Dramatica-specific event/action/causality classification is deferred.
- Scene/event/causality records must not be presented as Dramatica structural or thematic proof unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.
- Generic events, actions, cause/effect links, scene reviews, and continuity relationships are not Dramatica Issue, Variation, Problem, Solution, Relationship Story, Influence Character, CIPS, dynamics, Driver, Limit, Outcome, Judgment, or storyform proof.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, analysis system, or future event/action/causality helper.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved display.
- The first implementation of this page must not call a model.
- Generated scene summaries, generated event analysis, generated causal explanations, generated fixes, rewrite suggestions, scene suggestions, and causal repair suggestions are prohibited.

Required labels:

| Label | Use |
| --- | --- |
| `Approved Scene / Event / Causality Review` | Marks the page and applied approved records. |
| `Approved Scene Review` | Marks applied scene-level review records. |
| `Approved Event / Action` | Marks applied event/action records. |
| `Approved Causality Note` | Marks applied causality notes. |
| `Approved Memory` | Marks approved memory/canon records linked by selected review records. |
| `Approved Audit Context` | Marks approved provenance/audit records that support traceability but are not story prose. |
| `Candidate` | Marks OMI event/action/causality candidates outside the approved list. |
| `Pending Candidate` | Marks pending candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI candidates. |
| `Needs Revision` | Marks candidates needing revision. |
| `Archived Candidate` | Marks archived OMI candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no approved memory record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Locator Unavailable` | Marks missing, unsupported, broken, or unavailable locator state. |
| `Evidence Required` | Marks approved records whose referenced event/action/causality note needs evidence but none is recorded. |
| `Insufficient Evidence` | Marks evidence that exists but is incomplete, ambiguous, one-sided, weak, unsafe, or not enough for the approved record. |
| `Unknown` | Marks approved fields the owner has not approved or the system cannot verify. |
| `Not Approved Yet` | Marks fields pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields intentionally absent or not captured. |
| `Unresolved` | Marks causality or review state that remains unresolved by owner-approved metadata. |
| `Copyright / Source Safety Warning` | Marks unsafe or unapproved excerpt/source-display state. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Not Dramatica Proof` | Marks the page and relevant records as general story-knowledge/audit context, not Dramatica proof. |
| `Future / Not Implemented` | Marks editing, merge/split, archive/restore, extraction, causal inference, generated summaries, generated explanations, generated fixes, semantic search, source re-anchoring, visualization, apply-promotion, JSONL conversion, and Dramatica classification. |

## 3. Approved Display Model

Approved scene/event/causality records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `record_id` | Stable approved record ID; reject unsafe IDs and show duplicate warnings. |
| `record_type` | Stored type such as `scene_review_memory_record`, `event_action_memory_record`, `causality_note_memory_record`, or equivalent. |
| `display_title` | Owner-approved display label; do not generate, retitle, or rewrite. |
| `review_type` | Stored scene-review type only; do not infer from source text or candidates. |
| `event_type` | Stored event type only; do not infer timeline, Dramatica, or causal type. |
| `action_type` | Stored action type only; do not infer from scene text or candidates. |
| `causality_type` | Stored causality type only; do not infer cause/effect relation. |
| `status` | Stored record status only. |
| `scope` | Stored scope such as project, chapter, scene, note, material, memory record, candidate, promotion, or unknown. |
| `short_owner_approved_description` | Stored owner-approved description only; no generated summaries, explanations, or fixes. |
| `source_chapter_id` | Stored source chapter ID if available; broken references warn. |
| `source_scene_id` | Stored source scene ID if available; broken references warn. |
| `source_note_ids` | Stored source note IDs if available; broken references warn. |
| `source_material_ids` | Stored source material IDs if available; broken references warn. |
| `source_locator_type` | Stored locator type such as offset, line range, paragraph index, anchor text, hash, or unknown. |
| `source_locator` | Stored locator value only; unsupported or unavailable locators warn. |
| `source_hash if stored` | Stored source snapshot hash; mismatch warns and does not auto-repair. |
| `event_or_action_summary if owner-approved` | Stored owner-approved or explicitly approved navigation/review text only; never generated silently. |
| `cause_record_ids` | Approved cause links only; broken links warn. |
| `effect_record_ids` | Approved effect links only; broken links warn. |
| `related_event_record_ids` | Related approved event/action/review records only; broken links warn. |
| `related_timeline_event_ids` | Approved timeline links only; broken links warn. |
| `related_plot_thread_ids` | Approved plot-thread links only; broken links warn. |
| `related_continuity_issue_ids` | Approved continuity/consistency links only; broken links warn. |
| `related_contradiction_ids` | Approved contradiction links only; broken or cyclic links warn. |
| `linked_character_ids` | Approved character links only; broken links warn. |
| `linked_location_ids` | Approved location/setting links only; broken links warn. |
| `linked_object_ids` | Approved object/item links only; broken links warn. |
| `linked_organization_ids` | Approved organization/group links only; broken links warn. |
| `linked_relationship_ids` | Approved relationship links only; broken links warn. |
| `linked_open_question_ids` | Approved open-question links only; broken links warn. |
| `linked_annotation_ids` | Approved annotation links only; broken links warn. |
| `linked_evidence_record_ids` | Approved evidence links only; broken links warn. |
| `linked_provenance_record_ids` | Approved provenance/audit links only; broken links warn. |
| `affected_scene_ids` | Approved source/reference scene links only; broken links warn. |
| `affected_chapter_ids` | Approved source/reference chapter links only; broken links warn. |
| `first_seen_source` | First approved source/provenance locator if stored. |
| `latest_seen_source` | Latest approved source/provenance locator if stored. |
| `evidence/provenance summary` | Compact stored evidence/provenance metadata only; avoid long source copies and generated explanations. |
| `confidence/certainty label if stored` | Stored confidence/certainty at approval only; not objective truth or Dramatica proof. |
| `owner_notes` | Stored owner notes only. |
| `resolution_status if applicable` | Stored resolution state only; do not infer from candidates, source edits, or source availability. |
| `created_at` | Stored creation timestamp. |
| `updated_at` | Stored update timestamp. |
| `approved_at` | Stored approval timestamp. |
| `approved_by` | Stored owner/reviewer identifier. |
| `source_candidate_ids` | OMI candidate provenance links only. |
| `promotion_record_ids` | Promotion audit links only. |
| `revision_history` | Stored revision metadata. |
| `supersedes_record_ids` | Older approved records replaced by this one. |
| `superseded_by_record_id` | Newer approved record replacing this one. |
| `tags` | Stored approved tags. |
| `notes` | Stored notes, ambiguity notes, uncertainty notes, source-safety notes, or implementation notes. |

Display clarifications:

- Unapproved candidates must not appear as truth.
- Generated scene summaries, generated event analysis, generated causal explanations, generated fixes, rewrite suggestions, scene suggestions, and causal repair suggestions are prohibited.
- `event_or_action_summary` must be owner-approved or explicitly approved navigation/review text, never generated silently.
- Source excerpts must be limited, owner-approved, copyright-safe, and used only for locator/context display.
- Missing fields must be shown as `Unknown`, `Not approved yet`, `Not recorded`, or `Locator unavailable`.
- A causal link may remain unresolved, uncertain, or partly unknown without implying an error.
- Scene/event/causality records support approved memory review but do not automatically promote, repair, reorder, summarize, or validate candidates.
- Scene/event/causality records must not be presented as Dramatica Issue, Variation, Problem, Solution, Relationship Story, Influence Character, CIPS, dynamics, Driver, Limit, Outcome, Judgment, Signpost, Concern, or storyform proof.

## 4. Relationship to Existing Pages

Chapters / Scenes page:

- Owns authoring, navigation, save/reload, ordering, and owner-authored prose editing.
- Stores and displays scene bodies as owner-authored source material.
- May link to approved scene/event/causality review records later, but must not delegate scene prose editing to this page.

Approved Timeline page:

- Owns chronology/order-focused approved `timeline_event_memory_record` display.
- Owns timeline-specific chronology labels, sequence/order fields, date/time fields, timeline event list behavior, and timeline health warnings.
- May link to event/action/causality review records, but this page must not duplicate timeline visualization or chronology ownership.

Approved Scene / Event / Causality Review page:

- Owns scene-derived event/action/causality records, source-located review records, and cause/effect links where owner-approved.
- Provides source locator, evidence/provenance, cause/effect, related timeline, related plot-thread, related continuity/contradiction, and approved memory snapshots.
- Does not write source scenes, generate summaries, infer causal chains, or reorder timelines.

Approved Plot Threads page:

- Owns plot-thread status and linked event snapshots.
- May link to approved event/action records, but this page must not take over plot-thread status, thread resolution, payoff, or related open-question ownership.

Continuity / Consistency page:

- Owns approved continuity warning and consistency issue records.
- May link to scene/event/causality review records, but this page must not duplicate issue resolution or continuity warning workflows.

Approved Open Questions page:

- Owns approved open-question and unresolved-question records.
- May link to unresolved causality notes or event/action records, but this page must not generate answers or resolve causal questions.

Approved Contradictions page:

- Owns approved contradiction and cross-record conflict records.
- May link to event/action/causality records when a contradiction involves scene-level event/action claims, but this page must not detect contradictions or duplicate claim-pair workflows.

Approved Annotations / Evidence / Provenance page:

- Owns approved annotation, evidence-span, and provenance/audit records.
- This page links to evidence/provenance for traceability but does not redefine evidence storage or source-safety policy.

Other approved story-knowledge pages:

- Characters, locations/settings, objects/items, organizations/groups, relationships, plot threads, open questions, continuity/consistency, contradictions, and annotations/evidence/provenance remain owners of their category-specific records.
- This page links to those pages but must not duplicate or override their ownership.

## 5. First-Version Page Sections

Each section must define purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

### Spec / Page Header

Purpose:

- Identify the active project and Approved Scene / Event / Causality Review area.
- Show approved scene-review, event/action, and causality-note counts and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved records from `memory/scene_reviews.json`, `memory/events.json`, `memory/actions.json`, `memory/causality.json`, or an equivalent approved memory/audit store if present.

Candidate/canon boundary:

- Header approved counts must come from applied approved records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, scene summaries, event explanations, causal explanations, fixes, or Dramatica proof.

Empty state:

- Show that no approved scene/event/causality records exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Scene / Event / Causality Boundary Banner

Purpose:

- Explain that the page shows approved scene/event/causality records only.
- Point pending event/action/causality candidates to OMI.
- State that the page is not a scene summary generator, automatic causal inference engine, generated fix surface, rewrite surface, timeline visualizer, semantic-search surface, extractor surface, or Dramatica proof page.

Data source:

- Static page copy.
- Optional lightweight OMI event/action/causality candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not approved truth.
- State that approved records require future apply-promotion or an explicitly designed approved memory/audit process.

No-prose boundary:

- Prohibit generated scene summaries, generated causal explanations, generated fixes, rewrite suggestions, scene suggestions, bridge scenes, plot-hole patches, retcons, source rewrites, and prose-patching controls.

Empty state:

- Banner remains visible even when no approved records exist.

Error state:

- Banner remains visible even when optional OMI counts cannot load.

### Approved Scene Review List

Purpose:

- List approved scene-level review records for selection and local filtering.

Data source:

- Applied `scene_review_memory_record` or equivalent approved records only.

Candidate/canon boundary:

- Rows must be applied approved records only.
- Candidate rows must not be included.

No-prose boundary:

- List shows stored labels, review types, statuses, tags, source labels, and warning badges only.
- No generated scene summaries, descriptions, explanations, interpretations, fixes, or proof narratives.

Empty state:

- Show no approved scene review records and link to OMI Ideas / Candidates for candidate review when candidate counts exist.

Error state:

- Duplicate IDs, unsafe IDs, corrupt category envelope, unsupported schema, or unreadable records show warnings and block unsafe display for affected records.

### Approved Event / Action List

Purpose:

- List approved event/action records for selection and local filtering.

Data source:

- Applied `event_action_memory_record`, `timeline_event_memory_record` only when explicitly included for source-located review, or equivalent approved event/action records.

Candidate/canon boundary:

- Rows must be applied approved records only.
- Event/action candidates, timeline candidates, promotion records, and source-only material must remain outside the approved list.

No-prose boundary:

- Display stored labels, event/action type, status, source IDs, and warning badges only.
- No generated event summaries, action descriptions, causal explanations, or plot prose.

Empty state:

- Show no approved event/action records and link to OMI Ideas / Candidates for candidate review when candidate counts exist.

Error state:

- Duplicate IDs, unsafe IDs, event/action type conflicts, status conflicts, broken source links, unsupported schema, or corrupt records show non-destructive warnings.

### Causality Notes List

Purpose:

- List approved causality notes and approved cause/effect review records.

Data source:

- Applied `causality_note_memory_record` or equivalent approved records only.

Candidate/canon boundary:

- Causality candidates and timeline proximity must not appear as approved causal truth.
- Cause/effect links must come from approved records only.

No-prose boundary:

- List shows stored labels, causality type, status, linked cause/effect IDs, source labels, and warning badges only.
- No generated causal explanations, repairs, or scene fixes.

Empty state:

- Show no approved causality notes and link to OMI Ideas / Candidates for candidate review when candidate counts exist.

Error state:

- Broken cause/effect links, self-links, cycles if represented, status conflicts, unsupported causality type, corrupt records, or unsafe IDs show non-destructive warnings.

### Record Detail Panel

Purpose:

- Show selected approved record details, source candidate IDs, promotion record IDs, source locators, event/action/causality fields, evidence/provenance, linked source documents, linked approved memory, approval metadata, resolution metadata, revision history, and notes.

Data source:

- Selected applied approved record.
- Lightweight linked approved records, source documents, and OMI audit links where available.

Candidate/canon boundary:

- Detail fields are approved truth/audit context only when stored in the approved record.
- Source candidate and promotion links are provenance, not candidate truth display.
- The panel must not hydrate missing fields from OMI candidates.

No-prose boundary:

- Do not generate a scene summary, event analysis, causal explanation, fix, rewrite, bridge scene, plot-hole patch, retcon, source summary, or Dramatica proof.
- Owner-approved descriptions, event/action summaries, owner notes, and resolution notes may be displayed exactly as stored.

Empty state:

- No selection shows choose-a-record guidance.

Error state:

- Invalid selected ID, missing record, unsafe ID, unsupported schema, or broken relation links show non-destructive warnings.

### Source Locator Panel

Purpose:

- Show source document identity, locator type, locator value, safe source label, optional hash, optional line/paragraph/span locator, and source availability.

Data source:

- Stored source locator fields on the approved record.
- Source document metadata only where safe and project-local.

Candidate/canon boundary:

- Source documents are evidence/provenance, not canon by default.
- Source locators do not create approved claims unless the approved record stores them.

No-prose boundary:

- Do not summarize, rewrite, re-anchor, interpret, or quote source text beyond limited owner-approved copyright-safe excerpts.

Empty state:

- Show `Locator unavailable` or `Not recorded`.

Error state:

- Broken source documents, unsupported locator type, out-of-range line/paragraph/span locators, source hash mismatch, or unsafe IDs show non-destructive warnings.

### Cause / Effect Link Panel

Purpose:

- Show approved cause/effect links for the selected record and warn about missing, broken, unresolved, cyclic, or self-linked relationships.

Data source:

- Stored `cause_record_ids`, `effect_record_ids`, and related approved event/action/causality records.

Candidate/canon boundary:

- Cause/effect links must come from applied approved records only.
- Missing causal links must not be inferred from timeline order, scene order, source text, notes, or candidates.

No-prose boundary:

- No generated causal explanations, generated "why this caused that" prose, generated fixes, or repair suggestions.

Empty state:

- Show `Not recorded` or `No approved cause/effect links`.

Error state:

- Broken links, cycles if represented, self-links, duplicate relation IDs, or unsupported causality states show non-destructive warnings.

### Related Timeline Snapshot

Purpose:

- Show related approved timeline event links without duplicating the Approved Timeline page.

Data source:

- Approved record `related_timeline_event_ids`.
- Future approved `memory/timeline.json` where implemented.

Candidate/canon boundary:

- Related timeline links must come from approved records only.
- OMI timeline/event candidates remain candidate-only counts/links.

No-prose boundary:

- Do not generate chronology narratives, event summaries, causal explanations, or plot/timeline prose.

Empty state:

- Show `Not recorded` or `No linked approved timeline events`.

Error state:

- Broken timeline links or unimplemented related pages show warnings/placeholders.

### Related Plot Thread Snapshot

Purpose:

- Show approved plot-thread links tied to selected event/action/causality records without duplicating plot-thread status ownership.

Data source:

- Approved record `related_plot_thread_ids`.
- Future approved `memory/plot_threads.json` where implemented.

Candidate/canon boundary:

- Related plot-thread links must come from approved records only.
- OMI plot-thread or event/action candidates remain candidate-only.

No-prose boundary:

- Do not generate plot summaries, thread explanations, causal explanations, or fixes.

Empty state:

- Show `Not recorded` or `No linked approved plot threads`.

Error state:

- Broken plot-thread links or unimplemented related pages show warnings/placeholders.

### Related Continuity / Contradiction Snapshot

Purpose:

- Show approved continuity/consistency and contradiction records linked to the selected approved record.
- Clarify whether a scene event/action/causal relation is tied to broader continuity or contradiction work without duplicating those pages.

Data source:

- Approved record `related_continuity_issue_ids` and `related_contradiction_ids`.
- Future approved continuity/consistency and contradiction memory files where implemented.

Candidate/canon boundary:

- Related continuity/contradiction links must come from approved records only.
- OMI continuity/contradiction/event/action/causality candidates remain candidate-only.

No-prose boundary:

- Do not generate continuity explanations, contradiction explanations, fixes, scene rewrites, bridge scenes, or causal repair text.

Empty state:

- Show `Not recorded` or `No linked approved continuity / contradiction records`.

Error state:

- Broken continuity/contradiction links, cyclic related-record links, or unimplemented related pages show warnings/placeholders.

### Linked Approved Memory Snapshot

Purpose:

- Show linked approved memory/canon records across the selected scene/event/causality record.

Data source:

- Stored type-specific linked IDs and approved memory files when present.

Candidate/canon boundary:

- Linked records must be approved memory/canon records only.
- Pending candidates may be counted separately but not shown as linked truth.

No-prose boundary:

- Do not generate link explanations, summaries, proof narratives, or interpretations.

Empty state:

- Show no linked approved memory records.

Error state:

- Broken or unsafe linked memory references show warnings without repair.

### Evidence / Provenance Panel

Purpose:

- Show compact evidence/provenance metadata for the approved record, including first/latest sources, evidence IDs, provenance IDs, source candidate IDs, promotion record IDs, approval data, source hashes, and confidence/certainty labels where stored.

Data source:

- Approved record evidence/provenance fields.
- Approved evidence/provenance records where linked.
- Linked OMI candidate/promotion metadata for audit links only.

Candidate/canon boundary:

- Candidate/promotion data is provenance, not approved truth.
- If evidence is missing or insufficient, show `Evidence Required` or `Insufficient Evidence`.

No-prose boundary:

- Evidence summaries must be stored metadata only.
- Avoid long source copies and generated explanations.

Empty state:

- Show `Not Recorded`, `Evidence Required`, or `Insufficient Evidence` when no evidence/provenance is stored.

Error state:

- Missing source candidate, missing promotion record, missing evidence/provenance record, source hash mismatch, unsafe source path, unsafe excerpt, or broken evidence reference shows a warning.

### Linked Sources Panel

Purpose:

- Show project-local source links such as source scenes, chapters, notes, materials, source locators, affected scenes, and affected chapters.
- Let the owner open linked source scene/note/material/chapter if available.

Data source:

- Approved record source fields and evidence/provenance source locators.
- Project metadata for link validation.

Candidate/canon boundary:

- Linked sources are evidence/context, not canon by default.
- Broken source references must not be replaced from candidates, search results, or automatic re-anchoring.

No-prose boundary:

- Opening a source displays stored owner-authored/source material only.
- Do not summarize, rewrite, re-anchor, interpret, or quote source text beyond limited owner-approved copyright-safe excerpts.

Empty state:

- Show `Not Recorded` or `Locator unavailable` when no source links exist.

Error state:

- Broken scene, chapter, note, material, unsupported locator, out-of-range locator, unsafe reference, or host path leakage risk shows non-destructive warning.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for OMI scene/event/action/causality candidates by status.
- Help the owner navigate to OMI without blending candidates into approved truth.

Data source:

- OMI candidate metadata and promotion records where available.

Candidate/canon boundary:

- Candidate backlog may show counts and links only.
- Candidate event/action text, proposed source locator, proposed cause/effect link, proposed evidence, and proposed certainty must not be shown as approved truth.
- Approved-but-not-applied candidates and promotion records must be labeled `Not Yet Applied` and `Promotion Record Only`.

No-prose boundary:

- No generated candidate summaries or explanations.

Empty state:

- Show no scene/event/action/causality candidates in OMI.

Error state:

- Corrupt OMI metadata shows degraded counts and warnings without blocking approved record display.

### Empty State

Purpose:

- Explain the valid state where no approved scene/event/causality records exist yet.

Data source:

- Approved memory/audit counts and optional OMI counts.

Candidate/canon boundary:

- State that pending candidates, approved candidates, and promotion records are not approved memory/canon.
- If candidates exist, link to OMI with candidate labels only.

No-prose boundary:

- Empty-state guidance is operational only.
- Do not suggest generating scene summaries, extracting events, inferring causality, generating explanations, generating fixes, retcons, bridge scenes, plot-hole patches, or rewrites.

Empty state:

- Missing `memory/`, missing `memory/scene_reviews.json`, missing `memory/events.json`, missing `memory/actions.json`, missing `memory/causality.json`, or zero records all show a valid empty approved state.

Error state:

- If memory metadata is corrupt, show Warning State instead of a clean empty state.

### Warning State

Purpose:

- Surface non-destructive memory, source locator, event/action type, causality, evidence, provenance, schema, source-safety, linked-record, and candidate/canon warnings.

Data source:

- Project validation, memory category validation, OMI audit link validation, approved record cross-link validation, source-link validation, and source-safety validation.

Candidate/canon boundary:

- Warnings must not repair, promote, delete, merge, split, retitle, infer events, infer actions, infer causality, infer locators, infer source safety, re-anchor source text, invent evidence, validate candidates, or rewrite records.

No-prose boundary:

- Warning copy is factual status text only.
- No generated fixes, explanations, interpretations, summaries, retcons, bridge scenes, or replacement prose.

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

- Navigation links must not launch writing, rewriting, generation, explanation, fixing, semantic search, extraction, causal inference, graph visualization, timeline visualization, apply-promotion, or proof actions.

Empty state:

- Related page links may show `Related Page Not Implemented`.

Error state:

- Missing adjacent routes show future-only/placeholder labels.

## 6. Candidate / Canon Separation

Approved records:

- Approved records are read from future memory files such as `memory/scene_reviews.json`, `memory/events.json`, `memory/actions.json`, `memory/causality.json`, or an equivalent approved memory/audit store.
- Approved scene/event/causality truth exists only after owner approval, promotion record creation, and successful future apply-promotion into approved memory/canon, or another explicitly designed owner-approved approved-memory process.
- Approved records should preserve review type, event type, action type, causality type, status, source locator, evidence/provenance, source candidate IDs, promotion record IDs, linked records, certainty labels, approval metadata, uncertainty, and revision metadata where available.
- Approved records are project-local and must not leak across projects.

OMI candidates:

- OMI scene/event/action/causality candidates remain in OMI candidates.
- Pending, rejected, archived, duplicate, uncertain, needs-revision, and approved-but-not-applied candidates do not appear as approved records.
- Candidate backlog may show counts and links only.
- Source candidate and promotion audit links may be shown as provenance/audit context.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved scene/event/causality memory.
- Promotion records present without approved memory must not count as approved records.

Inference restrictions:

- Event type, action type, causal relation, status, source locator, linked records, evidence state, and certainty must not be inferred as truth from candidate output.
- Scene/event/causality records support approved memory review but do not automatically promote, repair, reorder, summarize, or validate candidates.
- Scene/event/causality records are not Dramatica structural/thematic claims unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.
- Missing approved fields must remain missing and be displayed honestly.
- No model, extractor, NotebookLM output, source material, raw idea, or raw analysis artifact may directly become approved scene/event/causality truth.

## 7. First-Version Operations

Allowed first-version operations:

- View approved scene review records.
- View approved event/action records.
- View approved causality notes.
- View record details.
- Filter/search approved records locally.
- Open linked source scene/note/material/chapter if available.
- Open linked approved memory/canon record if available.
- Open linked timeline/plot/continuity/open-question/contradiction record if available.
- Open linked OMI candidate or promotion record if available.
- Show cause/effect link panel.
- Show evidence/provenance panel.
- Show linked story-knowledge snapshot.

Future-only operations:

- Edit approved scene/event/causality memory.
- Merge/split approved records.
- Archive/restore.
- Mark causal link resolved.
- Apply-promotion.
- Extract event/action candidates.
- Extract causality candidates.
- Generate scene summaries.
- Generate event explanations.
- Generate causal explanations.
- Generate fixes.
- Rewrite scenes to fix causality.
- Semantic search.
- Automatic source re-anchoring.
- Timeline visualization.
- Causality graph visualization.
- Contradiction detection.
- Dramatica structural/thematic proof classification.
- JSONL/training conversion.

## 8. Local Search / Filter Planning

First-version local search/filter may operate over approved-record data only:

- `record_id`
- `record_type`
- `display_title`
- `review_type`
- `event_type`
- `action_type`
- `causality_type`
- `status`
- `scope`
- `source_chapter_id`
- `source_scene_id`
- `source_note_ids`
- `source_material_ids`
- `related_timeline_event_ids`
- `related_plot_thread_ids`
- `related_continuity_issue_ids`
- `related_contradiction_ids`
- `cause_record_ids`
- `effect_record_ids`
- Linked character/location/object/organization/relationship/open-question/annotation/evidence/provenance IDs.
- `source_candidate_ids`
- `promotion_record_ids`
- `tags` if available.
- Approved description if available.

Rules:

- Search is local and deterministic.
- Search labels results as approved-only.
- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No generated explanations.
- No generated fixes.
- No extraction during search.
- No causal inference during search.
- No re-anchoring during search.
- No Dramatica classification during search.
- Search must not create OMI records, promotion records, memory/canon records, JSONL records, or training data.
- Search must not mutate project files.

## 9. Warning and Invalid-State Behavior

Warnings are non-destructive. They must not auto-repair, auto-delete, rewrite identity, retitle, infer events, infer actions, infer causality, re-anchor source text, invent evidence, generate summaries, generate explanations, generate fixes, promote candidates, mutate memory/canon, or leak host filesystem paths.

Required warning/invalid states:

- Missing `memory/`.
- Missing/corrupt `memory/scene_reviews.json`.
- Missing/corrupt `memory/events.json`.
- Missing/corrupt `memory/actions.json` if used.
- Missing/corrupt `memory/causality.json`.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Approved record references missing promotion record.
- Approved record references missing approved memory record.
- Broken source scene/chapter/note/material reference.
- Broken source locator.
- Source hash mismatch if represented.
- Unsafe IDs.
- Duplicate record IDs.
- Unsupported `source_locator_type`.
- Locator out of range if represented.
- Event/action type/status conflicts.
- Causality status conflicts.
- Cause/effect record broken links.
- Cause/effect cycles if represented.
- Cause/effect self-link warning.
- Related timeline/plot/continuity/open-question/contradiction links broken.
- Linked story-knowledge references broken.
- Copyright-unsafe excerpt warning.
- Missing evidence for approved event/action/causality record.
- Promotion records present but no approved memory record.
- OMI event/action/causality candidates exist but no approved records yet.
- Related pages/entities not implemented yet.
- Corrupt `memory/index.json`.

Behavior:

- Missing memory folders and missing category files are valid empty states when no approved records exist.
- Corrupt memory files block approved display for the affected category and show a warning.
- Unsupported schema versions should show read-only or needs-migration warnings.
- Duplicate or unsafe IDs should fail closed for detail routing.
- Broken links should show target type and stored ID without exposing host paths.
- Locator warnings should preserve stored ambiguity rather than forcing a correction.
- Event/action type and status conflicts must not be silently normalized.
- Causality status conflicts, broken links, cycles, and self-links must not be repaired or removed automatically.
- Candidate backlog warnings must link to OMI and not display candidate content as truth.
- Source hash mismatch warnings must not re-anchor, rewrite, or delete source references.
- Copyright-unsafe excerpt warnings must hide unsafe excerpt display while preserving safe metadata.

## 10. API Planning

This section documents future route planning only. Do not implement routes in this task.

Scene reviews, events/actions, and causality notes may be represented as one `scene-events` endpoint family or split into parallel `scene-reviews`, `events`, `actions`, and `causality` endpoint families in a later decision. A future project memory/canon summary endpoint may also compose these responses instead of dedicated route groups.

Every route must validate `project_id` as a safe single path component. Scene-event routes must validate `record_id` as a safe record ID. Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose. Routes must not call Ollama or any model in the first implementation. Routes must not create OMI records, create memory files on read, apply promotions, write JSONL/training records, update dataset manifests, extract event/action candidates, infer causality, generate summaries, generate explanations, generate fixes, re-anchor sources, visualize timelines, visualize causality graphs, detect contradictions, or classify Dramatica proof.

Route group:

```text
GET /api/projects/{project_id}/memory/scene-events
GET /api/projects/{project_id}/memory/scene-events/{record_id}
GET /api/projects/{project_id}/memory/scene-events/{record_id}/provenance
GET /api/projects/{project_id}/memory/scene-events/health
```

### `GET /api/projects/{project_id}/memory/scene-events`

Purpose:

- Return approved scene review, event/action, and causality-note list payloads and warning summaries for one project.
- Optionally include approved-only counts and lightweight candidate backlog counts labeled separately.

Request shape:

- Path parameter: `project_id`.
- Optional local filter/search query parameters if implemented.
- No body.

Response shape:

- Project ID.
- Approved scene/event/causality records or compact list rows.
- Approved counts by `record_type`.
- Candidate backlog counts by status if included, labeled candidate-only.
- Warnings.

Validation:

- Safe project ID.
- Existing project.
- Optional existing memory folder read-only.
- `memory/scene_reviews.json`, `memory/events.json`, `memory/actions.json`, `memory/causality.json`, or equivalent approved store envelope is valid if present.
- Record IDs are unique and safe.

Path safety:

- Read only inside selected project.
- Reject traversal, absolute paths, empty IDs, `"."`, and `".."`.
- Return project-relative source references only.
- Do not expose absolute host filesystem paths.

Candidate/canon boundary:

- Return applied approved records only.
- Candidate records must remain OMI links/counts only.
- Promotion records are audit-only unless linked from an approved record after apply-promotion.

No-prose boundary:

- Return stored fields only.
- No generated scene summaries, event summaries, causal explanations, fixes, rewrites, source paraphrases, bridge scenes, retcons, or proof claims.

Source/evidence safety:

- Return only bounded, owner-approved, copyright-safe excerpts when stored.
- Hide or warn on unsafe excerpt state.
- Do not return full source bodies.

Expected errors:

- 400 invalid project ID or filters.
- 404 missing project.
- 422 corrupt memory metadata, unsupported schema, duplicate IDs, unsafe IDs, unsupported locator, type/status conflict, cause/effect conflict, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/scene-events/{record_id}`

Purpose:

- Return one approved scene/event/causality detail payload.

Request shape:

- Path parameters: `project_id`, `record_id`.
- No body.

Response shape:

- Approved record detail.
- Source locator status.
- Cause/effect link status.
- Evidence/provenance status.
- Linked approved memory status.
- Linked source document status.
- Related story-knowledge status.
- Warnings.

Validation:

- Safe project ID and record ID.
- Record exists in approved memory/audit store.
- Record type is supported.
- Linked IDs are safe before lookup.

Path safety:

- No filesystem paths from request values.
- No traversal, absolute paths, or host path leakage.

Candidate/canon boundary:

- Detail is approved memory/audit context only.
- Source candidate and promotion links are provenance only.
- Do not hydrate missing approved fields from OMI candidates.

No-prose boundary:

- Return stored owner-approved descriptions, event/action summaries, owner notes, and resolution notes only.
- No generated scene summaries, event analysis, causal explanations, fixes, rewrites, bridge scenes, retcons, or diagnostic prose generation.

Source/evidence safety:

- Return only bounded source locator metadata and copyright-safe excerpts.

Expected errors:

- 400 invalid ID.
- 404 missing project, missing category file where not treated as list empty, or missing record.
- 422 corrupt category file, duplicate IDs, unsafe links, unsupported locator, causality conflict, invalid cause/effect link, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/scene-events/{record_id}/provenance`

Purpose:

- Return compact provenance chain, source candidate, promotion record, approved-memory link, source locator, evidence, source hash, source-safety data, and cause/effect audit context for one approved record.

Request shape:

- Path parameters: `project_id`, `record_id`.
- No body.

Response shape:

- Provenance chain summary.
- Source locator metadata.
- Evidence IDs and status.
- Source candidate IDs and status.
- Promotion record IDs and audit status.
- Linked approved memory records and status.
- Cause/effect linked record status.
- Source hashes and source-safety warnings.
- Warnings.

Validation:

- Safe IDs.
- Provenance objects are bounded JSON objects/arrays.
- Source links remain project-relative where applicable.
- Provenance chain must not be trusted if cyclic, broken, corrupt, or missing required references.

Path safety:

- Do not expose raw host filesystem paths.
- Do not read long source bodies.

Candidate/canon boundary:

- Provenance explains how the approved record was created; it does not display candidates as approved truth.

No-prose boundary:

- No generated evidence narratives, source summaries, explanations, interpretations, retcons, fixes, or proof claims.

Source/evidence safety:

- Do not return unapproved or unsafe excerpts.
- Flag unsafe excerpt/anchor/source display state without returning unsafe source text.

Expected errors:

- Invalid IDs.
- Missing approved record.
- Broken source candidate, promotion, memory, evidence, provenance, cause/effect, or source references.
- Cyclic provenance chain if represented.
- Corrupt provenance.
- Sanitized partial read failure.

### `GET /api/projects/{project_id}/memory/scene-events/health`

Purpose:

- Return non-destructive health warnings for scene/event/causality memory/audit state.

Request shape:

- Path parameter only, with optional validation depth in a later design.
- No body.

Response shape:

- Health status.
- Warning list with code, severity, target type, target ID, and sanitized message.
- Approved record count by record type.
- Candidate backlog count if included, labeled separately.
- No repair actions.

Validation:

- Safe project ID.
- Read-only scans only.
- Validate memory envelope, IDs, schema version, duplicate IDs, linked sources, source locators, linked approved entities, cause/effect links, related record links, event/action type/status conflicts, causality status conflicts, source hashes, source safety, and evidence presence.

Path safety:

- Scan only approved project-local memory/OMI references.
- Sanitize paths.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, split, retitle, infer truth, infer events, infer actions, infer causality, infer locators, re-anchor sources, or validate candidates as canon.

No-prose boundary:

- Warnings are factual status only.
- Do not propose fixes or rewrites.

Source/evidence safety:

- Flag unsafe excerpt/anchor/source display state without returning unsafe source text.

Expected errors:

- 400 invalid project ID.
- 404 missing project.
- 500 sanitized partial scan failure.

## 11. Frontend Planning

Do not implement UI in this task. Future components:

- `ApprovedSceneEventCausalityReviewPage`
- `SceneEventCausalityBoundaryBanner`
- `ApprovedSceneReviewList`
- `ApprovedEventActionList`
- `CausalityNotesList`
- `SceneEventCausalityRecordDetailPanel`
- `SceneEventSourceLocatorPanel`
- `CauseEffectLinkPanel`
- `RelatedTimelineSnapshot`
- `RelatedPlotThreadSnapshot`
- `RelatedContinuityContradictionSnapshot`
- `LinkedSceneEventApprovedMemorySnapshot`
- `SceneEventEvidencePanel`
- `SceneEventSourceLinksPanel`
- `SceneEventCandidateBacklogSnapshot`
- `SceneEventSearchFilterControls`
- `SceneEventWarningsPanel`
- `SceneEventEmptyState`
- `SceneEventFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No generated scene summary button.
- No generated causal explanation button.
- No generated fix button.
- No rewrite button.
- No semantic-search button in the first version.
- No controls like extract events, infer causality, explain cause/effect, fix scene logic, rewrite scene, generate bridge scene, patch plot hole, create retcon, classify Dramatica Driver, classify Dramatica role, convert to training data, or promote candidate.
- Search/filter controls must be local and deterministic.
- Candidate backlog controls must route to OMI and remain labeled as candidate/audit state.
- Detail panels must display stored approved fields only.
- Warning panels must be non-destructive.
- Labels must distinguish approved scene/event/causality records, OMI candidates, promotion records, source/evidence, approved memory, source safety warnings, unresolved causality, and future/not implemented states.
- Missing fields must show `Unknown`, `Not approved yet`, `Not recorded`, or `Locator unavailable`.
- Opening the page must not trigger analysis, extraction, causal inference, semantic search, graph visualization, timeline visualization, model calls, OMI record creation, promotion, memory/canon mutation, project-file writes, JSONL writes, or dataset updates.

## 12. Future Tests

Future implementation tests should cover:

- No memory directory / no approved records.
- Load approved scene/event/causality records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt scene/event/causality memory file warning.
- Duplicate record IDs warning.
- Unsafe IDs rejected.
- Broken source scene/chapter/note/material links warning.
- Unsupported locator warning.
- Locator out-of-range warning if represented.
- Source hash mismatch warning if represented.
- Broken cause/effect links warning.
- Cause/effect cycle warning if represented.
- Cause/effect self-link warning.
- Broken timeline/plot/continuity/open-question/contradiction links warning.
- Broken candidate/promotion/memory links warning.
- Event/action/status/causality conflict warnings.
- Copyright-unsafe excerpt warning.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- Page does not write JSONL/training records.
- No AI prose-generation controls.
- No generated summaries/explanations/fixes/rewrites.
- No invented events/actions/causal links/evidence.
- No extraction or causal inference in first version.
- No source re-anchoring in first version.
- No Dramatica structural/thematic proof claims.
- `training/data/dataset_manifest.json` unchanged.

## 13. Deferred Decisions

Deferred to later tasks:

- Exact runtime schema for `scene_review_memory_record`, `event_action_memory_record`, and `causality_note_memory_record`.
- Whether scene reviews, events, actions, and causality live in separate files, a single `memory/scene_events.json`, extensions of `memory/timeline.json`, or an approved audit store.
- Whether `timeline_event_memory_record` can be reused for some approved event/action records without blurring timeline ownership.
- Exact allowed values for `review_type`, `event_type`, `action_type`, `causality_type`, `status`, `scope`, and `resolution_status`.
- Exact memory envelope version and migration behavior.
- Whether first implementation reads directly from category files, a memory summary endpoint, or both.
- Exact source locator format for scene, chapter, note, material, memory-record, candidate, and promotion links.
- Exact cause/effect relation model: direct IDs, relation objects, typed edges, or separate approved causality records.
- Whether cause/effect cycle checks are needed in the first implementation or only when graph visualization exists.
- Exact OMI filter for scene/event/action/causality candidates, including whether these are distinct from timeline candidates.
- Exact source hash algorithm and hash-mismatch display.
- Exact copyright/source safety policy for owner-authored, owner-supplied, public-domain, external, and unknown-license material.
- Exact apply-promotion behavior, rollback, and record supersession mechanics.
- Whether and when owner-controlled edit/resolution workflow is added.
- Whether future visualization uses a graph, table, source matrix, timeline overlay, or side-by-side evidence view.
- Whether semantic search belongs in a later approved-memory search page or this page.
- Any future Dramatica structural/thematic event/action/causality taxonomy.
- Browser/manual acceptance checklist for implemented Approved Scene / Event / Causality Review page.

## 14. Implementation Non-Goals

WORKSPACE-024 does not implement:

- Approved Scene / Event / Causality Review UI.
- Backend memory/canon routes.
- Apply-promotion.
- Event extraction.
- Action extraction.
- Causality extraction.
- Causal inference.
- Scene summaries.
- Timeline visualization.
- Causality graph visualization.
- Contradiction detection.
- Semantic search.
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
- Staging, commits, or pushes.
