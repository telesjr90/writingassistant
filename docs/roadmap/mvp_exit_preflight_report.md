# MVP Exit Preflight Report

## Purpose

Record the Phase 6 MVP completion matrix execution for the local Dramatica-informed writing assistant. This report is documentation-only. It does not implement features, apply OMI promotions, create training data, call live Ollama, or change runtime behavior.

## Date / Run Context

- Date: 2026-06-05
- Working directory: `/home/tjrpirateking/projects/WritingAssistantApplication`
- Branch: `main`
- Latest commit at start: `ee27f76 test: add omi boundary coverage`
- Remote: `origin https://github.com/telesjr90/writingassistant`
- Live qwen3 smoke: deferred because `RUN_LIVE_OLLAMA_MVP_EXIT` was not set.

## Git Status And Latest Commits

Repo safety did not pass cleanly. Before this preflight report was created, tracked project fixture files were already dirty:

- `projects/example/bible.json`
- `projects/example/scenes/scene_001.md`

Those files were not modified by this preflight task and were not reverted. Ignored build, cache, venv, training report, and generated local paths remained ignored.

Recent commits:

- `ee27f76 test: add omi boundary coverage`
- `b2c519e feat: improve omi lifecycle display`
- `f1a1516 docs: add optional extractors and mvp test matrix`
- `62ff147 feat: add omi promotion gate`
- `ad9fbb5 feat: add omi owner decision flow`

## Matrix Summary

| Area | Result | Evidence | Notes |
| --- | --- | --- | --- |
| Repo safety | blocked | `git status --short --branch` showed dirty `projects/example` files | Pre-existing tracked fixture edits require owner resolution |
| Full backend automated tests | pass | `176 passed` | `.venv-unsloth-clean/bin/python -m pytest tests -q` |
| Focused backend groups | pass | all listed focused groups passed | Counts listed below |
| Frontend build | pass | Vite build completed | Existing large-chunk warning remains non-blocking |
| Backend server smoke | pass | Uvicorn started on `127.0.0.1:8766` | Stopped by timeout intentionally |
| Frontend app smoke | pass | Vite dev server started on `127.0.0.1:5175` | Stopped by timeout intentionally |
| Offline Story Check baseline eval | pass | 6 fixtures, 0 errors, 0 no-prose violations | Report written to `/tmp/story_check_baseline_eval_mvp_exit.json` |
| Mock Story Check smoke | pass | task `story_check`, rich fields present, mode `mock`, no error | No live Ollama |
| Live qwen3 smoke | deferred | `RUN_LIVE_OLLAMA_MVP_EXIT` not set | Not a blocker because App-8 was previously verified |
| Static no-prose checks | pass | only expected guard/docs/tests/UI boundary hits | Binary cache matches were ignored |
| OMI boundary checks | pass | OMI route/project-manager/boundary tests passed | No apply-promotion route; no durable truth mutation |

## Automated Backend Test Results

- Full suite: `.venv-unsloth-clean/bin/python -m pytest tests -q`
- Result: `176 passed in 0.92s`

## Focused Backend Test Results

| Test group | Result |
| --- | --- |
| `tests/test_project_manager.py` | 35 passed |
| `tests/test_scene_routes.py` | 4 passed |
| `tests/test_context_routes.py` | 8 passed |
| `tests/test_story_check_route.py` | 7 passed |
| `tests/test_analysis_normalizer.py` | 11 passed |
| `tests/test_guardrails.py` | 5 passed |
| `tests/test_request_guards.py` | 6 passed |
| `tests/test_output_guards.py` | 6 passed |
| `tests/test_evaluation_fixtures.py` | 10 passed |
| `tests/test_story_check_baseline_eval.py` | 10 passed |
| `tests/test_omi_routes.py` | 19 passed |
| `tests/test_omi_boundaries.py` | 21 passed |

## Frontend Build Result

- Command: `npm run build`
- Result: pass
- Build output included the existing Vite warning that one generated chunk is larger than 500 kB after minification. This warning did not fail the build.

## Offline Baseline Evaluation Result

- Command: `.venv-unsloth-clean/bin/python training/scripts/run_story_check_baseline_eval.py --fixtures-dir tests/fixtures/story_check --output /tmp/story_check_baseline_eval_mvp_exit.json --pretty`
- JSON validation: passed via `python3 -m json.tool`
- Mode: `offline_fixtures`
- Fixture count: 6
- JSON fixtures: 5
- Malformed fixtures: 1
- Schema valid/applicable: 3/3
- Refusal exact match/applicable: 1/1
- Insufficient evidence preserved/applicable: 4/4
- Output guard triggered/applicable: 1/1
- No-prose violations: 0
- Errors: 0

## Mock Story Check Smoke Result

- Command used `ANALYSIS_MODE=mock`
- Result summary:
  - `task`: `story_check`
  - `coherence_score`: 7
  - throughline alignment present: yes
  - insufficient evidence present: yes
  - diagnostics analysis mode: `mock`
  - error present: no

## Live qwen3 Smoke Status

Deferred. `RUN_LIVE_OLLAMA_MVP_EXIT` was not set, so no live Ollama call was made. This is not an MVP blocker because App-8 was previously verified locally and the live qwen3 smoke is optional/manual for this preflight.

## Guardrail / No-Prose Status

Static checks found the standard refusal message in the expected guard, prompt, fixture, docs, and tests. Searches for generation/rewrite/continue/polish/improve/apply/write-to-scene phrases found only expected docs/tests and OMI UI boundary copy. No unsafe runtime UI controls were identified.

## OMI Boundary Status

OMI boundary coverage passed:

- prose-oriented candidate types and destinations are rejected
- owner-authored raw idea and candidate content remain candidate-only and are not treated as assistant request intent
- idea/candidate creation does not mutate durable truth files
- promotion records are record-only and do not apply candidate content
- promotion blockers fail closed for missing approval, confirmation, destination, provenance, content, target, unsafe target, and unknown candidate
- no model/Ollama OMI path is exercised
- `owner_sample_input.md` is not read or transformed automatically
- path traversal is blocked

## Documentation Consistency Updates

Updated planning docs to remove stale contradictions:

- OMI implementation is no longer described as TODO.
- Phase 6 MVP exit/preflight is identified as the current readiness step.
- The sample fixture mismatch is described as replaced locally by the public-domain aligned fixture, with future owner-created replacement optional.
- MVP-EXIT is marked as executed but blocked by dirty tracked project fixture files.
- Optional extractors remain post-MVP.
- Future apply-promotion behavior remains separate and unimplemented.
- Fine-tuning remains separate from the App MVP.

## Remaining Blockers

MVP readiness is blocked by repo safety only:

- `projects/example/bible.json` is dirty.
- `projects/example/scenes/scene_001.md` is dirty.

Resolve by owner-approved revert, acceptance, or separate fixture commit. After resolution, rerun at least repo safety, full backend tests, frontend build, offline baseline, and mock smoke before declaring local MVP ready.

## MVP Readiness Status

MVP readiness: blocked

Reason: automated validation passed, but repo safety did not pass because tracked project fixture files were dirty before this preflight task.

## Recommended Next Step

Resolve the dirty tracked `projects/example` fixture files, then rerun the MVP exit repo-safety check and commit the preflight documentation if the owner wants it recorded in Git.
