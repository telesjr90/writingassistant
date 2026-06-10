# WORKSPACE-017: Continuity / Consistency Page Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-008: `docs/roadmap/project_overview_page_spec.md`
- WORKSPACE-011: `docs/roadmap/project_memory_canon_page_structure_spec.md`
- WORKSPACE-012: `docs/roadmap/omi_ideas_candidates_page_spec.md`
- WORKSPACE-013: `docs/roadmap/approved_characters_page_spec.md`
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- WORKSPACE-016: `docs/roadmap/approved_plot_threads_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- WORKSPACE-019: `docs/roadmap/approved_relationships_page_spec.md`
- WORKSPACE-020: `docs/roadmap/approved_organizations_groups_page_spec.md`
- WORKSPACE-021: `docs/roadmap/approved_objects_items_page_spec.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The Continuity / Consistency page should be the future project-local destination for owner-approved continuity warning and consistency issue memory/canon records. It must show only continuity/consistency records that have been explicitly applied by a future apply-promotion step into the approved memory/canon store. Pending, rejected, archived, needs-revision, and approved-but-not-applied continuity candidates must remain clearly separated in the OMI Ideas / Candidates page defined by WORKSPACE-012.

The Continuity / Consistency page should:

- Show owner-approved `continuity_warning_memory_record` or `consistency_issue_memory_record` entries for the selected project.
- Read approved continuity/consistency truth only from future memory files such as `memory/continuity_warnings.json` or an equivalent approved memory store.
- Clearly distinguish approved continuity/consistency truth from OMI continuity candidates, including pending, approved-but-not-applied, rejected, needs-revision, archived, promotion-record-only, and source-only material.
- Link each approved issue back to source evidence, provenance, source candidate IDs, source promotion record IDs, and approval metadata where available.
- Show unresolved or missing fields honestly as `Unknown`, `Not approved yet`, or `Not recorded`.
- Show an empty state when no approved continuity/consistency records exist.
- Link to the OMI Ideas / Candidates page for pending continuity candidates.
- Avoid model/Ollama calls in the first implementation.
- Avoid automatic extraction.
- Avoid contradiction detection.
- Avoid apply-promotion behavior.
- Avoid generated fixes, rewrite suggestions, generated explanations, and any controls that would write or rewrite story prose.
- Avoid Dramatica-specific continuity, contradiction, plot, signpost, driver, Concern, Issue, Problem, Solution, or structural claims unless later approved and evidence-backed by a separate advanced-layer task.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Continuity / Consistency Concepts and Required Labels

The page must make the following concepts distinct.

### Owner-Authored Source Material

Definition:

- Scenes, chapters, notes, materials, project metadata, bible/storyform context, and OMI raw ideas are source material or project context.

Rules:

- Source material may provide evidence/provenance for continuity candidates.
- Source material is not approved continuity/consistency memory/canon by default.
- A mismatch mentioned in a scene, note, or material is not an approved continuity issue by itself.
- Source material must not be copied into approved continuity memory/canon by opening this page.

### OMI Raw Ideas

Definition:

- Owner-authored raw idea records under future/current OMI storage.

Rules:

- Raw ideas are owner input.
- Raw ideas are not durable project truth.
- A raw idea that mentions a contradiction, continuity issue, or consistency concern is not an approved continuity record.

### OMI Continuity Candidates

Definition:

- Structured `continuity_warning_candidate` or future equivalent `consistency_issue_candidate` records that have not been applied to approved memory/canon.

Rules:

- Continuity candidates are not canon.
- Continuity candidates must not appear in the approved issue list.
- Candidate review and status changes happen on the OMI Ideas / Candidates page, not on this page.
- Candidate severity, resolution state, contradiction state, affected entities, and affected sources must not be inferred as approved truth.

### Approved-but-Not-Applied Candidates

Definition:

- Continuity candidates the owner has approved and that have an associated promotion audit record but have not yet been applied to memory/canon.

Rules:

- Approved-but-not-applied candidates are not approved continuity/consistency memory/canon.
- Approved-but-not-applied candidates must not appear in the approved issue list.
- The page may show candidate counts and links only.

### Promotion Records

Definition:

- Audit records capturing owner-approved intent, selected destination, evidence/provenance, source candidate snapshot, and final confirmation data.

Rules:

- Promotion records are not canon by themselves.
- Promotion records must not be displayed as approved continuity issues.
- Promotion records may be linked as provenance from an approved continuity record that a future apply-promotion step actually created.
- Promotion records present without an approved memory record must show an audit-only warning or candidate backlog state, not an approved issue.

### Applied Continuity / Consistency Memory Records

Definition:

- Durable owner-approved `continuity_warning_memory_record` or `consistency_issue_memory_record` entries written to the future approved memory store by a future apply-promotion step.

Rules:

- Applied continuity/consistency records are the only records allowed in the approved issue list.
- They must reference source candidate IDs, promotion record IDs, evidence/provenance, and approval metadata where available.
- They must remain project-local.
- They must not be generated by the page itself; opening this page must not create `memory/continuity_warnings.json` entries or equivalent records.

### Contradiction and Consistency State

Definition:

- Future stored fields that represent an approved issue type, related/paired issue links, severity, status, resolution state, and affected story knowledge references.

Rules:

- Contradiction or consistency state must come from approved memory/canon records only.
- The first implementation must not run contradiction detection.
- Broken, missing, duplicate, conflicting, or cyclic issue links must surface as non-destructive warnings.
- Missing or unsupported contradiction links must be shown as `Unknown` or `Not Recorded`, not inferred.

### Future Dramatica Structural Claims

Definition:

- Future Dramatica storyform-specific continuity or contradiction classifications, such as signpost conflict, driver conflict, throughline contradiction, Concern/Issue/Problem/Solution inconsistency, or thematic contradiction claims.

Rules:

- Dramatica-specific continuity and structural contradiction claims are deferred.
- The first version of this page must not display any Dramatica-specific contradiction or structural diagnosis.
- Generic continuity labels must not be treated as Dramatica proof.

### Model Output

Definition:

- Any output from a model, extractor, NotebookLM-like tool, or analysis system.

Rules:

- No model output is durable truth by default.
- Model/extractor output must flow through candidates, owner review, promotion record creation, and future apply-promotion before approved continuity display.
- The first implementation of this page must not call a model.

### Insufficient Evidence

Definition:

- Continuity evidence/provenance is missing, weak, broken, unsafe, one-sided, or not enough for the approved destination.

Rules:

- Insufficient evidence should be visible without deleting or rewriting the issue record.
- Apply-promotion itself must fail closed if evidence requirements are missing; the page must surface that state for any issue that already exists.

## 3. Approved Continuity / Consistency Display Model

Approved continuity/consistency records should display these fields when present:

| Field | Display rule |
| --- | --- |
| `continuity_issue_id` | Stable approved issue ID; required for detail routing. |
| `display_title` | Owner-approved title/label. Missing title shows `Unknown`. |
| `issue_type` | Stored type such as continuity warning, consistency issue, contradiction, missing link, duplicate fact, timeline mismatch, location mismatch, character-state mismatch, object-state mismatch, or relationship mismatch. |
| `severity` | Stored severity only. Do not infer severity from candidate output or source text. |
| `status` | Stored record status only. |
| `short_owner_approved_description` | Owner-approved description only. Do not generate explanation text. |
| `affected_scene_ids` | Approved source references only; broken references show warnings. |
| `affected_chapter_ids` | Approved source references only; broken references show warnings. |
| `linked_character_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_location_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_object_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_timeline_event_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `linked_plot_thread_ids` | Approved memory/canon links only; unresolved links show warnings. |
| `contradiction_pair_ids` or `related_issue_ids` | Optional approved issue links; broken or cyclic links show warnings and are not auto-repaired. |
| `first_seen_source` | First approved source/provenance locator if stored. |
| `latest_seen_source` | Latest approved source/provenance locator if stored. |
| `evidence` / `provenance` summary | Compact evidence/provenance metadata only; avoid long source copies and generated summaries. |
| `confidence` / `certainty` label | Stored confidence/certainty label only; it is owner-review metadata, not objective proof. |
| `owner_resolution_note` | Owner-approved resolution note only. No generated fix text. |
| `resolution_status` | Stored resolution status only, such as unresolved, needs owner review, resolved, superseded, archived, or not recorded. |
| `created_at` | Stored timestamp. |
| `updated_at` | Stored timestamp. |
| `approved_at` | Stored owner approval timestamp. |
| `approved_by` | Stored owner/reviewer identifier. |
| `source_candidate_ids` | OMI candidate provenance links only. |
| `promotion_record_ids` | Promotion audit links only. |
| `revision_history` | Stored revision trail if available. |
| `supersedes_record_ids` | Stored supersession links if available. |
| `superseded_by_record_id` | Stored replacement link if available. |
| `notes` | Owner notes, ambiguity notes, or implementation notes. No generated prose fixes. |

Display clarifications:

- Unapproved candidates must not appear as truth.
- Generated fixes, rewrite suggestions, and unapproved generated explanations are prohibited.
- Missing fields must be shown as `Unknown`, `Not approved yet`, or `Not recorded`.
- Approved records may contain compact owner-approved descriptions and owner notes; those are not AI-generated rewrite/fix text.
- If the underlying memory schema supports only `continuity_warning_memory_record`, the page should label consistency issue variants through `issue_type` rather than inventing a second file.

## 4. Required Labels

The page must use the following labels visibly.

| Label | Use |
| --- | --- |
| `Approved Continuity / Consistency Issue` | Marks each applied approved memory/canon record. |
| `Approved Memory` | Marks that the list reads from applied memory/canon only. |
| `Candidate` | Marks OMI continuity candidates outside the approved list. |
| `Pending Candidate` | Marks pending OMI continuity candidates on the OMI page; this page may show counts and links only. |
| `Approved Candidate` | Marks approved-but-not-applied continuity candidates on the OMI page; this page may show counts and links only. |
| `Rejected Candidate` | Marks rejected OMI continuity candidates. |
| `Needs Revision` | Marks OMI continuity candidates needing revision. |
| `Archived Candidate` | Marks archived OMI continuity candidates. |
| `Promotion Record Only` | Marks promotion records that have not yet been applied. |
| `Not Yet Applied` | Marks promotion records or approved candidates that have no applied memory record. |
| `Source / Evidence` | Marks source scene, chapter, note, material, or other source reference. |
| `Evidence Required` | Marks records where evidence is required but missing or weak. |
| `Insufficient Evidence` | Marks records where evidence exists but is not enough. |
| `Unknown` | Marks approved issue fields the owner has not yet approved. |
| `Not Approved Yet` | Marks fields that are pending owner approval or future owner-authored entry. |
| `Not Recorded` | Marks fields that the owner has chosen not to record. |
| `Resolution Status Placeholder` | Marks that first-version resolution management is not implemented. |
| `Related Page Not Implemented` | Marks links to future approved pages or entity pages that are not yet implemented. |
| `Future / Not Implemented` | Marks extraction, contradiction detection, apply-promotion, graph visualization, and Dramatica structural classification. |

Labeling rules:

- Labels must appear in UI copy and any future route/page surfaces where those states are represented.
- No candidate may be visually blended into the approved issue list.
- Counts must be separated by status.
- Approved issue counts must come from applied memory/canon records only.
- Approved-candidate counts must be labeled `Approved Candidate` or `Not Yet Applied`, not `Approved Continuity / Consistency Issue`.
- Promotion-record counts must be labeled `Promotion Record Only` or `Audit Only`.
- Pending, rejected, archived, needs-revision, duplicate, uncertain, and insufficient-evidence candidates must remain outside the approved issue list.

## 5. First-Version Page Sections

First-version sections:

- Page Header.
- Continuity / Consistency Boundary Banner.
- Approved Issue List.
- Issue Detail Panel.
- Evidence / Provenance Panel.
- Linked Sources Panel.
- Affected Story Knowledge Snapshot.
- Resolution Status Placeholder.
- Candidate Backlog Snapshot.
- Empty State.
- Warning State.
- Future Page Link Reference.

### Page Header

Purpose:

- Identify the active project and Continuity / Consistency area.
- Show approved issue count and safe navigation.

Data source:

- Active project metadata from `project.json`.
- Approved continuity records from `memory/continuity_warnings.json` or equivalent approved memory store if present.

Candidate/canon boundary:

- Header approved count must come from applied memory/canon records only.
- Candidate counts must be separated into the Candidate Backlog Snapshot.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate project summaries, continuity explanations, fixes, or rewrite suggestions.

Empty state:

- Show that no approved continuity/consistency issues exist yet.
- Missing `memory/` directory is a valid empty state.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt approved memory metadata shows warning state and avoids approved display.

### Continuity / Consistency Boundary Banner

Purpose:

- Explain that the page shows approved memory/canon records only.
- Point pending continuity candidates to OMI.

Data source:

- Static page copy.
- Optional lightweight OMI continuity candidate counts.

Candidate/canon boundary:

- State that OMI candidates, approved-but-not-applied candidates, and promotion records are not canon.
- State that approved issues require future apply-promotion into memory/canon.

No-prose boundary:

- Prohibit generated fixes, rewrite suggestions, generated explanations, and prose-patching controls.

Empty state:

- Banner remains visible even when no records exist.

Error state:

- Banner remains visible when approved-memory load partially fails.

### Approved Issue List

Purpose:

- List approved continuity/consistency issues for the selected project.
- Support local filter/search over approved issue metadata.

Data source:

- Applied `continuity_warning_memory_record` or `consistency_issue_memory_record` entries.
- Optional derived `memory/index.json` for navigation, with category files remaining source of truth.

Candidate/canon boundary:

- Exclude all OMI candidates, promotion records without applied memory, and source-only material.
- Candidate backlog may be represented only as separate counts/links.

No-prose boundary:

- Do not generate issue explanations, fixes, summaries, or scene rewrite suggestions.
- List item descriptions must come from approved stored fields only.

Empty state:

- "No approved continuity or consistency issues yet" with link to OMI candidate review if candidate counts exist.

Error state:

- Corrupt memory file, unsupported schema, duplicate IDs, unsafe IDs, or invalid records should show warnings and omit unsafe/invalid records from normal detail display.

### Issue Detail Panel

Purpose:

- Show the selected approved issue's stored fields, source candidate IDs, promotion record IDs, evidence/provenance, affected sources, linked story knowledge, approval metadata, resolution metadata, revision history, and notes.

Data source:

- Selected approved continuity/consistency memory record.

Candidate/canon boundary:

- Detail panel must not hydrate missing fields from OMI candidates.
- Source candidate and promotion links are provenance only.

No-prose boundary:

- Do not generate a fix, explanation, rewrite, bridge scene, contradiction resolution, or patch suggestion.

Empty state:

- Prompt the owner to select an approved issue.

Error state:

- Invalid selected ID, missing record, unsafe ID, unsupported schema, or broken relation links show non-destructive warnings.

### Evidence / Provenance Panel

Purpose:

- Show the evidence/provenance trail behind the approved issue.
- Identify first/last seen sources, evidence IDs, source candidate IDs, promotion record IDs, approval data, and confidence/certainty labels where stored.

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
- Do not summarize or rewrite source material.

Empty state:

- Show `Not Recorded` when no source links exist.

Error state:

- Broken scene, chapter, note, material, or unsafe reference shows non-destructive warning without host filesystem path leakage.

### Affected Story Knowledge Snapshot

Purpose:

- Show linked approved characters, locations, objects, timeline events, plot threads, and related issue links when those records are available.
- Help the owner navigate across approved memory pages.

Data source:

- Approved issue record link fields.
- Future approved memory files for linked records where implemented.

Candidate/canon boundary:

- Only approved memory/canon links may be shown as affected story knowledge truth.
- Missing pages/entities must be labeled as future/not implemented or broken links.

No-prose boundary:

- Do not generate entity summaries, event explanations, or contradiction narratives.

Empty state:

- Show `Not Recorded` or `No linked approved story knowledge`.

Error state:

- Broken timeline/character/location/object/plot-thread links show warnings and do not auto-repair.

### Resolution Status Placeholder

Purpose:

- Reserve space for future owner-controlled resolution workflow without implementing mutation.
- Display stored `resolution_status` and `owner_resolution_note` when present.

Data source:

- Approved issue record fields only.

Candidate/canon boundary:

- Resolution status must not be inferred from candidates, source edits, or promotion records.

No-prose boundary:

- No "fix continuity", "rewrite scene", "resolve contradiction", "generate bridge scene", "patch plot hole", or "explain contradiction" controls.

Empty state:

- Show `Resolution status not recorded`.

Error state:

- Severity/status and resolution conflicts show non-destructive warnings.

### Candidate Backlog Snapshot

Purpose:

- Show lightweight counts and links for OMI continuity candidates by status.
- Help the owner navigate to OMI without blending candidate records into approved truth.

Data source:

- OMI index/candidate metadata where available.

Candidate/canon boundary:

- Candidate backlog may show counts and links only.
- Candidate text, proposed severity, proposed resolution, and proposed contradiction state must not be shown as approved truth.

No-prose boundary:

- Do not generate candidate summaries or explanations.

Empty state:

- Show `No pending continuity candidates`.

Error state:

- Corrupt OMI index/candidate metadata shows an OMI warning without blocking approved issue display.

### Empty State

Purpose:

- Provide safe guidance when no approved continuity/consistency records exist.

Data source:

- Approved memory file presence and record count.
- Optional OMI continuity candidate counts.

Candidate/canon boundary:

- Empty approved state remains empty even if candidates exist.
- If candidates exist, link to OMI with candidate labels only.

No-prose boundary:

- Empty-state guidance must not ask the AI to invent issues or fixes.

Empty state:

- "No approved continuity or consistency issues have been applied yet."

Error state:

- If memory load fails, use Warning State instead of empty state.

### Warning State

Purpose:

- Surface invalid, missing, corrupt, unsafe, unsupported, duplicate, broken-link, conflict, or insufficient-evidence states.

Data source:

- Project validation.
- Memory file validation.
- OMI candidate/promotion metadata validation when candidate counts are shown.

Candidate/canon boundary:

- Warnings are diagnostics, not approved story truth.
- Warnings must not promote, resolve, retitle, or repair records.

No-prose boundary:

- Warning copy is factual status text only.
- Do not generate fixes, rewrite suggestions, or explanatory story prose.

Empty state:

- Show "No continuity warnings detected in approved memory metadata" only when validation ran and found no warnings.

Error state:

- Partial validation failure should show partial warnings and preserve read-only page behavior.

### Future Page Link Reference

Purpose:

- Link to related approved pages and future page placeholders.
- Clarify implementation status for characters, locations/settings, objects, timeline, plot threads, OMI, and Project Memory / Canon.

Data source:

- Route/page availability metadata.
- Static planning copy.

Candidate/canon boundary:

- Links to approved pages must use approved-memory labels.
- Links to OMI must use candidate/audit labels.

No-prose boundary:

- Navigation only; no generated page summaries.

Empty state:

- Show future/not implemented labels for unavailable pages.

Error state:

- Broken route/page availability state shows a non-blocking navigation warning.

## 6. Candidate / Canon Separation

Approved records:

- Approved continuity/consistency records are read from future memory files such as `memory/continuity_warnings.json` or an equivalent approved memory store.
- Approved continuity/consistency truth exists only after owner approval, promotion record creation, and successful future apply-promotion into approved memory/canon.
- Approved records are project-local and must not leak across projects.

OMI candidates:

- OMI continuity candidates remain in OMI candidates.
- Pending, rejected, archived, duplicate, uncertain, and needs-revision candidates do not appear as approved issues.
- Approved-but-not-applied candidates do not appear as approved issues.
- Candidate backlog may show counts and links only.

Promotion records:

- Promotion records are audit-only unless future apply-promotion has created or updated approved continuity memory.
- Source candidate and promotion audit links may be shown as provenance from approved records.
- Promotion records present but no approved memory record must show `Promotion Record Only` or `Not Yet Applied`, not an approved issue.

Inference restrictions:

- Severity, resolution, contradiction status, affected entities, affected source references, and related issue links must not be inferred as truth from candidate output.
- Missing approved fields must remain missing and be displayed honestly.
- No model, extractor, NotebookLM output, source material, or raw analysis artifact may directly become approved continuity truth.

## 7. First-Version Operations

Allowed first-version operations:

- View approved continuity/consistency issue list.
- View issue details.
- Filter/search approved issues locally.
- Open linked source scene/note/material.
- Open linked timeline event, character, location, object, or plot-thread page if available.
- Open related OMI candidate or promotion record as provenance/audit context.
- Show resolution-status placeholder.
- Show affected story-knowledge snapshot.

Future-only operations:

- Edit approved continuity memory.
- Merge/split approved issues.
- Archive/restore.
- Mark issue resolved.
- Apply-promotion.
- Extract continuity candidates.
- Contradiction detection.
- Continuity graph visualization.
- Generate fixes.
- Rewrite scene to fix continuity.
- Dramatica structural contradiction classification.

## 8. Local Search and Filter Planning

First-version search/filter should be local and deterministic over approved records only.

Search/filter fields:

- `display_title`
- `issue_type`
- `severity`
- `status`
- `resolution_status`
- `tags` if available
- approved description if available
- linked source IDs
- affected scene/chapter IDs
- linked character/location/object/timeline/plot-thread IDs
- `source_candidate_ids`
- `promotion_record_ids`

Rules:

- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No extraction during search.
- No contradiction detection during search.
- Approved-only labels must remain visible in search results.
- Candidate counts/links may be separately filtered by status only if the UI makes them clearly non-canon.

## 9. Warning and Invalid-State Behavior

The page should warn for these states:

- Missing `memory/`.
- Missing or corrupt `memory/continuity_warnings.json`.
- Unsupported memory schema.
- Approved record references missing source candidate.
- Broken scene/note/material references.
- Broken timeline/character/location/object/plot-thread references.
- Duplicate continuity IDs.
- Unsafe IDs.
- Severity/status conflicts.
- Resolution status conflicts.
- Affected source references missing.
- Contradiction pair links broken/cyclic if represented.
- Promotion records present but no approved memory record.
- OMI continuity candidates exist but no approved issues yet.
- Related pages/entities not implemented yet.
- Missing or insufficient evidence.
- Corrupt `memory/index.json`.

Warning rules:

- Warnings are non-destructive.
- Warnings must not auto-repair records.
- Warnings must not auto-delete records.
- Warnings must not rewrite identity.
- Warnings must not retitle issues.
- Warnings must not correct severity or status.
- Warnings must not resolve issues.
- Warnings must not promote candidates.
- Warnings must not leak host filesystem paths.
- Warnings should use project-relative identifiers where needed.

## 10. Future API Planning

These routes are future planning only. Do not implement them in WORKSPACE-017.

Route group:

```text
GET /api/projects/{project_id}/memory/continuity-warnings
GET /api/projects/{project_id}/memory/continuity-warnings/{continuity_issue_id}
GET /api/projects/{project_id}/memory/continuity-warnings/{continuity_issue_id}/provenance
GET /api/projects/{project_id}/memory/continuity-warnings/health
```

### `GET /api/projects/{project_id}/memory/continuity-warnings`

Purpose:

- List approved continuity/consistency issues for one project.
- Optionally include approved-only counts and lightweight warning metadata.

Request shape:

- Path parameter `project_id`.
- Optional query parameters for local filter/sort/search over approved issue fields.
- No body.

Response shape:

- Project ID.
- Approved issue list or compact issue summaries.
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

- Do not generate issue descriptions, explanations, fixes, summaries, or rewrites.

Expected errors:

- Project not found.
- Missing memory store, treated as empty if project is valid.
- Corrupt memory file.
- Unsupported schema.
- Unsafe ID.
- Broken index warning.

### `GET /api/projects/{project_id}/memory/continuity-warnings/{continuity_issue_id}`

Purpose:

- Load one approved issue detail.

Request shape:

- Path parameters `project_id` and `continuity_issue_id`.
- No body.

Response shape:

- Approved issue detail record.
- Approved display fields.
- Warnings for missing linked records or unsupported optional fields.

Validation:

- `project_id` and `continuity_issue_id` must be safe IDs.
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
- No generated fix, rewrite, bridge scene, contradiction explanation, or diagnostic prose generation.

Expected errors:

- Project not found.
- Approved memory missing.
- Record not found.
- Duplicate record ID.
- Unsafe ID.
- Unsupported schema.

### `GET /api/projects/{project_id}/memory/continuity-warnings/{continuity_issue_id}/provenance`

Purpose:

- Return evidence/provenance metadata for one approved issue.
- Support audit links to source candidate IDs and promotion record IDs.

Request shape:

- Path parameters `project_id` and `continuity_issue_id`.
- No body.

Response shape:

- Evidence IDs.
- Provenance metadata.
- First/latest source locators if stored.
- Source candidate IDs.
- Promotion record IDs.
- Missing/broken reference warnings.

Validation:

- Same ID safety as issue detail.
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
- Do not generate summaries or explanations.

Expected errors:

- Project not found.
- Record not found.
- Corrupt provenance metadata.
- Broken source candidate reference.
- Broken promotion record reference.
- Unsafe source locator.

### `GET /api/projects/{project_id}/memory/continuity-warnings/health`

Purpose:

- Validate continuity/consistency memory health without mutation.
- Report missing/corrupt/unsupported/duplicate/broken-link/conflict states.

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
- Validate memory envelope, IDs, schema version, duplicate IDs, linked sources, linked approved entities, contradiction pair links, status/severity/resolution conflicts, and evidence presence.

Path safety:

- Do not expose host filesystem paths.
- Use project-relative IDs and safe labels.

Candidate/canon boundary:

- Health warnings are diagnostics, not approved story truth.
- Candidate counts remain candidate-only.

No-prose boundary:

- Warnings are factual status messages only.
- Do not propose fixes or rewrites.

Expected errors:

- Project not found.
- Corrupt memory file.
- Corrupt memory index.
- Unsupported schema.
- Unsafe ID.
- Partial validation failure.

## 11. Future Frontend Planning

These components are future planning only. Do not implement UI in WORKSPACE-017.

Future components:

- `ContinuityConsistencyPage`
- `ContinuityConsistencyBoundaryBanner`
- `ApprovedContinuityIssueList`
- `ApprovedContinuityIssueListItem`
- `ContinuityIssueDetailPanel`
- `ContinuityIssueEvidencePanel`
- `ContinuityIssueSourceLinksPanel`
- `ContinuityAffectedStoryKnowledgeSnapshot`
- `ContinuityResolutionStatusPlaceholder`
- `ContinuityCandidateBacklogSnapshot`
- `ContinuitySearchFilterControls`
- `ContinuityWarningsPanel`
- `ContinuityEmptyState`
- `ContinuityFuturePagesReference`

Component rules:

- No AI writing buttons.
- No generated fix button.
- No controls named or behaving like `fix continuity`, `rewrite scene`, `resolve contradiction`, `generate bridge scene`, `patch plot hole`, or `explain contradiction`.
- Search/filter controls must be local and deterministic.
- Candidate backlog controls must route to OMI and remain labeled as candidate/audit state.
- Detail panels must display stored approved fields only.
- Warning panels must be non-destructive.

## 12. Future Tests

Future tests should cover:

- No memory directory / no approved records.
- Load approved continuity records.
- Pending OMI candidates do not appear as approved truth.
- Promotion records without apply-promotion do not appear as approved truth.
- Corrupt memory file warning.
- Duplicate continuity IDs warning.
- Unsafe IDs rejected.
- Broken source links warning.
- Broken timeline/character/location/object/plot-thread links warning.
- Severity/status conflicts warning.
- Resolution status conflicts warning.
- Contradiction pair broken/cyclic warning if represented.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- No AI prose-generation controls.
- No generated fixes/rewrites/summaries/explanations.
- No Dramatica structural contradiction claims.
- No JSONL/training writes.

## 13. Page Relationships

Relationship to Project Memory / Canon:

- The Continuity / Consistency page is an approved-memory category page.
- It reads approved records only and should be reachable from the future Project Memory / Canon category cards.

Relationship to OMI:

- OMI is the review workspace for continuity candidates.
- The page may link to OMI candidate filters/counts but must not display candidates as approved issues.

Relationship to Approved Plot Threads:

- Approved plot threads may link to related continuity warnings only when those links exist on approved plot-thread records.
- This page may link back to approved plot threads only when approved issue records explicitly carry `linked_plot_thread_ids`.

Relationship to timeline, characters, locations, and objects:

- Linked affected story knowledge is approved-memory navigation only.
- Missing future pages should show `Related Page Not Implemented`.

Relationship to Dramatica:

- This page is general continuity/consistency support.
- Dramatica-specific contradiction classification is deferred.

## 14. Deferred Decisions

Deferred to later tasks:

- Exact runtime schema for `consistency_issue_memory_record` versus using `continuity_warning_memory_record.issue_type`.
- Exact allowed values for `issue_type`, `severity`, `status`, and `resolution_status`.
- Exact memory envelope version and migration behavior.
- Whether first implementation reads directly from `memory/continuity_warnings.json`, a memory summary endpoint, or both.
- Exact source/evidence locator format for scene, chapter, note, material, and memory-record links.
- Whether contradiction pairs use `contradiction_pair_ids`, `related_issue_ids`, or a separate relation object.
- Exact OMI filter for continuity candidates.
- Exact apply-promotion behavior, rollback, and record supersession mechanics.
- Whether and when an owner-controlled edit/resolution workflow is added.
- Whether future visualization uses a graph, table, timeline overlay, or side-by-side evidence view.
- Any future Dramatica structural contradiction taxonomy.

## 15. Non-Goals for WORKSPACE-017

WORKSPACE-017 does not implement:

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
- Continuity / Consistency page UI.
- Backend memory/canon routes.
- Apply-promotion.
- Continuity extraction.
- Contradiction detection.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- Staging, commits, or pushes.
