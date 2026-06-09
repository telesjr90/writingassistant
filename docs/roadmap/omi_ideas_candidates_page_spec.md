# WORKSPACE-012: OMI Ideas / Candidates Page Spec

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
- WORKSPACE-013: `docs/roadmap/approved_characters_page_spec.md`
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- OMI schema/lifecycle: `docs/roadmap/omi_mvp_schema_lifecycle.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

The OMI Ideas / Candidates page should be the dedicated project-local review workspace for owner-authored OMI raw ideas, structured OMI candidates, owner review decisions, destinations, evidence/provenance, promotion readiness, and promotion audit records.

The page should:

- Show project-local OMI raw ideas.
- Show project-local OMI candidates.
- Support owner review of candidates.
- Show owner decision, status, destination, provenance, evidence, timestamps, source links, confidence, and blockers.
- Show promotion readiness before promotion record creation.
- Show promotion records as audit-only records.
- Distinguish raw ideas, candidates, approved candidates, promotion records, and applied memory/canon.
- Keep OMI separate from project memory/canon until a future apply-promotion flow explicitly applies a promotion record.
- Avoid model/Ollama calls in the first implementation.
- Avoid Dramatica-specific requirements in this workspace phase.
- Avoid any story prose generation, rewriting, continuation, polish, improvement, expansion, imitation, or insertion controls.

The application may store, edit, and organize owner-authored raw ideas, notes, metadata, and materials. The application may display and review OMI candidates. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. OMI Concepts and Required Labels

The page must make the following concepts distinct.

### Owner Raw Idea

Definition:

- An owner-authored raw idea stored under project-local OMI storage.

Rules:

- A raw idea is owner input, not AI prose output.
- Saving or listing raw ideas must not be blocked as AI prose generation.
- Raw ideas are not canon.
- Raw ideas may remain unstructured.
- Raw ideas may link to candidates.
- Raw ideas must not be converted into project truth automatically.

Required label:

- `Owner Raw Idea`

### Candidate

Definition:

- Structured planning or story-knowledge material stored for review.

Rules:

- Candidate content must be clearly labeled.
- Candidates may be manual, extractor-created, or future model-assisted.
- Candidates are not canon until future explicit apply-promotion succeeds.
- Candidate records must not mutate scenes, notes, materials, bible/storyform, project metadata, or memory/canon.

Required labels:

- `Candidate`
- `Pending Candidate`
- `Approved Candidate`
- `Rejected Candidate`
- `Needs Revision`
- `Archived Candidate`

### Manual Candidate

Definition:

- A candidate created directly by the owner or through manual structured entry.

Rules:

- Manual candidate fields are owner review metadata and structured planning data.
- Manual candidate creation is not AI writing.

### Extractor-Created Candidate

Definition:

- A future candidate created by a deterministic or tool-assisted extraction path from owner-authored project material.

Rules:

- Extractor output is not authoritative.
- Extractor output must include source references and provenance where practical.
- Extractor output must land in OMI review, not approved memory/canon.

### Future Model-Assisted Candidate

Definition:

- A future candidate created with model assistance after a later approved task.

Rules:

- First implementation of this page must not create model-assisted candidates.
- Any future model-assisted candidate must be sanitized, labeled, candidate-only, and evidence/provenance-backed where required.
- Model-assisted candidates must not include generated story prose.

Required label:

- `Future / Not Implemented`

### Promotion-Ready Candidate

Definition:

- An approved candidate that currently satisfies promotion readiness requirements for record-only promotion creation.

Rules:

- Promotion-ready does not mean canon.
- Promotion-ready means a promotion audit record may be created after final owner confirmation.

Required labels:

- `Promotion Ready`
- `Promotion Blocked`

### Promotion Record

Definition:

- An audit record capturing owner-approved intent, selected destination, source candidate snapshot, evidence/provenance, and final confirmation.

Rules:

- A promotion record is not canon by itself.
- Promotion record creation must not mutate memory/canon.
- Promotion records should link back to the source candidate snapshot.
- Runtime apply-promotion remains future-only.

Required labels:

- `Promotion Record Only`
- `Not Yet Applied`

### Applied Memory / Canon Record

Definition:

- Durable project-local memory/canon created only by a future successful apply-promotion step.

Rules:

- Applied memory/canon is shown in approved memory/canon pages, not as raw OMI truth.
- Applied records may link back to candidate and promotion record IDs.

Required labels:

- `Approved Canon`

### Blocked Prose Request

Definition:

- A request or control that would ask the AI to write, rewrite, continue, polish, improve, imitate, expand, or extend story prose.

Rules:

- The page must not expose these controls.
- If a future freeform request field exists, prohibited requests must return the standard refusal.

### Insufficient Evidence

Definition:

- Candidate evidence/provenance is missing, weak, broken, unsafe, or not enough for the proposed destination.

Rules:

- Insufficient evidence blocks promotion readiness where evidence is required.
- Insufficient evidence should be visible without deleting or rewriting the candidate.

Required labels:

- `Insufficient Evidence`
- `Evidence Required`

Clarifications:

- An approved candidate is not durable canon until apply-promotion exists and is explicitly run.
- A promotion record is not canon by itself.
- A raw idea is owner input, not AI prose output.
- Candidate content must be clearly labeled wherever shown.

## 3. First-Version Page Layout

First-version sections:

- Page Header.
- OMI Boundary Banner.
- Raw Ideas List.
- Candidate List.
- Candidate Detail Panel.
- Owner Decision Panel.
- Destination / Target Panel.
- Evidence / Provenance Panel.
- Promotion Readiness Panel.
- Promotion Records Snapshot.
- Candidate vs Canon Explanation.
- Filters / Search.
- Empty-State Guidance.
- Warning / Error Area.
- Future Extraction Placeholder.

### Page Header

Purpose:

- Identify the active project and the OMI Ideas / Candidates workspace area.
- Show lightweight counts for raw ideas, candidates, approved candidates, blocked candidates, and promotion records.

Data source:

- Active project metadata from `project.json`.
- `omi/index.json` and OMI record metadata where present.

No-prose boundary:

- Header text is navigation/status only.
- Do not generate project summaries, idea summaries, candidate summaries, scene prose, premise prose, or recommendations.

Candidate/canon boundary:

- Counts must separate candidates, promotion records, and applied memory/canon.
- Approved memory/canon counts may be shown only from future applied `memory/*.json` records and must be labeled separately.

Empty state:

- Show zero OMI records and safe guidance to capture an owner raw idea or return to project navigation.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt OMI metadata shows warnings and degraded lists where safe.

### OMI Boundary Banner

Purpose:

- State that OMI is candidate review, not canon and not an AI writing surface.

Data source:

- Static product boundary copy.

No-prose boundary:

- Banner must include or link to the standard refusal policy.
- No write, rewrite, continue, polish, improve, imitate, expand, or generate controls.

Candidate/canon boundary:

- Banner should state that approved candidates and promotion records are not applied canon.

Empty state:

- Banner remains visible even when no OMI records exist.

Error state:

- Banner remains visible even when OMI data is partially corrupt.

### Raw Ideas List

Purpose:

- Show project-local owner raw ideas.
- Let the owner select a raw idea for detail and candidate links.

Data source:

- `omi/ideas/{idea_id}.json`.
- `omi/index.json` as a convenience lookup when valid.

No-prose boundary:

- Raw idea text is owner-authored input.
- The list must not rewrite, summarize, expand, polish, or classify ideas with a model.

Candidate/canon boundary:

- Each row must use `Owner Raw Idea`.
- Linked candidate counts must be candidate-only.
- Raw ideas are not canon.

Empty state:

- Missing `omi/ideas/` or no idea records should show a valid empty state.

Error state:

- Corrupt idea records show warning rows and should not be auto-deleted or auto-repaired.

### Candidate List

Purpose:

- Show OMI candidates for review and filtering.

Data source:

- `omi/candidates/{candidate_id}.json`.
- `omi/index.json` as a convenience lookup when valid.

No-prose boundary:

- Candidate list must display stored structured fields only.
- Do not synthesize summaries or infer story truth.

Candidate/canon boundary:

- Each row must use candidate status labels such as `Pending Candidate`, `Approved Candidate`, `Rejected Candidate`, `Needs Revision`, or `Archived Candidate`.
- Promotion record and applied canon links must be visually distinct.

Empty state:

- No candidates should show guidance that raw ideas may remain unstructured and extraction is future-only.

Error state:

- Corrupt candidate records show warnings and are excluded from unsafe actions.

### Candidate Detail Panel

Purpose:

- Show selected candidate details for review.

Data source:

- Selected candidate record.
- Linked raw idea, source references, and promotion records when available.

No-prose boundary:

- Show stored structured fields only.
- No prose generation, rewrite, continue, polish, improve, expand, imitate, or insert controls.

Candidate/canon boundary:

- Use `Candidate` labeling around all candidate content.
- Approved status does not make the detail panel canon.

Empty state:

- No selection should show choose-a-candidate guidance.

Error state:

- Unsupported schema, malformed content, or missing source links should show warnings and disable unsafe actions.

### Owner Decision Panel

Purpose:

- Let the owner review candidate status and decision metadata.

Data source:

- Candidate `status` and `owner_decision`.

No-prose boundary:

- Owner decision notes are owner-authored metadata.
- Decision controls are metadata/review controls, not AI writing controls.

Candidate/canon boundary:

- Allowed owner actions are `approve`, `reject`, `needs_revision`, and `archive`.
- Future structured field revision, evidence confirmation, destination choice, insufficient-evidence marking, and promotion record request are metadata/review actions.
- No action directly mutates memory/canon, scenes, notes, materials, bible/storyform, or storyform context.

Empty state:

- No selected candidate disables review controls.

Error state:

- Invalid status transitions or unsupported decisions should fail closed.

### Destination / Target Panel

Purpose:

- Show or select the candidate's proposed destination and future safe target metadata.

Data source:

- Candidate `destination`.
- Future destination allowlist.
- Promotion record `target_file` and `target_path` where present.

No-prose boundary:

- Destinations must not include scene prose, dialogue, chapter prose, final story text, rewrite, continuation, polish, or improvement targets.

Candidate/canon boundary:

- Destination selection is candidate metadata.
- Destination selection alone does not mutate the target.

Empty state:

- Missing destination shows `Promotion Blocked`.

Error state:

- Unsafe, unsupported, or prose destinations show blocking warnings.

### Evidence / Provenance Panel

Purpose:

- Show evidence, source references, source kind, author/tool/model fields, source paths, hashes, confidence, and timestamps.

Data source:

- Candidate `evidence`.
- Candidate `provenance`.
- Linked raw idea and source references.

No-prose boundary:

- Evidence display must not generate explanatory prose beyond stored metadata and fixed UI labels.
- No generated summaries of evidence.

Candidate/canon boundary:

- Evidence supports review; it does not establish truth without owner approval and future apply-promotion.

Empty state:

- Missing evidence shows `Evidence Required` or `Insufficient Evidence` where the destination requires it.

Error state:

- Broken source references, unsafe paths, or unsupported source kinds show warnings and block readiness where required.

### Promotion Readiness Panel

Purpose:

- Show whether a candidate is ready for record-only promotion creation.

Data source:

- Candidate status, owner decision, destination, safe target metadata, structured content, evidence/provenance, and final confirmation state.

No-prose boundary:

- Readiness checks are validation/status only.
- No model call, generated summary, or generated fix.

Candidate/canon boundary:

- `Promotion Ready` means eligible to create a promotion audit record only.
- `Promotion Blocked` means at least one required gate is missing.

Empty state:

- No selected candidate shows no readiness state.

Error state:

- Unsupported schema or unsafe destination fails closed.

Required readiness fields:

- Approved candidate status.
- Owner decision approval and explicit approval confirmation.
- Explicit destination.
- Safe target type.
- Structured candidate content.
- Evidence/provenance where required.
- Final owner confirmation before record creation.

### Promotion Records Snapshot

Purpose:

- Show existing promotion audit records related to the current project or selected candidate.

Data source:

- `omi/promotions/{promotion_id}.json`.
- Promotion IDs from `omi/index.json` when valid.

No-prose boundary:

- Snapshot displays stored audit metadata only.

Candidate/canon boundary:

- Promotion records must be labeled `Promotion Record Only` and `Not Yet Applied`.
- Promotion record creation must not apply memory/canon.
- Future apply-promotion remains separate and future-only.

Empty state:

- No promotion records should show that no promotion audit records exist.

Error state:

- Corrupt promotion records show warnings and are not auto-repaired.

### Candidate vs Canon Explanation

Purpose:

- Explain the boundary between raw ideas, candidates, approved candidates, promotion records, and applied memory/canon.

Data source:

- Static page copy tied to this spec and WORKSPACE-011.

No-prose boundary:

- Explanation is product boundary copy only.

Candidate/canon boundary:

- Must state that raw ideas and candidates are not canon.
- Must state that approved candidates are not durable canon.
- Must state that promotion records are audit-only.
- Must state that applied memory/canon records require future apply-promotion.

Empty state:

- Always visible or available.

Error state:

- Always visible or available.

### Filters / Search

Purpose:

- Help the owner find raw ideas, candidates, and promotion records locally.

Data source:

- Loaded OMI record metadata and cheap text fields.

No-prose boundary:

- No semantic search in the first version.
- No model/Ollama calls.
- No generated summaries.
- No extraction during search.

Candidate/canon boundary:

- Search results must distinguish raw ideas, candidates, promotion records, and approved canon.

Empty state:

- No results shows deterministic no-match guidance.

Error state:

- Corrupt records remain warning results or are excluded with visible warning counts.

First-version filters/search:

- Candidate status.
- Owner decision.
- Destination.
- Candidate type.
- Source kind.
- Evidence present/missing.
- Promotion readiness.
- Cheap/safe text fields from raw idea and candidate metadata.
- `created_at` and `updated_at`.

### Empty-State Guidance

Purpose:

- Explain what the owner can do when no OMI records exist.

Data source:

- Static copy plus route availability.

No-prose boundary:

- Guidance must not generate story ideas, prompts, premises, summaries, or prose.

Candidate/canon boundary:

- Guidance should say raw ideas are optional owner-authored inputs and candidates remain review material.

Empty state:

- Missing OMI folder, missing index, no raw ideas, no candidates, and no promotions are valid empty states.

Error state:

- If corruption prevents complete empty-state determination, show warnings and degraded counts.

### Warning / Error Area

Purpose:

- Surface non-destructive OMI health issues.

Data source:

- OMI folder/index/record validation and safe path checks.

No-prose boundary:

- Warnings are factual status messages only.

Candidate/canon boundary:

- Warnings must not repair, promote, delete, rewrite, or relabel records silently.

Empty state:

- Show no blocking warnings when clean.

Error state:

- Warnings are non-destructive and must not auto-repair unless a future owner-approved repair flow exists.

Warning categories:

- Missing OMI directory.
- Missing OMI index.
- Corrupt idea records.
- Corrupt candidate records.
- Corrupt promotion records.
- Unsupported OMI schema version.
- Approved candidate not applied.
- Promotion record not applied.
- Missing evidence/provenance.
- Unsafe destination.
- Blocked prose destination/type.
- Broken source references.
- Duplicate OMI IDs.
- Candidate references missing source.
- Future typed-candidate schema not implemented.

### Future Extraction Placeholder

Purpose:

- Reserve space for later extraction trigger strategy without implementing it.

Data source:

- Static placeholder and future task links.

No-prose boundary:

- Placeholder must not call a model, extractor, or hidden analysis path.

Candidate/canon boundary:

- Placeholder must state extraction output will land as OMI candidates for owner review.

Empty state:

- Show `Future / Not Implemented`.

Error state:

- No runtime error should occur because no extraction is implemented.

## 4. Raw Idea Behavior

Raw ideas:

- Are owner-authored input.
- May contain fragmentary planning language.
- May contain owner-written story fragments, but saving them is owner-authored storage, not AI prose generation.
- Are not canon.
- Can be linked to candidates.
- Can remain unstructured indefinitely.
- Can be archived later.
- Must not be converted into project truth automatically.
- Must not trigger a model call when saved or listed in the first implementation.

Raw idea save:

- Must not be blocked as AI prose generation.
- Must validate project ID and idea record shape.
- Must preserve owner text on save failure.
- Must not create candidate records unless the owner explicitly creates or triggers that behavior through a future approved flow.

Raw idea deletion:

- Requires separate future design.
- First implementation should prefer archive over permanent delete.

## 5. Candidate Behavior

Candidate display and review should show:

- Candidate ID.
- Candidate type.
- Candidate status.
- Owner decision.
- Destination.
- Structured content.
- Evidence.
- Provenance.
- Source references.
- Confidence.
- Blockers.
- `created_at`.
- `updated_at`.
- Source idea/candidate links.
- Promotion readiness.

Allowed owner actions:

- Approve.
- Reject.
- Mark `Needs Revision`.
- Archive.
- Revise structured fields if a future UI explicitly supports it.
- Choose destination.
- Attach or confirm evidence/provenance.
- Mark `Insufficient Evidence`.
- Request promotion record creation only if readiness passes.

Action boundaries:

- Owner actions are metadata/review actions, not AI writing.
- No action directly mutates memory/canon.
- No action directly mutates scenes, notes, materials, bible/storyform, storyform context, project metadata, or owner memory.
- No action inserts generated prose.
- No generated prose may be saved into candidate fields.

## 6. Promotion Readiness and Promotion Records

Readiness blockers should be visible before creating a promotion record.

Required readiness fields:

- Candidate exists.
- Candidate status is approved.
- Owner decision is approve.
- Owner approval confirmation is explicit.
- Destination is explicit.
- Destination is safe and allow-listed.
- Target type is safe.
- Candidate content is structured.
- Evidence/provenance exists where required.
- Final owner confirmation is provided.
- Source candidate snapshot can be recorded.

Promotion records:

- Remain audit-only.
- Must not apply memory/canon.
- Must not mutate project truth files.
- Must link back to source candidate ID.
- Should store a source candidate snapshot.
- Should preserve evidence/provenance at promotion time.
- Should use `Promotion Record Only` and `Not Yet Applied` labels until future apply-promotion succeeds.

Future apply-promotion:

- Remains separate and future-only.
- Must be owner-controlled.
- Must be atomic or fail closed.
- Must write applied memory/canon only through a later explicit design.

## 7. Filters and Search

First-version search is local and deterministic.

Allowed filters/search dimensions:

- Candidate status.
- Owner decision.
- Destination.
- Candidate type.
- Source kind.
- Evidence present/missing.
- Promotion readiness.
- Raw idea text if already loaded or cheap/safe to load.
- Candidate metadata text fields if already loaded or cheap/safe to load.
- `created_at`.
- `updated_at`.

Not allowed in the first version:

- Semantic search.
- Model/Ollama calls.
- Generated summaries.
- Hidden extraction.
- Generated search expansions.
- Automatic candidate creation from search.
- Automatic repair or promotion from search.

Result labeling:

- Raw ideas: `Owner Raw Idea`.
- Candidates: `Candidate` plus status.
- Promotion records: `Promotion Record Only` and `Not Yet Applied`.
- Applied memory/canon: `Approved Canon` only when future memory/canon records exist.

## 8. Warning and Error States

Warnings are non-destructive. The page must not auto-repair, auto-delete, silently promote, silently rewrite destinations, or silently create records.

Required warning/error states:

- Missing OMI directory.
- Missing OMI index.
- Corrupt idea records.
- Corrupt candidate records.
- Corrupt promotion records.
- Unsupported OMI schema version.
- Approved candidate not applied.
- Promotion record not applied.
- Missing evidence/provenance.
- Unsafe destination.
- Blocked prose destination/type.
- Broken source references.
- Duplicate OMI IDs.
- Candidate references missing source.
- Future typed-candidate schema not implemented.

Behavior:

- Missing optional OMI folders are valid empty states unless the active action requires them.
- Corrupt records should show warnings and disable unsafe actions for those records.
- Duplicate IDs should fail closed for actions that require a unique target.
- Unsupported schema versions should display read-only or needs-migration states.
- Broken source references should not invalidate the whole page.

## 9. API Planning

This section documents route planning only. Do not implement routes in this task.

### `GET /api/projects/{project_id}/omi`

Purpose:

- Load OMI summary/index, raw idea list, candidate list, and promotion record snapshot where current runtime supports it.

Page dependency:

- Page load, counts, lists, filters, and warnings.

Validation:

- Safe project ID.
- JSON object/array shape for returned data.
- Non-destructive degraded handling for missing folders/index.

No-prose boundary:

- Read-only metadata and record display.
- No model calls or generated summaries.

Candidate/canon boundary:

- Must label candidates and promotion records separately from approved canon.

Expected errors:

- Invalid project ID.
- Corrupt index.
- Corrupt record.
- Unsupported schema.

Status:

- Currently implemented as a bounded OMI summary route. Future first-page work may expand health details and filtering metadata.

### `POST /api/projects/{project_id}/omi/ideas`

Purpose:

- Save an owner-authored raw idea.

Page dependency:

- Raw idea capture.

Validation:

- Safe project ID.
- Non-empty owner raw idea.
- Provenance object when supplied.

No-prose boundary:

- Raw idea is owner input and must not be blocked as assistant request intent.
- No model call.

Candidate/canon boundary:

- Creates raw idea only, not canon.

Expected errors:

- Invalid project ID.
- Empty idea.
- Invalid provenance.
- Write failure.

Status:

- Currently implemented.

### `GET /api/projects/{project_id}/omi/ideas/{idea_id}`

Purpose:

- Load one raw idea.

Page dependency:

- Raw idea detail and source links.

Validation:

- Safe project ID and idea ID.
- JSON object record.

No-prose boundary:

- Read-only display of owner input.

Candidate/canon boundary:

- Raw idea is not canon.

Expected errors:

- Not found.
- Invalid ID.
- Corrupt record.

Status:

- Currently implemented.

### `POST /api/projects/{project_id}/omi/candidates`

Purpose:

- Create a structured candidate, usually linked to an idea in the current runtime.

Page dependency:

- Manual candidate creation and future candidate import.

Validation:

- Safe IDs.
- Allowed candidate type.
- Structured JSON object content.
- Allowed destination.
- Evidence array where supplied.
- Provenance object where supplied.

No-prose boundary:

- Candidate content must be structured planning material, not generated story prose.
- No model call in first page implementation.

Candidate/canon boundary:

- Creates candidate only, not memory/canon.

Expected errors:

- Missing source idea when required by current runtime.
- Unsupported type.
- Unsafe destination.
- Invalid content.

Status:

- Currently implemented for bounded generic candidate types. Future typed candidates are not fully implemented.

### `GET /api/projects/{project_id}/omi/candidates/{candidate_id}`

Purpose:

- Load one candidate.

Page dependency:

- Candidate detail panel.

Validation:

- Safe project ID and candidate ID.
- JSON object record.

No-prose boundary:

- Read-only display of stored structured candidate data.

Candidate/canon boundary:

- Candidate is not canon.

Expected errors:

- Not found.
- Invalid ID.
- Corrupt record.

Status:

- Currently implemented.

### Future `PATCH /api/projects/{project_id}/omi/candidates/{candidate_id}`

Purpose:

- Update candidate status, owner decision, destination, structured fields, evidence/provenance, or archive state.

Page dependency:

- Owner Decision Panel, Destination / Target Panel, Evidence / Provenance Panel.

Validation:

- Safe IDs.
- Allowed status transition.
- Allowed owner decision.
- Allowed destination.
- Structured content shape.
- Evidence/provenance shape.

No-prose boundary:

- Metadata/review updates only.
- No generated prose insertion.

Candidate/canon boundary:

- Updates candidate metadata only.
- No memory/canon mutation.

Expected errors:

- Invalid transition.
- Unsupported destination.
- Unsafe target.
- Corrupt record.

Status:

- Future first-page requirement. Current runtime has narrower decision/destination update routes.

### Future `GET /api/projects/{project_id}/omi/promotions`

Purpose:

- List promotion audit records.

Page dependency:

- Promotion Records Snapshot.

Validation:

- Safe project ID.
- JSON object/array shape.

No-prose boundary:

- Read-only audit display.

Candidate/canon boundary:

- Promotion records are not canon.

Expected errors:

- Missing promotions folder.
- Corrupt promotion records.

Status:

- Currently implemented as a bounded list route; future first-page work should add health/warning detail.

### Future `POST /api/projects/{project_id}/omi/promotions`

Purpose:

- Create a record-only promotion audit record after readiness passes and final owner confirmation is present.

Page dependency:

- Promotion Readiness Panel.

Validation:

- Safe project ID.
- Existing approved candidate.
- Owner approval confirmation.
- Safe destination and target.
- Structured candidate content.
- Evidence/provenance where required.
- Final confirmation.
- Source candidate snapshot.

No-prose boundary:

- Record-only metadata operation.
- No generated prose.

Candidate/canon boundary:

- Creates `Promotion Record Only`.
- Does not apply memory/canon.

Expected errors:

- Readiness blockers.
- Unsafe target.
- Missing confirmation.
- Corrupt candidate.

Status:

- Currently implemented as record-only creation. Future first-page work should preserve the record-only boundary.

### Future `GET /api/projects/{project_id}/omi/health`

Purpose:

- Return non-destructive OMI health warnings.

Page dependency:

- Warning / Error Area.

Validation:

- Safe project ID.
- OMI folder/index/record scans.

No-prose boundary:

- Static diagnostics only.

Candidate/canon boundary:

- Health checks do not promote, repair, or relabel truth.

Expected errors:

- Invalid project ID.
- Partial scan failure.

Status:

- Future first-page requirement.

### Future-Only `POST /api/projects/{project_id}/memory/apply-promotion`

Purpose:

- Apply a promotion record into durable memory/canon in a later explicit task.

Page dependency:

- Not a first implementation dependency.

Validation:

- Future apply-promotion design must define atomic writes, target mapping, evidence/provenance, revision history, rollback/fail-closed behavior, and owner confirmation.

No-prose boundary:

- Must not write generated story prose.

Candidate/canon boundary:

- This is the only future route group that may create applied memory/canon from a promotion record.

Expected errors:

- Deferred.

Status:

- Future-only. Do not implement for the OMI Ideas / Candidates first page.

## 10. Frontend Planning

Do not implement UI in this task. Future components:

- `OmiIdeasCandidatesPage`
- `OmiBoundaryBanner`
- `RawIdeasList`
- `RawIdeaDetail`
- `CandidateList`
- `CandidateDetailPanel`
- `CandidateReviewPanel`
- `CandidateDestinationPanel`
- `EvidenceProvenancePanel`
- `PromotionReadinessPanel`
- `PromotionRecordsSnapshot`
- `CandidateCanonExplanation`
- `OmiFiltersSearch`
- `OmiHealthWarning`
- `FutureExtractionPlaceholder`

Frontend rules:

- No AI writing buttons.
- No rewrite, continue, polish, improve, generate, expand, imitate, or insert controls.
- Analysis/candidate panels remain separate from editor body content.
- UI labels should distinguish owner-authored source, OMI candidates, promotion records, and approved canon.
- First implementation search/filter is local and deterministic.
- First implementation should not call Ollama, qwen3, or any model.
- First implementation should not run extraction on page load, list, filter, search, or review.

## 11. Relationship to Other Workspace Pages

Project Overview:

- May show OMI idea/candidate/promotion counts.
- May link to the OMI Ideas / Candidates page.
- Must label OMI counts as candidate/audit status, not approved canon.

Chapters / Scenes:

- May later send selected scene or scene metadata to candidate extraction.
- Extraction output must land here or in OMI candidate review, not directly in scene text or memory/canon.
- First implementation should not extract during page load, save, search, or navigation.

Notes / Materials:

- May later send selected source material to candidate extraction.
- Extraction output must land here or in OMI candidate review, not directly in notes/materials or memory/canon.
- First implementation should not extract during page load, save, search, or navigation.

Project Memory / Canon:

- Shows only applied approved memory/canon records.
- May link back here for pending, rejected, approved-but-not-applied, or promotion-record-only OMI records.
- Must not display OMI candidates as approved canon.

Project Context / Bible / Storyform:

- Must not be mutated by OMI without future explicit destination design.
- First implementation of this page must not write `bible.json`, `storyform.json`, `owner_memory.json`, project metadata, scene files, note files, material files, or `memory/*.json`.

## 12. Future Tests

Future implementation tests should cover:

- Page loads empty OMI state.
- Page loads raw ideas.
- Page loads candidates.
- Page loads promotion records as audit-only.
- Raw idea save is not overblocked by no-prose guard.
- Candidate review actions update status/decision only.
- Destination selection remains candidate metadata.
- Promotion readiness blockers display.
- Promotion record creation does not mutate memory/canon.
- Opening page does not create OMI records.
- Opening page does not create memory/canon files.
- No bible/storyform/scene/note/material mutation.
- No model/Ollama call during page load, list, filter, search, or review.
- No generated summaries.
- No AI prose-generation controls.
- Corrupt OMI records show warnings.
- Path traversal is rejected.
- Unsafe destination is rejected.
- No JSONL/training writes.
- `dataset_manifest.json` remains unchanged.

## 13. Deferred Decisions

Deferred to later tasks:

- Exact first implementation status vocabulary if legacy runtime record-only promotion wording needs migration.
- Whether runtime adopts `promotion_recorded` before apply-promotion exists.
- Raw idea archive UI timing.
- Raw idea deletion policy.
- Structured candidate field editing scope.
- Evidence requirements by candidate type and destination.
- Typed candidate validation timing.
- Merge/deduplication UI.
- Health route shape.
- Extraction trigger strategy.
- Apply-promotion route and memory/canon mutation design.
- Semantic search.
- Browser design for large OMI queues.
- Dramatica-specific candidate classes or analysis surfaces.

## 14. Acceptance Checklist

This planning spec is complete when it documents:

- Page purpose.
- OMI concepts and labels.
- First-version page layout.
- Raw idea behavior.
- Candidate behavior.
- Promotion readiness and promotion records.
- Filters/search.
- Warning/error states.
- API planning.
- Frontend planning.
- Relationship to other workspace pages.
- Future tests.
- Deferred decisions.

This spec does not implement runtime code, frontend UI, tests, packages, dataset files, JSONL records, training, model calls, project files, OMI records, memory/canon files, extraction, apply-promotion, or Dramatica-specific logic.
