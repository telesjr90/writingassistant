# WORKSPACE-023: Approved Contradictions Page Spec

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
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Contradictions page should be the future project-local destination for owner-approved contradiction memory/canon records and approved cross-record conflict audit context. It must show only contradiction records that have been explicitly applied by a future apply-promotion step or equivalent owner-approved approved-memory process. Pending, rejected, archived, needs-revision, and approved-but-not-applied contradiction candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

This page is not an automatic contradiction detector, not a generated fix page, not a rewrite page, not a semantic-search page, not a graph visualization page, and not a Dramatica structural proof page. It must not generate fixes, rewrite scenes, generate explanations, infer contradictions from candidates, classify Dramatica structure, or prove storyform claims.

The page should:

- Show owner-approved `contradiction_memory_record` records or equivalent contradiction/cross-record conflict memory entries for the selected project.
- Read approved contradiction truth only from future memory files such as `memory/contradictions.json` or an equivalent approved memory/audit store.
- Clearly distinguish approved contradiction truth from OMI contradiction candidates.
- Distinguish approved contradictions from continuity/consistency warnings without duplicating the Continuity / Consistency page.
- Link approved contradiction records to evidence/provenance where available.
- Link contradiction sides/claims to project-local source documents where available.
- Link contradiction records to approved memory/canon records and source candidates where available.
- Show unresolved, missing, broken, uncertain, partial, or unsupported fields honestly.
- Show an empty state when no approved contradiction records exist.
- Link to OMI Ideas / Candidates for pending contradiction candidates.
- Link to related characters, locations/settings, timeline events, plot threads, continuity/consistency issues, open questions, relationships, organizations/groups, objects/items, annotations/evidence/provenance, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic detection.
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

## 2. Contradiction Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for contradiction candidates or approved contradiction records.
- Source material is not approved contradiction memory/canon by default.
- Two source locators that appear to disagree are not an approved contradiction unless an approved contradiction record says so.
- Source material must not be copied, summarized, rewritten, or re-anchored into approved contradiction memory/canon by opening this page.

### OMI Contradiction Candidates

Definition:

- Structured `contradiction_candidate`, `continuity_warning_candidate` with contradiction type, or future equivalent records that have not been applied to approved memory/canon.

Rules:

- Contradiction candidates are not canon.
- Contradiction candidates must not appear in the approved contradiction list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate contradiction type, severity, claim pair state, evidence state, related links, certainty, and resolution state must not be inferred as approved truth.

### Approved-but-Not-Applied Candidates

Definition:

- Contradiction candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved contradiction memory/canon.
- Approved-but-not-applied candidates must not appear in the approved contradiction list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are audit-only unless future apply-promotion has created or updated approved contradiction memory.
- Promotion records present without approved memory must show `Promotion Record Only` or `Not Yet Applied`, not approved contradiction truth.
- Source candidate and promotion audit links may be shown as provenance/audit context only.

### Applied Contradiction Memory Records

Definition:

- Durable owner-approved `contradiction_memory_record` records or equivalent cross-record conflict records written to the future approved memory store by a future apply-promotion step or another explicitly designed owner-approved process.

Rules:

- Applied contradiction records are the only records allowed in the approved contradiction list.
- They should preserve source candidate IDs, promotion record IDs, evidence/provenance, source locators for both claims, linked approved-memory IDs, approval metadata, uncertainty, resolution metadata, revision metadata, and source-safety state where available.
- They remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/contradictions.json` entries or equivalent records.

### Contradiction Versus Continuity / Consistency

Definition:

- Continuity / Consistency handles broader approved warnings and consistency issues. Approved Contradictions focuses on approved paired or multi-sided conflicts between stored claims, source locators, approved records, or project-local source references.

Rules:

- A contradiction may link to continuity/consistency records, but this page should not duplicate the full continuity issue workflow.
- Continuity warnings may include contradiction-like issues; only approved contradiction records appear here.
- Resolution status and claim-pair state must come from approved contradiction memory only.

### Source Locator and Excerpt State

Definition:

- Future stored fields that identify each claim side's source type, source ID, source locator value, optional line/paragraph/span offsets, optional source hash, and optional owner-approved short excerpt.

Rules:

- Source locators must come from approved records only.
- Broken, missing, unsupported, out-of-range, same-locator, or hash-mismatched locators must surface non-destructive warnings.
- Source excerpts must be limited, owner-approved, copyright-safe, and used only for locator/context display.
- The page must not generate, expand, rewrite, summarize, or invent excerpts.
- The page must not re-anchor source text automatically.

### Future Dramatica Structural or Thematic Claims

Definition:

- Future Dramatica storyform-specific claims such as throughline contradiction proof, Relationship Story proof, IC/RS proof, Signpost, Concern, Issue, Problem/Solution, CIPS, dynamics, or thematic proof.

Rules:

- Dramatica-specific contradiction classification is deferred.
- Contradiction records must not be presented as Dramatica structural or thematic proof unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.
- Generic contradictions, continuity conflicts, and cross-record conflicts are not Dramatica Issue, Variation, Problem, Solution, Relationship Story, Influence Character, CIPS, dynamics, or storyform proof.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, analysis system, or future contradiction helper.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved contradiction display.
- The first implementation of this page must not call a model.
- Generated contradiction analysis, generated summaries, generated explanations, generated fixes, rewrite suggestions, scene suggestions, and contradiction-repair suggestions are prohibited.

Required labels:

| Label | Use |
| --- | --- |
| `Approved Contradiction` | Marks each applied approved contradiction record. |
| `Approved Memory` | Marks approved memory/canon records linked by the contradiction. |
| `Approved Audit Context` | Marks approved provenance/audit records that support traceability but are not story prose. |
| `Candidate` | Marks OMI contradiction candidates outside the approved list. |
| `Pending Candidate` | Marks pending candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI candidates. |
| `Needs Revision` | Marks candidates needing revision. |
| `Archived Candidate` | Marks archived OMI candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no approved memory record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Locator Unavailable` | Marks missing, unsupported, broken, or unavailable locator state. |
| `Evidence Required` | Marks approved records whose referenced contradiction needs evidence but none is recorded. |
| `Insufficient Evidence` | Marks evidence that exists but is incomplete, ambiguous, one-sided, weak, unsafe, or not enough for the approved contradiction. |
| `Unknown` | Marks approved fields the owner has not approved or the system cannot verify. |
| `Not Approved Yet` | Marks fields pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields intentionally absent or not captured. |
| `Unresolved` | Marks contradiction records that remain unresolved by owner-approved metadata. |
| `Resolution Status Placeholder` | Marks first-version resolution management as future-only. |
| `Copyright / Source Safety Warning` | Marks unsafe or unapproved excerpt/source-display state. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Not Dramatica Proof` | Marks the page and relevant records as general story-knowledge/audit context, not Dramatica proof. |
| `Future / Not Implemented` | Marks editing, merge/split, archive/restore, detection, extraction, generated fixes, semantic search, source re-anchoring, graph visualization, apply-promotion, JSONL conversion, and Dramatica classification. |

## 3. Approved Contradiction Display Model

Approved contradiction records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `contradiction_id` | Stable approved contradiction ID; reject unsafe IDs and show duplicate warnings. |
| `display_title` | Owner-approved display label; do not generate, retitle, or rewrite. |
| `contradiction_type` | Stored type only, such as claim conflict, timeline conflict, location conflict, relationship conflict, object-state conflict, organization/membership conflict, source conflict, continuity contradiction, or cross-record conflict. |
| `contradiction_status` | Stored record status only. |
| `severity` | Stored severity only; do not infer from source text or candidates. |
| `resolution_status` | Stored resolution status only, such as unresolved, needs owner review, resolved, superseded, archived, not recorded, or uncertain. |
| `scope` | Stored scope such as project, chapter, scene, note, material, memory record, candidate, promotion, or unknown. |
| `short_owner_approved_description` | Stored owner-approved description only; no generated summaries, explanations, or fixes. |
| `claim_a_summary` | Stored approved claim A summary only; no generated restatement. |
| `claim_b_summary` | Stored approved claim B summary only; no generated restatement. |
| `claim_a_source_type` | Stored source type for claim A. |
| `claim_a_source_id` | Stored source ID for claim A; broken references warn. |
| `claim_a_source_locator` | Stored locator for claim A; unsupported or unavailable locators warn. |
| `claim_b_source_type` | Stored source type for claim B. |
| `claim_b_source_id` | Stored source ID for claim B; broken references warn. |
| `claim_b_source_locator` | Stored locator for claim B; unsupported or unavailable locators warn. |
| `claim_a_linked_memory_record_ids` | Approved memory/canon links for claim A only; broken links warn. |
| `claim_b_linked_memory_record_ids` | Approved memory/canon links for claim B only; broken links warn. |
| `affected_scene_ids` | Approved source references only; broken references warn. |
| `affected_chapter_ids` | Approved source references only; broken references warn. |
| `linked_note_ids` | Approved source/reference links only; broken references warn. |
| `linked_material_ids` | Approved source/reference links only; broken references warn. |
| `linked_character_ids` | Approved character links only; broken links warn. |
| `linked_location_ids` | Approved location/setting links only; broken links warn. |
| `linked_object_ids` | Approved object/item links only; broken links warn. |
| `linked_organization_ids` | Approved organization/group links only; broken links warn. |
| `linked_relationship_ids` | Approved relationship links only; broken links warn. |
| `linked_timeline_event_ids` | Approved timeline links only; broken links warn. |
| `linked_plot_thread_ids` | Approved plot-thread links only; broken links warn. |
| `linked_open_question_ids` | Approved open-question links only; broken links warn. |
| `linked_continuity_issue_ids` | Approved continuity/consistency links only; broken links warn. |
| `linked_annotation_ids` | Approved annotation links only; broken links warn. |
| `linked_evidence_record_ids` | Approved evidence links only; broken links warn. |
| `linked_provenance_record_ids` | Approved provenance/audit links only; broken links warn. |
| `related_contradiction_ids` | Related approved contradiction links only; broken or cyclic links warn. |
| `first_seen_source` | First approved source/provenance locator if stored. |
| `latest_seen_source` | Latest approved source/provenance locator if stored. |
| `evidence/provenance summary` | Compact stored evidence/provenance metadata only; avoid long source copies and generated explanations. |
| `confidence/certainty label if stored` | Stored confidence/certainty at approval only; not objective truth or Dramatica proof. |
| `owner_resolution_note` | Owner-approved resolution note only; no generated fix text. |
| `resolution_decision` | Stored owner decision metadata only; do not infer resolution. |
| `created_at` | Stored creation timestamp. |
| `updated_at` | Stored update timestamp. |
| `approved_at` | Stored approval timestamp. |
| `approved_by` | Stored owner/reviewer identifier. |
| `source_candidate_ids` | OMI candidate provenance links only. |
| `promotion_record_ids` | Promotion audit links only. |
| `revision_history` | Stored revision metadata. |
| `supersedes_record_ids` | Older approved contradiction records replaced by this one. |
| `superseded_by_record_id` | Newer approved contradiction record replacing this one. |
| `tags` | Stored approved tags. |
| `notes` | Stored owner notes, ambiguity notes, uncertainty notes, source-safety notes, or implementation notes. |

Display clarifications:

- Unapproved candidates must not appear as truth.
- Generated contradiction analysis, generated summaries, generated explanations, generated fixes, rewrite suggestions, scene suggestions, and contradiction-repair suggestions are prohibited.
- Source excerpts must be limited, owner-approved, copyright-safe, and used only for locator/context display.
- Missing fields must be shown as `Unknown`, `Not approved yet`, `Not recorded`, or `Locator unavailable`.
- A contradiction may remain unresolved, uncertain, or partly unknown without implying an error.
- Contradiction records support approved memory review but do not themselves automatically promote, repair, or validate candidates.
- Contradiction records must not be presented as Dramatica Issue, Variation, Problem, Solution, Relationship Story, Influence Character, CIPS, dynamics, or storyform proof.

## 4. First-Version Page Sections

Each section must define purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

### Page Header

Purpose:

- Identify the active project and Approved Contradictions area.
- Show approved contradiction count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved contradiction records from `memory/contradictions.json` or an equivalent approved memory/audit store if present.

Candidate/canon boundary:

- Header approved count must come from applied approved records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, contradiction summaries, explanations, fixes, or Dramatica proof.

Empty state:

- Show that no approved contradiction records exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Contradictions Boundary Banner

Purpose:

- Explain that the page shows approved contradiction records only.
- Point pending contradiction candidates to OMI.
- State that the page is not a detector, generated explanation surface, generated fix surface, rewrite surface, semantic-search surface, graph visualization, or Dramatica proof page.

Data source:

- Static page copy.
- Optional lightweight OMI contradiction candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not approved truth.
- State that approved contradictions require future apply-promotion or an explicitly designed approved memory/audit process.

No-prose boundary:

- Prohibit generated explanations, generated fixes, rewrite suggestions, scene suggestions, bridge scenes, plot-hole patches, retcons, generated summaries, source rewrites, and prose-patching controls.

Empty state:

- Banner remains visible even when no approved contradiction records exist.

Error state:

- Banner remains visible even when optional OMI counts cannot load.

### Approved Contradiction List

Purpose:

- List approved contradiction records for selection and local filtering.

Data source:

- Applied records from approved memory/audit store only.
- `memory/index.json` may support navigation but must not override category files.

Candidate/canon boundary:

- Rows must be applied approved records only.
- Candidate rows must not be included.

No-prose boundary:

- List shows stored labels, types, statuses, severity, resolution status, tags, source labels, and warning badges only.
- No generated descriptions, summaries, explanations, fixes, interpretations, or proof narratives.

Empty state:

- Show no approved contradiction records and link to OMI Ideas / Candidates for candidate review when candidate counts exist.

Error state:

- Duplicate IDs, unsafe IDs, corrupt category envelope, unsupported schema, or unreadable records show warnings and block unsafe display for affected records.

### Contradiction Detail Panel

Purpose:

- Show selected approved contradiction details, claim pair metadata, source candidate IDs, promotion record IDs, evidence/provenance, linked source documents, linked approved memory, approval metadata, resolution metadata, revision history, and notes.

Data source:

- Selected applied contradiction memory record.
- Lightweight linked approved records, source documents, and OMI audit links where available.

Candidate/canon boundary:

- Detail fields are approved truth/audit context only when stored in the approved record.
- Source candidate and promotion links are provenance, not candidate truth display.
- The panel must not hydrate missing fields from OMI candidates.

No-prose boundary:

- Do not generate a contradiction explanation, fix, rewrite, bridge scene, plot-hole patch, retcon, source summary, or Dramatica proof.
- Owner-approved descriptions, claim summaries, resolution notes, and notes may be displayed exactly as stored.

Empty state:

- No selection shows choose-a-record guidance.

Error state:

- Invalid selected ID, missing record, unsafe ID, unsupported schema, or broken relation links show non-destructive warnings.

### Contradiction Claims / Pair Panel

Purpose:

- Show claim A and claim B as stored approved summaries, source references, locators, linked approved memory records, and claim-side evidence status.

Data source:

- Approved contradiction record claim fields.
- Source document metadata only where safe and project-local.

Candidate/canon boundary:

- Claim-side fields must come from approved contradiction memory only.
- Source documents are evidence/context, not canon by default.
- OMI candidate claim text must not fill missing approved claim fields.

No-prose boundary:

- Do not generate claim restatements, explanations, summaries, source paraphrases, or repair suggestions.
- Do not rewrite source text or invent claim wording.

Empty state:

- Show `Unknown`, `Not recorded`, or `Locator unavailable` for missing claim-side data.

Error state:

- Broken claim A or claim B source references, unsupported locators, out-of-range locators, same-locator warnings, or unsafe IDs show non-destructive warnings.

### Evidence / Provenance Panel

Purpose:

- Show compact evidence/provenance metadata for the approved contradiction, including first/latest sources, evidence IDs, provenance IDs, source candidate IDs, promotion record IDs, approval data, source hashes, and confidence/certainty labels where stored.

Data source:

- Approved contradiction record evidence/provenance fields.
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

- Show project-local source links such as claim A/B sources, affected scenes, chapters, notes, materials, and source locators.
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

### Linked Approved Memory Snapshot

Purpose:

- Show linked approved memory/canon records on each contradiction side and across the selected contradiction.

Data source:

- Stored claim-side linked memory IDs and type-specific linked IDs.
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

### Related Continuity / Consistency Snapshot

Purpose:

- Show approved continuity/consistency records linked to the selected approved contradiction without duplicating the full Continuity / Consistency page.
- Clarify whether the contradiction is linked to broader continuity/consistency work.

Data source:

- Approved contradiction `linked_continuity_issue_ids`.
- Future approved continuity/consistency memory files where implemented.

Candidate/canon boundary:

- Related continuity/consistency links must come from approved records only.
- OMI continuity/contradiction candidates remain in OMI counts/links only.

No-prose boundary:

- Do not generate continuity explanations, fixes, scene rewrites, bridge scenes, or contradiction narratives.

Empty state:

- Show `Not Recorded` or `No linked approved continuity / consistency issues`.

Error state:

- Broken continuity/consistency links or unimplemented related pages show warnings/placeholders.

### Related Open Questions Snapshot

Purpose:

- Show approved open questions linked to the selected contradiction, such as unresolved owner-review questions or decision points.

Data source:

- Approved contradiction `linked_open_question_ids`.
- Future approved open-question memory files where implemented.

Candidate/canon boundary:

- Related open-question links must come from approved memory/canon records only.
- OMI open-question or contradiction candidates remain candidate-only.

No-prose boundary:

- Do not generate answers, fixes, explanations, or missing story material.

Empty state:

- Show `Not Recorded` or `No linked approved open questions`.

Error state:

- Broken open-question links or unimplemented related pages show warnings/placeholders.

### Related Story Knowledge Snapshot

Purpose:

- Show stored links from the selected approved contradiction to approved characters, locations/settings, timeline events, plot threads, relationships, organizations/groups, objects/items, annotations/evidence/provenance, chapters, scenes, notes, and materials.

Data source:

- Approved contradiction link fields and approved linked-memory records.
- Source document metadata for chapters/scenes/notes/materials where safe.

Candidate/canon boundary:

- Story-knowledge links must be approved records only.
- Source document links are source/evidence context, not canon by default.

No-prose boundary:

- Do not generate relation explanations, summaries, continuity fixes, graph descriptions, or Dramatica proof.

Empty state:

- Show `Not Recorded` or `No related approved story knowledge`.

Error state:

- Broken linked story-knowledge references or related pages not implemented show warnings/placeholders.

### Resolution Status Placeholder

Purpose:

- Reserve space for future owner-controlled resolution workflow without implementing mutation.
- Display stored `resolution_status`, `owner_resolution_note`, and `resolution_decision` when present.

Data source:

- Approved contradiction record fields only.

Candidate/canon boundary:

- Resolution status must not be inferred from candidates, source edits, promotion records, or source availability.

No-prose boundary:

- No `fix contradiction`, `rewrite scene`, `resolve contradiction`, `generate bridge scene`, `patch plot hole`, `create retcon`, `explain contradiction`, or `generate fix` controls.

Empty state:

- Show `Resolution status not recorded`.

Error state:

- Severity/status/resolution conflicts show non-destructive warnings.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for OMI contradiction candidates by status.
- Help the owner navigate to OMI without blending candidates into approved truth.

Data source:

- OMI candidate metadata and promotion records where available.

Candidate/canon boundary:

- Candidate backlog may show counts and links only.
- Candidate contradiction text, proposed severity, proposed resolution, proposed claim pair, and proposed evidence must not be shown as approved truth.
- Approved-but-not-applied candidates and promotion records must be labeled `Not Yet Applied` and `Promotion Record Only`.

No-prose boundary:

- No generated candidate summaries or explanations.

Empty state:

- Show no contradiction candidates in OMI.

Error state:

- Corrupt OMI metadata shows degraded counts and warnings without blocking approved contradiction display.

### Empty State

Purpose:

- Explain the valid state where no approved contradiction records exist yet.

Data source:

- Approved memory/audit counts and optional OMI counts.

Candidate/canon boundary:

- State that pending candidates, approved candidates, and promotion records are not approved memory/canon.
- If candidates exist, link to OMI with candidate labels only.

No-prose boundary:

- Empty-state guidance is operational only.
- Do not suggest generating contradictions, explanations, fixes, retcons, bridge scenes, plot-hole patches, or rewrites.

Empty state:

- Missing `memory/`, missing `memory/contradictions.json`, or zero records all show a valid empty approved state.

Error state:

- If memory metadata is corrupt, show Warning State instead of a clean empty state.

### Warning State

Purpose:

- Surface non-destructive memory, claim-pair, locator, evidence, provenance, schema, source-safety, linked-record, and candidate/canon warnings.

Data source:

- Project validation, memory category validation, OMI audit link validation, approved record cross-link validation, source-link validation, and source-safety validation.

Candidate/canon boundary:

- Warnings must not repair, promote, delete, merge, split, retitle, infer claim state, infer locators, infer source safety, re-anchor source text, invent evidence, or rewrite records.

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

- Navigation links must not launch writing, rewriting, generation, explanation, fixing, semantic search, contradiction detection, extraction, graph visualization, apply-promotion, or proof actions.

Empty state:

- Related page links may show `Related Page Not Implemented`.

Error state:

- Missing adjacent routes show future-only/placeholder labels.

## 5. Candidate / Canon Separation

Approved records:

- Approved records are read from future memory files such as `memory/contradictions.json` or an equivalent approved memory/audit store.
- Approved contradiction truth exists only after owner approval, promotion record creation, and successful future apply-promotion into approved memory/canon, or another explicitly designed owner-approved approved-memory process.
- Approved records should preserve contradiction type, severity, status, resolution, claim pair state, evidence/provenance, source locators, related links, certainty labels, source candidate IDs, promotion record IDs, approval metadata, uncertainty, and revision metadata where available.
- Approved records are project-local and must not leak across projects.

OMI candidates:

- OMI contradiction candidates remain in OMI candidates.
- Pending, rejected, archived, duplicate, uncertain, needs-revision, and approved-but-not-applied candidates do not appear as approved contradictions.
- Candidate backlog may show counts and links only.
- Source candidate and promotion audit links may be shown as provenance/audit context.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved contradiction memory.
- Promotion records present without approved memory must not count as approved contradiction records.

Inference restrictions:

- Contradiction type, severity, status, resolution, claim pair state, evidence state, related links, and certainty must not be inferred as truth from candidate output.
- Contradiction records support approved memory review but do not themselves automatically promote, repair, or validate candidates.
- Contradiction records are not Dramatica structural/thematic claims unless a later Dramatica-specific approved memory record explicitly says so with owner approval and evidence.
- Missing approved fields must remain missing and be displayed honestly.
- No model, extractor, NotebookLM output, source material, raw idea, or raw analysis artifact may directly become approved contradiction truth.

## 6. First-Version Operations

Allowed first-version operations:

- View approved contradiction record list.
- View contradiction details.
- Filter/search approved contradiction records locally.
- Open linked source scene, note, material, or chapter if available.
- Open claim A and claim B source references if available.
- Open linked approved memory/canon record if available.
- Open linked OMI candidate or promotion record if available.
- Show contradiction claims/pair panel.
- Show evidence/provenance panel.
- Show linked story-knowledge snapshot.
- Show resolution status placeholder.

Future-only operations:

- Edit approved contradiction memory.
- Merge/split approved contradiction records.
- Archive/restore.
- Mark contradiction resolved.
- Apply-promotion.
- Detect contradictions.
- Extract contradiction candidates.
- Generate contradiction explanations.
- Generate fixes.
- Rewrite scenes to fix contradictions.
- Semantic search.
- Automatic source re-anchoring.
- Contradiction graph visualization.
- Dramatica structural/thematic proof classification.
- JSONL/training conversion.

## 7. Local Search / Filter Planning

First-version local search/filter may operate over approved-record data only:

- `contradiction_id`
- `display_title`
- `contradiction_type`
- `contradiction_status`
- `severity`
- `resolution_status`
- `scope`
- `claim_a_summary`
- `claim_b_summary`
- claim source IDs
- affected scene/chapter IDs
- linked note/material IDs
- linked character/location/object/organization/relationship/timeline/plot-thread/open-question/continuity/annotation/evidence/provenance IDs
- `source_candidate_ids`
- `promotion_record_ids`
- `tags` if available
- approved description if available

Rules:

- Search is local and deterministic.
- Search labels results as approved-only.
- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No generated explanations.
- No generated fixes.
- No detection during search.
- No extraction during search.
- No re-anchoring during search.
- No Dramatica classification during search.
- Search must not create OMI records, promotion records, memory/canon records, JSONL records, or training data.
- Search must not mutate project files.

## 8. Warning and Invalid-State Behavior

Warnings are non-destructive. They must not auto-repair, auto-delete, rewrite identity, retitle, infer contradiction claims, re-anchor source text, invent evidence, generate summaries, generate explanations, generate fixes, promote candidates, mutate memory/canon, or leak host filesystem paths.

Required warning/invalid states:

- Missing `memory/`.
- Missing/corrupt `memory/contradictions.json`.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Approved record references missing promotion record.
- Approved record references missing approved memory record.
- Broken claim A source reference.
- Broken claim B source reference.
- Claim locator missing or unsupported.
- Claim locator out of range if represented.
- Claim A and claim B reference same locator unexpectedly.
- Broken scene/chapter/note/material reference.
- Broken linked story-knowledge references.
- Broken continuity/open-question/evidence/provenance references.
- Unsafe IDs.
- Duplicate contradiction IDs.
- Contradiction type/status conflicts.
- Severity conflicts.
- Resolution status conflicts.
- Related contradiction links broken/cyclic if represented.
- Source hash mismatch if represented.
- Copyright-unsafe excerpt warning.
- Missing evidence for approved contradiction.
- Promotion records present but no approved memory record.
- OMI contradiction candidates exist but no approved records yet.
- Related pages/entities not implemented yet.
- Corrupt `memory/index.json`.

Behavior:

- Missing memory folders and missing category files are valid empty states when no approved records exist.
- Corrupt memory files block approved display for the affected category and show a warning.
- Unsupported schema versions should show read-only or needs-migration warnings.
- Duplicate or unsafe IDs should fail closed for detail routing.
- Broken links should show target type and stored ID without exposing host paths.
- Locator warnings should preserve stored ambiguity rather than forcing a correction.
- Same-locator warnings should not infer that the contradiction is invalid; they should ask for owner review through non-destructive warning copy.
- Candidate backlog warnings must link to OMI and not display candidate content as truth.
- Source hash mismatch warnings must not re-anchor, rewrite, or delete source references.
- Copyright-unsafe excerpt warnings must hide unsafe excerpt display while preserving safe metadata.

## 9. API Planning

This section documents future route planning only. Do not implement routes in this task.

Contradictions may be implemented as a dedicated endpoint family or composed from a future project memory/canon summary endpoint. Every route must validate `project_id` as a safe single path component. Contradiction routes must validate `contradiction_id` as a safe record ID. Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose. Routes must not call Ollama or any model in the first implementation. Routes must not create OMI records, create memory files on read, apply promotions, write JSONL/training records, update dataset manifests, detect contradictions, extract contradiction candidates, generate summaries, generate explanations, generate fixes, re-anchor sources, graph contradictions, or classify Dramatica proof.

Route group:

```text
GET /api/projects/{project_id}/memory/contradictions
GET /api/projects/{project_id}/memory/contradictions/{contradiction_id}
GET /api/projects/{project_id}/memory/contradictions/{contradiction_id}/provenance
GET /api/projects/{project_id}/memory/contradictions/health
```

### `GET /api/projects/{project_id}/memory/contradictions`

Purpose:

- Return approved contradiction list payload and warning summary for one project.
- Optionally include approved-only counts and lightweight candidate backlog counts labeled separately.

Request shape:

- Path parameter: `project_id`.
- Optional local filter/search query parameters if implemented.
- No body.

Response shape:

- Project ID.
- Approved contradiction records or compact list rows.
- Approved count.
- Candidate backlog counts by status if included, labeled candidate-only.
- Warnings.

Validation:

- Safe project ID.
- Existing project.
- Optional existing memory folder read-only.
- `memory/contradictions.json` or equivalent approved store envelope is valid if present.
- Record IDs are unique and safe.

Path safety:

- Read only inside selected project.
- Reject traversal, absolute paths, empty IDs, `"."`, and `".."`.
- Return project-relative source references only.
- Do not expose absolute host filesystem paths.

Candidate/canon boundary:

- Return applied approved records only.
- Candidate records must remain OMI links/counts only.
- Promotion records are audit-only unless linked from an approved contradiction record after apply-promotion.

No-prose boundary:

- Return stored fields only.
- No generated contradiction summaries, explanations, fixes, rewrites, source paraphrases, retcons, bridge scenes, or proof claims.

Source/evidence safety:

- Return only bounded, owner-approved, copyright-safe excerpts when stored.
- Hide or warn on unsafe excerpt state.
- Do not return full source bodies.

Expected errors:

- 400 invalid project ID or filters.
- 404 missing project.
- 422 corrupt memory metadata, unsupported schema, duplicate IDs, unsafe IDs, unsupported locator, conflict state, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/contradictions/{contradiction_id}`

Purpose:

- Return one approved contradiction detail payload.

Request shape:

- Path parameters: `project_id`, `contradiction_id`.
- No body.

Response shape:

- Approved contradiction detail.
- Claim A/B source locator status.
- Evidence/provenance status.
- Linked approved memory status.
- Linked source document status.
- Related story-knowledge status.
- Warnings.

Validation:

- Safe project ID and contradiction ID.
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

- Return stored owner-approved descriptions, claim summaries, resolution notes, and notes only.
- No generated contradiction analysis, summaries, explanations, fixes, rewrites, bridge scenes, retcons, or diagnostic prose generation.

Source/evidence safety:

- Return only bounded source locator metadata and copyright-safe excerpts.

Expected errors:

- 400 invalid ID.
- 404 missing project, missing category file where not treated as list empty, or missing record.
- 422 corrupt category file, duplicate IDs, unsafe links, unsupported locator, same-locator warning, invalid claim pair, or invalid record shape.
- 500 sanitized read failure.

### `GET /api/projects/{project_id}/memory/contradictions/{contradiction_id}/provenance`

Purpose:

- Return compact provenance chain, source candidate, promotion record, approved-memory link, claim-side source locator, evidence, source hash, and source-safety data for one approved contradiction.

Request shape:

- Path parameters: `project_id`, `contradiction_id`.
- No body.

Response shape:

- Provenance chain summary.
- Claim A/B source locator metadata.
- Evidence IDs and status.
- Source candidate IDs and status.
- Promotion record IDs and audit status.
- Linked approved memory records and status.
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
- Broken source candidate, promotion, memory, evidence, provenance, or source references.
- Cyclic provenance chain if represented.
- Corrupt provenance.
- Sanitized partial read failure.

### `GET /api/projects/{project_id}/memory/contradictions/health`

Purpose:

- Return non-destructive health warnings for contradiction memory/audit state.

Request shape:

- Path parameter only, with optional validation depth in a later design.
- No body.

Response shape:

- Health status.
- Warning list with code, severity, target type, target ID, and sanitized message.
- Approved record count.
- Candidate backlog count if included, labeled separately.
- No repair actions.

Validation:

- Safe project ID.
- Read-only scans only.
- Validate memory envelope, IDs, schema version, duplicate IDs, linked sources, claim locators, linked approved entities, related contradiction links, type/status/severity/resolution conflicts, source hashes, source safety, and evidence presence.

Path safety:

- Scan only approved project-local memory/OMI references.
- Sanitize paths.

Candidate/canon boundary:

- Health checks must not repair, promote, delete, merge, split, retitle, infer truth, infer claim pairs, infer locators, re-anchor sources, or validate candidates as canon.

No-prose boundary:

- Warnings are factual status only.
- Do not propose fixes or rewrites.

Source/evidence safety:

- Flag unsafe excerpt/anchor/source display state without returning unsafe source text.

Expected errors:

- 400 invalid project ID.
- 404 missing project.
- 500 sanitized partial scan failure.

## 10. Frontend Planning

Do not implement UI in this task. Future components:

- `ApprovedContradictionsPage`
- `ContradictionsBoundaryBanner`
- `ApprovedContradictionList`
- `ApprovedContradictionListItem`
- `ContradictionDetailPanel`
- `ContradictionClaimsPairPanel`
- `ContradictionEvidencePanel`
- `ContradictionSourceLinksPanel`
- `ContradictionLinkedApprovedMemorySnapshot`
- `ContradictionRelatedContinuitySnapshot`
- `ContradictionRelatedOpenQuestionsSnapshot`
- `ContradictionRelatedStoryKnowledgeSnapshot`
- `ContradictionResolutionStatusPlaceholder`
- `ContradictionCandidateBacklogSnapshot`
- `ContradictionSearchFilterControls`
- `ContradictionWarningsPanel`
- `ContradictionEmptyState`
- `ContradictionFuturePagesReference`

Frontend rules:

- No AI writing buttons.
- No generated contradiction explanation button.
- No generated fix button.
- No rewrite button.
- No semantic-search button in the first version.
- No controls like detect contradictions, explain contradiction, fix contradiction, rewrite scene, generate bridge scene, patch plot hole, create retcon, infer proof, classify Dramatica role, convert to training data, or promote candidate.
- Search/filter controls must be local and deterministic.
- Candidate backlog controls must route to OMI and remain labeled as candidate/audit state.
- Detail panels must display stored approved fields only.
- Warning panels must be non-destructive.
- Labels must distinguish approved contradiction records, OMI candidates, promotion records, source/evidence, approved memory, source safety warnings, and future/not implemented states.
- Missing fields must show `Unknown`, `Not approved yet`, `Not recorded`, or `Locator unavailable`.
- Opening the page must not trigger analysis, detection, extraction, semantic search, graph visualization, model calls, OMI record creation, promotion, memory/canon mutation, project-file writes, JSONL writes, or dataset updates.

## 11. Future Tests

Future implementation tests should cover:

- No memory directory / no approved records.
- Load approved contradiction records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt contradiction memory file warning.
- Duplicate contradiction IDs warning.
- Unsafe IDs rejected.
- Broken claim source links warning.
- Unsupported locator warning.
- Claim locator out-of-range warning if represented.
- Claim pair same-locator warning if represented.
- Broken candidate/promotion/memory links warning.
- Broken story-knowledge links warning.
- Related contradiction broken/cyclic warning if represented.
- Severity/status/resolution conflict warnings.
- Source hash mismatch warning if represented.
- Copyright-unsafe excerpt warning.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- Page does not write JSONL/training records.
- No AI prose-generation controls.
- No generated explanations/fixes/rewrites/summaries.
- No invented evidence.
- No contradiction detection in first version.
- No source re-anchoring in first version.
- No Dramatica structural/thematic proof claims.
- `training/data/dataset_manifest.json` unchanged.

## 12. Page Relationships

Relationship to Project Memory / Canon:

- The Approved Contradictions page is an approved-memory category page.
- It reads approved records only and should be reachable from the future Project Memory / Canon category cards.

Relationship to OMI:

- OMI is the review workspace for contradiction candidates.
- The page may link to OMI candidate filters/counts but must not display candidates as approved contradictions.

Relationship to Continuity / Consistency:

- Approved continuity/consistency records may link to approved contradictions only when those links exist on approved records.
- This page may link back to continuity/consistency only when approved contradiction records explicitly carry `linked_continuity_issue_ids`.
- The page should not duplicate the broader continuity/consistency issue list or resolution workflow.

Relationship to Approved Annotations / Evidence / Provenance:

- Approved contradiction records may link to approved annotations, evidence spans, and provenance records where stored.
- Evidence/provenance links are traceability/audit context and do not create contradiction truth by themselves.

Relationship to other approved story knowledge:

- Links to characters, locations/settings, objects/items, organizations/groups, relationships, timeline events, plot threads, and open questions are approved-memory navigation only.
- Missing future pages should show `Related Page Not Implemented`.

Relationship to chapters, scenes, notes, and materials:

- Linked source pages show owner-authored/source material only.
- Source links are evidence/context, not approved contradiction truth by themselves.

Relationship to Dramatica:

- This page is general contradiction/cross-record conflict support.
- Dramatica-specific structural/thematic contradiction classification is deferred.

## 13. Deferred Decisions

Deferred to later tasks:

- Exact runtime schema for `contradiction_memory_record` versus using `continuity_warning_memory_record.contradiction_type`.
- Exact allowed values for `contradiction_type`, `contradiction_status`, `severity`, `scope`, `resolution_status`, and `resolution_decision`.
- Exact memory envelope version and migration behavior.
- Whether first implementation reads directly from `memory/contradictions.json`, a memory summary endpoint, or both.
- Whether contradictions live in their own category file, a continuity subcategory, or an approved audit store.
- Exact claim A/B source locator format for scene, chapter, note, material, memory-record, candidate, and promotion links.
- Whether related contradiction links use `related_contradiction_ids` or a separate relation object.
- Exact OMI filter for contradiction candidates, including whether contradiction candidates are distinct from continuity warning candidates.
- Exact source hash algorithm and hash-mismatch display.
- Exact copyright/source safety policy for owner-authored, owner-supplied, public-domain, external, and unknown-license material.
- Exact apply-promotion behavior, rollback, and record supersession mechanics.
- Whether and when an owner-controlled edit/resolution workflow is added.
- Whether future visualization uses a graph, table, timeline overlay, source matrix, or side-by-side evidence view.
- Whether semantic search belongs in a later approved-memory search page or this page.
- Any future Dramatica structural/thematic contradiction taxonomy.
- Browser/manual acceptance checklist for implemented Approved Contradictions page.

## 14. Implementation Non-Goals

WORKSPACE-023 does not implement:

- Approved Contradictions UI.
- Backend memory/canon routes.
- Apply-promotion.
- Contradiction detection.
- Contradiction extraction.
- Automatic contradiction repair.
- Graph visualization.
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
