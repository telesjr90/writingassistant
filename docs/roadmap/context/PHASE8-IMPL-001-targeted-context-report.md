# PHASE8-IMPL-001 Targeted Context Report

## 1. Task Identity

- Parent: `PHASE8-IMPL-001`
- Child: `PHASE8-IMPL-001-T003`
- Purpose: targeted context collection and source inventory
- Method: direct file/source inspection
- Context tools used: none
- Execution date: 2026-06-16
- Status: complete

## 2. Files Inspected

### Roadmap/status files

- `docs/roadmap/context/PHASE8-IMPL-001-context-collection-plan.md`
- `docs/roadmap/tasks/PHASE8-IMPL-001.md`
- `docs/roadmap/inventory/PHASE8-IMPL-001.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-001.enrichment.json`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/roadmap_index.yaml`
- `docs/roadmap/validation/latest_roadmap_validation.md`

### Core specs

- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`

### Approved-memory/category specs

- `docs/roadmap/approved_characters_page_spec.md`
- `docs/roadmap/approved_locations_settings_page_spec.md`
- `docs/roadmap/approved_timeline_page_spec.md`
- `docs/roadmap/approved_plot_threads_page_spec.md`
- `docs/roadmap/continuity_consistency_page_spec.md`
- `docs/roadmap/approved_open_questions_page_spec.md`
- `docs/roadmap/approved_relationships_page_spec.md`
- `docs/roadmap/approved_organizations_groups_page_spec.md`
- `docs/roadmap/approved_objects_items_page_spec.md`
- `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
- `docs/roadmap/approved_contradictions_page_spec.md`
- `docs/roadmap/approved_scene_event_causality_review_spec.md`

### Backend runtime files

- `backend/main.py`
- `backend/project_manager.py`
- `backend/guardrails.py`
- `backend/analysis_engine.py`
- `backend/analysis_normalizer.py`

### Frontend runtime files

- `frontend/src/App.jsx`
- `frontend/src/api.js`
- `frontend/src/components/OMIPanel.jsx`
- `frontend/src/components/MemoryCanonShell.jsx`
- `frontend/src/components/ProjectOverview.jsx`
- `frontend/src/components/ProjectNav.jsx`
- `frontend/src/components/Editor.jsx`
- `frontend/src/sharedDocumentController.js`

### Test files

- `tests/test_omi_boundaries.py`
- `tests/test_omi_routes.py`
- `tests/test_project_manager.py`
- `tests/test_frontend_project_workspace_source.py`
- `tests/test_note_material_routes.py`
- `tests/test_scene_routes.py`
- `tests/test_guardrails.py`
- `tests/test_story_check_route.py`

## 3. Context Questions Answered

### A. Current OMI runtime surface

- Finding: Runtime OMI currently supports generic ideas, candidates, decision updates, promotion audit records, and summary/list reads.
- Evidence file(s): `backend/main.py`, `backend/project_manager.py`, `frontend/src/api.js`, `frontend/src/components/OMIPanel.jsx`, `tests/test_omi_boundaries.py`, `tests/test_omi_routes.py`, `tests/test_project_manager.py`.
- Implementation implication: Writer Assistant Core can build on OMI as the review/audit layer, but current runtime candidate types are MVP planning types, not the expanded story-knowledge candidate set.
- Risk or open question: The expanded CORE candidate types need a tested contract before runtime storage/routes/UI accept them.

### B. Current project storage surface

- Finding: Project storage has safe project IDs, safe document IDs, body files for scenes/notes/materials, separate metadata files, lazy OMI storage, and no runtime `memory/` implementation.
- Evidence file(s): `backend/project_manager.py`, `tests/test_project_manager.py`, `tests/test_note_material_routes.py`, `tests/test_scene_routes.py`.
- Implementation implication: Future candidate storage should reuse safe path and atomic JSON-write patterns, but must stay under OMI/candidate-only paths until a later approved memory/canon task.
- Risk or open question: Reusing generic JSON write helpers without a strict destination contract could accidentally introduce memory/canon mutation.

### C. Current frontend surfaces

- Finding: The frontend has distinct workspace views for Overview, editor, and Memory / Canon; OMI is a candidate/audit panel, and the editor handles exact owner-authored body content.
- Evidence file(s): `frontend/src/App.jsx`, `frontend/src/api.js`, `frontend/src/components/ProjectNav.jsx`, `frontend/src/components/OMIPanel.jsx`, `frontend/src/components/MemoryCanonShell.jsx`, `frontend/src/components/ProjectOverview.jsx`, `frontend/src/components/Editor.jsx`, `frontend/src/sharedDocumentController.js`.
- Implementation implication: Future candidate review/backlog UI should live with OMI or a candidate-only workspace surface, not inside Memory / Canon approved lists or editor body content.
- Risk or open question: The current OMI panel is generic and MVP-era; adding story-knowledge review UI before backend contracts are locked would risk UI drift.

### D. Candidate schema/spec alignment

- Finding: Specs define 12 story-knowledge candidate classes with base fields for identity, status, source locator, evidence, provenance, owner decision, promotion status, destination, confidence, and typed content.
- Evidence file(s): `docs/roadmap/writer_assistant_core_candidate_schemas.md`, `docs/roadmap/omi_story_knowledge_candidate_expansion.md`, `docs/roadmap/omi_mvp_schema_lifecycle.md`, `frontend/src/components/MemoryCanonShell.jsx`, `backend/project_manager.py`.
- Implementation implication: The first implementation slice should lock a schema/type contract before accepting runtime CORE candidate records.
- Risk or open question: Runtime `OMI_CANDIDATE_TYPES` currently excludes the CORE story-knowledge types.

### E. Evidence/provenance model

- Finding: Specs require evidence arrays and provenance objects for candidate trust and future promotion; existing OMI records store provenance and evidence, but evidence item shape is not deeply validated.
- Evidence file(s): `docs/roadmap/writer_assistant_core_candidate_schemas.md`, `docs/roadmap/omi_storage_model.md`, `docs/roadmap/project_memory_canon_storage_model.md`, `backend/project_manager.py`, `frontend/src/components/OMIPanel.jsx`.
- Implementation implication: A minimal first slice can validate source locator/evidence/provenance shapes without extraction or model work.
- Risk or open question: Exact source locator shape across scenes, notes, materials, candidates, and future memory records remains a T004/T005 contract decision.

### F. Guardrails/no-prose boundary

- Finding: Backend guardrails distinguish freeform assistant requests from owner-authored content fields; Story Check model output is normalized and sanitized. Existing owner-authored scene/note/material save paths are not scanned as assistant requests.
- Evidence file(s): `backend/guardrails.py`, `backend/analysis_engine.py`, `backend/analysis_normalizer.py`, `tests/test_guardrails.py`, `tests/test_story_check_route.py`, `tests/test_scene_routes.py`, `tests/test_omi_routes.py`.
- Implementation implication: Future model-backed or extraction routes must guard request fields before model calls and sanitize output after model calls. Pure owner-authored body storage must not be guarded as request intent.
- Risk or open question: Future candidate creation routes that accept both owner-authored source text and assistant instructions must split fields clearly.

### G. Existing tests

- Finding: Existing tests cover OMI no-prose/no-silent-promotion, OMI route contracts, path safety, frontend workspace boundaries, note/material/scene body-vs-metadata behavior, guardrails, and Story Check route guard integration.
- Evidence file(s): `tests/test_omi_boundaries.py`, `tests/test_omi_routes.py`, `tests/test_project_manager.py`, `tests/test_frontend_project_workspace_source.py`, `tests/test_note_material_routes.py`, `tests/test_scene_routes.py`, `tests/test_guardrails.py`, `tests/test_story_check_route.py`.
- Implementation implication: T005 should extend source-level and backend contract tests before production runtime behavior.
- Risk or open question: No dedicated Writer Assistant Core schema constants or validation tests exist yet.

### H. First runtime slice candidates

- Finding: The smallest safe options are schema/source-level tests and backend candidate schema constants; storage helpers and route/UI work have higher mutation or contract-drift risk.
- Evidence file(s): T002 plan, `backend/project_manager.py`, `frontend/src/components/OMIPanel.jsx`, `docs/roadmap/writer_assistant_core_candidate_schemas.md`, `tests/test_omi_boundaries.py`, `tests/test_frontend_project_workspace_source.py`.
- Implementation implication: T004 should decide between a schema-constants-first slice and a candidate-storage-contract-tests-first slice.
- Risk or open question: If T004 chooses storage before schema constants, the storage contract could encode the wrong shape.

## 4. OMI Runtime Inventory

### Current OMI routes in `backend/main.py`

- `GET /api/projects/{project_name}/omi` returns `project_manager.get_omi_summary(project_name)`.
- `POST /api/projects/{project_name}/omi/ideas` creates an owner-authored raw idea.
- `GET /api/projects/{project_name}/omi/ideas/{idea_id}` loads one idea.
- `POST /api/projects/{project_name}/omi/candidates` creates one structured candidate linked to an existing idea.
- `GET /api/projects/{project_name}/omi/candidates/{candidate_id}` loads one candidate.
- `PATCH` or fallback `POST /api/projects/{project_name}/omi/ideas/{idea_id}/decision` updates idea owner decision/status.
- `PATCH` or fallback `POST /api/projects/{project_name}/omi/candidates/{candidate_id}/decision` updates candidate owner decision/status/destination.
- `GET /api/projects/{project_name}/omi/promotions` lists promotion audit records.
- `GET /api/projects/{project_name}/omi/promotions/{promotion_id}` loads one promotion audit record.
- `POST /api/projects/{project_name}/omi/promotions` creates a promotion audit record.

### Current OMI helper/storage behavior in `backend/project_manager.py`

- OMI folders are lazy-created by `ensure_omi_storage(project_name)`.
- `_omi_dir`, `_omi_index_path`, and `_omi_record_path` keep OMI under `projects/{project_id}/omi/`.
- OMI JSON writes use `_write_json_object` with temp-file replacement and explicit overwrite behavior.
- `load_omi_index` returns a default index when `omi/index.json` is missing.
- `save_omi_index` normalizes index IDs and updates `last_updated`.
- `create_omi_idea` writes `omi/ideas/{idea_id}.json`, then updates `omi/index.json`.
- `create_omi_candidate` requires an existing idea, writes `omi/candidates/{candidate_id}.json`, links the candidate back to the idea, then updates `omi/index.json`.
- `create_omi_promotion_record` writes `omi/promotions/{promotion_id}.json` and updates `omi/index.json`.

### Ideas/candidates/promotions/index storage shape

- `omi/index.json`: `project_id`, `idea_ids`, `candidate_ids`, `promotion_ids`, `last_updated`.
- Idea records: `idea_id`, `project_id`, `raw_idea`, `status`, timestamps, `provenance`, `owner_decision`, `linked_candidate_ids`.
- Candidate records: `candidate_id`, `project_id`, `idea_id`, `candidate_type`, `candidate_content`, `status`, `destination`, `provenance`, `evidence`, `owner_decision`, `promotion_status`, timestamps.
- Promotion records: `promotion_id`, `project_id`, `candidate_id`, `destination`, `owner_approval`, `provenance`, `evidence`, `source_snapshot`, target file/path, timestamps, and `status`.

### Owner decision fields

- Runtime owner decision fields are `decision`, `approved`, `approval_confirmed`, `decided_by`, `decided_at`, and `notes`.
- Runtime decisions are `pending`, `approve`, `reject`, and `needs_revision`.
- Approve requires `approval_confirmed: true`.

### Destination fields

- Current runtime OMI destinations are `planning_notes`, `project_bible_candidate`, `storyform_context_candidate`, `scene_prompt_context_candidate`, `template_starter_candidate`, and `discard`.
- Blocked destinations include `scene_prose`, `chapter`, `dialogue`, `rewrite`, `continuation`, and `final_story_text`.
- Promotion targets are currently `bible.json`, `owner_memory.json`, `planning_notes`, and `storyform.json`; promotion target validation blocks scene/story/prose-like targets and path traversal.

### Provenance fields

- Runtime default provenance includes `source_type`, `source_path`, `source_label`, `created_by`, `tool`, `model`, `prompt_id`, `timestamp`, `source_hash`, `snapshot_hash`, `confidence`, and `notes`.
- Candidate provenance defaults to `source_path: omi/ideas/{idea_id}.json`.
- Promotion request provenance defaults to `source_path: omi/candidates/{candidate_id}.json`.

### Promotion record behavior

- Promotion record creation requires the candidate to be approved, confirmed, destination allow-listed, provenance present, and candidate content a JSON object.
- Promotion creation requires `final_confirmation: true` and a safe target file/path.
- Created promotion records snapshot the source candidate and use status `ready_for_manual_application`.
- Promotion records do not write to `bible.json`, `storyform.json`, `owner_memory.json`, scenes, project metadata, or future `memory/*.json`.

### Explicit absence of apply-promotion

- No backend apply-promotion route exists in `backend/main.py`.
- `project_manager.py` creates promotion audit records but has no helper that converts them to memory/canon or project truth.
- `MemoryCanonShell.jsx` explicitly says there is no apply-promotion in this phase and no memory/canon mutation.
- Tests assert promotion record creation is record-only and no apply route/truth mutation exists.

### Tests that protect no-silent-promotion

- `tests/test_omi_boundaries.py` covers no prose candidate destinations/types, candidate-only raw ideas, no silent project truth mutation, record-only promotion creation, promotion blockers, no model path, frontend boundary copy, and path traversal rejection.
- `tests/test_omi_routes.py` covers OMI route contracts, invalid type/destination rejection, owner-authored raw idea handling, decision routes, promotion route blockers, and no apply-truth mutation.
- `tests/test_project_manager.py` covers OMI create/update/promotion helpers and no project truth file mutation.

## 5. Project Storage Inventory

- Project metadata storage: `projects/{project_id}/project.json`; project creation creates core workspace folders only and intentionally does not create memory, OMI, bible, or storyform files.
- Scene body storage: `projects/{project_id}/scenes/{scene_id}.md`.
- Scene/chapter metadata storage: `scene_metadata/{scene_id}.json` and `chapters/{chapter_id}.json`; scene bodies remain separate.
- Note body and metadata storage: `notes/{note_id}.md` and `note_metadata/{note_id}.json`.
- Material body and metadata storage: `materials/{material_id}.md` and `material_metadata/{material_id}.json`.
- Bible/storyform storage: `bible.json` and `storyform.json`; storyform saves validate schema.
- OMI storage: `omi/ideas/{idea_id}.json`, `omi/candidates/{candidate_id}.json`, `omi/promotions/{promotion_id}.json`, and `omi/index.json`.
- Safe ID/path helpers: `validate_project_id`, `derive_project_id`, `_safe_path_component`, `_safe_document_id`, `_relative_reference_path_or_none`, `_omi_record_path`, and metadata normalizers.
- Reusable helpers for future candidate storage: safe component validation, OMI folder pathing, `_write_json_object`, OMI index normalization, provenance normalization, and evidence-array validation patterns.
- Helpers that must not be reused for canon/memory mutation: OMI promotion record helpers, bible/storyform save helpers, and future `memory/` helpers should not be used by candidate creation unless a later apply-promotion task explicitly authorizes durable truth mutation.

## 6. Frontend Workspace Inventory

- `App.jsx` owns selected project state, loads project-scoped scenes/notes/materials/bible/storyform/OMI data, and separates workspace views into `overview`, `memory-canon`, and `editor`.
- `ProjectNav.jsx` provides project library selection, blank project creation, Overview navigation, Memory / Canon navigation, and scene/note/material document selection by ID.
- `OMIPanel.jsx` shows raw ideas, candidates, candidate content JSON, owner decision controls, destination controls, provenance/evidence display, promotion readiness, and promotion audit records. It states that OMI stores candidate planning material only and that promotion records do not change project truth.
- `MemoryCanonShell.jsx` is prop-driven and read-only. It lists approved-only category cards for characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items. It does not consume OMI candidates or promotion records as approved canon.
- `ProjectOverview.jsx` displays deterministic counts and status for scenes, notes, materials, OMI, and approved memory; it does not read bodies or generate summaries.
- `Editor.jsx` and `sharedDocumentController.js` handle owner-authored scene/note/material body content only, with save/dirty/loading/error state separate from metadata and candidates.
- Likely safe future placement for candidate review/backlog UI: OMI or a new candidate-only workspace surface linked from Overview/Memory / Canon, not the approved Memory / Canon records list and not the editor body.
- UI surfaces that must remain read-only or candidate-only: Memory / Canon approved-only shell, candidate/audit areas in OMI, Overview status/count sections, and editor body saves.

## 7. Candidate Schema Alignment Findings

- Candidate types already specified:
  - `character_candidate`
  - `location_candidate`
  - `object_candidate`
  - `organization_candidate`
  - `timeline_event_candidate`
  - `relationship_candidate`
  - `plot_thread_candidate`
  - `navigation_summary_candidate`
  - `continuity_warning_candidate`
  - `contradiction_candidate`
  - `annotation_candidate`
  - `open_question_candidate`
- Overlap with Memory / Canon shell categories:
  - Characters -> `character_candidate`
  - Locations / Settings -> `location_candidate`
  - Timeline -> `timeline_event_candidate`
  - Plot Threads -> `plot_thread_candidate`
  - Continuity / Consistency -> `continuity_warning_candidate`
  - Open Questions -> `open_question_candidate`
  - Relationships -> `relationship_candidate`
  - Organizations / Groups -> `organization_candidate`
  - Objects / Items -> `object_candidate`
  - Annotations / Evidence / Provenance -> `annotation_candidate` plus evidence/provenance records
  - Contradictions -> `contradiction_candidate`
  - Scene / Event / Causality -> partially overlaps `timeline_event_candidate`; exact scene/event/action/causality candidate split is still deferred.
- Fields required for source locator: `source_scene_id`, `source_reference`, source path/type, line/offset/paragraph locators where available, and target/source IDs for linked records.
- Fields required for evidence span: `evidence_id`, `source_type`, `source_path`, `source_scene_id`, optional offsets/line locators, `quote_exact`, `summary`, `supports_claim`, `confidence`, and notes.
- Fields required for provenance: created-by/source/tool/model/extractor/prompt/timestamp/hash/review/license fields.
- Fields required for owner decision: decision, decided-by/date, notes, revision request, and approval confirmation.
- Fields required for status: candidate lifecycle status; current runtime excludes `promoted` and CORE-005 recommends reserving `promoted` for future apply-promotion success.
- Fields required for destination: proposed destination such as category memory candidate, project memory candidate, OMI candidate only, or discard.
- Fields required for confidence/uncertainty: candidate confidence, evidence confidence, uncertainty notes, and confidence at promotion time for future memory.
- Fields required for target category: candidate type and proposed destination map to future memory category targets.
- Schema gaps or conflicts:
  - Runtime candidate type allowlist is still MVP-only.
  - Runtime destination allowlist is still MVP-only and does not include category memory candidate destinations.
  - Runtime evidence validation only checks that evidence is a list.
  - Runtime does not support `idea_id: null` for scene-derived future candidates.
  - Scene/event/action/causality target category needs T004/T005 narrowing.
- Minimum viable candidate shape for first runtime slice:
  - `candidate_id`
  - `project_id`
  - `candidate_type`
  - `status`
  - `source_reference` or `source_scene_id`
  - `evidence`
  - `provenance`
  - `confidence`
  - `owner_decision`
  - `promotion_status`
  - `proposed_destination`
  - `candidate_content`
  - `notes`

## 8. Evidence/Provenance Findings

- OMI specs require provenance on ideas, candidates, and promotion records; promotion records snapshot source candidates and remain audit-only.
- Memory/canon specs require approved records to reference source candidate IDs, promotion record IDs, evidence IDs/summaries, provenance, approval metadata, and confidence at promotion time.
- Source locator forms already documented include scene IDs, source paths, source references, line/offset/paragraph locators, note/material paths, bible/storyform references, candidate IDs, promotion IDs, and future approved memory record IDs.
- Promotion prerequisites include owner approval, final confirmation, allowed destination/target, provenance, evidence where available, source snapshot, and safe target labels.
- First-slice implications:
  - A first slice can validate candidate type constants and evidence/provenance shape without implementing extraction.
  - A first slice can add source-level tests proving no model calls, no memory writes, and no apply-promotion.
  - A first slice should avoid creating `memory/` files or routes.
- What can be validated before extraction/model work exists:
  - Candidate type and destination allowlists.
  - Evidence/provenance JSON shape.
  - Source locator path safety.
  - Owner decision and promotion status defaults.
  - No-prose/no-silent-promotion forbidden behavior in route/source tests.

## 9. Guardrails/No-Prose Findings

- Backend guardrail functions:
  - `classify_request`
  - `is_prose_generation_request`
  - `should_guard_request_field`
  - `guard_freeform_request`
  - `refusal_response`
  - `output_text_appears_unsafe`
  - `sanitize_story_check_output`
- Current route policy:
  - Owner-authored fields such as `content`, `raw_idea`, `scene`, `note`, `planning_note`, `bible`, and `storyform` are treated as owner-authored content fields and should not be blocked as assistant request intent.
  - Story Check is the model-backed route and uses model-output normalization plus guardrail sanitization.
  - OMI create/update routes currently do not call model paths.
- Story Check output guard behavior:
  - `analysis_engine.py` parses or loads Story Check output through `analysis_normalizer.normalize_story_check_output` and `guardrails.sanitize_story_check_output`.
  - `analysis_normalizer.py` bounds warnings/suggestions/evidence counts and provides fallback diagnostics for malformed model output.
- Frontend safety copy/surfaces:
  - OMIPanel states OMI does not write story prose or change project truth.
  - MemoryCanonShell states candidate records remain in review and promotion/audit records are not canon.
  - Editor labels are document-type aware but remain owner-authored body surfaces.
- Future route types requiring `guard_freeform_request`:
  - Any route that accepts freeform assistant instructions, extraction prompts, model requests, or analysis requests before a model/tool call.
  - Candidate extraction orchestration if it ever accepts user instructions beyond stored source selectors.
- Forbidden behaviors first-slice tests must lock:
  - Generated prose, rewrite/continuation/style imitation/prose improvement.
  - Silent promotion or approved-memory mutation.
  - Summary-as-truth.
  - Model/Ollama calls.
  - Story Check auto-runs.
  - Backend extraction routes and frontend extraction UI.
- Owner-authored scene/note/material text must not be treated as an assistant request because body saves store owner content, not instructions to the assistant.

## 10. Test Coverage Findings

- OMI lifecycle/no-silent-promotion tests: `tests/test_omi_boundaries.py` covers no-prose candidate types/destinations, candidate-only raw ideas/content, no silent truth mutation, record-only promotion creation, blockers, no model path calls, frontend boundary copy, and path traversal.
- OMI route tests: `tests/test_omi_routes.py` covers create/list/get ideas and candidates, invalid type/destination rejection, decision updates, promotion create/list/get, promotion blockers, no Ollama, and no apply truth mutation.
- Project manager path safety/storage tests: `tests/test_project_manager.py` covers project, scene, note, material, metadata, OMI storage/index, decision, promotion, and no truth-file mutation behavior.
- Frontend workspace source tests: `tests/test_frontend_project_workspace_source.py` covers project selection, Overview, OMI/staged setup, Memory / Canon shell, editor body-only behavior, unsafe term exclusions, and no backend/API dependency drift for approved memory.
- Note/material route tests: `tests/test_note_material_routes.py` covers body/metadata separation, safe IDs, metadata-only source/provenance fields, no metadata creation on body save/list, and missing body errors.
- Scene route tests: `tests/test_scene_routes.py` covers legacy/metadata scenes, body-only save, no owner-text guard, missing scene safety, and deferred staged setup route scope.
- Guardrail tests: `tests/test_guardrails.py` covers prose-generation request refusal, allowed analysis requests, refusal shape, and scene-like content not treated as command.
- Story Check route tests: `tests/test_story_check_route.py` covers minimal/rich/fallback/error-shaped reports, mock mode without Ollama, and scene text not guarded as request intent.
- Likely first test files to extend:
  - `tests/test_project_manager.py` for candidate schema constants/evidence-provenance validation if backend constants are chosen.
  - `tests/test_omi_boundaries.py` for no-prose/no-silent-promotion contract around expanded story-knowledge candidates.
  - `tests/test_frontend_project_workspace_source.py` only after a future UI decision.
- Gaps to cover before runtime implementation:
  - Dedicated CORE candidate type constants.
  - Evidence/provenance shape validation.
  - Source locator validation.
  - `idea_id: null` or source-derived candidate contract, if selected.
  - Explicit tests that expanded candidate types remain candidate-only and cannot mutate memory/canon.

## 11. First Runtime Slice Candidates

| Option | Description | Benefits | Risks | Required files | Likely tests | Boundary concerns | Recommendation score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Schema/source-level tests only | Add tests that lock expected Writer Assistant Core candidate types, fields, destinations, and no-prose/no-promotion boundaries without production changes. | Zero runtime mutation; forces contract clarity; lowest blast radius. | Does not give runtime code something to import yet. | Test files only in T005; no production files if pure tests. | `tests/test_project_manager.py`, `tests/test_omi_boundaries.py`. | Must not overfit to an implementation not yet chosen. | High |
| Backend candidate schema constants only | Add a small backend constants module or constants in an existing module for candidate types/fields/destinations. | Gives implementation a shared contract; can be paired with tests. | Constants without validation can drift; adding to `project_manager.py` may imply runtime acceptance too soon. | Likely backend schema/constant file and focused tests in a later child. | New or existing backend/source tests. | Must not enable routes/storage by merely defining constants. | High |
| Project-local candidate storage helper skeleton | Create helper contracts for project-local candidate storage under candidate-only paths. | Prepares OMI handoff and reuses path-safety patterns. | Higher mutation risk; could duplicate OMI storage; could imply durable truth. | `backend/project_manager.py` or future backend module, tests. | `tests/test_project_manager.py`, OMI boundary tests. | Must not create memory/canon files or apply records. | Medium |
| Route contract tests before route implementation | Specify route expectations before implementation. | Prevents accidental model/extraction/apply-promotion API shape. | May over-specify API before storage and schema decisions. | Route test file only at first. | `tests/test_omi_routes.py` or new route contract tests. | Must not add actual extraction routes in same slice. | Medium |
| Frontend read-only candidate backlog placeholder | Add a UI placeholder for candidate backlog/review. | Makes candidate/canon separation visible to owner. | UI would precede backend schema contract; current OMI panel is generic. | Frontend components and source tests. | `tests/test_frontend_project_workspace_source.py`. | Must not imply extraction or approved canon. | Low |
| Evidence/provenance validation helper | Add validation helpers for evidence/provenance/source locator shapes. | Locks promotion prerequisites early; useful without extraction/model calls. | Could duplicate current OMI validation or expand scope too much. | Backend validation helper and tests. | `tests/test_project_manager.py`, `tests/test_omi_boundaries.py`. | Must not create evidence records or memory/canon files. | Medium |

## 12. Recommended First Runtime Slice for T004 Decision

Recommendation input for T004: start with **Writer Assistant Core candidate schema constants plus source-level/contract tests**, with tests first or in the same tiny slice. This is better supported than storage-first because current runtime OMI storage is already generic but does not know the expanded CORE candidate types, while specs define a rich contract that is not yet executable.

Why it is smallest:

- It avoids storage mutation, route creation, UI work, extraction, and model calls.
- It can be limited to candidate type/destination/source/evidence/provenance constants and tests.
- It aligns runtime vocabulary with the already-approved specs before any candidate records are accepted.

Why it is safe:

- It can preserve current OMI behavior while adding no route and no project writes.
- It can explicitly assert no apply-promotion and no memory/canon mutation.
- It can keep source/evidence/provenance as validation contract only.

What it does not implement:

- No extraction runtime.
- No model/Ollama calls.
- No backend extraction routes.
- No frontend extraction UI.
- No OMI candidate promotion.
- No apply-promotion.
- No `memory/` files.
- No project runtime files.

What T004 must decide next:

- Whether the first slice is pure tests/source-level contract or includes a tiny backend constants module.
- Exact location of schema constants if production constants are included.
- Whether expanded CORE candidate types are added to runtime OMI allowlists immediately or kept separate as future schema constants.
- Minimum evidence/provenance/source locator validation depth for T005.

What T005 tests should lock before runtime implementation:

- Exact expanded candidate type list.
- Candidate-only destination categories.
- Required base candidate fields.
- Evidence/provenance/source locator required fields.
- No generated prose or summary-as-truth fields.
- No apply-promotion or memory/canon mutation.
- No model/Ollama call path.
- Owner-authored body fields not treated as assistant request intent.

## 13. Risks and Open Questions

- Schema drift risks: runtime OMI types/destinations are MVP-only while CORE specs define expanded story-knowledge types/destinations.
- Candidate/canon boundary risks: promotion targets include `bible.json`, `storyform.json`, and `owner_memory.json` as audit targets; tests must keep promotion records from mutating those files.
- Evidence/provenance ambiguity: current runtime evidence is list-only; exact evidence span/source locator validation is still open.
- Storage duplication risks: adding a parallel candidate store outside OMI could split the candidate lifecycle unless T004 explicitly chooses that boundary.
- Future UI placement ambiguity: OMI is the safest candidate surface, but a dedicated candidate backlog page may be needed later.
- Guardrail route-scope risks: future routes combining owner source text and assistant instructions must keep field policies explicit.
- Context-tool overbreadth risk: T003 was answerable by direct inspection, so no context tools were needed.
- Docs/source conflict discovered: docs define future typed story-knowledge candidates and memory category destinations, but runtime currently allows only MVP OMI candidate types/destinations.

## 14. Boundary Confirmation

- No context tools run.
- No runtime code changed.
- No tests changed.
- No generated prose/model/extraction behavior added.
- No apply-promotion.
- No memory/canon mutation.
- No training/JSONL/dataset work.
- No project runtime files changed.
