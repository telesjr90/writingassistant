# PHASE8-IMPL-023-T021B — Cross-Tool Fusion Real-Runtime Validation Rerun

Status: complete/PASS  
Parent: `PHASE8-IMPL-023-T021` — complete/PASS  
Active parent: `PHASE8-IMPL-023` — published/active

## Result

The corrected same-six real-runtime rerun passed. One authoritative `analyze_omi_raw_idea_with_tools` invocation used the controlled owner-authored source, exact adapter order (`spacy`, `ollama_model`, `story_check`, `ncp`, `subtxt_informed_rubric`, `dramatica_flow_informed_rubric`), `persist_candidates=False`, no fixtures or injected runners, and no deterministic fallback. Process-local runtime deltas included `OMI_LIVE_NCP_VALIDATE_WITH_NODE=1` and `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=600`.

All six mandatory contributors succeeded with non-empty results: spaCy 17, Ollama 5, Story Check 11, NCP 64, Subtxt-informed rubric 7, and dramatica-flow-informed rubric 9, for 113 findings total. The temporary NCP helper wrapper only counted and delegated; the real production helper ran exactly once and returned true. The authoritative call took 573.0 seconds.

## Fusion and replay

The committed T010 fusion contract preserved all 113 inputs as 113 outputs with evidence and provenance intact. It produced 113 unique deterministic normalized finding IDs, 113 candidate fingerprints, 101 evidence fingerprints, zero natural duplicate groups/findings, two conflict groups preserving nine claims without selecting truth, and 23 support-only uncertain findings. Candidate state remained pending/unapproved and candidate-review-pending throughout.

Forward-order and reverse-order in-memory re-fusion used the same authoritative findings without re-executing adapters. Fusion summaries, fingerprints, normalized IDs, duplicate links, related IDs, conflict group IDs, uncertainty labels, evidence, provenance, owner decisions, and review states were identical by normalized finding ID.

## Safety and persistence

`analysis_status` was `succeeded`. Persistence was not requested and `persisted_candidate_ids`, `new_candidate_ids`, and `reused_candidate_ids` were all empty. Every safety-envelope flag was true. Before/after project snapshots, protected-path snapshots, `.external_sources` status, selected NCP SHA-256/size/nanosecond mtime, HEAD, and branch were identical. The original blocked T021 evidence remained unchanged. No project, candidate, review, promotion, Memory, or Canon record was created or changed.

BookNLP was not executed because T021B was the exact same-six rerun; this does not negate its separate runtime evidence. No T009 Subtxt or dramatica-flow fixture ran, no live Subtxt ran, and no live dramatica-flow or `df` ran. No persistence, promotion/apply-promotion, generated story prose, implementation/test change, package installation/dependency mutation, or `.external_sources` mutation occurred.

## Evidence and validation

The 13 ignored, untracked evidence files are under `.codex-context/PHASE8-IMPL-023/manual-validation/T021B-cross-tool-fusion-real-runtime-rerun/`. The prior blocked evidence remains preserved under `.codex-context/PHASE8-IMPL-023/manual-validation/T021-cross-tool-fusion-real-runtime/`.

- Python byte-compilation of the orchestrator and focused NCP test: passed.
- Focused NCP Node-validation contract: 25 passed.
- Prescribed combined regression command: 270 passed, 1 environment-only Torch/NVML warning.
- Enrichment JSON parse, enrichment checker, roadmap validator, and diff checks: passed.

## Frontier

`PHASE8-IMPL-023-T021B` and `PHASE8-IMPL-023-T021` are complete/PASS. `PHASE8-IMPL-023` remains published/active and full MVP completion remains blocked. The next planned child is `PHASE8-IMPL-023-T022 — Candidate-only persistence validation using real runtime outputs`; T022 is not implemented here.

No staging, commit, or push was performed.
