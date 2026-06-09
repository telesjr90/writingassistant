# Open Questions

Owner decisions have answered the original roadmap questions. Remaining items below are implementation or verification follow-ups, not unresolved product decisions.

## Accepted Answers

| Original question | Accepted owner decision |
| --- | --- |
| Canonical product and repository name | Canonical repo: `telesjr90/writingassistant`. Product working name: Dramatica-Informed Writing Assistant. |
| License | MIT for app source code only. Training data, book sources, packet evidence, model artifacts, and datasets are excluded pending separate provenance/license review. |
| Git initialization/repair | Local Git is initialized/repaired on `main`; `origin` is `https://github.com/telesjr90/writingassistant`; first safe local baseline commit is `25ef64d chore: initialize safe project baseline`. Push safe local `main` to GitHub later, but do not push during App-3a. |
| Python dependency strategy | Use simple requirements files now. `backend/requirements.txt` exists and remains separate from `training/requirements-unsloth.txt`. Revisit `pyproject.toml`/`uv` later. |
| Node version | Target Node `>=22.12.0 <23`. Use both `.nvmrc` and `frontend/package.json` engines later; do not edit package metadata in this documentation task. |
| Example fixture identity | Replace the Elena/Ember Crown mismatch later with a small owner-created aligned sample for MVP. Public-domain material can be used later for broader evaluation. |
| Minimum OMI schema | OMI is in the App MVP as bounded analysis-only candidate planning. Design target fields are `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`. OMI may propose candidate storyform slots plus diagnostic questions, but candidate-only until owner approval. |
| Promotion action | Owner must explicitly approve, choose destination, attach evidence/provenance, and confirm promotion. |
| No-prose enforcement point | Enforce both before model call and after model output. Shared guard location is `backend/guardrails.py`; GUARD-001 has implemented the reusable module, GUARD-002 has implemented request-field policy for future freeform routes, and GUARD-003 has implemented post-normalization Story Check output sanitization. |
| Mock mode behavior | Story Check deterministic fixture JSON is implemented for `ANALYSIS_MODE=mock`; `throughline_classification`, `writer_questions`, `out_of_scope_refusal`, malformed JSON, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion fixtures remain future work. |
| UI throughline label | Use Overall Story in UI; accept Objective Story as an alias. |
| Unknown NCP fields | Hide unknown NCP fields in normal MVP UI; preserve them for advanced/raw context later. |
| Project identity | Keep filesystem-safe `project_id` separate from display title. |
| Owner memory | Include `owner_memory.json` as a design target; defer full runtime behavior until core Story Check and OMI basics. |
| Story Check artifact saving | Manual owner save only for MVP. |
| OMI location | Project-local for MVP; global idea inbox later. |
| Schema validation | Use `jsonschema` plus custom normalizer; schema validity is not story truth. BE-002 implements the reusable Story Check normalizer with schema diagnostics and safe fallback behavior. |
| Story Check prompt schema | SC-001 aligns `backend/prompts/story_check.txt` to the rich Story Check schema, JSON-only output, no-prose boundaries, and insufficient-evidence reporting. |
| Story Check compatibility | SC-002 verifies minimal, rich, fallback, diagnostic, missing-rich-field, unknown-field, and error-shaped Story Check reports through the current route and sidebar compatibility path. |
| GitHub Issues/Projects | Not yet; wait until Phase 1 and early Phase 2 task structure are approved. |
| Reference repo role | Prose-generation and autonomous-agent repos remain documentation-only. NCP may inform structure. |
| qwen25 cloud config | Revise/create cloud smoke config before RunPod smoke. |
| Books 4-5 need | Conditional only after cross-book coverage review. |
| Book folders in Git | Keep raw source text outside Git. Store only safe derived metadata/review artifacts in repo. |
| IC/RS threshold | Require owner-approved exact evidence per record. Target at least 15-20 strong IC and 15-20 strong RS examples, preferably 30+ each. |
| Book evidence approval format | Use a consolidated owner-review worksheet with candidate answer, excerpt IDs, evidence, weak/contradicting evidence, confidence, owner decision, and final training status. |
| Book 1-3 owner-answer inventory | Owner supplied final row decisions for Books 1-3. These have been implemented as local prep reports and a mapping queue only; positive, insufficient-evidence, needs-revision, and context-only rows remain separated. |
| Fine-tuning prep pause | Fine-tuning/book-backed prep is paused after the Book 1-3 review JSONL mapping dry-run. No JSONL records were created, no records were promoted, the manifest was not updated, and no training ran. |

## Remaining Verification / Setup Tasks

1. Push the safe local `main` branch to GitHub in a separate task.
2. Declare Node `>=22.12.0 <23` in package metadata in a later implementation task.
3. Optionally replace the public-domain sample fixture with an owner-created aligned project in a later task.
4. Extend OMI runtime beyond the OMI-003/OMI-004/OMI-005/OMI-006 raw idea/candidate/review/promotion-record/status-provenance slices only through separately approved tasks; apply-promotion behavior remains unimplemented.
5. Reuse shared `backend/guardrails.py` request and output guard helpers when future freeform/model routes are implemented without treating scene text as user request intent.
6. Extend runtime schema validation patterns beyond Story Check when new analysis routes are implemented.
7. Add broader route tests where useful without live Ollama.
8. Create remaining deterministic mock-mode fixtures beyond Story Check: `throughline_classification`, `writer_questions`, `out_of_scope_refusal`, malformed JSON, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion.
9. Continue frontend hardening after FE-001, App-4, and App-5; rich Story Check UI sections, scene editor dirty-state handling, and owner-controlled bible/storyform JSON editing are implemented.
10. Record owner acceptance/documentation of the current committed public-domain `projects/example` fixture state. Phase 6 Step 1 refresh found no dirty tracked fixture files; ignored local `projects/example/omi/` artifacts remain local-only.
11. Revise or create a RunPod cloud smoke config before smoke training in a future training task; this is not current while fine-tuning prep is paused.
12. Fine-tuning is paused pending P0 evidence extraction/verification before any Book 1-3 JSONL drafting.
13. Define the safe derived book metadata/review artifact set that may be committed while keeping raw source text outside Git.
14. Re-run the repo safety portion of the MVP completion test matrix after the dirty fixture files are resolved before declaring MVP exit; this is the next active project task.
15. Evaluate optional analysis extractors only after the Project Workspace Foundation and internal contracts are ready; external tools remain replaceable adapters whose outputs are candidate-only and routed through OMI.
16. Books 4-5 remain conditional and should not start while the fine-tuning/book-backed track is paused.
17. Decide whether to accept the Step 2 sandbox limitation for localhost backend/frontend server smokes or rerun those smokes in a local environment where socket binding is permitted.

## Project Workspace Foundation Follow-Up Questions

These must be answered before or during the pre-Dramatica workspace implementation:

WORKSPACE-001 planning defaults are documented in `docs/roadmap/project_workspace_foundation_spec.md`. WORKSPACE-002 project creation defaults are documented in `docs/roadmap/project_creation_flow_spec.md`, including the recommended title-derived owner-editable `project_id`, metadata-only `project.json`, hybrid folder strategy, scan-first library support, and OMI-guided setup boundaries. WORKSPACE-003 project selector/library defaults are documented in `docs/roadmap/project_selector_library_spec.md`, including scan-first discovery, invalid/corrupt warning states, lightweight metadata, local search/filter/sort, Project Overview opening, unsaved-change warnings on switch, future-only archive/delete, and rebuildable-only `projects/index.json`. WORKSPACE-004 OMI-guided setup defaults are documented in `docs/roadmap/omi_guided_project_creation_spec.md`, including owner-authored setup inputs, setup candidates, wizard flow, staged setup storage, project handoff, and no-prose/no-silent-promotion tests. WORKSPACE-005 chapter/scene defaults are documented in `docs/roadmap/chapter_scene_data_model_spec.md`, including chapter records, scene Markdown compatibility, scene metadata, generated stable IDs, `chapter.scene_ids` ordering, save/reload behavior, and future extraction provenance. WORKSPACE-006 notes/materials defaults are documented in `docs/roadmap/notes_materials_data_model_spec.md`, including Markdown/text body files, separate metadata, generated stable IDs, organization links, local search/filter, reference/license boundaries, save/reload behavior, and future extraction provenance. WORKSPACE-007 editor workflow defaults are documented in `docs/roadmap/user_authored_document_editor_workflow_spec.md`, including shared scene/note/material document types, editor state, body and metadata dirty tracking, save/reload semantics, unsaved-change protections, conflict detection planning, no-prose UI safety, and analysis/extraction separation. WORKSPACE-008 overview defaults are documented in `docs/roadmap/project_overview_page_spec.md`, including safe landing page content, quick actions, recent document metadata, OMI status, approved memory/canon snapshot, health warnings, API/UI planning, and candidate/canon labels. WORKSPACE-009 Chapters / Scenes page defaults are documented in `docs/roadmap/chapters_scenes_page_spec.md`, including page layout, chapter/scene operations, shared editor behavior, ordering consistency, local search/filter, candidate-only analysis placeholder, and API/UI planning. WORKSPACE-010 Notes / Materials page defaults are documented in `docs/roadmap/notes_materials_page_spec.md`, including page layout, note/material operations, shared editor behavior, organization/linking behavior, local search/filter, provenance/license warnings, candidate-only extraction placeholder, and API/UI planning. WORKSPACE-011 Project Memory / Canon page defaults are documented in `docs/roadmap/project_memory_canon_page_structure_spec.md`, including approved-only page structure, memory/canon concepts, approved-vs-candidate labels, category cards, promotion-record snapshots, empty states before apply-promotion, health warnings, API/UI planning, and apply-promotion boundaries. WORKSPACE-012 OMI Ideas / Candidates page defaults are documented in `docs/roadmap/omi_ideas_candidates_page_spec.md`, including owner raw ideas, candidates, owner review, destinations, evidence/provenance, promotion readiness, audit-only promotion records, local filters/search, warning states, API/UI planning, and page relationships. The questions below remain implementation decisions to confirm or refine during WORKSPACE-013 through WORKSPACE-023.

1. What is the minimum chapter/scene data model for the first usable workspace? WORKSPACE-005 recommends `chapters/{chapter_id}.json`, `scenes/{scene_id}.md`, and `scene_metadata/{scene_id}.json`, with scene prose kept as owner-authored Markdown.
2. Should chapters contain scenes, scenes reference chapters, or should both directions be stored with an index? WORKSPACE-005 recommends `chapter.scene_ids` as canonical first-version scene order and `scene_metadata.chapter_id` as a consistency aid; a rebuildable chapter index remains deferred.
3. What fields are required for notes/materials, and how should owner-authored notes differ from approved canon/memory? WORKSPACE-006 recommends Markdown/text body files plus separate metadata for note/material IDs, titles, types, status, tags, links, provenance, summaries, and reference/license fields; notes/materials remain owner-authored or owner-provided sources, not approved canon by default.
4. What is the minimum project creation form: title only, title plus project ID, title plus format/genre metadata, or OMI-guided setup?
5. How should OMI-created projects differ from blank projects in metadata, setup candidates, and review state?
6. Should candidate extraction run automatically after save, manually by owner action, scheduled in batches, or through a hybrid trigger strategy?
7. What counts as approved project canon for the first usable version? WORKSPACE-011 defines applied memory/canon records as approved truth only after owner approval, promotion record creation, and successful future apply-promotion; source material, candidates, approved-but-not-applied candidates, and promotion records are not durable canon by themselves.
8. Which project memory files/pages are required first: overview, canon index, characters, locations/settings, timeline, plot threads, continuity/consistency, OMI ideas/candidates, or all of them? WORKSPACE-008 recommends a Project Overview approved memory/canon placeholder or approved-count snapshot first, and WORKSPACE-011 recommends a Project Memory / Canon shell with category cards, approved-only empty states, candidate/canon labels, and promotion-record snapshots before detailed category pages are implemented.
9. How should contradictions be shown to the user: inline flags, side-by-side evidence, page-level list, OMI candidate queue, or a combination?
10. How should continuity flags be distinguished from Dramatica structural issues?
11. Should project memory be stored in one canon file, separated by category, or category files plus a derived index?
12. How should chapter/scene summaries be labeled so they remain navigation aids and candidate analysis, not rewritten prose? WORKSPACE-005 recommends `summary_candidate_id` for pending OMI candidates and `approved_navigation_summary` only for owner-authored or owner-approved navigation aids.
13. What extraction confidence or evidence threshold is required before a candidate appears in the UI?
14. What is the first browser/manual acceptance checklist for a usable workspace? WORKSPACE-009 identifies the Chapters / Scenes page checks for create/select/save/reload/reorder/move, unsaved-change warnings, corrupt metadata handling, no model calls, and no AI prose-generation controls. WORKSPACE-010 identifies the Notes / Materials page checks for create/select/save/reload/tag/search/filter, provenance/license warnings, broken-link warnings, missing-body versus empty-body handling, no model calls, no extraction during search, and no AI prose-generation controls.
15. How should owner-authored prose save tests prove the no-prose guard is not overblocking while AI prose generation stays blocked? WORKSPACE-007 recommends testing scene, note, and material body saves as owner-authored storage fields that bypass freeform assistant-request guards, while UI/API/model paths still block write/continue/rewrite/polish/improve/imitate controls and outputs.
16. Should `project_id` collision suffixes be generated server-side, client-side, or both?
17. Should OMI-guided project setup use temporary wizard state, browser-local draft state, or a durable pre-project inbox before a `project_id` exists? WORKSPACE-004 recommends staged setup state first, with durable pre-project inbox deferred.
18. Should blank project creation immediately create `omi/index.json`, or should OMI folders remain lazy until the first idea/candidate is created?
19. Should new blank workspace projects create compatibility `bible.json` and `storyform.json`, or defer them until Story Check or later Dramatica context is explicitly enabled?
20. Should project title rename ever migrate `project_id`, or should `project_id` remain stable after creation?
21. Should invalid project folders be hidden by default, shown in a warning section, or shown in a recovery tab?
22. Should the first Project Library UI use project cards, a table, or both?
23. Should unsaved project-specific editor state be preserved per project, or should project switching require explicit save/discard? WORKSPACE-007 recommends explicit Save/Discard/Cancel before project switch for the first implementation unless per-project draft preservation is deliberately implemented later.
24. When should archive support be added relative to the selector implementation, and should permanent delete remain absent until a separate owner-approved task?

## Writer Assistant Core Follow-Up Questions

These are implementation follow-ups after the Project Workspace Foundation, not blockers for the completed MVP foundation:

1. Project memory/canon file structure: CORE-004 recommends folder-based `memory/*.json` plus `memory/index.json` as the first implementation target; runtime implementation details remain future work.
2. Which subset of the CORE-002 candidate types should be implemented first: characters, aliases, locations, objects, organizations, timeline events, relationships, plot threads, open questions, continuity warnings, annotations, or a smaller subset?
3. Should the first runtime evidence-span locator use character offsets, line ranges, paragraph indices, source hashes, or a hybrid? CORE-003 defines all as optional-capable planning fields.
4. Should annotations be stored per scene, per entity, globally, or in an OMI-linked annotation store?
5. Should the first extractor be deterministic/rule-based, `spaCy`-adapter-assisted, LLM-assisted, or hybrid?
6. What UI should approve, reject, revise, merge, split, mark duplicate/uncertain, request more evidence, and annotate candidate story knowledge? CORE-005 documents the future action set, but not implementation.
7. What qualifies a relationship, timeline event, or plot-thread item for promotion to canon?
8. When should Dramatica analysis return as an advanced layer after Writer Assistant Core is stable?
9. Which adapter spike should be first once workspace storage, schemas, OMI candidate flow, and evidence contracts are ready?
10. How should runtime typed validation handle scene-derived candidates with `idea_id: null` and source-scene/source-reference locators?

## Book 1-3 Owner-Answer Status

Resolved by owner inventory and implemented locally:

- Book 1 parent rows and split/local candidates have final owner decisions recorded.
- Book 2 parent rows and split candidates have final owner decisions recorded, with B2-010a Optionlock replacing the contradicted Timelock parent.
- Book 3 parent/review rows and split candidates have final owner decisions recorded, with Book 3 RS validity retained as insufficient evidence.

Still unresolved or blocked for direct conversion:

- Parent rows marked `needs_revision` remain blocked from direct conversion.
- Context-only master packet rows remain do-not-convert.
- Insufficient-evidence rows remain negative calibration only.
- P0 evidence extraction/verification remains required before any JSONL draft.
- Later review JSONL conversion, promotion, manifest update, and training remain pending and paused.
- App MVP Phase 6 / MVP exit matrix preflight is the next active project task.

## Owner Questions

No additional owner decisions are required for the completed App MVP slices. The current owner decision needed for local MVP readiness is whether to accept/document the current committed public-domain `projects/example` fixture state and leave ignored local `projects/example/omi/` artifacts as local-only state. The current product-direction decision has shifted: after Phase 6 owner acceptance, the next roadmap priority is Project Workspace Foundation, then Writer Assistant Core, while Dramatica, Books 4-5, and fine-tuning remain deferred.

Phase 6 Step 2 adds one MVP exit decision: true backend/frontend dev-server smokes are blocked by this sandbox's socket/listen restrictions, while in-process mock route smoke passed. The owner can either accept this as an environment limitation for documentation purposes or request a rerun in a socket-enabled local environment.

Resolved sample/source roles:

1. `project_id`: `example`, kept for MVP compatibility with the current hard-coded frontend project ID.
2. Display title: `The Princess and the Pea`, from `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt`.
3. First scene text: copied verbatim from `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt` into the local ignored fixture.
4. `/mnt/e/WritingAssistantApplication/docs/owner_sample_input.md`: reserved for future OMI raw idea/candidate-planning tests only, not Story Check fixture prose or project truth.
5. MC, IC, RS, CIPS, and dynamics evidence: not asserted for the public-domain fixture, so these remain unresolved for insufficient-evidence behavior.
6. Commit status: tracked project fixture files are clean in `HEAD` as of the Phase 6 Step 1 refresh; no revert is needed unless the owner rejects the committed fixture state.
