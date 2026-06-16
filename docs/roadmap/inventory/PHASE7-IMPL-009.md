# PHASE7-IMPL-009 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-009`
- Canonical title: `Memory / Canon shell (approved-only empty states)`
- Type: runtime parent
- Status: `active_next` in `docs/roadmap/roadmap_index.yaml`
- Depends on: `PHASE7-IMPL-008`

Registered roadmap boundary tags:

- `empty_states_only`
- `read_only`
- `no_auto_promotion`
- `no_model_calls`
- `no_generated_prose`
- `no_memory_canon_mutation`

Additional boundary concepts preserved in prose:

- memory/canon shell
- approved-only display
- candidate-only exclusions
- no apply-promotion
- no extraction
- no semantic search
- no Story Check auto-run
- local-first behavior

## Spec Inventory

The Memory / Canon specs define an approved-only project knowledge shell. The only records allowed in approved category lists are future applied records under `memory/*.json` or an equivalent approved memory store after a future owner-confirmed apply-promotion step. OMI candidates, approved-but-not-applied candidates, rejected candidates, archived candidates, raw ideas, owner source material, and promotion audit records are not canon.

| Category | Approved-only source of truth | Empty-state behavior | Candidate exclusions | First shell need |
| --- | --- | --- | --- | --- |
| Characters | future `memory/characters.json` `character_memory_record` entries | show no approved character records yet | OMI/raw/source mentions are not approved characters | category card/page shell and future data source |
| Locations / Settings | future `memory/locations.json` `location_memory_record` entries | show no approved location/setting records yet | location candidates and source mentions stay candidate/source-only | category card/page shell and future data source |
| Timeline | future `memory/timeline.json` `timeline_event_memory_record` entries | show no approved timeline events yet | event candidates, chronology guesses, and source dates are not canon | category card/page shell and future data source |
| Plot Threads | future `memory/plot_threads.json` `plot_thread_memory_record` entries | show no approved plot threads yet | thread candidates and note summaries are not approved threads | category card/page shell and future data source |
| Continuity / Consistency | future `memory/continuity_warnings.json` or equivalent approved records | show no approved continuity/consistency records yet | warnings/candidate issues stay in OMI or future review | category card/page shell and future data source |
| Open Questions | future `memory/open_questions.json` approved records | show no approved open questions yet | unresolved candidate questions and owner notes are not approved records | category card/page shell and future data source |
| Relationships | future `memory/relationships.json` `relationship_memory_record` entries | show no approved relationships yet | generic relationship candidates are not Dramatica Relationship Story proof | category card/page shell and future data source |
| Organizations / Groups | future `memory/organizations.json`, `memory/groups.json`, or equivalent approved records | show no approved organizations/groups yet | group candidates and source mentions are not structural truth | category card/page shell and future data source |
| Objects / Items | future `memory/objects.json`, `memory/items.json`, or equivalent approved records | show no approved objects/items yet | object candidates and source mentions are not approved memory | category card/page shell and future data source |

Common category rules:

- No extraction, generation, summary creation, relationship graph generation, contradiction detection, model/Ollama calls, Story Check auto-runs, or Dramatica-specific claims in this parent.
- No apply-promotion behavior in this parent.
- No memory/canon mutation in this parent.
- Candidate backlog information, if shown later, must be labeled as candidate-only and not displayed as approved records.

## Current Frontend Implementation Surfaces

### `frontend/src/App.jsx`

- Tracks active project, project list, scenes, notes, materials, OMI summary, selected document IDs, dirty state, and `activeWorkspaceView`.
- Current workspace views are `overview` and `editor`.
- Project switches reset selected scene/note/material state and return to Overview.
- Scene/note/material selection switches to editor view and uses existing unsaved-change guards.
- No Memory / Canon workspace view exists today.
- A Memory / Canon shell can be added as a new workspace view alongside Overview without entering the shared owner-authored editor save path.

### `frontend/src/components/ProjectNav.jsx`

- Renders project library controls, blank project creation, Overview button, and scene/note/material document navigation.
- Does not render a Memory / Canon nav item today.
- Safe future pattern: add a Memory / Canon workspace nav button parallel to Overview, driven by workspace view state, not document type/ID state.
- The nav must not present OMI candidates or promotion records as approved canon pages.

### `frontend/src/components/ProjectOverview.jsx`

- Shows deterministic project identity, scene/note/material counts, OMI status, and a simple Approved Memory / Canon empty-state line.
- It is not the Memory / Canon shell.
- Future Memory / Canon shell should stay separate from overview summaries and avoid generated project/canon summaries.

### `frontend/src/components/OMIPanel.jsx`

- Handles project-local raw ideas, candidates, owner decisions, promotion readiness, and promotion audit records.
- Labels candidate and promotion states.
- Promotion records are audit-only and not apply-promotion.
- OMI candidates and promotion records must not feed approved-memory shell data unless a future apply-promotion step creates applied memory records.

### `frontend/src/components/OmiGuidedProjectCreation.jsx`

- Keeps staged setup data frontend-transient.
- Shows setup/candidate labels and requires explicit final confirmation before project creation.
- Staged setup draft data is not approved canon and must not appear in Memory / Canon approved lists.

### `frontend/src/components/Editor.jsx` and `frontend/src/sharedDocumentController.js`

- Shared editor supports only scene, note, and material document types.
- It saves owner-authored body content for selected documents.
- Memory / Canon shell must not become a document type, editor surface, dirty document, or save path in this phase.

### `frontend/src/api.js`

- Provides project, scene, note, material, bible/storyform, Story Check, and OMI helpers.
- No approved-memory read helper exists.
- No API is required for the initial approved-only empty-state shell if it renders static category structure and safe empty states.

## Current Backend Implementation Surfaces

### `backend/project_manager.py`

- Provides project creation/listing, scene/chapter metadata compatibility, notes/materials helpers, bible/storyform helpers, and OMI ideas/candidates/promotion audit helpers.
- Blank project creation intentionally does not create memory/canon files.
- OMI promotion records are audit records only.
- No approved-memory/canon storage helpers exist.
- No apply-promotion helper exists.
- No memory/canon mutation helper exists.
- Initial Memory / Canon empty-state shell can launch without backend changes.

### `backend/main.py`

- Provides project list/create, scene, bible/storyform, Story Check, OMI, note, and material routes.
- Existing OMI promotion route creates promotion audit records only.
- No Memory / Canon read routes exist.
- No apply-promotion or memory/canon mutation routes exist.
- Initial shell can be frontend-only and read-only until a later contract proves a backend read helper is needed.

## Existing Test Surfaces

- `tests/test_frontend_project_workspace_source.py` covers frontend source contracts for project switching, overview/editor separation, shared editor behavior, ProjectNav parity, overview shell behavior, and staged creation safety.
- `tests/test_project_manager.py` covers project creation safety, project ID validation, collision handling, OMI lifecycle, and no hidden write patterns.
- `tests/test_scene_routes.py` covers scene route compatibility.
- `tests/test_note_material_routes.py` covers note/material route compatibility.
- Existing OMI tests cover no-prose and no-silent-promotion boundaries.

PHASE7-IMPL-009 gaps:

- No source-level approved-memory shell contract yet.
- No Memory / Canon component.
- No ProjectNav/App integration for a Memory / Canon workspace view.
- No regression coverage proving OMI candidates/promotion records are excluded from approved lists.
- No tests locking no apply-promotion, no memory/canon mutation, no generated summary/extraction/model path in the shell.

## Safe Implementation Opportunities

- Add a read-only Memory / Canon shell component.
- Add static or prop-driven category cards/tabs for characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items.
- Display safe approved-only empty states such as `No approved records yet`.
- Include boundary copy: OMI candidates remain candidates until a future approved apply step exists.
- Use existing project selection/workspace view state only.
- Avoid backend reads until approved-memory storage/read-only contract exists.
- Keep OMI candidate data out of approved pages.
- Add a ProjectNav workspace entry separate from scene/note/material document selection.
- Keep the shell read-only and separate from Project Overview, Editor, and OMIPanel mutation paths.

## Gaps and Risks

- OMI candidates could be accidentally treated as approved canon.
- Promotion audit records could be mistaken for applied memory.
- Apply-promotion could be added too early.
- Memory/canon mutation could be added too early.
- Generated summaries, extraction, semantic search, or model calls could drift into the shell.
- Memory / Canon shell could accidentally enter the editor save path.
- Backend routes could be added before a read-only storage contract exists.
- Category-specific components could become brittle before shared category data is locked.
- Project Overview could be overloaded with canon shell behavior.
- Browser/manual validation remains deferred.

## Deferred Work

- Apply-promotion.
- Owner approval mutation workflow for memory/canon records.
- Extraction/candidate creation from prose.
- Semantic search, graph queries, and canon query assistant.
- Generated summaries.
- Dramatica analysis.
- Browser/manual validation.
- Durable approved-memory storage mutation.
- Category-specific detail editing.
- Cross-category graph/relationship visualization.
- Import/upload/create UI for notes/materials.

## Recommended Next Child

`PHASE7-IMPL-009-T002` - Approved-memory shell data contract and source-level tests.

Likely scope:

- Lock the category list, approved-only empty states, candidate exclusion, no apply-promotion, no memory/canon mutation, no extraction/model/summaries, and workspace integration boundaries.
- Keep this test-only unless a tiny source comment fix is required.
