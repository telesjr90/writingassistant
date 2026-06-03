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
| OMI-003 | Implement OMI candidate creation flow | Candidate creation path | TODO; raw ideas can produce/display structured candidate planning material only, with no story prose |
| OMI-004 | Implement owner decision and destination selection | Decision/destination flow | TODO; owner explicitly chooses approval/rejection and destination |
| OMI-005 | Prevent OMI candidate promotion without explicit owner approval | Promotion guard | TODO; no OMI output mutates durable truth without approval, destination, provenance, and status |
| OMI-006 | OMI UI for raw idea, candidates, status, provenance, and destination | OMI UI | TODO; candidate status and provenance labels are visible |
| OMI-007 | OMI tests for no-prose and no-silent-promotion behavior | Test coverage | TODO; verifies OMI cannot generate story prose or silently promote candidates |

## App MVP Phase Order

| Phase | Scope | Status |
| --- | --- | --- |
| Phase 0 | Repo baseline and source-of-truth sync | Git repair, safe metadata, and local baseline commit done; push and ongoing doc sync TODO |
| Phase 1 | App architecture audit and project model decisions | COMPLETE locally; App-1 architecture audit, App-2 project file model, App-3 NCP subset, App-3a/OMI-001, sample alignment spec, and public-domain sample fixture alignment done |
| Phase 2 | Backend safety and schema foundation | COMPLETE locally for Story Check MVP; GUARD-001, GUARD-002, GUARD-003, BE-001, BE-002, SC-001, and SC-002 done |
| Phase 3 | Mock and baseline Story Check | COMPLETE locally for Story Check MVP; App-7 mock mode, App-8 live qwen3 baseline verification, App-12 evaluation fixtures, and App-13 offline baseline harness done; remaining mock fixtures beyond Story Check are future work |
| Phase 4 | Frontend MVP diagnostics | IN PROGRESS; FE-001 rich Story Check diagnostics sidebar, App-4 scene editor hardening, App-5 bible/storyform context editing, and Story Check guard integration done; remaining App MVP OMI hardening remains TODO |
| Phase 5 | OMI MVP implementation | IN PROGRESS; OMI-001 schema/lifecycle and OMI-002 storage model are complete, while runtime candidate creation, owner decision UI, promotion guard, OMI UI, and tests remain TODO |
| Phase 6 | MVP hardening | TODO |

## Packet/Dataset

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Data-1 | Finish packet 003-008 owner decision path | Owner decision application | Only owner-approved OS/MC labels advance |
| Data-2 | Process packets 009-020 through E/F/G/H/I | Candidate review reports | No direct promotion to training |
| Data-3 | Convert approved packets to review JSONL | Review candidates | Validation passes, candidates remain review status |
| Data-4 | Promote validated records | Promoted JSONL and manifest | No draft, blocked, eval-only, unresolved-source, or license-unreviewed records in train |
| Data-5 | Restore task mix | More throughline/refusal records | Manifest moves toward 40-45/25-30/20-25/5-10 mix |
| Data-6 | Reach 500 gate | 500+ eligible records | Manifest readiness is ready |

## Book-Backed Review

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Book-1 | Cross-book coverage matrix | Matrix for Books 1-3 | IC, RS, MC/IC contrast, dynamics, CIPS, throughline, insufficient-evidence coverage counted |
| Book-2 | Evidence triage | Excerpt-backed candidate list | Only owner-approved excerpt-backed evidence can feed SFT review candidates |
| Book-3 | Books 4-5 decision | Owner decision | Proceed only if cross-book review shows coverage gaps |
| Book-4 | Books 6+ block review | Block retained or lifted | Default remains blocked for this phase |

## External Dataset Research

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Ext-1 | Dataset registry | Registry with license/provenance/use fields | Allowed and disallowed task uses explicit |
| Ext-2 | Refusal/schema/routing candidates | Review-only conversion plan | No positive Dramatica truth imported |
| Ext-3 | Malformed repair/evidence calibration | Eval/review candidates | Human review status recorded |

## RunPod/Fine-Tuning

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| Train-1 | RunPod environment check | Readiness report | GPU, CUDA, Unsloth, model cache verified |
| Train-2 | Smoke training | Smoke artifact only | `smoke_only_not_final_model: true`, never deployed |
| Train-3 | Full training gate | Gate report | 500+ eligible records and ready manifest |
| Train-4 | Full QLoRA | Adapter/checkpoints | Non-smoke run completes |
| Train-5 | GGUF export | `q4_k_m`, `q8_0` | Artifacts labeled and copied back |
| Train-6 | Ollama import/eval | `dramatica-analyst:8b` candidate | Eval passes before app swap |

## Suggested Labels

`app`, `backend`, `frontend`, `storage`, `ncp`, `story-check`, `guardrails`, `dataset`, `book-backed`, `external-dataset`, `training`, `runpod`, `evaluation`, `deployment`, `docs`, `blocked`, `decision-needed`.
