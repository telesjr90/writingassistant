# PHASE8-IMPL-001 Context Collection Plan

## 1. Task Identity

| Field | Value |
| --- | --- |
| Parent | `PHASE8-IMPL-001` — Writer Assistant Core implementation readiness and first runtime slice plan |
| Child | `PHASE8-IMPL-001-T002` — Context collection plan for Writer Assistant Core |
| Purpose | Context collection planning only; no tool execution in T002 |
| Execution deferred to | `PHASE8-IMPL-001-T003` — Targeted context collection and source inventory |
| Status | Complete when this plan and roadmap validators pass |

T002 defines what T003 must collect and how. T002 does not run context tools, create context reports, or inspect runtime source beyond what is listed here as future T003 targets.

## 2. Context Collection Goal

Context collection is required to choose the first safe Writer Assistant Core runtime slice in `PHASE8-IMPL-001-T004`.

The plan must support future work around:

- **Candidate schema alignment** — map `docs/roadmap/writer_assistant_core_candidate_schemas.md` types and base contract fields to current OMI and storage surfaces.
- **OMI candidate-first lifecycle** — confirm how ideas, candidates, promotions, and index records are stored, reviewed, and blocked from silent promotion.
- **Source/evidence/provenance boundaries** — identify required locator, evidence span, and provenance fields before any future promotion or extraction slice.
- **Project-local storage** — inventory safe path/ID helpers and project folder layout for future story-knowledge candidate storage.
- **Guardrails/no-prose boundaries** — locate enforcement points and routes that must not scan owner-authored text as assistant requests.
- **First runtime slice selection** — compare smallest-safe slice options without choosing the final slice in T002.
- **Tests/contract coverage** — identify existing OMI, guardrail, path-safety, and workspace tests to extend first.

Context output from T003 is evidence for T004 decision-making, not roadmap truth. Roadmap truth remains `roadmap_index.yaml`, `implementation_status.md`, task records, enrichment JSON, and validation docs.

## 3. Questions to Answer in T003

### A. Current OMI Runtime Surface

1. What OMI routes currently exist in `backend/main.py`?
2. What OMI helpers currently exist in `backend/project_manager.py` (or related modules)?
3. How are ideas, candidates, promotions, and index records stored under `projects/{project_id}/omi/`?
4. Which fields are already required for owner decision, destination, provenance, and promotion records?
5. Where is apply-promotion absent or explicitly deferred in code and specs?
6. Which tests protect no-silent-promotion behavior (`tests/test_omi_boundaries.py`, `tests/test_omi_routes.py`)?

### B. Current Project Storage Surface

1. Where are project metadata, scenes, notes, materials, bible, storyform, and OMI records stored?
2. What safe ID/path helpers exist in `backend/project_manager.py`?
3. Which helpers are reusable for future story-knowledge candidate storage (read/list/write with path safety)?
4. Which helpers must not be reused because they imply canon/memory mutation or approved-truth writes?

### C. Current Frontend Surfaces

1. Which components display project workspace navigation (`ProjectNav.jsx`, `App.jsx`)?
2. Which components display OMI candidates and promotion-readiness records (`OMIPanel.jsx`)?
3. Which components display Memory / Canon empty states (`MemoryCanonShell.jsx`)?
4. Where would future candidate extraction review UI fit without adding extraction in this readiness parent?
5. Which UI surfaces must remain read-only or candidate-only (Memory / Canon shell, OMI panel, Overview)?

### D. Candidate Schema/Spec Alignment

1. What candidate types are specified in `writer_assistant_core_candidate_schemas.md`?
   - `character_candidate`, `location_candidate`, `object_candidate`, `organization_candidate`, `timeline_event_candidate`, `relationship_candidate`, `plot_thread_candidate`, `navigation_summary_candidate`, `continuity_warning_candidate`, `contradiction_candidate`, `annotation_candidate`, `open_question_candidate`
2. Which candidate types overlap with existing Memory / Canon shell categories (characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, objects/items, annotations/evidence/provenance, contradictions, scene/event/causality)?
3. Which fields are required for source locators, evidence spans, provenance, owner decisions, status, and destination per the base contract?
4. Which schema decisions are still open or risky per spec section 11 (Deferred Decisions)?

### E. Evidence/Provenance Model

1. What evidence/provenance requirements exist in OMI specs (`omi_mvp_schema_lifecycle.md`, `omi_storage_model.md`, `omi_story_knowledge_candidate_expansion.md`) and memory/canon specs (`project_memory_canon_storage_model.md`)?
2. Which source locator forms are documented (scene ID, note/material ID, bible/storyform reference, offset/line locators)?
3. Which fields are required before any future promotion (evidence array, provenance object, owner_decision, promotion_status, proposed_destination)?
4. What should the first runtime slice collect or validate without becoming extraction/model work?

### F. Guardrails/No-Prose Boundary

1. Which backend files enforce no-prose boundaries (`backend/guardrails.py`, `backend/analysis_engine.py`, `backend/analysis_normalizer.py`)?
2. Which routes currently avoid scanning owner-authored scene/note/material text as assistant requests?
3. Which future route types would need `guard_freeform_request` before model calls?
4. What forbidden behaviors must be tested before any runtime extraction slice (prose generation, silent promotion, canon mutation, summary-as-truth)?

### G. Existing Tests

1. Which tests protect OMI lifecycle and no-silent-promotion (`test_omi_boundaries.py`, `test_omi_routes.py`)?
2. Which tests protect project manager path safety (`test_project_manager.py`)?
3. Which tests protect frontend workspace boundaries (`test_frontend_project_workspace_source.py`)?
4. Which tests should be extended first for Writer Assistant Core (schema constants, evidence validation, candidate storage contract)?

### H. First Runtime Slice Candidates

Evaluate each option without choosing the final slice in T002:

| Option | Benefits | Risks | Smallest-safe assessment |
| --- | --- | --- | --- |
| Schema/source-level tests only | Zero runtime mutation; locks contract before code | May lag if runtime helpers needed first | Strong candidate; validates spec alignment cheaply |
| Backend candidate schema constants only | Establishes bounded types without storage/routes | Constants without tests may drift from specs | Good if paired with tests in T005 |
| Project-local candidate storage helper skeleton | Reuses path-safety patterns; prepares OMI handoff | Risk of implying memory/canon writes if mis-scoped | Viable only if strictly candidate-only paths |
| Route contract tests before route implementation | Documents API shape early | May over-specify before storage decision | Good companion to schema tests |
| Frontend read-only candidate backlog placeholder | Surfaces candidate/canon separation in UI | UI work may precede backend contract | Higher risk; likely not smallest first |
| Evidence/provenance validation helper | Enforces promotion gates early | May duplicate OMI validation; scope creep toward extraction | Viable as pure validation module without extraction |

T003 must record findings for each option. T004 chooses one.

## 4. Files to Inspect in T003

### Required source/spec docs

| File | Purpose |
| --- | --- |
| `docs/roadmap/writer_assistant_core_candidate_schemas.md` | Candidate types, base contract, evidence/provenance |
| `docs/roadmap/omi_story_knowledge_candidate_expansion.md` | OMI typed review, lifecycle, promotion readiness |
| `docs/roadmap/omi_mvp_schema_lifecycle.md` | OMI idea/candidate lifecycle, owner decisions |
| `docs/roadmap/omi_storage_model.md` | OMI storage layout, index, promotions |
| `docs/roadmap/project_memory_canon_storage_model.md` | Approved memory storage model (future-only) |
| `docs/roadmap/project_memory_canon_page_structure_spec.md` | Memory / Canon page structure |
| `docs/roadmap/project_memory_canon_cross_linking_health_spec.md` | Cross-linking and health warnings |
| `docs/roadmap/approved_characters_page_spec.md` | Characters category |
| `docs/roadmap/approved_locations_settings_page_spec.md` | Locations/settings category |
| `docs/roadmap/approved_timeline_page_spec.md` | Timeline category |
| `docs/roadmap/approved_plot_threads_page_spec.md` | Plot threads category |
| `docs/roadmap/continuity_consistency_page_spec.md` | Continuity/consistency category |
| `docs/roadmap/approved_open_questions_page_spec.md` | Open questions category |
| `docs/roadmap/approved_relationships_page_spec.md` | Relationships category |
| `docs/roadmap/approved_organizations_groups_page_spec.md` | Organizations/groups category |
| `docs/roadmap/approved_objects_items_page_spec.md` | Objects/items category |
| `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md` | Annotations/evidence/provenance category |
| `docs/roadmap/approved_contradictions_page_spec.md` | Contradictions category |
| `docs/roadmap/approved_scene_event_causality_review_spec.md` | Scene/event/causality review category |
| `docs/roadmap/project_workspace_implementation_decision_sweep.md` | Phase 7 implementation decisions and boundaries |

### Required runtime source files

| File | Purpose |
| --- | --- |
| `backend/main.py` | Route inventory, OMI endpoints, guard usage |
| `backend/project_manager.py` | Storage helpers, path safety, OMI I/O |
| `backend/guardrails.py` | No-prose guard module |
| `backend/analysis_engine.py` | Story Check path, model call boundary |
| `backend/analysis_normalizer.py` | Output normalization and sanitization |
| `frontend/src/App.jsx` | Workspace view routing, OMI/Memory integration |
| `frontend/src/api.js` | API helpers for project/OMI/workspace |
| `frontend/src/components/OMIPanel.jsx` | OMI candidate/promotion UI |
| `frontend/src/components/MemoryCanonShell.jsx` | Memory / Canon empty states |
| `frontend/src/components/ProjectOverview.jsx` | Overview shell |
| `frontend/src/components/ProjectNav.jsx` | Workspace navigation |
| `frontend/src/components/Editor.jsx` | Owner-authored document editor |
| `frontend/src/sharedDocumentController.js` | Shared document state contract |

### Required test files

| File | Purpose |
| --- | --- |
| `tests/test_omi_boundaries.py` | OMI no-prose and no-silent-promotion |
| `tests/test_omi_routes.py` | OMI route contracts |
| `tests/test_project_manager.py` | Path safety and storage helpers |
| `tests/test_frontend_project_workspace_source.py` | Frontend workspace boundaries |
| `tests/test_note_material_routes.py` | Note/material route contracts |
| `tests/test_scene_routes.py` | Scene route contracts |
| `tests/test_guardrails.py` | Guardrail module behavior |
| `tests/test_story_check_route.py` | Story Check route and guard integration |

T003 must not inspect files outside this list unless a direct dependency is discovered during inspection and the deviation is recorded in the T003 report.

## 5. Allowed Context Tools for T003

Policy definition only. T002 does not run tools.

### Allowed in T003 only if explicitly authorized by the T003 task prompt

| Tool / method | Allowed when |
| --- | --- |
| Direct file/source inspection | Always; primary method |
| CCE | Available and scoped to Writer Assistant Core / OMI / project storage / guardrails / tests |
| Repomix | Limited to explicit file allowlists from section 4 |
| Graphify | Scoped to source relationships for OMI, project_manager, frontend workspace files |
| AI Context generation | Scoped to exact T003 questions and target files |

### Forbidden in T003 unless a later owner decision authorizes

- Broad repo dumps
- Package/dependency installs
- Runtime server execution
- Browser/manual validation
- Model/Ollama calls
- Training/JSONL/dataset operations
- Code generation
- Runtime feature implementation
- Apply-promotion implementation
- Memory/canon mutation
- Extraction implementation
- LeanCTX (unless a future task explicitly authorizes it)
- MCP tools (unless a future task explicitly authorizes them)

### Out of scope for all T003 collection

- `projects/` runtime artifacts (except path patterns documented in specs)
- `training/` data, JSONL, dataset manifests
- Book source files
- Model artifacts
- Package/dependency files

## 6. Tool-by-Tool Collection Plan for T003

| Tool / method | Purpose | Exact scope | Inputs | Expected output | Acceptance criteria | Stop conditions | Forbidden outputs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Direct source inspection | Primary evidence collection | Section 4 runtime and test files only | T003 question list | Per-file notes: routes, helpers, fields, boundaries | Each question A–H has file-backed evidence or explicit "not found" | File missing or unreadable; record and continue | Generated prose, implementation recommendations beyond slice inventory |
| Docs/spec inspection | Schema and boundary alignment | Section 4 spec docs only | T003 question list D–E | Candidate type list, required fields, open decisions | All 12 candidate types mapped; evidence/provenance fields listed | Spec conflict unresolvable without owner input | Treating spec as implemented runtime |
| Test inspection | Coverage inventory | Section 4 test files only | T003 question list G | Test class/function inventory per boundary | OMI, guardrail, path-safety, workspace tests cataloged | Test file structure unreadable | New test code |
| Optional CCE | Compressed navigation if available | OMI, project_manager, guardrails, main routes, listed tests | File allowlist from section 4 | Scoped symbol/route summary | Output fits review; no training/project runtime paths | Output too broad; includes forbidden paths | Canon mutation paths, extraction implementation plans |
| Optional Repomix | Packaged allowlist context | Explicit paths from section 4 only | `--include` allowlist matching section 4 | XML/text pack of allowlisted files | Pack size reviewable in one session | Pack includes repo-wide dump or forbidden paths | Full-repo Repomix |
| Optional Graphify | Relationship map for scoped files | `backend/main.py`, `project_manager.py`, `guardrails.py`, OMI frontend components | `graphify query` scoped to listed symbols/paths | Subgraph of OMI/storage/guardrail relationships | Relationships aid T003 inventory only | Graph too large or includes unrelated communities | Implementation sequencing beyond T004 handoff |
| Optional AI Context generation | Summarized evidence pack | T003 questions + section 4 allowlist | `scripts/generate_ai_context.sh` with explicit scope | Context pack under `.codex-context/PHASE8-IMPL-001/` | Pack labeled as evidence not truth; matches allowlist | Pack includes training/book/runtime project data | Roadmap truth claims, prose examples, slice choice |

## 7. Evidence Output Format for T003

T003 must produce:

`docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md`

### Required report sections

1. **Context questions answered** — map each question in section 3 to evidence or explicit gap.
2. **Files inspected** — complete list with inspection status.
3. **Tools used** — which methods ran; which were skipped and why.
4. **OMI runtime inventory** — routes, helpers, storage paths, required fields, apply-promotion absence.
5. **Project storage inventory** — layout, safe helpers, reusable vs forbidden helpers.
6. **Frontend workspace inventory** — navigation, OMI, Memory / Canon, future review UI fit.
7. **Candidate schema alignment findings** — type overlap, required fields, open decisions.
8. **Evidence/provenance findings** — locator forms, promotion prerequisites, first-slice validation scope.
9. **Guardrail/no-prose findings** — enforcement files, route audit, future guard needs.
10. **Test coverage findings** — existing tests and recommended first extensions.
11. **First runtime slice candidates** — benefits/risks table populated from inspection.
12. **Recommended first runtime slice for T004 decision** — evidence-based recommendation, not final choice.
13. **Risks/open questions** — blockers for T004.
14. **Boundary confirmation** — no extraction, no model calls, no apply-promotion, no canon mutation during T003.

Report content is evidence for T004. It does not replace roadmap status files.

## 8. Stop Conditions for T003

T003 must stop and report **PARTIAL** if:

- Context tool output is too broad to review safely.
- Context tools attempt to include training/book/source data.
- Context tools attempt to include project runtime artifacts under `projects/`.
- Context tools recommend generated prose.
- Context tools recommend apply-promotion or canon mutation as first slice.
- Context tools require package installs.
- Context tools require model/Ollama calls.
- Source/docs conflict on the first runtime slice boundary without resolvable evidence.
- Evidence/provenance requirements are unclear enough to block first-slice selection.

When PARTIAL, T003 must record what was collected, what blocked completion, and what T004 may still decide with partial evidence.

## 9. T004 Handoff Criteria

T004 may choose the first runtime slice only after T003 has answered:

| Prerequisite | Evidence required |
| --- | --- |
| Current OMI candidate storage supports | Storage paths, record shapes, index behavior |
| Current storage helpers can safely reuse | List of safe path/ID/read/write helpers |
| Candidate schema fields are required | Base contract + per-type fields from spec vs runtime gap |
| Evidence/provenance fields are required | Minimum fields before promotion; validation-only scope |
| Guardrails must be preserved | Files, routes, and tests enforcing no-prose/no-promotion |
| Tests should be extended first | Prioritized test files and contract areas |
| First slice category | Whether tests-only, schema-only, storage-only, route-only, or UI-placeholder-only |

T004 does not run context tools unless a gap requires a narrowly scoped T003 follow-up authorized by the owner.

## 10. Explicit Exclusions

T002 does **not**:

- Run context tools (CCE, Graphify, Repomix, AI Context, LeanCTX, MCP).
- Create context reports (`PHASE8-IMPL-001-targeted-context-report.md` is T003 output).
- Inspect broad repo context beyond the T003 target lists in section 4.
- Implement runtime code.
- Write tests.
- Add extraction.
- Add model calls.
- Add frontend extraction UI.
- Add backend extraction routes.
- Add apply-promotion.
- Add memory/canon mutation.
- Add generated prose behavior.
- Add summaries as canon/truth.
- Add training/JSONL/dataset artifacts.

Standard refusal message when prose generation is requested:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`
