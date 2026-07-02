# MVP Owner Manual Acceptance Checklist

## Status

- Task: `MVP-READINESS-OWNER-ACCEPTANCE-001`
- Current decision: **READY FOR OWNER MANUAL ACCEPTANCE TESTING**
- MVP completion: **Pending owner acceptance**
- This checklist does **not** mark MVP complete.
- Generated prose/prose-production remains permanently forbidden.
- Fine-tuning remains deferred after MVP.

## Evidence Review

- `PHASE8-IMPL-022` closeout plus repair evidence supports readiness for manual acceptance testing.
- The prior project isolation blocker is repaired by the committed project isolation routing repair.
- Live browser evidence passed after repair:
  - Script: `scripts/mvp-project-isolation-browser-smoke.mjs`
  - Evidence report: `artifacts/mvp-readiness/project-isolation/evidence-report.md`
  - Workflow log: `artifacts/mvp-readiness/project-isolation/workflow-log.json`
  - Result: **PASS**
  - `SCRIPT_EXIT=0`
  - Blockers: None
- The passing browser evidence confirms project creation, active project switching, Scenes, and Memory/Canon project isolation for the covered smoke path.
- Owner manual MVP acceptance remains pending until this checklist is completed and explicitly accepted by the owner.

## Startup Requirements

- [ ] Backend is running.
- [ ] Frontend is running.
- [ ] Ollama is reachable if model-backed workflows are tested.
- [ ] If backend or tests run in WSL/Ubuntu while Ollama runs on Windows, WSL uses the Windows host IP from the default gateway instead of assuming `localhost`.
- [ ] Browser evidence script is available at `scripts/mvp-project-isolation-browser-smoke.mjs`.
- [ ] Owner understands that model-backed, BookNLP/spaCy, NCP/Subtxt/dramatica-flow, and extraction checks must remain evidence-backed, candidate-first, and non-canon unless explicitly approved through the allowed workflow.

WSL test harness readiness command:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_HOST="http://$WINDOWS_HOST:11434"
curl "$OLLAMA_HOST/api/version"
```

The owner acceptance browser harness tries `OLLAMA_BASE_URL`, `OLLAMA_HOST`, `http://localhost:11434`, and then a detected WSL Windows-host fallback. It records selected and attempted Ollama candidates in the evidence artifacts. This is startup/readiness configuration only, not product behavior and not MVP completion.

The owner acceptance browser harness now defaults to the owner-authored `Cyber detective` MVP acceptance fixture unless a different fixture is provided with `MVP_ACCEPTANCE_FIXTURE`. The fixture includes mature/violent material and must be used only for analysis/testing boundaries. It must not be used to generate, continue, rewrite, polish, improve, imitate, expand, draft, or outline story prose.

Backend Story Check startup in WSL uses `OLLAMA_BASE_URL` based on `backend/analysis_engine.py`:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_BASE_URL="http://$WINDOWS_HOST:11434"
PY=".venv-unsloth-clean/bin/python"
"$PY" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Project Isolation

- [ ] Playwright browser evidence is reviewed.
- [ ] `scripts/mvp-project-isolation-browser-smoke.mjs` records PASS.
- [ ] `SCRIPT_EXIT=0` is recorded.
- [ ] No blockers are recorded in the evidence report or workflow log.
- [ ] New project creation activates the new project in the header, selector, and Overview.
- [ ] Scenes for a new project do not leak `example`, `scene_001`, or unrelated project data.
- [ ] Memory/Canon for a new project does not leak unrelated project data.

## Manual Workspace Checks

- [ ] Create a project.
- [ ] Select an existing project.
- [ ] Confirm Overview reflects the active project only.
- [ ] Confirm Scenes show empty/new project behavior for a new project.
- [ ] Confirm Notes are project-scoped and owner-authored/owner-provided only.
- [ ] Confirm Materials are project-scoped and owner-authored/owner-provided only.
- [ ] Confirm Memory/Canon shows approved-only boundaries.
- [ ] Confirm setup/OMI candidates remain candidates or planning state, not approved memory/canon.

## Runtime Extraction Checks

- [ ] Unavailable dependency states are explicit and fail closed.
- [ ] Runtime failures do not silently claim extraction success.
- [ ] Raw artifacts remain support data only.
- [ ] Raw artifacts do not become candidates, canon, approved memory, training data, or truth by themselves.
- [ ] Runtime extraction does not mutate approved memory/canon.
- [ ] Runtime extraction outputs remain candidate-first and owner-review-gated.

## Candidate / Review Checks

- [ ] Candidate-first behavior is visible and preserved.
- [ ] Review queue entries are not treated as approval.
- [ ] Read-only review state is available where expected.
- [ ] Owner-action execution happens only through explicit owner commands.
- [ ] Confidence values are not presented as truth.
- [ ] Candidate persistence is not canon.

## Apply-Promotion Checks

- [ ] Apply-promotion requires explicit owner confirmation.
- [ ] Apply-promotion records audit details.
- [ ] Approved memory/canon mutation happens only through the approved workflow.
- [ ] Failed or rejected promotion leaves approved memory/canon unchanged.
- [ ] No extraction, model, queue, or candidate state bypasses apply-promotion.

## Model-Assisted / Analysis Runtime Checks

- [ ] Model-assisted observations are evidence-backed only.
- [ ] Confidence is not truth.
- [ ] Model output is not canon.
- [ ] NCP remains structured context interchange only.
- [ ] Subtxt remains rubric/diagnostic guidance only.
- [ ] dramatica-flow remains analysis-only through audited allowlists.
- [ ] NCP/Subtxt/dramatica-flow outputs do not generate prose, outlines, canon, training artifacts, or automatic promotion.

## No-Prose Checks

- [ ] No rewrite behavior is exposed or accepted.
- [ ] No continuation behavior is exposed or accepted.
- [ ] No outline generation behavior is exposed or accepted.
- [ ] No generated prose behavior is exposed or accepted.
- [ ] No imitation, polish, improvement, expansion, draft, chapter generation, or prose-production path is exposed or accepted.

## Cyber Detective Fixture Checks

- [ ] Cyber detective owner-authored fixture project is created through the browser UI.
- [ ] Cyber detective owner-authored source is visible on review before creation as setup/candidate/planning material.
- [ ] Cyber detective project is active and scoped in the header, selector, and Overview.
- [ ] Cyber detective OMI/setup material remains candidate/planning only.
- [ ] Cyber detective fixture content does not appear as approved Memory/Canon.
- [ ] Cyber detective owner-authored source/scene is safely selected for Story Check (`cyber_fixture_story_check_source_selected`).
- [ ] Story Check is submitted only through the visible app UI after safe source selection (`cyber_fixture_story_check_submitted`).
- [ ] Story Check result is diagnostic/candidate-first only (`cyber_fixture_story_check_result_diagnostic_only`).
- [ ] Story Check result contains no generated story prose (`cyber_fixture_story_check_no_generated_prose`).
- [ ] Model-backed output, if safely run, is not presented as canon, approved memory, or truth.
- [ ] No-prose negative rewrite prompt is refused, blocked, redirected to diagnostics, unavailable, or fail-closed (`cyber_fixture_no_prose_rewrite_refused`).
- [ ] No-prose negative continuation prompt is refused, blocked, redirected to diagnostics, unavailable, or fail-closed (`cyber_fixture_no_prose_continue_refused`).
- [ ] No-prose negative outline prompt is refused, blocked, redirected to diagnostics, unavailable, or fail-closed (`cyber_fixture_no_prose_outline_refused`).
- [ ] No-prose negative draft, polish, improve, expand, and imitate prompts are refused, blocked, redirected to diagnostics, unavailable, or fail-closed (`cyber_fixture_no_prose_draft_polish_imitation_refused`).
- [ ] Runtime extraction labels/states are reviewed if visible; BookNLP, spaCy, NCP, Subtxt, and dramatica-flow are not executed directly by the harness.
- [ ] Apply-promotion is not performed automatically; fixture content must not become approved memory/canon without an explicitly owner-approved workflow.

Current automated diagnosis: the app exposes a visible `Run Story Check` control, but the Cyber fixture setup project has no browser-visible create/import scene/source workflow, so the harness keeps Story Check and no-prose negative prompt checks at `MANUAL_REVIEW_REQUIRED` unless a future safe browser-visible workflow is present.

This fixture improves owner acceptance evidence but does not mark MVP complete and does not claim owner acceptance.

## Final Owner Decision

Choose exactly one after manual review:

- [ ] **Pending owner acceptance** — checklist not yet complete or not yet accepted.
- [ ] **Accepted by owner** — owner explicitly accepts MVP manual readiness. Record owner/date/notes below.
- [ ] **Blocked with reason** — owner finds a blocker. Record reason and required follow-up below.

Owner/date/notes:

```text
Pending owner acceptance.
```

Blocked reason / required follow-up:

```text
None recorded.
```
