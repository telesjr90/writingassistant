# Implementation Status

Status source: this file and `docs/roadmap/roadmap_index.yaml` are the current roadmap execution truth layer.

## Active Frontier

- Current track: Writer Assistant Core.
- Immediate active parent task: `PHASE8-IMPL-007` - Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation.
- Active child task: `PHASE8-IMPL-007-T005` - Entity/quote/event mocked normalization helpers.
- Next child task: `PHASE8-IMPL-007-T006` - Candidate draft builder, fail-closed behavior, and boundary hardening.
- Last completed child task: `PHASE8-IMPL-007-T004` - Manifest and raw artifact bundle validators.
- Last completed parent task: `PHASE8-IMPL-006` - Writer Assistant Core evidence-first extraction foundation and BookNLP-ready adapter strategy.
- Prior completed child under last parent: `PHASE8-IMPL-004-T006` - Index safety repair or hardening (validation-only).
- Prior completed child under last parent: `PHASE8-IMPL-003-T006` - Candidate list/index helper implementation.
- Prior completed child under last parent: `PHASE8-IMPL-003-T005` - Candidate list/index contract tests.
- Prior completed child under last parent: `PHASE8-IMPL-003-T004` - Minimal candidate persistence helpers.
- Prior completed child under last parent: `PHASE8-IMPL-003-T003` - Candidate persistence write/read contract tests.
- Prior completed child under last parent: `PHASE8-IMPL-003-T002` - Candidate persistence contract decision.
- Prior completed child under last parent: `PHASE8-IMPL-003-T001` - Publish candidate persistence parent and child-task plan.
- Prior completed parent task: `PHASE8-IMPL-002` - Writer Assistant Core candidate storage contract and evidence/provenance validation.
- Prior completed child under prior parent: `PHASE8-IMPL-002-T007` - Roadmap/status closeout.
- Prior completed child under last parent: `PHASE8-IMPL-002-T006` - Candidate storage helper skeleton.
- Prior completed child under last parent: `PHASE8-IMPL-002-T005` - Project-local candidate storage path contract tests.
- Prior completed child under last parent: `PHASE8-IMPL-002-T004` - Candidate record validation helpers.
- Prior completed child under last parent: `PHASE8-IMPL-002-T003` - Candidate storage/evidence contract tests.
- Prior completed child under last parent: `PHASE8-IMPL-002-T002` - Candidate storage and evidence/provenance contract decision.
- Prior completed child under last parent: `PHASE8-IMPL-002-T001` - Publish candidate storage/evidence validation parent and child-task plan.
- Prior completed parent task: `PHASE8-IMPL-001` - Writer Assistant Core implementation readiness and first runtime slice plan.
- Prior completed child under prior parent: `PHASE8-IMPL-001-T007` - Roadmap/status closeout.
- Prior completed child: `PHASE8-IMPL-001-T006` - Writer Assistant Core candidate schema constants.
- Prior completed child: `PHASE8-IMPL-001-T005` - Writer Assistant Core candidate schema contract tests.
- Prior completed child: `PHASE8-IMPL-001-T004` - First runtime slice decision.
- Prior completed child: `PHASE8-IMPL-001-T003` - Targeted context collection and source inventory.
- Prior completed child: `PHASE8-IMPL-001-T002` - Context collection plan for Writer Assistant Core.
- Prior completed child: `PHASE8-IMPL-001-T001` - Publish Writer Assistant Core parent and child-task plan.
- Prior completed child: `PHASE7-IMPL-010-T006` - Final validation regression pass.
- Prior completed child: `PHASE7-IMPL-010-T005` - Validation repair triage.
- Prior completed child: `PHASE7-IMPL-010-T004` - Browser/manual smoke execution (PARTIAL).
- Prior completed parent task: `PHASE7-IMPL-010` - Workspace Validation / Browser and Manual Smoke.
- Completed parent task: `PHASE7-IMPL-010` - Workspace Validation / Browser and Manual Smoke.
- Completed parent task: `PHASE7-IMPL-009` - Memory / Canon shell (approved-only empty states).
- Completed parent task: `PHASE7-IMPL-008` - OMI-guided project creation staged flow.
- Completed parent task: `PHASE7-IMPL-007` - Project Overview shell.
- Completed parent task: `PHASE7-IMPL-006` - Shared owner-authored document editor.
- Completed parent task: `PHASE7-IMPL-005` - Notes / Materials Storage.
- Completed closeout micro-task: `PHASE7-IMPL-010-T007` - Roadmap/status closeout.
- Phase 7 published sequence is complete (`PHASE7-IMPL-001` through `PHASE7-IMPL-010`).
- Next child: none published; next parent/child requires owner/roadmap confirmation.
- Deferred validation: interactive browser flows D, E, H, I, J, K, L when Playwright deps or browser MCP are available; note/material flows F/G unless controlled fixtures are authorized later.
- Local smoke artifact (uncommitted): `projects/smoke-blank-1781586974/`.

`PHASE8-IMPL-001` is complete as the first Writer Assistant Core readiness parent. T001 published the parent and child-task plan. T002 published the context collection plan at `docs/roadmap/context/PHASE8-IMPL-001-context-collection-plan.md`. T003 produced the targeted context report at `docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md` using direct file/source inspection only. T004 accepted `docs/roadmap/decisions/PHASE8-IMPL-001-first-runtime-slice-decision.md` and selected Writer Assistant Core candidate schema constants plus source-level/contract tests as the first runtime slice. T005 added tests-first contract coverage in `tests/test_writer_assistant_core_candidate_schema_contract.py`. T006 added constants-only schema metadata in `backend/story_knowledge/candidate_schema.py` and satisfied the T005 contract. T007 closed the parent with final validation. PHASE8-IMPL-001 completed schema contract/constants only and did not add extraction, candidate creation runtime, backend routes, frontend extraction UI, model/Ollama calls, apply-promotion, memory/canon mutation, package changes, candidate storage writes, training data, JSONL records, or dataset artifacts.

`PHASE8-IMPL-002` is complete as the second Writer Assistant Core parent. It prepared candidate storage contracts and evidence/provenance validation before extraction/runtime expansion. `PHASE8-IMPL-002-T001` published the parent, inventory, enrichment JSON, child-task plan, and roadmap/status updates. `PHASE8-IMPL-002-T002` accepted the storage record contract in `docs/roadmap/decisions/PHASE8-IMPL-002-candidate-storage-evidence-contract-decision.md`, selected T003 as tests-only, deferred validation helpers to T004, and deferred storage writes until T005/T006. `PHASE8-IMPL-002-T003` added tests-only contract coverage in `tests/test_writer_assistant_core_candidate_record_contract.py` for record shape, source locator, evidence/provenance, status/destination, path safety, and forbidden mutation. `PHASE8-IMPL-002-T004` added pure validation helpers in `backend/story_knowledge/candidate_record.py` and satisfied the T003 contract tests with no file I/O. `PHASE8-IMPL-002-T005` added tests-only storage path contract coverage in `tests/test_writer_assistant_core_candidate_storage_contract.py` for `writer_assistant/candidates/` and `writer_assistant/index.json` boundaries. `PHASE8-IMPL-002-T006` added pure path helpers in `backend/story_knowledge/candidate_storage.py` and satisfied the T005 storage contract tests. `PHASE8-IMPL-002-T007` closed the parent with final validation. Final behavior: candidate record validation helpers are pure; storage helpers are pure path helpers only; no directories/files are created; no JSON read/write/list behavior exists. Phase 8 still has no extraction runtime, no candidate JSON persistence, no backend extraction routes, no frontend extraction/review UI, no model/Ollama calls, no apply-promotion, and no memory/canon mutation.

`PHASE8-IMPL-003` is complete as the third Writer Assistant Core parent. `PHASE8-IMPL-003-T001` published the parent, inventory, enrichment JSON, child-task plan, and roadmap/status updates. `PHASE8-IMPL-003-T002` accepted the candidate persistence contract decision at `docs/roadmap/decisions/PHASE8-IMPL-003-candidate-persistence-contract-decision.md`, selected T003 as tests-only write/read, T004 as minimal write/read helpers, T005 as tests-only list, T006 as list helper only if T005 authorizes, and deferred index read/write to a later parent. `PHASE8-IMPL-003-T003` added tests-only write/read persistence contract coverage in `tests/test_writer_assistant_core_candidate_persistence_contract.py`. `PHASE8-IMPL-003-T004` created `backend/story_knowledge/candidate_persistence.py` with minimal candidate-only JSON write/read helpers and satisfied the targeted persistence contract test. `PHASE8-IMPL-003-T005` added tests-only list contract coverage in `tests/test_writer_assistant_core_candidate_list_contract.py`. `PHASE8-IMPL-003-T006` added `list_candidate_records` to `backend/story_knowledge/candidate_persistence.py` and satisfied the targeted list contract test. `PHASE8-IMPL-003-T007` closed the parent with final validation. Final behavior: `write_candidate_record`, `read_candidate_record`, and `list_candidate_records` provide candidate-only JSON persistence; candidate JSON files under `writer_assistant/candidates/*.json` are source of truth; write validates before persistence; read/list validate loaded records and are side-effect free; list is direct-file-only, non-recursive, and deterministic by `candidate_id`; no index is read/written/created. T005/T006 are list-only despite the child labels mentioning list/index; index read/write was deferred to `PHASE8-IMPL-004`.

`PHASE8-IMPL-004` is complete as the fourth Writer Assistant Core parent. `PHASE8-IMPL-004-T001` published the parent, inventory, enrichment JSON, child-task plan, and roadmap/status updates. `PHASE8-IMPL-004-T002` accepted the derived index contract decision at `docs/roadmap/decisions/PHASE8-IMPL-004-candidate-index-contract-decision.md`, selected T003 as tests-only index contract coverage, T004 as minimal index helpers in `backend/story_knowledge/candidate_index.py`, and deferred incremental sync/update APIs, routes, UI, extraction, model calls, apply-promotion, and memory/canon mutation. `PHASE8-IMPL-004-T003` added tests-only index contract coverage in `tests/test_writer_assistant_core_candidate_index_contract.py`. `PHASE8-IMPL-004-T004` created `backend/story_knowledge/candidate_index.py` with `build_candidate_index`, `write_candidate_index`, and `read_candidate_index`; derived index helpers use candidate JSON as source of truth and T003 index contract tests now pass. `PHASE8-IMPL-004-T005` added focused regression coverage in `tests/test_writer_assistant_core_candidate_index_safety_regression.py`; targeted regression pytest passes with no repair gap. `PHASE8-IMPL-004-T006` completed as validation-only because T005 found no repair or hardening gaps; T004 index helpers already satisfy T005 safety/stale/corrupt regression coverage. `PHASE8-IMPL-004-T007` closed the parent with final validation. Final behavior: `build_candidate_index`, `write_candidate_index`, and `read_candidate_index` provide derived candidate index helpers; candidate JSON files under `writer_assistant/candidates/{candidate_id}.json` remain source of truth; `writer_assistant/index.json` is derived convenience metadata only; build derives from `list_candidate_records` and is side-effect free; write refreshes index from candidate JSON; read validates index shape only and does not rebuild/repair; stale-but-valid index can be read as-is; corrupt index raises `ValueError` on read and is ignored by build; corrupt index may be overwritten by write if candidate JSON records validate. Writer Assistant Core currently has schema constants, candidate record validation, candidate storage path helpers, candidate JSON write/read/list persistence, and derived candidate index build/write/read helpers. Writer Assistant Core still has no backend routes for candidate review/index, frontend candidate review/backlog UI, runtime extraction, model/Ollama calls, semantic search, apply-promotion, or memory/canon mutation. No extraction implementation has started. The next work is tool evaluation and extraction strategy for exactly nine approved tools/references, not runtime extraction.

`PHASE8-IMPL-005` is complete as the fifth Writer Assistant Core parent. `PHASE8-IMPL-005-T001` published the parent, inventory, enrichment JSON, child-task plan, and roadmap/status updates. It recorded the narrowed nine-tool scope (dramatica-flow, Narrative Context Protocol, Subtxt docs, spaCy, segram, BookNLP, GLiNER, LangExtract, Renard) and the official source retrieval policy for later children. T001 did not evaluate tools, retrieve sources, install tools, or change runtime code/tests. `PHASE8-IMPL-005-T002` accepted the evaluation scope, fixture category plan, 0-5 scoring rubric with hard blockers and pass/fail gates, provisional tool grouping, and T003 source inventory requirements in `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`. T002 did not retrieve sources, create fixtures, install tools, or change runtime code/tests. `PHASE8-IMPL-005-T003` completed the official source inventory and license/dependency screen at `docs/roadmap/inventory/PHASE8-IMPL-005-tool-source-inventory.md` using Cursor web access and read-only terminal fetch of official docs/repos only; preliminary classifications: spaCy likely runtime adapter candidate; segram, BookNLP, GLiNER, LangExtract, and Renard possible runtime adapter candidates; dramatica-flow, NCP, and Subtxt docs reference-only; dramatica-flow B1 generation risk blocks runtime adapter. T003 did not install, clone, or execute tools; did not change runtime code/tests. `PHASE8-IMPL-005-T004` accepted dramatica-flow as `reference-only` for analysis-pattern/rubric inspiration in `docs/roadmap/decisions/PHASE8-IMPL-005-dramatica-flow-analysis-only-reference-decision.md`. Runtime adapter use is REJECT/DEFER. Safe reference concepts (causal chain, foreshadowing/promise lifecycle, emotional arc, relationship delta, timeline/thread activity, information boundaries, audit dimensions without revision) may inform future app-owned candidate rubrics only. Writer/Reviser/Architect generation, prose/outline generation, continuation, rewrite/revise APIs, world_state writes, and automatic canon settlement are rejected. T004 did not install, clone, or execute dramatica-flow; did not change runtime code/tests. `PHASE8-IMPL-005-T005` accepted NCP as `reference-only` and future `approved-context import/export candidate`, and Subtxt docs as `reference-only` and future `semantic rubric candidate`, in `docs/roadmap/decisions/PHASE8-IMPL-005-ncp-subtxt-structural-interpretation-strategy-decision.md`. Runtime adapter/import/export/Subtxt analysis implementation is REJECT/DEFER. NCP import as automatic truth, NCP export of raw candidates as final truth, automatic storyform labeling, and Subtxt/Dramatica labels without evidence are rejected. T005 did not install, clone, or execute tools; did not implement NCP import/export or Subtxt analysis; did not change runtime code/tests. `PHASE8-IMPL-005-T006` accepted the NLP/extraction adapter strategy decision at `docs/roadmap/decisions/PHASE8-IMPL-005-nlp-extraction-adapter-strategy-decision.md`: first extraction strategy is spaCy-first local deterministic/rule-assisted candidate extraction foundation; first implementation style is app-owned, local, deterministic/rule-assisted, and candidate-only. The first slice should focus on source segmentation/source locators, simple entity candidates, source evidence spans, candidate normalization, and no-prose/no-canon-mutation contracts. segram, BookNLP, GLiNER, LangExtract, and Renard are deferred from the first implementation slice; LangExtract remains later/local-only/model-assisted only if privacy/local model policy is approved, and Renard remains deferred pending GPL/license review and relationship-network scope. dramatica-flow, NCP, and Subtxt remain reference-only according to T004/T005. `PHASE8-IMPL-005-T007` closed the parent and recommends `PHASE8-IMPL-006 - Writer Assistant Core analysis-only candidate extraction architecture and spaCy-first local extraction foundation` as the next parent. No runtime extraction exists yet. PHASE8-IMPL-005 did not install, clone, execute, or locally evaluate external tools; did not change runtime code/tests/packages; and did not add backend routes, frontend UI, project runtime files, model calls, apply-promotion, memory/canon mutation, training data, JSONL records, or dataset files.

`PHASE8-IMPL-006` is complete as the sixth Writer Assistant Core parent. `PHASE8-IMPL-006-T001` published the evidence-first extraction foundation and BookNLP-ready adapter strategy with docs/status/planning artifacts only. `PHASE8-IMPL-006-T002` accepted the evidence/source-map contract decision at `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-source-map-contract-decision.md`. The accepted contract defines app-owned source document identity, source maps, source locators, primary character offsets over exact UTF-8 decoded source snapshots, source hashes/snapshots, Evidence Ledger shape, evidence records, extraction run provenance, raw output policy, BookNLP-ready mapping assumptions, candidate normalization boundaries, and owner-review/no-canon guardrails before runtime extraction. `PHASE8-IMPL-006-T003` added tests-first source/evidence contract coverage in `tests/test_writer_assistant_core_source_evidence_contract.py`. `PHASE8-IMPL-006-T004` added pure validation helpers in `backend/story_knowledge/source_map.py` and `backend/story_knowledge/evidence.py`; the source/evidence contract tests now pass. `PHASE8-IMPL-006-T005` accepted the BookNLP-ready raw output and adapter contract decision at `docs/roadmap/decisions/PHASE8-IMPL-006-booknlp-ready-raw-output-adapter-contract-decision.md`. `PHASE8-IMPL-006-T006` added tests-first BookNLP-ready adapter contract coverage in `tests/test_writer_assistant_core_booknlp_adapter_contract.py` for future `backend.story_knowledge.booknlp_adapter_contract` APIs: `validate_booknlp_run_manifest`, `validate_booknlp_raw_artifact_bundle`, `normalize_booknlp_entity_mentions`, `normalize_booknlp_quotes`, `normalize_booknlp_events`, and `build_booknlp_candidate_drafts`. `PHASE8-IMPL-006-T007` closed the parent. Final behavior now available: pure source document reference, source segment, source map, source locator, evidence record, extraction run provenance, and raw output reference validation; source/evidence contract tests pass; existing Writer Assistant Core candidate contract regressions pass. The BookNLP adapter contract test remains expected red until future `backend.story_knowledge.booknlp_adapter_contract` exists. No runtime extraction exists yet. BookNLP and spaCy are not installed or run. No production adapter code exists yet. Recommended next parent: `PHASE8-IMPL-007` - Writer Assistant Core BookNLP adapter contract implementation and mocked normalization foundation.

`PHASE8-IMPL-007` is active as the seventh Writer Assistant Core parent. `PHASE8-IMPL-007-T001` published the parent task record, inventory, enrichment JSON, and roadmap/status updates and confirmed the four `.external_sources/` clone paths (`.external_sources/booknlp`, `.external_sources/dramatica-flow`, `.external_sources/narrative-context-protocol`, `.external_sources/subtxt-docs`) exist locally and are protected from commit via `.git/info/exclude`. `PHASE8-IMPL-007-T002` completed the read-only official source inventory from `.external_sources/`, created `docs/roadmap/inventory/PHASE8-IMPL-007-official-source-inventory.md`, created `docs/roadmap/decisions/PHASE8-IMPL-007-implementation-source-refresh-decision.md`, and verified local repo SHAs for BookNLP (`3d900fc2224e55960c3363826ae28539b77b4204`), dramatica-flow (`890f099bfcb64adbf407fd83ab708c48e92b0766`), Narrative Context Protocol (`b1222748376aae3d309176b3bb5afb884eb281ea`), and Subtxt docs (`ec66121364c039693314dcce4cde464e497bece4`). T002 confirmed BookNLP real output fields and refined `booknlp_events` as an app-owned derived abstraction from `.tokens.event`; confirmed dramatica-flow runtime remains blocked/deferred; confirmed NCP remains future approved-context import/export reference only; and confirmed Subtxt docs remain semantic guardrail/reference only. `PHASE8-IMPL-007-T003` completed the docs-only implementation decision at `docs/roadmap/decisions/PHASE8-IMPL-007-booknlp-adapter-implementation-decision.md`, accepting T004 validators/API symbols first, T005 mocked normalizers, and T006 builder/boundary hardening. `PHASE8-IMPL-007-T004` created `backend/story_knowledge/booknlp_adapter_contract.py` as a pure mocked standard-library-only module, exposed all six public APIs, implemented run manifest and raw artifact bundle validators, and added minimal in-memory draft shaping required by the current contract tests. The targeted BookNLP adapter contract pytest now passes. The active child is now `PHASE8-IMPL-007-T005`, with `PHASE8-IMPL-007-T006` next and `PHASE8-IMPL-007-T007` planned to close the parent. Real BookNLP/spaCy install or execution remains deferred, and no external repo code has been executed or vendored. No runtime extraction, backend routes, frontend UI, package/dependency changes, model calls, generated prose, apply-promotion, memory/canon mutation, project runtime files, or training/JSONL/dataset work was added by T004.

`PHASE7-IMPL-004` must remain `Chapter / Scene Metadata Compatibility Layer`.

`PHASE7-IMPL-004` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-004-T002`: read-only backend scene metadata compatibility for legacy Markdown scenes.
- `PHASE7-IMPL-004-T003`: backend scene/chapter metadata write/create helpers.
- `PHASE7-IMPL-004-T004`: route compatibility tests preserving legacy scene route contracts.
- `PHASE7-IMPL-004-T005`: frontend display compatibility for metadata-shaped scene records while preserving legacy string scene IDs.
- `PHASE7-IMPL-004-T006`: legacy scene fallback regression tests.
- `PHASE7-IMPL-004-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-004` behavior preserves existing `scenes/{scene_id}.md` scene bodies, keeps chapter and scene metadata separate from owner-authored Markdown, preserves legacy list/read route shapes, and does not add model calls, generated prose, extraction, OMI/memory/canon mutation, training/JSONL/dataset changes, or browser/manual validation scope.

`PHASE7-IMPL-005` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-005-T001`: inventory/task/enrichment setup for notes/materials storage and routes.
- `PHASE7-IMPL-005-T002`: backend note/material body and metadata storage helpers.
- `PHASE7-IMPL-005-T003`: backend note/material routes.
- `PHASE7-IMPL-005-T004`: route compatibility and path-safety tests.
- `PHASE7-IMPL-005-T005`: frontend API compatibility helpers.
- `PHASE7-IMPL-005-T006`: minimal notes/materials navigation/display shell.
- `PHASE7-IMPL-005-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-005` behavior stores owner-authored notes and owner-provided materials as separate body and metadata files; keeps body saves from creating metadata; requires existing bodies for metadata writes in this slice; keeps reads/lists side-effect free; enforces safe identity/path derivation; wires route/API/frontend shell compatibility; and does not add generated prose, note/material summaries, extraction, semantic search, model/Ollama calls, metadata editing UI, full shared editor refactor, OMI/memory/canon mutation, or training/JSONL/dataset changes.

`PHASE7-IMPL-006` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-006-T001`: shared owner-authored document editor inventory and child-task plan.
- `PHASE7-IMPL-006-T002`: shared document state contract and source-level tests.
- `PHASE7-IMPL-006-T003`: shared editor controller helpers.
- `PHASE7-IMPL-006-T004`: document-neutral `Editor.jsx` prop cleanup and behavior parity.
- `PHASE7-IMPL-006-T005`: `ProjectNav.jsx` scene/note/material document selection parity.
- `PHASE7-IMPL-006-T006`: shared editor regression coverage.
- `PHASE7-IMPL-006-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-006` behavior keeps scene/note/material document selection ID-based; loads and saves exact owner-authored body content only; keeps metadata out of editor bodies; preserves dirty-state, keyboard-save, project-switch, and document-switch guards; and does not add metadata editing UI, note/material create/import/upload UI, generated prose, summaries, extraction, model/Ollama calls, OMI/memory/canon mutation, or training/JSONL/dataset changes. Browser/manual validation remains deferred to `PHASE7-IMPL-010`.

`PHASE7-IMPL-007` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-007-T001`: Project Overview shell inventory and child-task plan.
- `PHASE7-IMPL-007-T002`: overview data contract and source-level tests.
- `PHASE7-IMPL-007-T003`: backend/project data helper compatibility decision; no backend overview helper was needed.
- `PHASE7-IMPL-007-T004`: standalone prop-driven `ProjectOverview` component.
- `PHASE7-IMPL-007-T005`: ProjectNav/App overview integration.
- `PHASE7-IMPL-007-T006`: overview regression coverage.
- `PHASE7-IMPL-007-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-007` behavior adds Overview as a workspace view, not an owner-authored document type. It uses existing deterministic project/list/status state, passes project/scenes/notes/materials/OMI/status/approved-memory shell props, derives scene/note/material counts from arrays/lists only, omits/defer chapter count, resets project switches to Overview, switches scene/note/material selection to editor view, keeps keyboard save editor-view-only, and adds no `/overview` backend/API dependency or backend overview helper. It does not add generated summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, OMI/memory/canon mutation, metadata editing UI, note/material create/import/upload UI, training/JSONL/dataset changes, or browser/manual validation.

`PHASE7-IMPL-008` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-008-T001`: OMI-guided project creation staged flow inventory and child-task plan.
- `PHASE7-IMPL-008-T002`: staged flow data contract and source-level tests.
- `PHASE7-IMPL-008-T003`: backend staged setup storage helpers; Path A selected and backend staged storage deferred.
- `PHASE7-IMPL-008-T004`: backend staged setup routes and compatibility tests; backend staged routes deferred.
- `PHASE7-IMPL-008-T005`: frontend API helpers and staged creation UI shell.
- `PHASE7-IMPL-008-T006`: staged flow regression coverage.
- `PHASE7-IMPL-008-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-008` behavior adds a frontend-transient OMI-guided staged project creation shell with owner-authored setup input, visible setup/candidate labels, review/cancel/reset behavior, and explicit final confirmation before the existing create-project path runs. Backend staged storage and backend staged routes are intentionally deferred. No staged backend API helpers, OMI writes during staged draft steps, hidden pre-confirmation project writes, generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, apply-promotion, memory/canon mutation, training/JSONL/dataset changes, metadata editing UI, note/material create/import/upload UI, or browser/manual validation were added.

`PHASE7-IMPL-009` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-009-T001`: Memory / Canon shell inventory and child-task plan.
- `PHASE7-IMPL-009-T002`: approved-memory shell data contract and source-level tests.
- `PHASE7-IMPL-009-T003`: standalone `MemoryCanonShell.jsx` component.
- `PHASE7-IMPL-009-T004`: App/ProjectNav integration as separate `memory-canon` workspace view.
- `PHASE7-IMPL-009-T005`: per-category approved-only empty-state hardening.
- `PHASE7-IMPL-009-T006`: Memory / Canon shell regression coverage.
- `PHASE7-IMPL-009-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-009` behavior adds a read-only Memory / Canon workspace shell with approved-only empty states for characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items. App/Nav integration exposes the shell as a separate `memory-canon` workspace view. OMI candidates, approved-but-not-applied candidates, and promotion records are not displayed as approved canon. No backend approved-memory routes, backend approved-memory helpers, frontend approved-memory API helpers, apply-promotion, memory/canon mutation, generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, training/JSONL/dataset changes, metadata editing UI, note/material create/import/upload UI, or browser/manual validation were added. Browser/manual validation remains deferred to `PHASE7-IMPL-010`.

`PHASE7-IMPL-010` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-010-T001`: docs/status only; inventory, task record, enrichment JSON, and roadmap/status updates.
- `PHASE7-IMPL-010-T002`: automated regression validation pass; all relevant pytest suites passed on first run.
- `PHASE7-IMPL-010-T003`: browser smoke checklist preparation.
- `PHASE7-IMPL-010-T004`: browser/manual smoke execution (PARTIAL; Playwright `libnspr4.so` missing; browser MCP unavailable).
- `PHASE7-IMPL-010-T005`: validation repair triage; no product defect confirmed; no runtime repair authorized.
- `PHASE7-IMPL-010-T006`: final validation regression pass; all suites passed on first run.
- `PHASE7-IMPL-010-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-010` behavior validated the completed Phase 7 workspace foundation from `PHASE7-IMPL-004` through `PHASE7-IMPL-009` using automated regression checks, a prepared browser/manual smoke checklist, partial browser/manual smoke execution with environment-limited fallback evidence, validation repair triage, and final regression confirmation. It did not add generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, apply-promotion, memory/canon mutation, OMI candidate promotion, backend approved-memory routes/helpers, frontend approved-memory API helpers, metadata editing UI, note/material create/import/upload UI, runtime features, package/dependency changes, or training/JSONL/dataset work. Interactive UI browser validation remains deferred to owner/environment rerun when browser tooling is available.

The published Phase 7 parent sequence (`PHASE7-IMPL-001` through `PHASE7-IMPL-010`) is complete. `PHASE8-IMPL-001`, `PHASE8-IMPL-002`, `PHASE8-IMPL-003`, `PHASE8-IMPL-004`, `PHASE8-IMPL-005`, and `PHASE8-IMPL-006` are complete as the first six published Writer Assistant Core parents in `docs/roadmap/roadmap_index.yaml`. `PHASE8-IMPL-007` is now active as the seventh Writer Assistant Core parent in `docs/roadmap/roadmap_index.yaml`; `PHASE8-IMPL-007-T001`, `PHASE8-IMPL-007-T002`, `PHASE8-IMPL-007-T003`, and `PHASE8-IMPL-007-T004` are complete and `PHASE8-IMPL-007-T005` is ready/active.

`PHASE7-IMPL-010` must remain validation-only. It must not add runtime feature scope, apply-promotion, memory/canon mutation, generated prose, model calls, extraction, or training/JSONL/dataset work unless explicitly authorized by a separate roadmap task.

Any prior smoke-test/manual-validation use of `PHASE7-IMPL-004` is a numbering drift issue, not a reason to renumber. Correct the reference by moving validation language under `PHASE7-IMPL-010` or a child task of `PHASE7-IMPL-010`; do not change the identity of `PHASE7-IMPL-004`.

## Authority

- GitHub Issues and GitHub Projects are not authoritative yet.
- Published parent task IDs in `docs/roadmap/roadmap_index.yaml` are authoritative for Codex task prompts.
- Parent task identity is immutable after publication.
- New implementation detail belongs in child micro-tasks, not in renamed or repurposed parent IDs.
- Child micro-tasks may use `planning_microtask`, `runtime_microtask`, or `validation_microtask` types.

## Codex Execution Role

Codex is a strict micro-task implementer, not a planner.

Codex prompts should specify one task ID, the exact files allowed to change, the exact validation commands to run, and the final response format. Codex should not infer new roadmap structure during implementation work.

## Context Tool Boundary

Repomix, Graphify, LeanCTX, and CCE are planning/context tools only and must not be run during Codex implementation micro-tasks.

LeanCTX is exceptional fallback only. It is not part of normal Codex implementation execution for this repository.

Context packs and generated maps are refreshable artifacts, not roadmap truth. The control layer is:

1. `docs/roadmap/roadmap_index.yaml`
2. `docs/roadmap/implementation_status.md`
3. `docs/roadmap/validation/latest_roadmap_validation.md`

## Roadmap enrichment scaffold

- The orchestrator scaffold is local and deterministic.
- The orchestrator must not decide task order.
- The orchestrator must not change `active_frontier` automatically.
- The orchestrator must not mark tasks complete.
- The orchestrator must not modify application code.
- The orchestrator may create task manifests, evidence files, enrichment JSON, and rendered task records.
- Generated context files are evidence artifacts, not source of truth.
- Source of truth remains `implementation_status.md`, `roadmap_index.yaml`, reviewed task records, `decision_log.md`, `risk_register.md`, and `open_questions.md`.
- CCE, Graphify, and Repomix may only be run in explicit collect mode after this scaffold is validated.
- `PHASE7-IMPL-004` should be the first orchestrator test case.

## Local tool command syntax

- Local tool command syntax discovery exists for CCE, Graphify, Repomix, and `scripts/generate_ai_context.sh`.
- Exact discovered syntax is recorded in `scripts/roadmap_enrichment/tool_commands.md`.
- AI Context command candidates for `PHASE7-IMPL-004` are recorded under `.codex-context/PHASE7-IMPL-004/`.
- Command discovery does not mean context collection has run.
- `collect-plan` mode exists for the enrichment orchestrator.
- `collect-plan` creates planned evidence files but does not run context tools.
- `PHASE7-IMPL-004` is the first planned collection target.
- CCE readiness was checked before collection.
- Exact CCE syntax is recorded in `scripts/roadmap_enrichment/tool_commands.md`.
- CCE readiness is now ready for explicit authorized collection.
- This does not mean CCE evidence has been collected.
- The first actual use of CCE should happen only in a future explicit collect step for `PHASE7-IMPL-004`.
- `cce init` remains prohibited.
- `PHASE7-IMPL-004` collection attempt 1 produced mixed evidence.
- Enrichment JSON and task record rendering are intentionally deferred.
- `.codex-context/PHASE7-IMPL-004/collection_repair_plan.md` controls the next evidence pass.
