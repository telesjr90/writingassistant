# WORKSPACE-018: Approved Open Questions Page Spec

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
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Approved Open Questions page should be the future project-local destination for owner-approved open-question or unresolved-question memory/canon records. It must show only records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, needs-revision, and approved-but-not-applied open-question candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

The page should:

- Show owner-approved `open_question_memory_record` or `unresolved_question_memory_record` entries for the selected project.
- Read approved open-question truth only from future memory files such as `memory/open_questions.json` or an equivalent approved memory store.
- Clearly distinguish approved open-question truth from OMI open-question candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved open question back to source evidence, provenance, source candidate IDs, promotion record IDs, and approval metadata where available.
- Show unresolved or missing fields honestly as `Unknown`, `Not approved yet`, or `Not recorded`.
- Show an empty state when no approved open-question records exist.
- Link to the OMI Ideas / Candidates page for pending open-question candidates.
- Link to related plot threads, timeline events, characters, locations, objects, continuity/consistency issues, chapters, scenes, notes, and materials if available.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic extraction.
- Avoid answer generation.
- Avoid contradiction detection.
- Avoid apply-promotion behavior.
- Avoid generated answers, generated explanations, rewrite suggestions, and plot-fix suggestions.
- Avoid Dramatica-specific structural unresolved-question claims unless later approved and evidence-backed by a separate advanced-layer task.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Open Questions Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for open-question candidates.
- Source material is not approved open-question memory/canon by default.
- A question, uncertainty, or unresolved note mentioned in a scene, note, or material is not an approved open-question record by itself.
- Source material must not be copied into approved open-question memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that raises a question is not an approved open-question record.

### OMI Open-Question Candidates

Definition:

- Structured `open_question_candidate` or future equivalent `unresolved_question_candidate` records that have not been applied to approved memory/canon.

Rules:

- Open-question candidates are not canon.
- Open-question candidates must not appear in the approved open-question list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate priority, status, answer state, resolution state, and linked entities must not be inferred as approved truth.

### Approved-but-Not-Applied Candidates

Definition:

- Open-question candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved open-question memory/canon.
- Approved-but-not-applied candidates must not appear in the approved open-question list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved open questions.
- Promotion records may be linked as provenance from an approved open-question record that a future apply-promotion step actually created.
- Promotion records present without an approved memory record must show an audit-only warning or candidate backlog state, not an approved question.

### Applied Open-Question Memory Records

Definition:

- Durable owner-approved `open_question_memory_record` or `unresolved_question_memory_record` entries written to the future approved memory store by a future apply-promotion step.

Rules:

- Applied open-question records are the only records allowed in the approved open-question list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, approval metadata, answer/resolution metadata, and related record links where available.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/open_questions.json` entries or equivalent records.

### Owner Answer and Resolution State

Definition:

- Future stored fields that represent the owner's answer note, answer status, resolution status, priority, scope, and related story-knowledge links.

Rules:

- Answer and resolution state must come from approved memory/canon records only.
- Questions may remain unresolved without implying an error.
- Missing answer or resolution state must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- The first implementation must not generate answers, explanations, fixes, or resolution suggestions.

### Future Dramatica Structural Claims

Definition:

- Future Dramatica storyform-specific unresolved-question classifications, such as unresolved story point, signpost gap, throughline issue, Concern/Issue/Problem/Solution question, CIPS question, dynamic question, or Relationship Story question.

Rules:

- Dramatica-specific unresolved-question classification is deferred.
- The first version of this page must not display any Dramatica-specific unresolved-question diagnosis.
- Generic open-question labels must not be treated as Dramatica proof.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved open-question display.
- The first implementation of this page must not call a model.

### Insufficient Evidence

Definition:

- Open-question evidence/provenance is missing, weak, broken, unsafe, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting or rewriting the open-question record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any question that already exists.

## 3. Approved Open-Question Display Model

Approved open-question records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `open_question_id` | Stable approved question ID; required for detail routing. |
| `display_title` | Owner-approved title/label. Missing title shows `Unknown`. |
| `question_text` | Owner-approved question text only. Must not be rewritten or expanded. |
| `question_type` | Stored type such as open question, unresolved decision, continuity question, timeline question, plot-thread question, character question, location question, object question, or relationship question. |
| `status` | Stored record status only. |
| `priority` | Stored priority only. Do not infer priority from source text or candidate output. |
| `scope` | Stored scope only, such as project, chapter, scene, plot thread, timeline, character, location, or object. |
| `short_owner_approved_description` | Owner-approved description only. Do not generate explanation text. |
| `owner_answer_note` | Owner-approved answer note only. No generated answers or fix text. |
| `answer_status` | Stored answer state only, such as unanswered, partially answered, answered, not recorded, or needs owner review. |
| `resolution_status` | Stored resolution state only, such as unresolved, resolved, superseded, archived, not recorded, or needs owner review. |
| `affected_scene_ids` | Approved source references only; broken references show warnings. |
| `affected_chapter_ids` | Approved source references only; broken references show warnings. |
| `linked_note_ids` | Approved source/reference links only; broken references show warnings. |
| `linked_material_ids` | Approved source/reference links only; broken references show warnings. |
| `linked_character_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_location_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_object_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_timeline_event_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_plot_thread_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_continuity_issue_ids` | Approved continuity/consistency links only; unresolved links show warnings. |
| `related_open_question_ids` | Optional approved question links; broken or cyclic links show warnings and are not auto-repaired. |
| `first_seen_source` | First approved source/provenance locator if stored. |
| `latest_seen_source` | Latest approved source/provenance locator if stored. |
| `evidence` / `provenance` summary | Compact evidence/provenance metadata only; avoid long source copies and generated summaries. |
| `confidence` / `certainty` label | Stored confidence/certainty label only; it is owner-review metadata, not objective proof. |
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
| `notes` | Owner notes, ambiguity notes, or implementation notes. No generated prose fixes. |

Display clarifications:

- Unapproved candidates must not appear as truth.
- Generated answers, generated explanations, rewrite suggestions, and plot-fix suggestions are prohibited.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- Questions may remain unresolved without implying an error.
- Owner-approved descriptions and owner answer notes may be displayed only as stored approved fields.
- If the underlying memory schema supports only `open_question_memory_record`, the page should label unresolved-question variants through `question_type` rather than inventing a second file.

## 4. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Open Question` | Marks each applied approved memory/canon record. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Candidate` | Marks OMI open-question candidates outside the approved list. |
| `Pending Candidate` | Marks pending OMI open-question candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied open-question candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI open-question candidates. |
| `Needs Revision` | Marks OMI open-question candidates needing revision. |
| `Archived Candidate` | Marks archived OMI open-question candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied memory record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved question fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Owner Answer Placeholder` | Marks that first-version owner-answer editing is not implemented. |
| `Resolution Placeholder` | Marks that first-version resolution management is not implemented. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Future / Not Implemented` | Marks extraction, apply-promotion, contradiction detection, graph visualization, answer generation, and Dramatica structural classification. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved open-question list.
- Counts must be separated by status.
- Approved open-question counts must come from applied memory/canon records only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Open Question`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, needs-revision, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved open-question list.

## 5. First-Version Page Sections

First-version sections:

- Page Header.
- Open Questions Boundary Banner.
- Approved Open Question List.
- Open Question Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Linked Story Knowledge Snapshot.
- Related Plot Thread / Continuity Snapshot.
- Owner Answer / Resolution Placeholder.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and Approved Open Questions area.
- Show approved question count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved open-question records from `memory/open_questions.json` or equivalent approved memory store if present.

Candidate/canon boundary:

- Header approved count must come from applied memory/canon records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, question explanations, answers, fixes, or rewrite suggestions.

Empty state:

- Show that no approved open questions exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Open Questions Boundary Banner

Purpose:

- Explain that the page shows approved memory/canon records only.
- Point pending open-question candidates to OMI.
- State that the page is not an answer-generation or writing surface.

Data source:

- Static page copy.
- Optional lightweight OMI open-question candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not canon.
- State that approved questions require future apply-promotion into memory/canon.

No-prose boundary:

- Prohibit generated answers, generated explanations, rewrite suggestions, continuity fixes, and prose-patching controls.

Empty state:

- Banner remains visible even when no records exist.

Error state:

- Banner remains visible when approved-memory load partially fails.

### Approved Open Question List

Purpose:

- List approved open-question records for the selected project.
- Support local filter/search over approved question metadata.

Data source:

- Applied `open_question_memory_record` or `unresolved_question_memory_record` entries.
- Optional derived `memory/index.json` for navigation, with category files remaining source of truth.

Candidate/canon boundary:

- Exclude all OMI candidates, promotion records without applied memory, and source-only material.
- Candidate backlog may be represented only as separate counts/links.

No-prose boundary:

- Do not generate answers, explanations, summaries, fixes, or scene rewrite suggestions.
- List item descriptions must come from approved stored fields only.

Empty state:

- "No approved open questions yet" with link to OMI candidate review if candidate counts exist.

Error state:

- Corrupt memory file, unsupported schema, duplicate IDs, unsafe IDs, or invalid records should show warnings and omit unsafe/invalid records from normal detail display.

### Open Question Detail Panel

Purpose:

- Show the selected approved question's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, affected sources, linked story knowledge, approval metadata, answer metadata, resolution metadata, revision history, and notes.

Data source:

- Selected approved open-question memory record.

Candidate/canon boundary:

- Detail panel must not hydrate missing fields from OMI candidates.
- Source candidate and promotion links are provenance only.

No-prose boundary:

- Do not generate an answer, explanation, fix, rewrite, bridge scene, plot-hole patch, contradiction resolution, or continuity suggestion.

Empty state:

- Prompt the owner to select an approved question.

Error state:

- Invalid selected ID, missing record, unsafe ID, unsupported schema, or broken relation links show non-destructive warnings.

### Evidence / Provenance Panel

Purpose:

- Show the evidence/provenance trail behind the approved question.
- Identify first/latest sources, evidence IDs, source candidate IDs, promotion record IDs, approval data, and confidence/certainty labels where stored.

Data source:

- Approved memory record evidence/provenance fields.
- Linked OMI candidate/promotion metadata for audit links only.

Candidate/canon boundary:

- Candidate/promotion data is provenance, not approved truth.
- If evidence is missing or insufficient, show `Evidence Required` or `Insufficient Evidence`.

No-prose boundary:

- Evidence summaries must be stored metadata only.
- Avoid long source copies and generated explanations.

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
- Do not summarize, rewrite, or answer from source material.

Empty state:

- Show `Not Recorded` when no source links exist.

Error state:

- Broken scene, chapter, note, material, or unsafe reference shows non-destructive warning without host filesystem path leakage.

### Linked Story Knowledge Snapshot

Purpose:

- Show linked approved characters, locations, objects, timeline events, and related open questions when those records are available.
- Help the owner navigate across approved memory pages.

Data source:

- Approved question record link fields.
- Future approved memory files for linked records where implemented.

Candidate/canon boundary:

- Only approved memory/canon links may be shown as story knowledge truth.
- Missing pages/entities must be labeled as future/not implemented or broken links.

No-prose boundary:

- Do not generate entity summaries, event explanations, answers, or "why this matters" prose.

Empty state:

- Show `Not Recorded` or `No linked approved story knowledge`.

Error state:

- Broken timeline/character/location/object links show warnings and do not auto-repair.

### Related Plot Thread / Continuity Snapshot

Purpose:

- Show linked approved plot threads and continuity/consistency issues when approved links exist.
- Help the owner see whether the question is tied to unresolved plot, timeline, continuity, or consistency work without creating fixes.

Data source:

- Approved question `linked_plot_thread_ids` and `linked_continuity_issue_ids`.
- Future approved plot-thread and continuity/consistency memory files where implemented.

Candidate/canon boundary:

- Related plot thread and continuity links must come from approved memory/canon records only.
- OMI candidates and promotion records may be linked only as provenance/audit context, not as approved related issues.

No-prose boundary:

- Do not generate plot fixes, continuity fixes, answers, causal explanations, or rewrite suggestions.

Empty state:

- Show `Not Recorded` or `No approved plot-thread or continuity links`.

Error state:

- Broken plot-thread or continuity links show non-destructive warnings and do not auto-repair.

### Owner Answer / Resolution Placeholder

Purpose:

- Reserve space for future owner-controlled answer/resolution workflow without implementing mutation.
- Display stored `owner_answer_note`, `answer_status`, and `resolution_status` when present.

Data source:

- Approved question record fields only.

Candidate/canon boundary:

- Answer status and resolution status must not be inferred from candidates, source edits, or promotion records.

No-prose boundary:

- No `answer this`, `generate answer`, `resolve question`, `fix plot hole`, `rewrite scene`, `generate missing scene`, `patch continuity`, or `explain answer` controls.

Empty state:

- Show `Answer status not recorded` or `Resolution status not recorded`.

Error state:

- Status, answer-status, and resolution-status conflicts show non-destructive warnings.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for OMI open-question candidates by status.
- Help the owner navigate to OMI without blending candidate records into approved truth.

Data source:

- OMI index/candidate metadata where available.

Candidate/canon boundary:

- Candidate backlog may show counts and links only.
- Candidate text, proposed priority, proposed answer, proposed resolution state, and proposed linked entities must not be shown as approved truth.

No-prose boundary:

- Do not generate candidate summaries, explanations, or answers.

Empty state:

- Show `No pending open-question candidates`.

Error state:

- Corrupt OMI index/candidate metadata shows an OMI warning without blocking approved question display.

### Empty State

Purpose:

- Provide safe guidance when no approved open-question records exist.

Data source:

- Approved memory file presence and record count.
- Optional OMI open-question candidate counts.

Candidate/canon boundary:

- Empty approved state remains empty even if candidates exist.
- If candidates exist, link to OMI with candidate labels only.

No-prose boundary:

- Empty-state guidance must not ask the AI to invent questions, answer questions, generate fixes, or write missing story material.

Empty state:

- "No approved open questions have been applied yet."

Error state:

- If memory load fails, use Warning State instead of empty state.

### Warning State

Purpose:

- Surface invalid, missing, corrupt, unsafe, unsupported, duplicate, broken-link, conflict, cyclic-link, or insufficient-evidence states.

Data source:

- Project validation.
- Memory file validation.
- OMI candidate/promotion metadata validation when candidate counts are shown.

Candidate/canon boundary:

- Warnings are diagnostics, not approved story truth.
- Warnings must not promote, answer, resolve, retitle, or repair records.

No-prose boundary:

- Warning copy is factual status text only.
- Do not generate answers, fixes, rewrite suggestions, or explanatory story prose.

Empty state:

- Show "No open-question warnings detected in approved memory metadata" only when validation ran and found no warnings.

Error state:

- Partial validation failure should show partial warnings and preserve read-only page behavior.

### Future Page Link Reference

Purpose:

- Link to related approved pages and future page placeholders.
- Clarify implementation status for OMI, Project Memory / Canon, plot threads, timeline, characters, locations/settings, objects, and continuity/consistency.

Data source:

- Route/page availability metadata.
- Static planning copy.

Candidate/canon boundary:

- Links to approved pages must use approved-memory labels.
- Links to OMI must use candidate/audit labels.

No-prose boundary:

- Navigation only; no generated page summaries or answers.

Empty state:

- Show future/not implemented labels for unavailable pages.

Error state:

- Broken route/page availability state shows a non-blocking navigation warning.

## 6. Candidate / Canon Separation

Approved records:

- Approved open-question records are read from future memory files such as `memory/open_questions.json` or an equivalent approved memory store.
- Approved open-question truth exists only after owner approval, promotion record creation, and successful future apply-promotion into approved memory/canon.
- Approved records are project-local and must not leak across projects.

OMI candidates:

- OMI open-question candidates remain in OMI candidates.
- Pending, rejected, archived, duplicate, uncertain, and needs-revision candidates do not appear as approved questions.
- Approved-but-not-applied candidates do not appear as approved questions.
- Candidate backlog may show counts and links only.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved open-question memory.
- Source candidate and promotion audit links may be shown as provenance from approved records.
- Promotion records present but no approved memory record must show `Promotion Record Only` or `Not Yet Applied`, not an approved question.

Inference restrictions:

- Priority, status, answer state, resolution state, linked entities, affected sources, and related open-question links must not be inferred as truth from candidate output.
- Missing approved fields must remain missing and be displayed honestly.
- No model, extractor, NotebookLM output, source material, raw idea, or raw analysis artifact may directly become approved open-question truth.

## 7. First-Version Operations

Allowed first-version operations:

- View approved open-question list.
- View open-question details.
- Filter/search approved open questions locally.
- Open linked source scene/note/material.
- Open linked timeline event, character, location, object, plot-thread, or continuity/consistency page if available.
- Open related OMI candidate or promotion record as provenance/audit context.
- Show owner-answer/resolution placeholder.
- Show linked story-knowledge snapshot.

Future-only operations:

- Edit approved open-question memory.
- Merge/split approved open questions.
- Archive/restore.
- Mark answered/resolved.
- Apply-promotion.
- Extract open-question candidates.
- Generate answers.
- Suggest fixes.
- Rewrite scene to answer question.
- Contradiction detection.
- Open-question graph visualization.
- Dramatica structural unresolved-question classification.

## 8. Local Search and Filter Planning

First-version search/filter should be local and deterministic over approved records only.

Search/filter fields:

- `display_title`
- `question_text`
- `question_type`
- `status`
- `priority`
- `scope`
- `answer_status`
- `resolution_status`
- `tags` if available
- approved description if available
- linked source IDs
- affected scene/chapter IDs
- linked character/location/object/timeline/plot-thread/continuity IDs
- `source_candidate_ids`
- `promotion_record_ids`

Rules:

- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No generated answers.
- No extraction during search.
- No contradiction detection during search.
- Approved-only labels must remain visible in search results.
- Candidate counts/links may be separately filtered by status only if the UI makes them clearly non-canon.

## 9. Warning and Invalid-State Behavior

The page should warn for these states:

- Missing `memory/`.
- Missing or corrupt `memory/open_questions.json`.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Broken scene/note/material references.
- Broken timeline/character/location/object/plot-thread/continuity references.
- Duplicate open-question IDs.
- Unsafe IDs.
- Status conflicts.
- Answer/resolution status conflicts.
- Affected source references missing.
- Related open-question links broken/cyclic if represented.
- Promotion records present but no approved memory record.
- OMI open-question candidates exist but no approved questions yet.
- Related pages/entities not implemented yet.
- Missing or insufficient evidence.
- Corrupt `memory/index.json`.

Warning rules:

- Warnings are non-destructive.
- Warnings must not auto-repair records.
- Warnings must not auto-delete records.
- Warnings must not rewrite identity.
- Warnings must not retitle questions.
- Warnings must not answer the question.
- Warnings must not resolve the question.
- Warnings must not correct priority, answer state, resolution state, or status.
- Warnings must not promote candidates.
- Warnings must not leak host filesystem paths.
- Warnings should use project-relative identifiers where needed.

## 10. Future API Planning

These routes are future planning only. Do not implement them in WORKSPACE-018. These route groups may be implemented directly or composed from a future project memory/canon summary endpoint.

Route group:

```text
GET /api/projects/{project_id}/memory/open-questions
GET /api/projects/{project_id}/memory/open-questions/{open_question_id}
GET /api/projects/{project_id}/memory/open-questions/{open_question_id}/provenance
GET /api/projects/{project_id}/memory/open-questions/health
```

Every route must preserve no-prose and candidate/canon boundaries:

- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- First-version routes must not call Ollama or any model.
- First-version routes must not create OMI records.
- First-version routes must not create or modify `memory/open_questions.json` or `memory/index.json` on read.
- First-version routes must not apply promotions.
- Routes must not write JSONL/training records or update dataset manifests.

### `GET /api/projects/{project_id}/memory/open-questions`

Purpose:

- List approved open questions for one project.
- Optionally include approved-only counts and lightweight warning metadata.

Request shape:

- Path parameter `project_id`.
- Optional query parameters for local filter/sort/search over approved question fields.
- No body.

Response shape:

- Project ID.
- Approved open-question list or compact question summaries.
- Approved count.
- Optional warning list.
- Optional candidate backlog counts labeled separately if included.

Validation:

- `project_id` must be a safe single path component.
- Load approved memory store read-only.
- Validate envelope/schema before displaying records.
- Reject unsafe record IDs.

Path safety:

- Use project path helpers.
- Reject absolute paths, traversal, empty IDs, `"."`, and `".."`.
- Return project-relative source references only.

Candidate/canon boundary:

- Return applied memory/canon records only.
- Do not include candidate bodies as approved records.

No-prose boundary:

- Do not generate question descriptions, explanations, answers, summaries, fixes, or rewrites.

Expected errors:

- Project not found.
- Missing memory store, treated as empty if project is valid.
- Corrupt memory file.
- Unsupported schema.
- Unsafe ID.
- Broken index warning.

### `GET /api/projects/{project_id}/memory/open-questions/{open_question_id}`

Purpose:

- Load one approved open-question detail.

Request shape:

- Path parameters `project_id` and `open_question_id`.
- No body.

Response shape:

- Approved open-question detail record.
- Approved display fields.
- Warnings for missing linked records or unsupported optional fields.

Validation:

- `project_id` and `open_question_id` must be safe IDs.
- Record must exist in approved memory store.
- Record type must be supported.

Path safety:

- No filesystem paths from request values.
- No host-path leakage in errors.

Candidate/canon boundary:

- Candidate and promotion links are IDs/provenance only.
- Do not hydrate missing approved fields from OMI candidates.

No-prose boundary:

- Return stored fields only.
- No generated answer, fix, rewrite, bridge scene, contradiction explanation, or diagnostic prose generation.

Expected errors:

- Project not found.
- Approved memory missing.
- Record not found.
- Duplicate record ID.
- Unsafe ID.
- Unsupported schema.

### `GET /api/projects/{project_id}/memory/open-questions/{open_question_id}/provenance`

Purpose:

- Return evidence/provenance metadata for one approved question.
- Support audit links to source candidate IDs and promotion record IDs.

Request shape:

- Path parameters `project_id` and `open_question_id`.
- No body.

Response shape:

- Evidence IDs.
- Provenance metadata.
- First/latest source locators if stored.
- Source candidate IDs.
- Promotion record IDs.
- Missing/broken reference warnings.

Validation:

- Same ID safety as question detail.
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
- Do not generate summaries, explanations, or answers.

Expected errors:

- Project not found.
- Record not found.
- Corrupt provenance metadata.
- Broken source candidate reference.
- Broken promotion record reference.
- Unsafe source locator.

### `GET /api/projects/{project_id}/memory/open-questions/health`

Purpose:

- Validate open-question memory health without mutation.
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
- Validate memory envelope, IDs, schema version, duplicate IDs, linked sources, linked approved entities, related question links, status/answer/resolution conflicts, and evidence presence.

Path safety:

- Do not expose host filesystem paths.
- Use project-relative IDs and safe labels.

Candidate/canon boundary:

- Health warnings are diagnostics, not approved story truth.
- Candidate counts remain candidate-only.

No-prose boundary:

- Warnings are factual status messages only.
- Do not propose fixes, answers, or rewrites.

Expected errors:

- Project not found.
- Corrupt memory file.
- Corrupt memory index.
- Unsupported schema.
- Unsafe ID.
- Partial validation failure.

## 11. Future Frontend Planning

These components are future planning only. Do not implement UI in WORKSPACE-018.

Future components:

- `ApprovedOpenQuestionsPage`
- `OpenQuestionsBoundaryBanner`
- `ApprovedOpenQuestionList`
- `ApprovedOpenQuestionListItem`
- `OpenQuestionDetailPanel`
- `OpenQuestionEvidencePanel`
- `OpenQuestionSourceLinksPanel`
- `OpenQuestionLinkedStoryKnowledgeSnapshot`
- `OpenQuestionRelatedPlotContinuitySnapshot`
- `OpenQuestionOwnerAnswerPlaceholder`
- `OpenQuestionCandidateBacklogSnapshot`
- `OpenQuestionSearchFilterControls`
- `OpenQuestionWarningsPanel`
- `OpenQuestionEmptyState`
- `OpenQuestionFuturePagesReference`

Component rules:

- No AI writing buttons.
- No generated answer button.
- No controls named or behaving like `answer this`, `fix plot hole`, `rewrite scene`, `generate missing scene`, `resolve question`, `explain answer`, `patch continuity`, `generate answer`, or `suggest fix`.
- Search/filter controls must be local and deterministic.
- Candidate backlog controls must route to OMI and remain labeled as candidate/audit state.
- Detail panels must display stored approved fields only.
- Warning panels must be non-destructive.

## 12. Future Tests

Future tests should cover:

- No memory directory / no approved records.
- Load approved open-question records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt memory file warning.
- Duplicate open-question IDs warning.
- Unsafe IDs rejected.
- Broken source links warning.
- Broken timeline/character/location/object/plot-thread/continuity links warning.
- Status conflicts warning.
- Answer/resolution status conflicts warning.
- Related open-question broken/cyclic warning if represented.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- No AI prose-generation controls.
- No generated answers/fixes/rewrites/summaries/explanations.
- No Dramatica structural unresolved-question claims.
- No JSONL/training writes.

## 13. Page Relationships

Relationship to Project Memory / Canon:

- The Approved Open Questions page is an approved-memory category page.
- It reads approved records only and should be reachable from the future Project Memory / Canon category cards.

Relationship to OMI:

- OMI is the review workspace for open-question candidates.
- The page may link to OMI candidate filters/counts but must not display candidates as approved questions.

Relationship to Approved Plot Threads:

- Approved plot threads may link to related open questions only when those links exist on approved plot-thread records.
- This page may link back to approved plot threads only when approved question records explicitly carry `linked_plot_thread_ids`.

Relationship to Continuity / Consistency:

- Approved continuity/consistency records may link to related open questions only when those links exist on approved continuity records.
- This page may link back to continuity/consistency only when approved question records explicitly carry `linked_continuity_issue_ids`.

Relationship to timeline, characters, locations, and objects:

- Linked affected story knowledge is approved-memory navigation only.
- Missing future pages should show `Related Page Not Implemented`.

Relationship to chapters, scenes, notes, and materials:

- Linked source pages show owner-authored/source material only.
- Source links are evidence/context, not approved question truth by themselves.

Relationship to Dramatica:

- This page is general open-question/unresolved-question support.
- Dramatica-specific unresolved-question classification is deferred.

## 14. Deferred Decisions

Deferred to later tasks:

- Exact runtime schema for `unresolved_question_memory_record` versus using `open_question_memory_record.question_type`.
- Exact allowed values for `question_type`, `status`, `priority`, `scope`, `answer_status`, and `resolution_status`.
- Exact memory envelope version and migration behavior.
- Whether first implementation reads directly from `memory/open_questions.json`, a memory summary endpoint, or both.
- Exact source/evidence locator format for scene, chapter, note, material, and memory-record links.
- Whether related open-question links use `related_open_question_ids` or a separate relation object.
- Exact OMI filter for open-question candidates.
- Exact apply-promotion behavior, rollback, and record supersession mechanics.
- Whether and when an owner-controlled answer/resolution workflow is added.
- Whether future visualization uses a graph, table, dependency map, timeline overlay, or side-by-side evidence view.
- Any future Dramatica structural unresolved-question taxonomy.

## 15. Non-Goals for WORKSPACE-018

WORKSPACE-018 does not implement:

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
- Approved Open Questions page UI.
- Backend memory/canon routes.
- Apply-promotion.
- Question extraction.
- Contradiction detection.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- Staging, commits, or pushes.
