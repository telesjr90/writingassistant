# WORKSPACE-022: Approved Annotations / Evidence / Provenance Page Spec

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

The Approved Annotations / Evidence / Provenance page should be the future project-local destination for owner-approved annotation, evidence-span, and provenance/audit records. It must show only records that have been explicitly approved and applied into the approved memory/canon or equivalent approved audit store. Pending, rejected, archived, needs-revision, and approved-but-not-applied annotation/evidence/provenance candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

This page is not a generated summary page, not a writing-assistance page, not an extractor page, not a semantic-search page, not a contradiction-detection page, and not a Dramatica structural proof page.

The page should:

- Show owner-approved `annotation_memory_record`, `evidence_span_memory_record`, `provenance_record`, or equivalent approved audit records for the selected project.
- Read approved annotation/evidence/provenance truth only from future memory files such as `memory/annotations.json`, `memory/evidence_spans.json`, `memory/provenance.json`, or an equivalent approved memory/audit store.
- Clearly distinguish approved evidence/provenance truth and audit context from OMI annotation/evidence/provenance candidates.
- Link approved evidence/provenance to project-local source documents where available.
- Link evidence/provenance records to approved memory/canon records and source candidates where available.
- Show unresolved, missing, broken, ambiguous, partial, or unsupported fields honestly.
- Show an empty state when no approved annotation/evidence/provenance records exist.
- Link to OMI Ideas / Candidates for pending annotation/evidence/provenance candidates.
- Link to related characters, locations/settings, timeline events, plot threads, continuity/consistency issues, open questions, relationships, organizations/groups, objects/items, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic extraction.
- Avoid evidence-span extraction.
- Avoid provenance indexing.
- Avoid generated summaries.
- Avoid generated interpretations.
- Avoid generated evidence explanations.
- Avoid rewritten source text.
- Avoid semantic search.
- Avoid contradiction detection.
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

- Source material may provide evidence/provenance for candidates and approved records.
- Source material is not approved memory/canon by default.
- A source locator, source excerpt, or source hash does not create approved truth by itself.
- Source material must not be copied, summarized, rewritten, or re-anchored into approved memory/canon by opening this page.

### OMI Annotation / Evidence / Provenance Candidates

Definition:

- Structured `annotation_candidate`, evidence-span candidate, provenance candidate, or future equivalent records that have not been applied to approved memory/canon or an approved audit store.

Rules:

- Candidates are not canon.
- Candidates must not appear in the approved record list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate record type, locator, certainty, linked memory records, source safety state, and evidence/provenance meaning must not be inferred as approved truth.

### Approved-but-Not-Applied Candidates

Definition:

- Annotation/evidence/provenance candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon or an approved audit store.

Rules:

- Approved-but-not-applied candidates are not approved annotation/evidence/provenance records.
- Approved-but-not-applied candidates must not appear in the approved record list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are audit-only unless future apply-promotion has created or updated approved memory/canon.
- Promotion records present without an approved memory/audit record must show an audit-only warning or candidate backlog state, not approved evidence/provenance truth.
- Source candidate and promotion audit links may be shown as provenance/audit context only.

### Approved Annotation / Evidence / Provenance Records

Definition:

- Durable owner-approved `annotation_memory_record`, `evidence_span_memory_record`, `provenance_record`, or equivalent records written to the future approved memory/audit store by a future apply-promotion step or another explicitly designed owner-approved process.

Rules:

- Applied approved records are the only records allowed in the approved record list.
- They should preserve source candidate IDs, promotion record IDs, evidence/provenance, source locators, linked approved-memory IDs, approval metadata, uncertainty, revision metadata, and source safety state where available.
- They remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/annotations.json`, `memory/evidence_spans.json`, `memory/provenance.json`, or equivalent records.

### Source Locator and Excerpt State

Definition:

- Future stored fields that identify a source document, source locator type, source locator value, optional line/paragraph/span offsets, optional source hash, and optional owner-approved short excerpt.

Rules:

- Source locators must come from approved records only.
- Broken, missing, unsupported, out-of-range, or hash-mismatched locators must surface non-destructive warnings.
- Source excerpts must be limited, owner-approved, copyright-safe, and used only for locator/context display.
- The page must not generate, expand, rewrite, or invent excerpts.
- The page must not re-anchor source text automatically.

### Future Dramatica Structural or Thematic Claims

Definition:

- Future Dramatica storyform-specific claims such as throughline proof, Relationship Story proof, IC/RS proof, Signpost, Concern, Issue, Problem/Solution, CIPS, dynamics, or thematic proof.

Rules:

- Dramatica-specific evidence/provenance classification is deferred.
- Evidence records must not be presented as Dramatica proof unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.
- Generic annotations, evidence spans, and provenance links are not Dramatica structural or thematic claims.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, analysis system, or future annotation/evidence helper.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved display.
- The first implementation of this page must not call a model.
- Generated summaries, generated explanations, generated interpretations, rewritten excerpts, invented evidence, and generated Dramatica proof are prohibited.

Required labels:

| Label | Use |
| --- | --- |
| `Approved Annotation / Evidence / Provenance` | Marks each applied approved record. |
| `Approved Memory` | Marks approved memory/canon records linked by the selected evidence/provenance record. |
| `Approved Audit Context` | Marks approved provenance/audit records that support traceability but are not story prose. |
| `Candidate` | Marks OMI annotation/evidence/provenance candidates outside the approved list. |
| `Pending Candidate` | Marks pending candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI candidates. |
| `Needs Revision` | Marks candidates needing revision. |
| `Archived Candidate` | Marks archived OMI candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no approved memory/audit record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Locator Unavailable` | Marks missing, unsupported, or broken locator state. |
| `Evidence Required` | Marks approved records whose referenced claim needs evidence but none is recorded. |
| `Insufficient Evidence` | Marks evidence that exists but is incomplete, ambiguous, weak, unsafe, or not enough for the intended claim. |
| `Unknown` | Marks approved fields the owner has not approved or the system cannot verify. |
| `Not Approved Yet` | Marks fields pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields intentionally absent or not captured. |
| `Copyright / Source Safety Warning` | Marks unsafe or unapproved excerpt/source-display state. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Not Dramatica Proof` | Marks the page and relevant records as evidence/provenance audit context, not Dramatica proof. |
| `Future / Not Implemented` | Marks editing, merge/split, extraction, semantic search, contradiction detection, graph visualization, apply-promotion, JSONL conversion, and Dramatica classification. |

## 3. Approved Display Model

Approved annotation/evidence/provenance records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `record_id` | Stable approved record ID; reject unsafe IDs and show duplicate warnings. |
| `record_type` | Stored type such as `annotation_memory_record`, `evidence_span_memory_record`, `provenance_record`, or equivalent. |
| `display_title` | Owner-approved display label; do not generate or retitle. |
| `annotation_type` | Stored annotation type only; show `Unknown` when missing. |
| `evidence_type` | Stored evidence type only; do not infer from source text or candidates. |
| `provenance_type` | Stored provenance/audit type only; do not infer. |
| `status` | Stored record status only. |
| `scope` | Stored scope such as project, chapter, scene, note, material, memory record, candidate, promotion, or unknown. |
| `short_owner_approved_description` | Stored owner-approved description only; no generated summaries, explanations, or interpretations. |
| `source_project_id` | Stored project-local source project ID; missing or mismatched IDs warn. |
| `source_document_type` | Stored source type such as chapter, scene, note, material, OMI candidate, promotion record, memory record, bible, storyform, or project metadata. |
| `source_document_id` | Stored source document ID; broken references warn. |
| `source_chapter_id` | Stored source chapter ID if available. |
| `source_scene_id` | Stored source scene ID if available. |
| `source_note_id` | Stored source note ID if available. |
| `source_material_id` | Stored source material ID if available. |
| `source_file_label` | Stored safe display label only; do not expose host filesystem paths. |
| `source_locator_type` | Stored locator type such as offset, line range, paragraph index, anchor text, hash, source path, or unknown. |
| `source_locator` | Stored locator value only; unsupported or broken locators warn. |
| `source_hash if stored` | Stored source snapshot hash; mismatch warns and does not auto-repair. |
| `source_quote_excerpt if owner-approved and copyright-safe` | Limited owner-approved excerpt only; no generated, expanded, rewritten, or unsafe source text. |
| `evidence_span_start if stored` | Stored span start; out-of-range values warn. |
| `evidence_span_end if stored` | Stored span end; out-of-range values warn. |
| `line_start if stored` | Stored line start; out-of-range values warn. |
| `line_end if stored` | Stored line end; out-of-range values warn. |
| `paragraph_index if stored` | Stored paragraph locator; out-of-range values warn. |
| `anchor_text if stored and copyright-safe` | Limited owner-approved anchor text only; unsafe anchors warn. |
| `linked_candidate_ids` | Candidate links for provenance only; candidates remain OMI records. |
| `linked_promotion_record_ids` | Promotion audit links only. |
| `linked_memory_record_ids` | Approved memory/canon links only; broken links warn. |
| `linked_character_ids` | Approved character links only; broken links warn. |
| `linked_location_ids` | Approved location/setting links only; broken links warn. |
| `linked_timeline_event_ids` | Approved timeline links only; broken links warn. |
| `linked_plot_thread_ids` | Approved plot-thread links only; broken links warn. |
| `linked_continuity_issue_ids` | Approved continuity/consistency links only; broken links warn. |
| `linked_open_question_ids` | Approved open-question links only; broken links warn. |
| `linked_relationship_ids` | Approved relationship links only; broken links warn. |
| `linked_organization_ids` | Approved organization/group links only; broken links warn. |
| `linked_object_ids` | Approved object/item links only; broken links warn. |
| `confidence/certainty label if stored` | Stored confidence/certainty at approval only; not objective truth or Dramatica proof. |
| `owner_notes` | Stored owner notes only. |
| `created_at` | Stored creation timestamp. |
| `updated_at` | Stored update timestamp. |
| `approved_at` | Stored approval timestamp. |
| `approved_by` | Stored owner/reviewer identifier. |
| `source_candidate_ids` | Candidate IDs that led to the approved record; provenance only. |
| `promotion_record_ids` | Promotion audit IDs; provenance only. |
| `revision_history` | Stored revision metadata. |
| `supersedes_record_ids` | Older approved records replaced by this one. |
| `superseded_by_record_id` | Newer approved record replacing this one. |
| `tags` | Stored approved tags. |
| `notes` | Stored notes, ambiguity notes, uncertainty notes, source-safety notes, or implementation notes. |

Display rules:

- Unapproved candidates must not appear as truth.
- Generated summaries, generated explanations, generated interpretations, rewritten excerpts, and invented evidence are prohibited.
- Missing fields must be shown as `Unknown`, `Not approved yet`, `Not recorded`, or `Locator unavailable`.
- Evidence/provenance records may remain ambiguous, unresolved, partly unknown, insufficiently evidenced, or locator-limited without implying an error.
- Evidence/provenance records support approved memory but do not themselves automatically promote or validate candidates.
- Evidence records must not be presented as Dramatica proof unless a later Dramatica-specific approved memory record explicitly says so.

## 4. First-Version Page Sections

Each section must define purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

### Page Header

Purpose:

- Identify the active project and Approved Annotations / Evidence / Provenance area.
- Show approved record count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved annotation/evidence/provenance records from `memory/annotations.json`, `memory/evidence_spans.json`, `memory/provenance.json`, or equivalent approved memory/audit store if present.

Candidate/canon boundary:

- Header approved count must come from applied approved records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, evidence explanations, provenance narratives, interpretations, or Dramatica proof.

Empty state:

- Show that no approved annotation/evidence/provenance records exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Annotations / Evidence / Provenance Boundary Banner

Purpose:

- Explain that the page shows approved annotation/evidence/provenance records only.
- Point pending annotation/evidence/provenance candidates to OMI.
- State that the page is not a generated summary, writing, interpretation, semantic search, contradiction detection, source-rewrite, extractor, or Dramatica proof surface.

Data source:

- Static page copy.
- Optional lightweight OMI annotation/evidence/provenance candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not approved truth.
- State that approved records require future apply-promotion or an explicitly designed approved audit process.

No-prose boundary:

- Prohibit generated summaries, generated explanations, generated interpretations, generated excerpts, source rewrites, evidence invention, and prose-patching controls.

Empty state:

- Banner remains visible even when no approved records exist.

Error state:

- Banner remains visible even when optional OMI counts cannot load.

### Approved Record List

Purpose:

- List approved annotation/evidence/provenance records for selection and local filtering.

Data source:

- Applied records from approved memory/audit store only.
- `memory/index.json` may support navigation but must not override category files.

Candidate/canon boundary:

- Rows must be applied approved records only.
- Candidate rows must not be included.

No-prose boundary:

- List shows stored labels, types, statuses, tags, source labels, and warning badges only.
- No generated descriptions, summaries, interpretations, proof narratives, or evidence explanations.

Empty state:

- Show no approved annotation/evidence/provenance records and link to OMI Ideas / Candidates for candidate review.

Error state:

- Duplicate IDs, unsafe IDs, corrupt category envelope, unsupported schema, or unreadable records show warnings and block unsafe display for affected records.

### Record Detail Panel

Purpose:

- Show selected approved record details and related approved links.

Data source:

- Selected applied annotation/evidence/provenance record.
- Lightweight linked approved records, source documents, and OMI audit links where available.

Candidate/canon boundary:

- Detail fields are approved truth/audit context only when stored in the approved record.
- Source candidate and promotion links are provenance, not candidate truth display.

No-prose boundary:

- Do not generate annotations, summaries, evidence explanations, source interpretations, or Dramatica proof.
- Owner-approved descriptions and notes may be displayed exactly as stored.

Empty state:

- No selection shows choose-a-record guidance.

Error state:

- Broken linked records show warnings while preserving the stored approved record.

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

### Evidence Span Panel

Purpose:

- Show approved evidence-span metadata such as start/end offsets, line range, paragraph index, anchor text state, quote safety, evidence type, and confidence/certainty label when stored.

Data source:

- Approved evidence-span fields on the selected record.

Candidate/canon boundary:

- Evidence spans support traceability but do not automatically prove candidate truth, promote candidates, or establish Dramatica proof.

No-prose boundary:

- No generated evidence explanations, generated summaries, expanded excerpts, or source rewrites.

Empty state:

- Show `Evidence Required`, `Insufficient Evidence`, `Unknown`, `Not recorded`, or `Locator unavailable` as appropriate.

Error state:

- Span out of range, anchor unsafe, anchor missing, copyright-unsafe excerpt, unsupported locator, or hash mismatch show warnings and do not auto-repair.

### Provenance Chain Panel

Purpose:

- Show compact source-to-candidate-to-promotion-to-approved-record chain where stored.

Data source:

- Approved record provenance fields.
- Linked candidate IDs and promotion record IDs by link/status only.
- Approved memory record links where available.

Candidate/canon boundary:

- Candidate and promotion links are audit context only.
- Promotion records are not canon unless future apply-promotion has created/updated approved memory.

No-prose boundary:

- No generated provenance narratives, explanations, or interpretations.

Empty state:

- Show no provenance chain recorded.

Error state:

- Broken, missing, or cyclic provenance chains show warnings and do not auto-repair.

### Linked Approved Memory Snapshot

Purpose:

- Show linked approved memory/canon records supported or referenced by the selected evidence/provenance record.

Data source:

- Stored `linked_memory_record_ids` and type-specific linked IDs.
- Approved memory files only when present.

Candidate/canon boundary:

- Linked records must be approved memory/canon records only.
- Pending candidates may be counted separately but not shown as linked truth.

No-prose boundary:

- Do not generate link explanations, summaries, proof narratives, or interpretations.

Empty state:

- Show no linked approved memory records.

Error state:

- Broken or unsafe linked memory references show warnings without repair.

### Linked Candidate / Promotion Audit Snapshot

Purpose:

- Show source candidate IDs and promotion record IDs as audit context.

Data source:

- OMI candidate metadata and promotion records where available.

Candidate/canon boundary:

- Counts and links only; candidate contents remain in OMI.
- Approved-but-not-applied candidates and promotion records must be labeled `Not Yet Applied` and `Promotion Record Only`.

No-prose boundary:

- No generated candidate summaries or promotion explanations.

Empty state:

- Show no linked candidates or promotion records.

Error state:

- Corrupt OMI metadata shows degraded counts and warnings.

### Related Story Knowledge Snapshot

Purpose:

- Show stored links from the selected approved record to approved characters, locations/settings, timeline events, plot threads, continuity/consistency issues, open questions, relationships, organizations/groups, objects/items, chapters, scenes, notes, and materials.

Data source:

- Approved record link fields and approved linked-memory records.
- Source document metadata for chapters/scenes/notes/materials where safe.

Candidate/canon boundary:

- Story-knowledge links must be approved records only.
- Source document links are source/evidence context, not canon by default.

No-prose boundary:

- Do not generate relation explanations, summaries, continuity fixes, graph descriptions, or Dramatica proof.

Empty state:

- Show no related approved story knowledge.

Error state:

- Broken linked story-knowledge references or related pages not implemented show warnings/placeholders.

### Copyright / Source Safety Notice

Purpose:

- Explain and enforce safe source display boundaries for excerpts, anchors, locators, hashes, and external/reference material.

Data source:

- Stored source safety fields, source document type, license/provenance metadata where available, and fixed policy copy.

Candidate/canon boundary:

- Source safety state is display/audit metadata unless approved in the record.
- Unsafe excerpts do not create or remove approved truth.

No-prose boundary:

- Do not generate excerpts, paraphrases, replacements, interpretations, or source summaries.

Empty state:

- Show that no source excerpt is approved for display.

Error state:

- Copyright-unsafe excerpt, unapproved excerpt, unknown license/source safety, or unsafe anchor text shows a warning and hides the excerpt.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for pending annotation/evidence/provenance candidates outside the approved list.

Data source:

- OMI candidate metadata and promotion records where available.

Candidate/canon boundary:

- Counts and links only; candidate contents remain in OMI.
- Approved-but-not-applied candidates and promotion records must be labeled `Not Yet Applied` and `Promotion Record Only`.

No-prose boundary:

- No candidate summaries generated for this page.

Empty state:

- Show no annotation/evidence/provenance candidates in OMI.

Error state:

- Corrupt OMI metadata shows degraded counts and warnings.

### Empty State

Purpose:

- Explain the valid state where no approved annotation/evidence/provenance records exist yet.

Data source:

- Approved memory/audit counts and optional OMI counts.

Candidate/canon boundary:

- State that pending candidates, approved candidates, and promotion records are not approved memory/canon.

No-prose boundary:

- Empty-state guidance is operational only.
- Do not suggest generating annotations, explanations, excerpts, summaries, interpretations, or proof.

Empty state:

- Missing `memory/`, missing `memory/annotations.json`, missing `memory/evidence_spans.json`, missing `memory/provenance.json`, or zero records all show a valid empty approved state.

Error state:

- If memory metadata is corrupt, show warning state instead of a clean empty state.

### Warning State

Purpose:

- Surface non-destructive memory, locator, evidence, provenance, schema, source-safety, and candidate/canon warnings.

Data source:

- Project validation, memory category validation, OMI audit link validation, approved record cross-link validation, source-link validation, and source-safety validation.

Candidate/canon boundary:

- Warnings must not repair, promote, delete, merge, split, retitle, infer locators, infer source safety, re-anchor source text, invent evidence, or rewrite records.

No-prose boundary:

- Warning copy is factual status text only.
- No generated fixes, explanations, interpretations, or replacement prose.

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

- Navigation links must not launch writing, rewriting, generation, interpretation, semantic search, contradiction detection, extraction, or proof actions.

Empty state:

- Related page links may show `Related Page Not Implemented`.

Error state:

- Missing adjacent routes show future-only/placeholder labels.

## 5. Candidate / Canon Separation

Approved records:

- Approved records are read from future memory files such as `memory/annotations.json`, `memory/evidence_spans.json`, `memory/provenance.json`, or an equivalent approved memory/audit store.
- Approved records are durable project truth or approved audit context only when a future apply-promotion or explicitly designed owner-approved process has created or updated the approved record.
- Approved records should preserve source candidate IDs, promotion record IDs, evidence/provenance, source locators, source safety state, linked memory records, approval metadata, uncertainty, and revision metadata where available.

OMI candidates:

- OMI annotation/evidence/provenance candidates remain in OMI candidates.
- Pending, rejected, archived, needs-revision, duplicate, uncertain, and approved-but-not-applied candidates do not appear as approved evidence/provenance truth.
- Candidate backlog may show counts and links only.
- Source candidate and promotion audit links may be shown as provenance/audit context.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved memory.
- Promotion records present without approved memory/audit records must not count as approved annotation/evidence/provenance records.

Inference limits:

- Record type, locator, certainty, linked memory records, source safety state, and evidence/provenance meaning must not be inferred as truth from candidate output.
- Evidence/provenance records support approved memory but do not themselves automatically promote or validate candidates.
- Evidence/provenance records are not Dramatica structural/thematic claims unless a later Dramatica-specific approved memory record explicitly says so.

## 6. First-Version Operations

Allowed first-version operations:

- View approved annotation/evidence/provenance record list.
- View record details.
- Filter/search approved records locally.
- Open linked source scene, note, material, or chapter if available.
- Open linked approved memory/canon record if available.
- Open linked OMI candidate or promotion record if available.
- Show source locator panel.
- Show evidence span metadata.
- Show provenance chain snapshot.
- Show linked story-knowledge snapshot.
- Show copyright/source safety notice.

Future-only operations:

- Edit approved annotation/evidence/provenance memory.
- Merge/split approved evidence records.
- Archive/restore approved records.
- Apply-promotion.
- Extract evidence spans.
- Generate annotations.
- Generate summaries.
- Generate interpretations.
- Generate source excerpts.
- Semantic search.
- Automatic source re-anchoring.
- Evidence graph visualization.
- Contradiction detection.
- Dramatica structural/thematic proof classification.
- JSONL/training conversion.

## 7. Local Search / Filter Planning

First-version local search/filter may operate over approved-record data only:

- `record_id`
- `record_type`
- `display_title`
- `annotation_type`
- `evidence_type`
- `provenance_type`
- `status`
- `scope`
- `source_document_type`
- `source_document_id`
- `source_chapter_id`
- `source_scene_id`
- `source_note_id`
- `source_material_id`
- `source_locator_type`
- `linked_candidate_ids`
- `linked_promotion_record_ids`
- `linked_memory_record_ids`
- Linked character IDs.
- Linked location IDs.
- Linked timeline event IDs.
- Linked plot-thread IDs.
- Linked continuity/open-question/relationship/organization/object IDs.
- `tags` if available.
- Approved description if available.

Rules:

- Search is local and deterministic.
- Search labels results as approved-only.
- No semantic search in the first version.
- No model/Ollama calls.
- No generated summaries.
- No generated explanations.
- No extraction during search.
- No re-anchoring during search.
- No contradiction detection during search.
- No Dramatica classification during search.
- Search must not create OMI records, promotion records, memory/canon records, JSONL records, or training data.
- Search must not mutate project files.

## 8. Warning and Invalid-State Behavior

Warnings are non-destructive. They must not auto-repair, auto-delete, rewrite identity, retitle, infer locators, re-anchor source text, invent evidence, generate summaries, promote candidates, mutate memory/canon, or leak host filesystem paths.

Required warning/invalid states:

- Missing `memory/`.
- Missing/corrupt `memory/annotations.json`.
- Missing/corrupt `memory/evidence_spans.json`.
- Missing/corrupt `memory/provenance.json`.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Approved record references missing promotion record.
- Approved record references missing approved memory record.
- Broken source document reference.
- Broken chapter/scene/note/material reference.
- Broken source locator.
- Source hash mismatch if represented.
- Unsafe IDs.
- Duplicate record IDs.
- Unsupported `source_locator_type`.
- Line/paragraph/span locator out of range if represented.
- Copyright-unsafe excerpt warning.
- Missing evidence for approved claim.
- Provenance chain broken.
- Provenance chain cyclic if represented.
- Candidate/promotion links broken.
- Linked story-knowledge references broken.
- Promotion records present but no approved memory record.
- OMI evidence/provenance candidates exist but no approved records yet.
- Related pages/entities not implemented yet.
- Corrupt `memory/index.json`.

Behavior:

- Missing memory folders and missing category files are valid empty states when no approved records exist.
- Corrupt memory files block approved display for the affected category and show a warning.
- Unsupported schema versions should show read-only or needs-migration warnings.
- Duplicate or unsafe IDs should fail closed for detail routing.
- Broken links should show target type and stored ID without exposing host paths.
- Locator warnings should preserve stored ambiguity rather than forcing a correction.
- Candidate backlog warnings must link to OMI and not display candidate content as truth.

## 9. API Planning

This section documents future route planning only. Do not implement routes in this task.

Annotations, evidence spans, and provenance may be represented as one evidence/audit endpoint family or split into parallel annotations/evidence/provenance endpoints in a later decision. A future project memory/canon summary endpoint may also compose these responses instead of dedicated route groups.

Every route must validate `project_id` as a safe single path component. Evidence routes must validate `record_id` as a safe record ID. Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose. Routes must not call Ollama or any model in the first implementation. Routes must not create OMI records, create memory files on read, apply promotions, write JSONL/training records, update dataset manifests, generate summaries, generate interpretations, extract evidence spans, re-anchor sources, or classify Dramatica proof.

### `GET /api/projects/{project_id}/memory/evidence`

Purpose:

- Return approved annotation/evidence/provenance list payload and warning summary.

Request shape:

- Path parameter: `project_id`.
- Optional local filter/search query parameters if implemented.

Response shape:

- Project ID.
- Approved annotation/evidence/provenance records or compact list rows.
- Candidate backlog counts by status if included, labeled candidate-only.
- Warnings.

Validation:

- Safe project ID.
- Existing project.
- Optional existing memory folder read-only.
- `memory/annotations.json`, `memory/evidence_spans.json`, `memory/provenance.json`, or equivalent approved store envelope is valid if present.
- Record IDs are unique and safe.

Path safety:

- Read only inside selected project.
- Do not expose absolute paths.

Candidate/canon boundary:

- Return applied approved records only.
- Candidate records must remain OMI links/counts only.

No-prose boundary:

- Return stored fields only.
- No generated summaries, explanations, interpretations, excerpts, or proof claims.

Copyright/source safety:

- Return only bounded, owner-approved, copyright-safe excerpts when stored.
- Hide or warn on unsafe excerpt state.

Expected errors:

- 400 invalid project ID or filters.
- 404 missing project.
- 422 corrupt memory metadata, unsupported schema, duplicate IDs, unsafe IDs, unsupported locator, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/evidence/{record_id}`

Purpose:

- Return one approved annotation/evidence/provenance detail payload.

Request shape:

- Path parameters: `project_id`, `record_id`.

Response shape:

- Approved record detail.
- Source locator status.
- Evidence span status.
- Linked approved story-knowledge status.
- Linked candidate/promotion audit status.
- Warnings.

Validation:

- Safe project ID and record ID.
- Record exists in approved memory/audit store.
- Linked IDs are safe before lookup.

Path safety:

- No traversal, absolute paths, or host path leakage.

Candidate/canon boundary:

- Detail is approved memory/audit context only.
- Source candidate and promotion links are provenance only.

No-prose boundary:

- Return stored owner-approved descriptions/notes only.
- No generated annotations, summaries, explanations, interpretations, or proof claims.

Copyright/source safety:

- Return only bounded source locator metadata and copyright-safe excerpts.

Expected errors:

- 400 invalid ID.
- 404 missing project, missing category file where not treated as list empty, or missing record.
- 422 corrupt category file, duplicate IDs, unsafe links, unsupported locator, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/evidence/{record_id}/provenance`

Purpose:

- Return compact provenance chain, source candidate, promotion record, approved-memory link, source locator, and source-safety data for one approved record.

Request shape:

- Path parameters: `project_id`, `record_id`.

Response shape:

- Provenance chain summary.
- Source candidate IDs and status.
- Promotion record IDs and audit status.
- Linked approved memory records and status.
- Source locators, hashes, and source-safety warnings.
- Warnings.

Validation:

- Safe IDs.
- Provenance objects are bounded JSON objects/arrays.
- Source links remain project-relative where applicable.
- Provenance chain must not be trusted if cyclic, broken, or corrupt.

Path safety:

- Do not expose raw host filesystem paths.
- Do not read long source bodies.

Candidate/canon boundary:

- Provenance explains how the approved record was created; it does not display candidates as approved truth.

No-prose boundary:

- No generated evidence narratives, source summaries, explanations, interpretations, or proof claims.

Copyright/source safety:

- Do not return unapproved or unsafe excerpts.

Expected errors:

- Invalid IDs.
- Missing approved record.
- Broken source candidate, promotion, memory, or provenance references.
- Cyclic provenance chain.
- Corrupt provenance.
- Sanitized partial read failure.

### `GET /api/projects/{project_id}/memory/evidence/health`

Purpose:

- Return non-destructive health warnings for annotation/evidence/provenance memory/audit state.

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

- Health checks must not repair, promote, delete, merge, split, retitle, infer truth, infer locators, re-anchor sources, or validate candidates as canon.

No-prose boundary:

- Warnings are factual status only.

Copyright/source safety:

- Flag unsafe excerpt/anchor/source display state without returning unsafe source text.

Expected errors:

- 400 invalid project ID.
- 404 missing project.
- 500 sanitized partial scan failure.

## 10. Frontend Planning

Do not implement UI in this task. Future components:

- `ApprovedAnnotationsEvidenceProvenancePage`
- `AnnotationsEvidenceBoundaryBanner`
- `ApprovedEvidenceRecordList`
- `ApprovedEvidenceRecordListItem`
- `EvidenceRecordDetailPanel`
- `SourceLocatorPanel`
- `EvidenceSpanPanel`
- `ProvenanceChainPanel`
- `LinkedApprovedMemorySnapshot`
- `LinkedCandidatePromotionAuditSnapshot`
- `RelatedStoryKnowledgeSnapshot`
- `CopyrightSourceSafetyNotice`
- `EvidenceCandidateBacklogSnapshot`
- `EvidenceSearchFilterControls`
- `EvidenceWarningsPanel`
- `EvidenceEmptyState`
- `EvidenceFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No generated annotation button.
- No generated summary button.
- No generated interpretation button.
- No semantic-search button in the first version.
- No controls like generate evidence, explain evidence, summarize source, rewrite source, create annotation, infer proof, classify Dramatica role, convert to training data, or promote candidate.
- Labels must distinguish approved records, OMI candidates, promotion records, source/evidence, approved memory, source safety warnings, and future/not implemented states.
- Missing fields must show `Unknown`, `Not approved yet`, `Not recorded`, or `Locator unavailable`.
- Opening the page must not trigger analysis, extraction, model calls, OMI record creation, promotion, memory/canon mutation, project-file writes, JSONL writes, or dataset updates.

## 11. Future Tests

Future implementation tests should cover:

- No memory directory / no approved records.
- Load approved evidence/provenance records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt annotation/evidence/provenance memory file warning.
- Duplicate record IDs warning.
- Unsafe IDs rejected.
- Broken source document links warning.
- Broken locator warning.
- Unsupported locator type warning.
- Source hash mismatch warning if represented.
- Copyright-unsafe excerpt warning.
- Broken candidate/promotion/memory links warning.
- Broken provenance chain warning.
- Cyclic provenance chain warning if represented.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- Page does not write JSONL/training records.
- No AI prose-generation controls.
- No generated annotations/summaries/explanations/interpretations.
- No invented evidence.
- No source re-anchoring in first version.
- No Dramatica structural/thematic proof claims.
- `training/data/dataset_manifest.json` unchanged.

## 12. Deferred Decisions

Deferred to later tasks:

- Whether annotations, evidence spans, and provenance live in separate files or one approved evidence/audit store.
- Whether `memory/evidence_spans.json` and `memory/provenance.json` are approved memory files, audit files, or derived indexes.
- Exact approved annotation/evidence/provenance record type enum.
- Exact source locator type enum and first-version locator strategy.
- Whether offsets, line ranges, paragraph indices, source hashes, anchor text, or a hybrid become required.
- Exact source hash algorithm and hash-mismatch display.
- Exact copyright/source safety policy for owner-authored, owner-supplied, public-domain, external, and unknown-license material.
- Whether approved evidence records may be edited directly or only through future OMI/apply-promotion revisions.
- Merge/split/archive/restore/supersede UI timing.
- Whether provenance-chain cyclic checks are needed in the first implementation.
- Whether evidence graph visualization is useful after approved memory exists.
- Whether semantic search belongs in a later approved-memory search page or this page.
- Browser/manual acceptance checklist for implemented Approved Annotations / Evidence / Provenance page.

## 13. Implementation Non-Goals

WORKSPACE-022 does not implement:

- Approved Annotations / Evidence / Provenance UI.
- Backend memory/canon routes.
- Apply-promotion.
- Annotation extraction.
- Evidence-span extraction.
- Provenance indexing.
- Semantic search.
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
