# Task Backlog

This backlog is implementation-ready but not yet converted into GitHub Issues. Create issues only after the owner approves the plan structure.

## App MVP

| ID | Task | Output | Acceptance |
| --- | --- | --- | --- |
| App-0 | Plan/source-of-truth | Master plan and roadmap files | Docs exist and match verified repo state |
| App-1 | Architecture audit | Runtime audit report or issue set | Routes, storage, model path, and UI gaps captured |
| App-2 | Project file model | Local project schema | Project identity, bible, storyform, scenes, and owner memory separated |
| App-3 | NCP compatibility subset | MVP NCP subset | OS/MC/IC/RS fields validated without overclaiming |
| App-4 | Scene editor hardening | Reliable save/load UX | No scene data loss in normal local workflow |
| App-5 | Bible/storyform read/write layer | Backend APIs and UI | Candidate output cannot overwrite owner-approved truth |
| App-6 | Story Check rich schema parser | Parser/normalizer | Malformed model output becomes safe fallback |
| App-7 | Mock analysis mode | `ANALYSIS_MODE=mock` | Deterministic fixtures drive UI/tests |
| App-8 | Ollama baseline mode | `ANALYSIS_MODE=ollama_baseline` | Uses `qwen3:8b` via config |
| App-9 | Analysis parser/normalizer | Normalized response object | UI receives bounded structured data |
| App-10 | No-prose runtime guard | Input/output guardrails | Prose requests refuse with standard message |
| App-11 | Story Check sidebar UI | Rich diagnostic sidebar | Four throughlines, drift, consistency, warnings, and questions render clearly |
| App-12 | Evaluation fixtures | Fixture set | Valid, invalid, refusal, and insufficient-evidence cases covered |
| App-13 | Baseline evaluation harness | Baseline report | JSON validity, schema compliance, refusal violations counted |

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
