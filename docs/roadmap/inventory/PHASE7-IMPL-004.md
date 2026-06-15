# PHASE7-IMPL-004 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-004`
- Canonical title: Chapter / Scene Metadata Compatibility Layer
- Type: `runtime`
- Status: `active_next`
- Depends on: `PHASE7-IMPL-003`
- Context pack: `.codex-context/PHASE7-IMPL-004/`
- Boundary tags: `owner_authored_prose_storage`, `metadata_only`, `no_scene_rewrite`, `no_model_calls`, `no_generated_prose`, `no_memory_canon_mutation`, `local_first`

## Boundary Summary

`PHASE7-IMPL-004` is a metadata-only compatibility layer for chapters and scenes. The task must preserve legacy flat Markdown scene files at `scenes/{scene_id}.md` and add chapter/scene metadata without rewriting owner-authored scene bodies.

The roadmap control layer says chapter/scene storage should add `chapters/{chapter_id}.json` and `scene_metadata/{scene_id}.json`, treat legacy scenes without metadata as standalone compatible scenes, use `chapter.scene_ids` as first-version ordering, and keep `scene_metadata.chapter_id` as a consistency aid.

## Relevant Backend Files and Functions

Evidence sources: repaired CCE findings, clean CCE verification, and scoped Repomix output.

- `backend/project_manager.py`
  - `_scene_path(project_name: str, scene_id: str) -> Path`
  - `save_scene(project_name: str, scene_id: str, content: str) -> None`
  - `list_scenes(project_name: str) -> list[str]`
  - Current evidence shows flat Markdown scene assumptions around scene path resolution, save, and sorted scene ID listing.
- `backend/main.py`
  - `get_scenes(project_name: str) -> dict[str, list[str]]`
  - `get_scene(project_name: str, scene_id: str) -> dict[str, str]`
  - `story_check(project_name: str, scene_id: str) -> dict`
  - Current route evidence shows scene list/read handlers return legacy scene IDs/content and Story Check reads scene content by scene ID.
- `backend/__init__.py`
  - Package marker only; appears in CCE results but has no known PHASE7-IMPL-004 implementation relevance.

Backend implementation assumptions for child tasks:

- Metadata helpers should be added beside existing project storage helpers rather than replacing scene body storage.
- Legacy `list_scenes` behavior must keep returning Markdown-backed scene IDs until route contracts are deliberately expanded.
- Any metadata write/create helper must never mutate `scenes/{scene_id}.md` body content as a side effect.
- Story Check is not part of PHASE7-IMPL-004 implementation scope except that compatibility changes must not break its existing scene lookup behavior.

## Relevant Frontend API/UI Files and Assumptions

Evidence sources: repaired CCE findings and scoped Repomix file inventory.

- `frontend/src/api.js`
  - Scene list request: `GET /projects/${projectId}/scenes`
  - Scene read request: `GET /projects/${projectId}/scenes/${sceneId}`
  - Scene save request: `PUT /projects/${projectId}/scenes/${sceneId}` with `{ content }`
  - Current evidence shows API functions still assume project-scoped scene IDs and Markdown body save/load.
- `frontend/src/App.jsx`
  - Included in scoped Repomix as project workspace UI context; likely owns selected project/scene state after PHASE7-IMPL-003.
- `frontend/src/components/Editor.jsx`
  - Included in scoped Repomix as the owner-authored scene editor surface.
- `frontend/src/components/ProjectContext.jsx`
  - Included in scoped Repomix as project context UI, but not identified as directly handling scene metadata.
- `frontend/src/components/ProjectNav.jsx`
  - Included in Graphify output for project selection label formatting; Graphify did not provide reliable scene topology.

Frontend implementation assumptions for child tasks:

- Initial compatibility work should tolerate either legacy string scene IDs or expanded metadata responses only where explicitly implemented and tested.
- UI display of scene titles/order belongs in `PHASE7-IMPL-004-T005` after backend read compatibility exists.
- The editor body must remain owner-authored content and must not receive generated prose, summaries, or automatic rewrites.

## Relevant Tests

Evidence sources: repaired CCE findings and clean CCE verification.

- `tests/test_project_manager.py`
  - `test_list_scenes_returns_sorted_markdown_scene_ids`
  - `test_list_scenes_returns_empty_list_when_scenes_dir_is_missing`
  - Existing tests protect legacy flat Markdown scene listing behavior.
- `tests/test_scene_routes.py`
  - Included in scoped Repomix file inventory and likely relevant for route-level scene read/write compatibility.
- `tests/test_frontend_project_workspace_source.py`
  - Existing frontend source tests cover project workspace/project API assumptions and may be relevant when frontend scene metadata display is added.
- `tests/test_project_library.py`
  - Contains route coverage around project collection routing; evidence shows it may protect route shadowing but is not primary scene metadata coverage.
- `tests/test_story_check_route.py`
  - Relevant only as a regression guard for existing scene lookup used by Story Check; PHASE7-IMPL-004 must not broaden into model or Story Check behavior.

## Relevant Roadmap and Spec Files

- `docs/roadmap/roadmap_index.yaml`
  - Authoritative task identity, dependency, status, pointers, boundary tags, and child task sequence.
- `docs/roadmap/implementation_status.md`
  - Active frontier and context-tool boundaries.
- `docs/roadmap/project_workspace_implementation_decision_sweep.md`
  - Consolidated Phase 7 decisions; Chapter / Scene Storage defaults.
- `docs/roadmap/task_backlog.md`
  - Workspace backlog entry for `PHASE7-IMPL-004`.
- `docs/roadmap/phase_map.md`
  - Phase 7 position and workspace layer order.
- `docs/roadmap/chapter_scene_data_model_spec.md`
  - Source spec for chapter/scene metadata model.
- `docs/roadmap/chapters_scenes_page_spec.md`
  - Source spec for later page behavior after metadata/editor foundations.
- `docs/roadmap/project_file_model.md`
  - Existing project storage model context.
- `docs/roadmap/decision_log.md`, `docs/roadmap/risk_register.md`, `docs/roadmap/open_questions.md`
  - Supporting governance and unresolved decision/risk context.
- `scripts/roadmap_enrichment/README.md`
  - Confirms enrichment JSON creation and task record rendering are explicit later steps in the scaffold.
- `scripts/roadmap_enrichment/tool_commands.md`
  - Records tool syntax and CCE cleanup findings; evidence artifacts remain non-authoritative.

## Evidence Quality Notes

- Roadmap control files and `.codex-context/PHASE7-IMPL-004/task_manifest.json` are the authority for task identity, dependency, status, pointers, and boundary tags.
- Clean CCE verification on 2026-06-14 returned useful scoped hits for `frontend/src/api.js`, `backend/main.py`, `backend/project_manager.py`, and `tests/test_project_manager.py`.
- CCE cleanup was required because an earlier index was contaminated by generated Graphify/cache artifacts. The polluted index was cleared and rebuilt with scoped paths only: `backend`, `frontend/src`, `tests`, and `docs/roadmap`.
- CCE full re-index previously exited with status 139. Future collection should prefer scoped CCE indexing and must not run `cce init`.
- Graphify output is weak supporting evidence only. The recorded Graphify queries returned noisy or irrelevant topology, including OMI panel, package dependency, README, and documentation nodes rather than reliable chapter/scene route relationships.
- Scoped Repomix is useful for file inventory and high-level function names, but it remains supporting evidence rather than roadmap authority.
- AI Context is fallback status evidence only. The repaired pass intentionally skipped AI Context generation because task mode writes to a shared path.

## Explicit Non-goals

- Do not implement runtime app code in this artifact-generation task.
- Do not modify backend runtime behavior.
- Do not modify frontend runtime behavior.
- Do not rewrite, polish, continue, expand, imitate, or improve owner-authored scene prose.
- Do not rewrite scene Markdown during metadata creation, repair, move, reorder, listing, or display.
- Do not create generated prose, summaries, navigation prose, or model-authored scene content.
- Do not call Ollama, live models, Story Check, extraction tools, or Dramatica-specific logic.
- Do not mutate memory/canon, OMI candidates, OMI promotions, project truth, training data, JSONL files, dataset manifests, or model artifacts.
- Do not implement Project Overview, Notes / Materials, Shared Editor, OMI setup, Memory / Canon, or Phase 7 validation work under this parent task.

## Implementation Micro-task Sequence

1. `PHASE7-IMPL-004-T001` - Read-only chapter and scene metadata compatibility inventory.
   - Status: `ready`
   - Scope: documentation inventory only.
   - Suggested output: focused inventory of existing chapter/scene storage, routes, UI assumptions, tests, gaps, and next-task allowlist.
2. `PHASE7-IMPL-004-T002` - Implement legacy scene Markdown compatibility metadata reads.
   - Status: completed and reviewed.
   - Scope: read compatibility that can surface metadata while preserving legacy standalone scene Markdown behavior.
   - Completed behavior: `backend/project_manager.py` now exposes read-only metadata-compatible scene records for legacy Markdown scenes without creating metadata files.
   - Review confirmed stale or unsafe metadata `project_id`, `scene_id`, and `content_path` are normalized from the safe requested project/scene path.
   - Suggested focus: `backend/project_manager.py`, `backend/main.py`, focused route/helper tests.
3. `PHASE7-IMPL-004-T003` - Backend metadata write/create helpers.
   - Status: `draft`
   - Next child task; not started by T002.
   - Scope: create/update metadata records separately from scene Markdown bodies.
   - Suggested focus: helper-level behavior and failure/rollback tests; no prose body mutation.
4. `PHASE7-IMPL-004-T004` - Route compatibility tests.
   - Status: `draft`
   - Scope: route-level guarantees for legacy scenes, metadata-backed scenes, missing metadata, and no scene body rewrites.
5. `PHASE7-IMPL-004-T005` - Frontend display of scene titles/order if metadata exists.
   - Status: `draft`
   - Scope: UI/API adaptation for metadata display only after backend read compatibility is stable.
6. `PHASE7-IMPL-004-T006` - Legacy scene fallback tests.
   - Status: `draft`
   - Scope: explicit regression tests proving flat Markdown scene compatibility remains intact.
7. `PHASE7-IMPL-004-T007` - Roadmap/status update after PHASE7-IMPL-004 completion.
   - Status: `draft`
   - Scope: documentation/status update only after the implementation and validation children are complete.
