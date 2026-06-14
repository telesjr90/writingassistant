# PHASE7-IMPL-004

## ID

`PHASE7-IMPL-004`

## Title

Chapter / Scene Metadata Compatibility Layer

## Goal

Add a metadata-only compatibility layer for chapters and scenes while preserving legacy flat Markdown scene files at `scenes/{scene_id}.md`.

## Why now

`PHASE7-IMPL-004` is the active parent task after project creation, selector/library, and frontend project switching. Chapter/scene compatibility is the next Phase 7 foundation step before notes/materials storage, shared document editing, overview shells, OMI-guided setup, memory/canon shells, and final workspace validation.

## Inputs / dependencies

- Parent task: none.
- Required prior task IDs: `PHASE7-IMPL-003`.
- Current first child task: `PHASE7-IMPL-004-T001`.
- Task manifest: `.codex-context/PHASE7-IMPL-004/task_manifest.json`.
- Inventory: `docs/roadmap/inventory/PHASE7-IMPL-004.md`.
- Enrichment JSON: `docs/roadmap/enrichment/PHASE7-IMPL-004.enrichment.json`.
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
  - `docs/roadmap/task_backlog.md`
  - `docs/roadmap/phase_map.md`
- Supporting evidence:
  - `.codex-context/PHASE7-IMPL-004/cce-clean-index-verification.md`
  - `.codex-context/PHASE7-IMPL-004/cce-index-cleanup-resolution.md`
  - `.codex-context/PHASE7-IMPL-004/cce-findings.md`
  - `.codex-context/PHASE7-IMPL-004/repomix-output.md`
  - `.codex-context/PHASE7-IMPL-004/graphify-output.md`

## Scope

- Include: chapter/scene metadata compatibility planning and child implementation slices.
- Include: preserving legacy standalone Markdown scenes when metadata is missing.
- Include: separate chapter metadata and scene metadata behavior.
- Include: route/helper/frontend compatibility tests in child validation tasks.
- Exclude: runtime implementation in this artifact-generation record.
- Exclude: project overview, notes/materials, shared editor expansion, OMI-guided setup, memory/canon, and Phase 7 browser/manual validation.
- Exclude: model calls, extraction, Dramatica-specific logic, generated prose, and memory/canon mutation.

## Must not touch

- Owner-authored scene Markdown body content except through explicit owner save paths in future runtime tasks.
- `backend/**`, `frontend/**`, `tests/**`, `projects/**`, training files, JSONL files, dataset manifests, model artifacts, and package/dependency files unless a future child task explicitly authorizes them.
- OMI candidate records, OMI promotion records, memory/canon files, context-generation outputs, and book source files.

## Product boundaries

- Preserve owner-authored prose exactly.
- No scene rewrite during metadata creation, repair, move, reorder, listing, or display.
- No generated prose.
- No prose rewriting, continuation, imitation, polishing, expansion, or improvement.
- No silent promotion to project truth.
- No model calls.
- No memory/canon mutation.
- No OMI apply-promotion behavior.

## Current Evidence Summary

The repaired evidence identifies existing scene compatibility surfaces:

- `backend/project_manager.py`: `_scene_path`, `save_scene`, and `list_scenes`.
- `backend/main.py`: `get_scenes`, `get_scene`, and `story_check`.
- `frontend/src/api.js`: project-scoped scene list/read/save API calls.
- `tests/test_project_manager.py`: legacy sorted Markdown scene listing and missing-scenes-dir behavior.
- `tests/test_scene_routes.py` and `tests/test_frontend_project_workspace_source.py`: likely route/source regression surfaces for future child tasks.

Evidence quality is mixed. Clean CCE verification after scoped re-indexing is the strongest code inventory evidence. Graphify output was noisy and is weak supporting topology evidence only. Repomix is useful for scoped file inventory. AI Context is fallback status evidence only.

## Child Micro-task Sequence

1. `PHASE7-IMPL-004-T001` - Read-only chapter and scene metadata compatibility inventory. Status: ready/planning inventory recorded.
2. `PHASE7-IMPL-004-T002` - Implement legacy scene Markdown compatibility metadata reads. Status: completed and reviewed.
3. `PHASE7-IMPL-004-T003` - Backend metadata write/create helpers. Status: completed and reviewed.
4. `PHASE7-IMPL-004-T004` - Route compatibility tests. Status: completed.
5. `PHASE7-IMPL-004-T005` - Frontend display of scene titles/order if metadata exists. Status: completed.
6. `PHASE7-IMPL-004-T006` - Legacy scene fallback tests. Status: completed.
7. `PHASE7-IMPL-004-T007` - Roadmap/status update after PHASE7-IMPL-004 completion. Status: completed by closeout validation.

## T002 Completion Record

`PHASE7-IMPL-004-T002` is complete and reviewed.

Implemented behavior:

- Added read-only scene metadata helpers in `backend/project_manager.py`.
- Legacy `scenes/{scene_id}.md` files surface metadata-compatible read data without creating `scene_metadata/*.json`.
- Missing metadata returns safe compatibility defaults: `chapter_id: None`, empty `title`, safe derived `content_path`, and `metadata_exists: False`.
- Existing scene metadata JSON is read if present and normalized with compatibility defaults.
- Existing metadata JSON cannot echo stale or unsafe `project_id`, `scene_id`, or `content_path`; those fields are derived from the safe requested project/scene path.
- Added `load_scene_record()` and `list_scene_metadata()`.
- `load_scene()` and `save_scene()` remain unchanged.
- Scene routes and frontend behavior remain unchanged.

Review validation recorded for T002:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py`: PASS, 40 passed.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- `git diff --check`: PASS via approved LeanCTX fallback.
- `git status --short --branch`: PASS via approved LeanCTX fallback.

## T003 Completion Record

`PHASE7-IMPL-004-T003` is complete and reviewed.

Implemented behavior:

- Added backend helper-level scene metadata create/update behavior for `scene_metadata/{scene_id}.json`.
- Added backend helper-level chapter metadata create/update behavior for `chapters/{chapter_id}.json`.
- Preserved legacy scene Markdown body files; metadata helpers do not create, edit, truncate, reorder, or rewrite `scenes/{scene_id}.md`.
- Derived safe persisted identity fields from requested project/chapter/scene IDs.
- Preserved the T002 read compatibility contract including `metadata_version` and `order_index` while bridging `order` input to `order_index`.

Validation recorded for T003:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py`: PASS, 47 passed.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- `git diff --check`: PASS via approved LeanCTX fallback.
- `git status --short --branch`: PASS via approved LeanCTX fallback.

## T004 Completion Record

`PHASE7-IMPL-004-T004` is complete.

Validated behavior:

- Existing scene list route remains legacy-compatible: `{"scenes": [...]}`.
- Existing scene read route remains legacy-compatible: `{"content": "..."}`.
- Existing scene update route continues to update only the explicit owner-authored scene Markdown body.
- Metadata presence does not rename scene IDs, inject metadata into scene bodies, or mutate metadata during route update.

Validation recorded for T004:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_scene_routes.py`: PASS, 9 passed.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py`: PASS, 47 passed.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- `git diff --check`: PASS via approved LeanCTX fallback.
- `git status --short --branch`: PASS via approved LeanCTX fallback.

## T005 Completion Record

`PHASE7-IMPL-004-T005` is complete.

Implemented behavior:

- Frontend scene navigation supports legacy string scene IDs and metadata-shaped scene records.
- Metadata-shaped scene records may display nonblank `title` and sort by `order_index` / `order` when a future backend route returns that shape.
- Blank or missing metadata titles fall back to the safe scene ID.
- Scene selection, loading, and saving continue to use scene IDs, not titles.
- Current backend routes still return legacy scene string IDs only.

Validation recorded for T005:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_frontend_project_workspace_source.py`: PASS, 62 passed.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_scene_routes.py`: PASS, 9 passed.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py`: PASS, 47 passed.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- `git diff --check`: PASS via approved LeanCTX fallback.
- `git status --short --branch`: PASS via approved LeanCTX fallback.
- `frontend/package.json` was inspected; no lightweight frontend validation script exists, and build/server commands were skipped by boundary.

## T006 Completion Record

`PHASE7-IMPL-004-T006` is complete.

Validated behavior:

- Legacy flat Markdown scenes with no `scene_metadata/{scene_id}.json` remain valid standalone scenes.
- Legacy scenes remain readable, listable, display-safe, and writable through the existing explicit scene save/update path.
- Helper and route reads/lists do not silently create metadata files.
- Scene updates do not create metadata files for legacy-only scenes.
- Mixed metadata-backed and legacy-only scene collections remain compatible.

Validation recorded for T006:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py`: PASS, 47 passed.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_scene_routes.py`: PASS, 11 passed.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_frontend_project_workspace_source.py`: PASS, 63 passed.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- `git diff --check`: PASS via approved LeanCTX fallback.
- `git status --short --branch`: PASS via approved LeanCTX fallback.

## T007 Completion Record

`PHASE7-IMPL-004-T007` is complete after roadmap/status validation.

Closeout behavior:

- `PHASE7-IMPL-004` is recorded complete in the roadmap authority.
- `PHASE7-IMPL-004-T002` through `PHASE7-IMPL-004-T007` are recorded complete.
- Active frontier moved to the next published Phase 7 parent task: `PHASE7-IMPL-005` - Notes / Materials Storage.

## Parent Completion Result

`PHASE7-IMPL-004` is complete.

Final compatibility summary:

- Metadata compatibility preserves existing `scenes/{scene_id}.md` behavior.
- Legacy scenes without metadata remain standalone compatible scenes.
- Chapter metadata and scene metadata records are separate from owner-authored scene Markdown bodies.
- Metadata operations do not rewrite owner-authored scene prose.
- Existing scene route contracts remain legacy-compatible: list route returns `{"scenes": [...]}` and read route returns `{"content": "..."}`.
- Frontend display compatibility is conditional for future metadata-shaped scene records; current backend routes still return legacy scene strings.
- No model/Ollama calls, generated prose, extraction behavior, OMI/memory/canon mutation, training/JSONL/dataset changes, or browser/manual validation scope were added.

## Acceptance criteria

- Metadata compatibility preserves existing `scenes/{scene_id}.md` behavior.
- Legacy scenes without metadata remain valid standalone scenes.
- Chapter/scene metadata records are separate from scene body files.
- Metadata operations do not rewrite owner-authored scene prose.
- Existing route contracts remain compatible or are changed only in explicitly tested child tasks.
- Frontend metadata display is conditional and does not generate, summarize, or rewrite prose.

## Validation

Required commands for this artifact-generation task:

- `python3 scripts/roadmap_enrichment/render_task_record.py --task PHASE7-IMPL-004 --dry-run`
- `python3 scripts/roadmap_enrichment/render_task_record.py --task PHASE7-IMPL-004`
- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

Renderer note: the current renderer's non-dry-run path is scaffold-only and returns a deliberate failure instead of writing task records. This task record was created from the local task record template and enrichment JSON without modifying the renderer.

## Deferred work

- Migration behavior, route schema expansion, chapter/scene UI page expansion, generated navigation summaries, extraction, memory/canon mutation, and browser/manual validation remain outside `PHASE7-IMPL-004`.
- Browser/manual validation belongs under `PHASE7-IMPL-010`.
- Renderer implementation remains future scaffold work unless separately authorized.
- The next published Phase 7 parent task is `PHASE7-IMPL-005` - Notes / Materials Storage.
