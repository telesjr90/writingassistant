# PHASE7-IMPL-006 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-006`
- Canonical title: Shared owner-authored document editor
- Type: runtime parent
- Status: `active_next` in `docs/roadmap/roadmap_index.yaml`
- Depends on: `PHASE7-IMPL-004`, `PHASE7-IMPL-005`
- Primary predecessor: `PHASE7-IMPL-005` - Notes / Materials Storage

Boundary tags:

- `owner_authored_prose_storage`
- `shared_editor`
- `no_generated_prose`
- `no_model_calls`
- `no_extraction`
- `no_memory_canon_mutation`
- `local_first`

## Current Implementation Surfaces

### `frontend/src/App.jsx`

- Owns separate state groups for scenes, notes, and materials.
- Scene state includes `selectedSceneId`, `sceneContent`, `lastSavedContent`, `isLoadingScene`, `isSaving`, `saveStatus`, and `sceneError`.
- Note state includes `selectedNoteId`, `noteContent`, `lastSavedNoteContent`, `isLoadingNote`, `isSavingNote`, `noteSaveStatus`, and `noteError`.
- Material state includes `selectedMaterialId`, `materialContent`, `lastSavedMaterialContent`, `isLoadingMaterial`, `isSavingMaterial`, `materialSaveStatus`, and `materialError`.
- `selectedDocumentType` tracks active document type across `scene`, `note`, and `material`.
- `hasUnsavedDocumentChanges` combines scene, note, and material dirty checks.
- Project switch and project creation paths confirm before discarding unsaved document changes.
- Scene, note, and material selection handlers load exact body content from the body routes and set a last-saved baseline.
- Scene, note, and material save handlers call body save helpers with selected IDs and current editor content.
- `beforeunload` guards unsaved scene/note/material content.
- Keyboard save behavior is not clearly shared across document types in the inspected source and should be treated as a PHASE7-IMPL-006 gap.
- Load/save logic is duplicated across document types and is the main shared-editor consolidation target.

### `frontend/src/components/Editor.jsx`

- Receives `content`, `disabled`, `hasUnsavedChanges`, `isLoading`, `isSaving`, `onChange`, `onSave`, `saveDisabled`, `saveStatus`, `documentError`, `selectedDocumentId`, and `documentType`.
- Uses `DOCUMENT_TYPE_LABELS` for scene, note, and material labels.
- Uses TipTap `useEditor` with `StarterKit`.
- Converts plain text/Markdown-ish body content into paragraphs for display and returns text via `getText({ blockSeparator: "\n\n" })`.
- Updates editor content when the `content` prop changes and toggles editability from `disabled`.
- Shows selected document ID as the editor title after replacing hyphen/underscore runs with spaces.
- Shows generic save status, unsaved state, loading state, save failure state, empty selected-document copy, and document error copy.
- Does not mention scene-specific selected IDs internally, but still combines editor UI, document-type labels, and save status in one component.

### `frontend/src/components/ProjectNav.jsx`

- Normalizes legacy scene strings and metadata-shaped scene records.
- Normalizes note records and material records, including title fallback to IDs.
- Renders separate sections for scenes, notes, and materials.
- Provides loading, error, and empty states for notes and materials.
- Applies active highlighting using `activeDocumentType` plus the selected document ID.
- Selection callbacks pass IDs (`sceneId`, `noteId`, `materialId`), not display labels.
- Scene ordering supports `order_index`, `orderIndex`, and `order`; note/material ordering currently preserves provided order after normalization.

### `frontend/src/api.js`

- Scene body helpers: `fetchScenes`, `fetchScene`, `saveScene`.
- Note body helpers: `fetchNotes`, `fetchNote`, `saveNote`.
- Note metadata helpers exist but are not imported by the minimal shell: `fetchNoteMetadata`, `saveNoteMetadata`.
- Material body helpers: `fetchMaterials`, `fetchMaterial`, `saveMaterial`.
- Material metadata helpers exist but are not imported by the minimal shell: `fetchMaterialMetadata`, `saveMaterialMetadata`.
- Helpers use the existing `client`, `requestData()`, and `PROJECT_ID` default pattern.

### `frontend/src/components/ProjectContext.jsx`

- Provides owner-editable Bible and storyform JSON panels.
- Not part of the scene/note/material shared body editor.
- Should remain separate unless a later task explicitly scopes project-context editor reuse.

### Backend Route and Helper Surfaces

- `backend/main.py` exposes scene body routes with legacy response shapes.
- `backend/main.py` exposes note/material list, body read/write, and metadata read/write routes.
- `backend/project_manager.py` provides safe project/document path helpers and body/metadata helpers for scenes, notes, and materials.
- PHASE7-IMPL-006 should not change backend route or storage behavior unless a later child task identifies a frontend contract bug requiring a narrow fix.

### Existing Source-Level Tests

- `tests/test_frontend_project_workspace_source.py` checks frontend source patterns for:
  - project-scoped API calls,
  - scene metadata display compatibility,
  - note/material API helpers,
  - notes/materials navigation sections,
  - ID-based note/material selection,
  - exact note/material body load/save calls,
  - Editor document-type support,
  - absence of metadata editing UI in `App.jsx`,
  - absence of model/prose/extraction terms.
- Current tests are source-level string/regex guards, not browser/runtime UI tests.
- Browser/manual validation remains deferred to the Phase 7 validation task unless roadmap authority changes.

## Existing Working Behavior From PHASE7-IMPL-005

- The current minimal shell lists notes and materials.
- Notes and materials are selected by ID.
- Note/material body reads load exact body content from the backend response.
- Note/material saves send exact owner-authored body content through body save helpers.
- Existing `Editor.jsx` is reused minimally with `documentType`.
- Metadata editing UI was not added.
- Extraction, summaries, model calls, OMI promotion, memory/canon mutation, training/JSONL/dataset work, and generated prose were not added.
- Scene behavior is preserved by existing source-level and route/helper tests.

## Shared Editor Gaps and Risks

- `App.jsx` duplicates selection, load, save, dirty-state, loading, error, and status handling across scenes, notes, and materials.
- Document-type-specific logic is partially centralized through `selectedDocumentType`, but not yet represented by a clear shared state contract.
- Dirty-state handling spans three document state groups and needs consistent save/reload/project-switch behavior.
- Project switch and create confirmations protect unsaved document changes, but shared editor tests should make the contract explicit.
- Keyboard save behavior is not clearly documented as shared across document types.
- Active navigation highlighting depends on both document type and ID; parity should be tested for all document types.
- Error/status naming still reflects the incremental T006 shell rather than a deliberate shared editor contract.
- Metadata/body separation is preserved now, but future shared editor work must not inject metadata into body content or add metadata editing UI accidentally.
- Selection must continue to use IDs, not titles.
- Existing source-level tests do not prove browser runtime behavior.
- Browser/manual validation belongs under `PHASE7-IMPL-010` unless roadmap authority says otherwise.

## Boundaries

PHASE7-IMPL-006 must not add:

- generated prose,
- rewriting, continuation, style imitation, polishing, or prose improvement,
- summaries or navigation prose,
- extraction or semantic search,
- model/Ollama calls,
- OMI/canon/memory mutation,
- metadata editing UI unless a later child task explicitly allows it,
- Dramatica-specific analysis,
- training, JSONL, dataset, model artifact, or runtime project fixture changes.

## Recommended Next Child

`PHASE7-IMPL-006-T002` - Shared document state contract and source-level tests.

Likely allowed files:

- `tests/test_frontend_project_workspace_source.py`
- Documentation/status files only if the validator requires a docs-only adjustment.

Likely scope:

- Define the expected frontend state/handler contract for active document type, active document ID, content, dirty state, loading state, save status, and error handling.
- Add or strengthen source-level tests for that contract.
- Avoid runtime refactor unless a tiny source-test-support adjustment is explicitly required by the T002 task.
