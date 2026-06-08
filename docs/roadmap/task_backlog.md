# Task Backlog

This backlog is implementation-ready but not yet converted into GitHub Issues. Create issues only after the owner approves the plan structure.

## App MVP

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| App-0 | Repo baseline/source-of-truth sync | Master plan and roadmap files | DONE locally: Git initialized/repaired on `main`, safe metadata exists, local baseline commit `25ef64d` exists; TODO: push safe baseline to GitHub |
| App-1 | Architecture audit | `docs/roadmap/app_mvp_architecture_audit.md` | DONE; routes, storage, model path, UI gaps, tests, Story Check, NCP, and OMI readiness captured |
| App-2 | Project file model | `docs/roadmap/project_file_model.md` | DONE; project identity, bible, storyform, scenes, analysis artifacts, OMI candidates, provenance, and owner-approved truth boundaries separated |
| App-3 | NCP compatibility subset | `docs/roadmap/ncp_compatibility_subset.md` | DONE; supported NCP/storyform fields, OS/MC/IC/RS separation, owner-gated claims, and insufficient-evidence boundaries documented |
| App-3a | OMI MVP design schema | `docs/roadmap/omi_mvp_schema_lifecycle.md` | DONE; OMI idea/candidate schema, lifecycle, destinations, owner decisions, provenance, no-prose, and no-silent-promotion boundaries documented |
| App-3b | Owner-created sample project alignment spec | `docs/roadmap/sample_project_alignment_spec.md` | DONE; owner-created sample requirements, mismatch replacement strategy, Story Check/OMI fixture implications, provenance, and no-prose boundaries documented |
| App-3c | Sample fixture source correction and alignment | `projects/example/` local ignored fixture | DONE locally; public-domain scene source replaced the mismatched sample and prior owner-idea mix-up; `owner_sample_input.md` reserved for future OMI tests; MC/IC/RS/CIPS/dynamics remain unresolved |
| App-4 | Scene editor hardening | Reliable save/load UX | DONE; dirty state, save/load status, scene-switch confirmation, empty scene support, and route/storage tests are in place |
| App-5 | Bible/storyform read/write layer | Backend APIs and UI | DONE; raw bible/storyform JSON can be viewed, edited, validated, and saved only through explicit owner action, while candidate output remains separate |
| BE-002 | Story Check normalizer | `backend/analysis_normalizer.py`, `tests/test_analysis_normalizer.py` | DONE; malformed model output becomes safe fallback, minimal UI fields remain stable, rich fields are preserved, and schema errors are diagnostic only |
| SC-001 | Story Check rich prompt alignment | `backend/prompts/story_check.txt`, `tests/test_story_check_prompt.py` | DONE; prompt requests the rich schema, JSON-only output, no-prose boundaries, and insufficient-evidence handling without changing runtime routes |
| SC-002 | Minimal-to-rich Story Check compatibility | `tests/test_story_check_route.py`, sidebar inspection | DONE; minimal, rich, fallback, diagnostic, missing-rich-field, unknown-field, and error-shaped reports remain route-safe and current sidebar-compatible through minimal fields/raw JSON |
| BE-001 | Analysis mode config | `backend/analysis_modes.py`, `.env.example` | DONE; missing/empty `ANALYSIS_MODE` defaults to `ollama_baseline`, `mock` is explicit, and invalid modes return a stable error path |
| App-7 | Mock analysis mode | `ANALYSIS_MODE=mock`, `backend/mock_responses/story_check.json` | DONE; deterministic rich Story Check fixture drives UI/tests without Ollama and remains candidate-only |
| App-8 | Ollama baseline mode | `ANALYSIS_MODE=ollama_baseline`, `OLLAMA_BASE_URL` | VERIFIED locally; Windows Ollama/qwen3 reached from WSL and 2026-06-01 live smoke returned normalized schema-valid rich Story Check JSON |
| App-9 | Analysis parser/normalizer | Normalized response object | UI receives bounded structured data |
| GUARD-001 | Shared no-prose guard module | `backend/guardrails.py`, `tests/test_guardrails.py` | DONE; prose-generation request classifier, standard refusal response, allowed-help list, and Story Check suggestion filtering integration |
| GUARD-002 | Request-path no-prose guard integration | Route/service guard use | DONE; freeform request helper and field policy exist, current routes are audited, and tests verify owner-authored scene/bible/storyform content is not overblocked |
| GUARD-003 | Output no-prose guard integration | Model-output guard use | DONE; normalized Story Check output is sanitized after parsing to remove unsafe model-authored prose-generation content while preserving evidence spans |
| App-11 / FE-001 | Story Check sidebar UI | Rich diagnostic sidebar | DONE; normalized rich Story Check fields render as first-class candidate diagnostics with raw JSON kept in an advanced details view and frontend build validation passes |
| App-12 | Evaluation fixtures | Fixture set | DONE; app-level Story Check fixtures cover valid rich, minimal, malformed, refusal, insufficient-evidence, and unsafe-output guard cases without creating training data |
| App-13 | Baseline evaluation harness | Baseline report | DONE; offline fixture harness reports JSON validity, schema compliance, fallback/parser warnings, refusal exactness, insufficient evidence, output guard behavior, no-prose violations, and evidence preservation |
| OMI-001 | Define OMI MVP schema and lifecycle | `docs/roadmap/omi_mvp_schema_lifecycle.md` | DONE; fields include `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status` |
| OMI-002 | Design OMI storage model | `docs/roadmap/omi_storage_model.md` | DONE; OMI ideas, candidates, promotions, index, statuses, destinations, provenance, and promotion gates are specified without runtime files |
| OMI-003 | Implement OMI candidate creation flow | Candidate creation path | DONE; owner-authored raw ideas and structured candidate planning records can be created/listed/loaded under project-local `omi/` storage with no story prose, no model generation, and no promotion path |
| OMI-004 | Implement owner decision and destination selection | Decision/destination flow | DONE; owner can update idea/candidate decisions, status, approval confirmation, notes, and candidate destinations without promotion |
| OMI-005 | Prevent OMI candidate promotion without explicit owner approval | Promotion guard | DONE; approved candidates can create promotion audit records only after owner approval, final confirmation, allowed destination, provenance, source snapshot, and safe target labels are present, with no durable truth mutation |
| OMI-006 | OMI UI for raw idea, candidates, status, provenance, and destination | OMI UI | DONE; OMI panel shows raw ideas, candidates, selected candidate lifecycle details, owner decisions, destinations, timestamps, provenance, evidence, promotion readiness blockers, and promotion records without apply-promotion behavior |
| OMI-007 | OMI tests for no-prose and no-silent-promotion behavior | Test coverage | DONE; focused tests verify blocked prose destinations/types, owner-authored content remains candidate-only, promotion records do not apply durable truth mutation, promotion blockers fail closed, UI boundary copy remains present, no model path is called, and path traversal is blocked |
| MVP-EXIT | MVP completion test matrix | `docs/roadmap/mvp_exit_preflight_report.md` | ACTIVE NEXT; Step 1 refresh found no dirty tracked `projects/example` fixture files and automated checks passed; Step 2 passed mock backend server smoke, backend route smoke, mock Story Check route smoke, and frontend dev-server smoke after approved localhost execution. Final exit recording needs owner acceptance of fixture state and browser/manual checklist disposition |

## App MVP Phase Order

| Phase | Scope | Status |
| --- | --- | --- |
| Phase 0 | Repo baseline and source-of-truth sync | Git repair, safe metadata, and local baseline commit done; push and ongoing doc sync TODO |
| Phase 1 | App architecture audit and project model decisions | COMPLETE locally; App-1 architecture audit, App-2 project file model, App-3 NCP subset, App-3a/OMI-001, sample alignment spec, and public-domain sample fixture alignment done |
| Phase 2 | Backend safety and schema foundation | COMPLETE locally for Story Check MVP; GUARD-001, GUARD-002, GUARD-003, BE-001, BE-002, SC-001, and SC-002 done |
| Phase 3 | Mock and baseline Story Check | COMPLETE locally for Story Check MVP; App-7 mock mode, App-8 live qwen3 baseline verification, App-12 evaluation fixtures, and App-13 offline baseline harness done; remaining mock fixtures beyond Story Check are future work |
| Phase 4 | Frontend MVP diagnostics | COMPLETE locally; FE-001 rich Story Check diagnostics sidebar, App-4 scene editor hardening, App-5 bible/storyform context editing, and Story Check guard integration done |
| Phase 5 | OMI MVP implementation | COMPLETE locally; OMI-001 schema/lifecycle, OMI-002 storage model, OMI-003 raw idea/candidate creation, OMI-004 owner decision/destination selection, OMI-005 promotion gate records, OMI-006 status/provenance UI, and OMI-007 no-prose/no-silent-promotion tests are complete |
| Phase 6 | MVP hardening | ACTIVE NEXT; tracked fixture files are clean, automated checks pass, and Step 2 safe CLI/server smokes pass. Final exit recording needs owner acceptance of fixture state plus OWNER-MANUAL browser checklist disposition |

## Post-MVP / Future App Track

## Project Workspace Foundation

Near-term pre-Dramatica product foundation after owner acceptance of the Phase 6 MVP foundation. These tasks are future implementation tasks unless explicitly marked documentation-only. They make the app a usable writing-project workspace before Dramatica-specific analysis, fine-tuning, advanced extractor dependency work, graph/timeline visualization, relationship-network automation, RunPod work, or Books 4-5.

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| WORKSPACE-001 | Project Workspace Foundation plan/spec | `docs/roadmap/project_workspace_foundation_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines the first usable workspace target, creation flows, project library, pages, storage/model targets, safety rules, candidate/canon display rules, task sequence, and acceptance checklist without runtime code, tests, datasets, training records, model calls, package installs, project memory files, OMI records, staging, or commits |
| WORKSPACE-002 | Project creation flow | `docs/roadmap/project_creation_flow_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines blank and OMI-guided project creation principles, `project_id` strategy, `project.json` schema, hybrid folder strategy, scan-first project library support, API/UI planning, future tests, and safety boundaries without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-003 | Project selector/library | `docs/roadmap/project_selector_library_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines scan-first local project discovery, card/list metadata, sorting/filtering/search, opening/switching behavior, invalid/corrupt project handling, archive/delete planning, API/UI planning, path safety, and future tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-004 | OMI-guided project creation and idea capture | `docs/roadmap/omi_guided_project_creation_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines owner-authored setup inputs, setup candidate classes, wizard flow, staged setup storage recommendation, OMI-to-project handoff, API/UI planning, no-prose/no-silent-promotion rules, and future tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-005 | Chapter and scene data model | `docs/roadmap/chapter_scene_data_model_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines chapter records, scene Markdown compatibility, separate scene metadata, generated stable IDs, ordering/movement behavior, save/reload rules, API/UI planning, future extraction provenance, and safety tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-006 | Notes/materials data model | `docs/roadmap/notes_materials_data_model_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines note/material Markdown/text body storage, separate metadata, generated stable IDs, organization/linking, save/reload behavior, local search/filter, reference/license boundaries, API/UI planning, future extraction provenance, and safety tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-007 | User-authored document editor and save/reload workflow | `docs/roadmap/user_authored_document_editor_workflow_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines shared scene/note/material document types, editor state, save/reload behavior, unsaved-change protections, conflict detection, no-prose UI safety, analysis/extraction separation, API/UI planning, and future tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-008 | Project overview page | `docs/roadmap/project_overview_page_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines safe overview content, page sections, quick actions, recent documents, OMI status, approved memory/canon snapshot, health warnings, API/UI planning, and future tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-009 | Chapters/scenes page | `docs/roadmap/chapters_scenes_page_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines page layout, chapter and scene operations, shared editor behavior, ordering/consistency behavior, local search/filter, candidate-only analysis placeholder, API/UI planning, and future tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-010 | Notes/materials page | `docs/roadmap/notes_materials_page_spec.md` plus roadmap references and local report | DONE locally as documentation only when the spec is complete; defines page layout, note and material operations, shared editor behavior, organization/linking behavior, local search/filter, provenance/license warnings, candidate-only extraction placeholder, API/UI planning, and future tests without runtime code, tests, project files, OMI records, memory/canon files, model calls, packages, training, staging, or commits |
| WORKSPACE-011 | Project memory/canon page structure | Approved memory/canon UI shell | Pages distinguish approved memory/canon from OMI candidates, analysis artifacts, pending extraction, and rejected items |
| WORKSPACE-012 | Approved characters page | Characters memory page | Approved character records display only after explicit owner-controlled promotion |
| WORKSPACE-013 | Approved locations/settings page | Locations/settings memory page | Approved location/setting records display separately from pending candidates |
| WORKSPACE-014 | Approved timeline page | Timeline memory page | Approved timeline events display with source/evidence links and uncertainty where retained |
| WORKSPACE-015 | Approved plot threads page | Plot threads memory page | Approved plot-thread records display with related chapters/scenes and unresolved-question links |
| WORKSPACE-016 | Continuity/consistency page | Continuity page | Candidate and approved continuity/consistency issues are visibly separated; no rewrite/prose fixes are generated |
| WORKSPACE-017 | OMI ideas/candidates page | OMI workspace page | Owner can review project setup ideas and story-knowledge candidates with status, evidence, and provenance labels |
| WORKSPACE-018 | Candidate extraction trigger strategy | Trigger policy/spec | Decide manual, after-save, scheduled, or hybrid extraction behavior with no silent promotion and no automatic canon writes |
| WORKSPACE-019 | Owner approval workflow for extracted candidates | Approval workflow task | Owner can approve, reject, revise, archive, merge, split, mark uncertain, or request more evidence before promotion |
| WORKSPACE-020 | Tests for user-authored prose save without no-prose overblocking | Future test task | Saving owner-authored chapters/scenes/notes/materials is allowed and not treated as assistant request intent |
| WORKSPACE-021 | Tests for no AI prose generation | Future test task | No UI/API/model path writes, rewrites, continues, imitates, polishes, improves, or extends story prose |
| WORKSPACE-022 | Tests for no silent promotion | Future test task | Pending/rejected candidates and promotion records cannot become canon without explicit owner approval and future apply-promotion |
| WORKSPACE-023 | Project-local canon/memory visibility tests | Future test task | Approved project memory appears only in the selected project and pending/rejected candidates remain excluded from approved canon pages |

## Writer Assistant Core

Product direction after the Project Workspace Foundation is usable. These tasks are future implementation tasks, not completed runtime work unless explicitly marked documentation-only. All outputs must remain analysis-only, candidate-first, routed through OMI where extracted knowledge is involved, and blocked from writing or rewriting story prose.

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| CORE-001 | Product pivot documentation update | Master/roadmap pivot docs and local report | DONE locally when the prior Writer Assistant Core documentation package is complete; no runtime code, package install, JSONL, training, or Ollama call |
| CORE-002 | Story knowledge candidate schema design | `docs/roadmap/writer_assistant_core_candidate_schemas.md` | DONE locally as documentation; defines first candidate types, base contract, statuses, owner decision, promotion status, and candidate content fields |
| CORE-003 | Evidence span and provenance model | `docs/roadmap/writer_assistant_core_candidate_schemas.md` | DONE locally as documentation; defines minimum reusable evidence/provenance fields with offsets/line locators optional at first |
| CORE-004 | Project memory/canon storage model | `docs/roadmap/project_memory_canon_storage_model.md` | DONE locally as documentation; recommends folder-based `memory/*.json` plus `memory/index.json`; no runtime files or apply-promotion behavior implemented |
| CORE-005 | OMI candidate type expansion | `docs/roadmap/omi_story_knowledge_candidate_expansion.md` | DONE locally as documentation; defines typed OMI review behavior, lifecycle/status targets, owner actions, merge/dedup planning, UI needs, promotion readiness, and future tests without runtime implementation |
| CORE-006 | Extraction orchestrator and adapter contract | Candidate extraction architecture plan | Defines `backend/story_knowledge/` future shape, normalized CORE candidate schemas, evidence/provenance, OMI handoff, and replaceable adapters without creating runtime files |
| CORE-007 | Character/location/object extraction candidate pipeline | Candidate extraction plan/prototype | Extracts candidate entities only into OMI with evidence and uncertainty after workspace save/edit paths exist |
| CORE-008 | Timeline event extraction candidate pipeline | Timeline candidate plan/prototype | Extracts event/action candidates with locators; does not assert canon without owner approval |
| CORE-009 | Relationship extraction candidate pipeline | Relationship candidate plan/prototype | Extracts relationship candidates with uncertainty; does not imply Dramatica Relationship Story proof |
| CORE-010 | Plot thread, open-question, and navigation-summary candidate pipeline | Plot/open-question/summary candidate plan | Tracks plot threads, unresolved questions, and chapter/scene summaries as candidates/navigation aids only |
| CORE-011 | Annotation sidebar/review UI | Review UI plan/implementation | Shows evidence spans, candidate status, approve/reject/revise controls, and no-prose boundary labels |
| CORE-012 | Candidate-to-canon owner promotion flow | Owner-approved promotion flow | Promotes only after owner approval, destination, provenance/evidence, and final confirmation; never mutates scene prose |
| CORE-013 | Continuity and contradiction checks | Candidate warning flow | Produces continuity/contradiction candidates with evidence and uncertainty, not automatic truth |
| CORE-014 | Story knowledge search/query assistant | Query/search design | Helps inspect approved and candidate project knowledge without writing prose |
| CORE-015 | Extractor evaluation harness | Evaluation fixtures/report | Evaluates extractor candidates for precision, provenance, safety, evidence grounding, owner review, and no-prose behavior |
| CORE-016 | `spaCy` adapter spike evaluation | Spike report | Likely first future local NLP spike after workspace and contracts are ready; evaluate NER, POS, dependency parsing, sentence segmentation, lemmatization, entity linking, matchers, license, privacy/local-first behavior, evidence grounding, and OMI integration; do not install now |
| CORE-017 | `segram` semantic/action extraction spike | Spike report | Later semantic/action spike only after a basic spaCy-style adapter, review UI, and evidence model exist; do not install now |
| CORE-018 | `BookNLP` long-document/literary spike | Spike report | Later offline chapter/manuscript spike for characters, aliases, coreference, quote attribution, and events; do not install now |
| CORE-019 | `GLiNER` custom entity spike | Spike report | Later arbitrary-label NER spike for fictional locations, magical objects, artifacts, organizations, factions, species, and titles; do not install now |
| CORE-020 | Evidence/relationship/timeline reference spikes | Spike report | LangExtract-style grounding, Renard relationships, and CoreNLP/OpenIE/SUTime relation/timeline references evaluated only after evidence spans and review UI exist |
| CORE-021 | Graph/timeline visualization research | UI research report | Evaluates AI-Reader-V2-style maps/timelines/relationship graphs and narrative-blueprint batch/eval inspiration without adopting runtime dependencies |

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| EXT-001 | Optional analysis extractor research | `docs/roadmap/optional_analysis_extractors.md` | RECLASSIFIED under Writer Assistant Core; evaluate external tools as replaceable adapters around the app-owned pipeline, not as authorities or MVP blockers |
| EXT-002 | Extractor proof of concept | Offline candidate extraction fixture/report | FUTURE via CORE-006 to CORE-017; extractor output routes to OMI candidates only and never directly mutates project truth or training data |
| EXT-003 | Extractor integration tests | Extractor/OMI candidate tests | FUTURE via CORE-014; verifies no prose generation, provenance, owner review, guardrails, and no direct promotion |

## Packet/Dataset

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Data-1 | Finish packet 003-008 owner decision path | Owner decision application | Only owner-approved OS/MC labels advance |
| Data-2 | Process packets 009-020 through E/F/G/H/I | Candidate review reports | No direct promotion to training |
| Data-3 | Convert approved packets to review JSONL | Review candidates | PAUSED/BLOCKED; Book 1-3 mapping dry-run is complete, but P0 evidence extraction/verification is required before any JSONL drafting |
| Data-4 | Promote validated records | Promoted JSONL and manifest | BLOCKED; no review JSONL exists and no validation/promotion has run |
| Data-5 | Restore task mix | More throughline/refusal records | PAUSED; mapping dry-run would help throughline mix later, but evidence extraction and review JSONL drafting are not active now |
| Data-6 | Reach 500 gate | 500+ eligible records | BLOCKED; manifest remains at 149 eligible records and readiness is blocked |

## Book-Backed Review

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Book-1 | Cross-book coverage matrix | Matrix for Books 1-3 | DONE; Book 1-3 coverage matrix completed in `training/reports/book_1_3_cross_book_coverage_matrix.md` |
| Book-2 | Owner decision extraction worksheet | Owner-decision worksheet | DONE; extraction worksheet completed with 39 candidate rows across Books 1-3 |
| Book-3 | Books 4-5 decision | Owner decision | PAUSED; Books 4-5 remain conditional and should not start while fine-tuning/book-backed prep is paused |
| Book-4 | Books 6+ block review | Block retained or lifted | Default remains blocked for this phase |
| Book-5 | Implement Book 1-3 owner answers as prep artifacts | Local implementation report and mapping queue | DONE; owner answers are recorded in reports only, with no JSONL creation, promotion, manifest update, training, or Ollama call |
| Book-6 | Review JSONL mapping dry-run for Book 1-3 owner candidates | Candidate-to-review-record mapping plan | DONE; mapping dry-run completed with 51 positive structural mappings, 14 insufficient-evidence mappings, 1 refusal mapping, and 3 writer-question mappings, with no JSONL writes |
| Book-7 | P0 evidence extraction/verification for Book 1-3 mappings | Safe evidence locator checklist | PAUSED / NEXT WHEN FINE-TUNING RESUMES; required before any review JSONL drafting |

## External Dataset Research

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Ext-1 | Dataset registry | Registry with license/provenance/use fields | Allowed and disallowed task uses explicit |
| Ext-2 | Refusal/schema/routing candidates | Review-only conversion plan | No positive Dramatica truth imported |
| Ext-3 | Malformed repair/evidence calibration | Eval/review candidates | Human review status recorded |

## RunPod/Fine-Tuning

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Train-1 | RunPod environment check | Readiness report | FUTURE; not active while dataset gate is blocked and fine-tuning prep is paused |
| Train-2 | Smoke training | Smoke artifact only | BLOCKED/NOT NOW; `smoke_only_not_final_model: true`, never deployed |
| Train-3 | Full training gate | Gate report | BLOCKED; requires 500+ eligible records and ready manifest |
| Train-4 | Full QLoRA | Adapter/checkpoints | Non-smoke run completes |
| Train-5 | GGUF export | `q4_k_m`, `q8_0` | Artifacts labeled and copied back |
| Train-6 | Ollama import/eval | `dramatica-analyst:8b` candidate | Eval passes before app swap |

## Suggested Labels

`app`, `backend`, `frontend`, `storage`, `ncp`, `story-check`, `guardrails`, `dataset`, `book-backed`, `external-dataset`, `training`, `runpod`, `evaluation`, `deployment`, `docs`, `blocked`, `decision-needed`.
