# PHASE8-UX-001 - Master Plan UX / Navigation Proposal

## 1. Executive Summary

This proposal explains the current and planned UI/UX for the Dramatica-Informed Writing Assistant.

The app is a local-first writing workspace that keeps owner-authored prose, raw artifacts, candidate records, review queue state, apply-promotion audit records, and approved memory/canon clearly separated.

The app is analysis-only, candidate-first, evidence/provenance-backed, and owner-controlled.

The app must never offer generated prose, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.

This proposal is docs-only. It does not change frontend code, backend code, routes, or tests.

## 2. Current UI/UX Inventory

Based on the available frontend files, the current UI includes:

- Project navigation sidebar with project selector, workspace views, scenes, notes, and materials.
- Project overview workspace.
- Memory/Canon shell placeholder.
- Editor workspace with project context, OMI panel, review queue panel, editor, and analysis sidebar.
- Scene editor with save status and dirty state.
- Notes and materials editor shell.
- Project context panel for bible and storyform JSON editing.
- OMI panel for ideas, candidates, owner decisions, and promotion records.
- Review queue panel.
- Analysis sidebar for Story Check diagnostics.
- Apply-promotion confirmation UI.
- Guided project creation flow.

Uncertain items that need verification:

- Exact mobile/responsive behavior.
- Exact accessibility labels and focus order.
- Exact empty states shown for all document types.
- Exact filtering and sorting controls in the review queue.
- Exact approved memory/canon browsing experience beyond the shell.

## 3. Planned UI/UX from the Master Plan

The planned UI/UX includes:

- Project workspace with overview, memory/canon, and editor views.
- Scene editor for owner-authored prose only.
- Notes and materials editor for owner-authored planning material.
- Story Check analysis sidebar for candidate diagnostics only.
- OMI ideas and candidates panel for planning material.
- Review Queue for owner review of candidates.
- Apply-Promotion confirmation for explicit owner-confirmed canon mutation.
- Approved Memory/Canon browser for approved records only.
- Raw artifact viewer for support data only.
- Future Subtxt/NCP/dramatica-flow analysis lenses for candidate diagnostics.

## 4. Gap Analysis

Implemented:

- Project navigation sidebar.
- Project overview.
- Scene editor with save/dirty state.
- Notes/materials editor shell.
- Project context panel.
- OMI ideas/candidates/promotion records.
- Review queue panel.
- Analysis sidebar.
- Apply-promotion confirmation UI.
- Guided project creation.

Partially implemented:

- Memory/Canon shell exists but approved record browsing is not populated.
- Raw artifact viewer is planned but not implemented.
- Future analysis lenses are planned but not implemented.
- Project-scoped navigation after OMI-guided project creation: header/selector/overview activation passed browser evidence (`MVP-READINESS-BROWSER-EVIDENCE-001-C`), but scenes nav and OMI/Memory views still leak example project data (`scene_001`, `The Princess and the Pea`).

Confirmed MVP manual readiness blockers (browser evidence, exit code `1`, not tooling blocked):

- Scenes navigation is not fully project-scoped — example `scene_001` appears for newly created projects.
- OMI/Memory/Canon navigation is not fully project-scoped — example project strings leak into new project context.
- Setup candidate from guided project creation is not visibly labeled as candidate/planning; must not appear as approved memory or canon.
- Evidence: `artifacts/mvp-readiness/project-isolation/` (script: `scripts/mvp-project-isolation-browser-smoke.mjs`).
- MVP manual readiness blocked until isolation passes; `PHASE8-IMPL-022` smoke-harness closeout does not equal owner MVP acceptance.

Planned but not implemented:

- Full approved memory/canon browser.
- Raw artifact viewer.
- Subtxt/NCP/dramatica-flow analysis lenses.
- Mobile-optimized review flows.

Unclear / needs owner decision:

- Exact canon categories and labels.
- Exact raw artifact display format.
- Exact future analysis lens scope.
- Exact review queue filtering/sorting UX.

## 5. Recommended Navigation Model

Recommended navigation:

- Left navigation: project selector, workspace views, scenes, notes, materials.
- Main workspace: overview, memory/canon, or editor.
- Editor workspace: project context, OMI, review queue, editor, analysis sidebar.
- OMI: ideas, candidates, promotion records.
- Review Queue: candidate review list.
- Apply-Promotion: confirmation dialog/page.
- Approved Memory/Canon: dedicated view.
- Raw Artifacts: dedicated viewer.
- Future analysis lenses: dedicated views or tabs.

## 6. Recommended Information Architecture

Separate:

- Owner-authored prose: scenes, notes, materials.
- Raw artifacts/support data: extraction outputs, source maps.
- Analysis diagnostics: Story Check, future lenses.
- Candidates: OMI ideas/candidates.
- Review queue state: queue entries, owner decisions.
- Apply-promotion audit records: promotion records.
- Approved memory/canon: approved records only.

Never merge these layers in the same UI surface.

## 7. Primary User Workflows

Recommended workflows:

- Create/select project.
- Write/edit scene.
- Add notes/materials.
- Run Story Check analysis.
- Review OMI ideas/candidates.
- Review queue entries.
- Apply promotion with explicit confirmation.
- Browse approved memory/canon.
- Inspect raw artifacts.
- Handle insufficient evidence notes.

## 8. Detailed ASCII Wireframes

### 8.1 Project Overview

    +--------------------------------------------------------------------------------+
    | Project: Example Project                                                       |
    +----------------------+---------------------------------------------------------+
    | Project              | Overview                                                |
    | - Selector           |                                                         |
    | - Overview *         | Owner-authored documents                                |
    | - Memory/Canon       | - Scenes: 3                                             |
    |                      | - Notes: 2                                              |
    | Documents            | - Materials: 1                                          |
    | - Scenes             |                                                         |
    | - Notes              | Candidate/review state                                  |
    | - Materials          | - OMI ideas: 2                                          |
    |                      | - Candidates: 3                                         |
    | Review               | - Review Queue: 1 pending                               |
    | - OMI                |                                                         |
    | - Review Queue       | Approved truth                                          |
    |                      | - Approved Memory/Canon: 0 records                      |
    | Support Data         |                                                         |
    | - Raw Artifacts      | Warning: candidates and queue entries are not canon.    |
    +----------------------+---------------------------------------------------------+

### 8.2 Scene Editor + Analysis Sidebar

    +--------------------------------------------------------------------------------+
    | Project: Example Project                                                       |
    +----------------------+--------------------------------------+-------------------+
    | Left Nav             | Editor: Scene 1                      | Analysis           |
    |----------------------|--------------------------------------|-------------------|
    | Overview             | [Save] Unsaved changes               | Story Check        |
    | Memory/Canon         |                                      | Coherence: 7/10    |
    |                      | Owner-authored scene content.        | Warnings: 2        |
    | Scenes               |                                      | Suggestions: 3     |
    | - Scene 1 *          |                                      | Throughline notes  |
    | - Scene 2            |                                      | Evidence status    |
    | - Scene 3            |                                      | Raw JSON           |
    | Review               |                                      | [Run Story Check]  |
    | - OMI                |                                      |                   |
    | - Review Queue       |                                      |                   |
    +----------------------+--------------------------------------+-------------------+

### 8.3 OMI Ideas/Candidates

    +--------------------------------------------------------------------------------+
    | Workspace: OMI Ideas/Candidates                                                |
    +----------------------+---------------------------------------------------------+
    | Left Nav             | Raw Idea                                                |
    | Review               | [Create idea]                                           |
    | - OMI *              |                                                         |
    | - Review Queue       | Candidate                                               |
    |                      | - Linked idea                                           |
    | Support Data         | - Candidate type                                        |
    | - Raw Artifacts      | - Destination                                           |
    |                      | - Evidence/provenance required                          |
    |                      | Status panels                                           |
    |                      | - Ideas: 2                                              |
    |                      | - Candidates: 3                                         |
    |                      | - Promotion records: 0                                  |
    +----------------------+---------------------------------------------------------+

### 8.4 Review Queue

    +--------------------------------------------------------------------------------+
    | Workspace: Review Queue                                                        |
    +----------------------+---------------------------------------------------------+
    | Left Nav             | Queue summary                                           |
    | Review               | - Pending review: 1                                     |
    | - OMI                | - Reviewed: 0                                           |
    | - Review Queue *     | - Needs evidence: 0                                     |
    |                      | - Quarantined: 0                                        |
    |                      | Candidate: candidate-001                                |
    |                      | Status: Pending review                                  |
    |                      | Evidence: 2 items                                       |
    |                      | Provenance: owner-authored                              |
    |                      | [Approve] [Reject] [Needs revision]                     |
    |                      | [Request evidence] [Defer] [Quarantine]                 |
    |                      | Warning: queue presence is not approval.                |
    +----------------------+---------------------------------------------------------+

### 8.5 Candidate Detail

    +--------------------------------------------------------------------------------+
    | Workspace: Candidate Detail                                                    |
    +----------------------+---------------------------------------------------------+
    | Left Nav             | Candidate: candidate-001                                |
    | Review               | Status: Pending review                                  |
    | - OMI                | Decision: Pending                                       |
    | - Review Queue       | Destination: planning_notes                             |
    |                      | Provenance                                              |
    |                      | - Source type: owner-authored                           |
    |                      | - Source label: scene-001                               |
    |                      | - Created by: owner                                     |
    |                      | Evidence                                                |
    |                      | - 2 evidence items                                      |
    |                      | Promotion readiness                                     |
    |                      | - Owner approval: pending                               |
    |                      | - Confirmation: missing                                 |
    |                      | - Destination allowed: yes                              |
    |                      | - Safe target path: needs verification                  |
    |                      | [Save decision] [Create promotion record]               |
    +----------------------+---------------------------------------------------------+

### 8.6 Apply-Promotion Confirmation

    +--------------------------------------------------------------------------------+
    | Workspace: Apply-Promotion Confirmation                                        |
    +----------------------+---------------------------------------------------------+
    | Left Nav             | Candidate: candidate-001                                |
    | Review               | Destination: approved_character                         |
    | - OMI                | Destination path: memory/characters/character-001.json  |
    | - Review Queue       | Evidence refs: 2                                        |
    |                      | Provenance refs: 1                                      |
    |                      | Source locator refs: 2                                  |
    |                      | Owner confirmation required                             |
    |                      | [ ] I confirm applying this candidate to approved       |
    |                      |     memory/canon.                                       |
    |                      | [Cancel] [Submit apply-promotion]                       |
    |                      | Warning: this is the only canon mutation gate.          |
    +----------------------+---------------------------------------------------------+

### 8.7 Approved Memory/Canon

    +--------------------------------------------------------------------------------+
    | Workspace: Approved Memory/Canon                                               |
    +----------------------+---------------------------------------------------------+
    | Left Nav             | Approved categories                                     |
    | Project              | - Characters                                            |
    | - Overview           | - Locations/settings                                    |
    | - Memory/Canon *     | - Timeline events                                       |
    |                      | - Plot threads                                          |
    |                      | - Continuity/consistency                                |
    |                      | - Open questions                                        |
    |                      | - Relationships                                         |
    |                      | - Organizations/groups                                  |
    |                      | - Objects/items                                         |
    |                      | - Annotations/evidence/provenance                       |
    |                      | Empty state: no approved memory/canon yet.              |
    |                      | Apply-promotion is required to add records.             |
    +----------------------+---------------------------------------------------------+

### 8.8 Raw Artifact Viewer

    +--------------------------------------------------------------------------------+
    | Workspace: Raw Artifacts                                                       |
    +----------------------+---------------------------------------------------------+
    | Left Nav             | Bundle: bundle-001                                      |
    | Support Data         | Status: valid                                           |
    | - Raw Artifacts *    | Artifact files                                          |
    |                      | - tokens.tsv                                            |
    |                      | - entities.tsv                                          |
    |                      | - quotes.tsv                                            |
    |                      | Source refs: 1                                          |
    |                      | Evidence refs: 2                                        |
    |                      | Provenance refs: 1                                      |
    |                      | Source locator refs: 2                                  |
    |                      | [View artifact]                                         |
    |                      | Warning: raw artifacts are support data only, not canon.|
    +----------------------+---------------------------------------------------------+

### 8.9 Future Analysis Lenses

    +--------------------------------------------------------------------------------+
    | Workspace: Analysis Lenses                                                     |
    +----------------------+--------------------------------------+-------------------+
    | Left Nav             | Lens selector                        | Lens Output        |
    | Analysis             | [Story Check]                        | Diagnostics only   |
    | - Story Check *      | [Subtxt - future]                    | Evidence           |
    | - Subtxt future      | [NCP - future]                       | Concerns           |
    | - NCP future         | [Dramatica-flow - future]            | Insufficient proof |
    | - Dramatica future   | Warning: analysis lenses create      | No canon mutation  |
    |                      | candidate diagnostics only.          | from analysis.     |
    +----------------------+--------------------------------------+-------------------+

## 9. UX Safety Rules

- No generated prose controls.
- No rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.
- Owner-authored writing and editing must remain allowed.
- Candidate records must be visually distinct from approved memory/canon.
- Confidence is support strength, not truth.
- Queue presence is not approval.
- Candidate persistence is not canon.
- Raw artifacts are support data only.
- Evidence/provenance must be visible near candidate claims.
- Final owner confirmation is required before memory/canon mutation.
- Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.

### Recommended Status Labels and Badges

- Owner-authored: Saved, Unsaved changes, Saving, Loading.
- Candidate: Pending, Approved for promotion, Rejected, Needs revision, Uncertain.
- Review Queue: Pending review, Reviewed, Needs evidence, Quarantined.
- Promotion: Blocked, Ready, Confirmed, Applied.
- Canon: Approved.
- Raw Artifact: Support data only.

### Recommended Empty States

- No scenes yet.
- No notes yet.
- No materials yet.
- No OMI ideas yet.
- No OMI candidates yet.
- No review queue entries yet.
- No approved memory/canon yet.
- No raw artifacts yet.

### Recommended Warning Copy

- "Story Check is candidate analysis. It does not change project truth."
- "Candidates in the review queue are not approved truth."
- "Confidence scores indicate support strength, not truth."
- "Candidate persistence is not canon."
- "Raw artifacts are support data, not canon."
- "Apply-promotion requires explicit owner confirmation."

## 10. Impeccable UI/UX QA Workflow

Impeccable is a frontend/design QA, critique, and polishing layer only.

Use Impeccable for:

- Project workspace UI audit.
- Scene editor UI audit.
- Analysis sidebar UI audit.
- OMI candidate panel UI audit.
- Review queue UI audit.
- Apply-promotion confirmation UI audit.
- Approved memory/canon UI audit.
- Raw artifact viewer UI audit.
- Empty/error/warning state review.
- Accessibility audit.
- Mobile/responsive adaptation.

Do not use Impeccable for:

- Backend-only tasks.
- Runtime extraction tasks.
- Model integration tasks.
- Roadmap context collection tasks.
- Canon mutation.
- Candidate creation.
- Generated prose features.

Useful commands:

- /impeccable audit
- /impeccable critique the review queue
- /impeccable clarify the apply-promotion confirmation screen
- /impeccable harden the raw artifact viewer
- /impeccable adapt the project workspace for mobile
- /impeccable polish the memory canon pages

Required prompt boundary for Impeccable-assisted tasks:

- Do not change backend behavior.
- Do not create candidates.
- Do not mutate canon.
- Do not call models.
- Do not add generated prose features.
- Do not add rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.
- Only improve UI clarity, layout, accessibility, copy, empty states, warning states, and responsive behavior.
- Preserve analysis-only, candidate-first, evidence/provenance-backed, owner-controlled boundaries.

Validation after Impeccable-assisted frontend work:

- npm --prefix frontend run build
- python3 scripts/check_enrichment.py
- python3 scripts/validate_roadmap.py
- git diff --check
- git status --short --branch

## 11. OpenUI/OpenUI Lang Usage Policy

OpenUI/OpenUI Lang may be used as prototype/reference material during PHASE8-UX-001.

Allowed use:

- Reference material for UI component ideas.
- Prototype sketches for layout/copy exploration.
- Design inspiration for complex review and inspector layouts.

Disallowed use:

- Adding OpenUI/OpenUI Lang as a production runtime dependency.
- Generating production frontend code during PHASE8-UX-001.
- Treating OpenUI/OpenUI Lang output as implementation truth.
- Bypassing OMI, Review Queue, apply-promotion, or approved memory/canon boundaries.

Possible future spike:

- Evaluate OpenUI/OpenUI Lang for prototype/reference use only.
- Do not add as a production runtime dependency without explicit owner approval.

## 12. Aider Recommendations

Immediate UX improvements:

- Tighten empty states.
- Tighten warning states.
- Clarify candidate vs canon copy.
- Clarify support-data copy for raw artifacts.
- Clarify confidence-is-not-truth copy.
- Clarify save/dirty/loading status in the editor.

MVP UX improvements:

- Add dedicated Candidate Detail page or confirm panel-based alternative.
- Add dedicated Raw Artifact Viewer.
- Add dedicated Review Queue workspace with filters.
- Add dedicated Apply-Promotion confirmation workspace.
- Add approved memory/canon category pages.
- Add mobile review flows.

Post-MVP UX improvements:

- Add timeline/graph views.
- Add search across approved memory/canon.
- Add mobile-first review flows.
- Add future Subtxt/NCP/dramatica-flow analysis lens UI.

Safe Aider use for future frontend tasks:

- Use one-task/one-file or narrow allowlist discipline.
- Specify exact files allowed to change.
- Specify exact validation commands.
- Do not infer new roadmap structure.
- Do not run context tools inside implementation prompts.
- Do not add generated prose controls.
- Do not mutate backend behavior unless explicitly authorized.

## 13. UI/UX Reference Search Targets

Recommended reference categories:

- Writing app navigation.
- Evidence/provenance UI.
- Review queue UX.
- Approval workflow UX.
- Knowledge base/canon browser UX.
- Timeline/graph UX.
- Accessibility for complex dashboards.
- Empty/error/warning states.
- Data lineage and audit-trail UX.
- Complex editor and inspector layouts.

These searches should focus on patterns, not implementation dependencies.

### PHASE8-UX-002 Prepublication Reference Research Boundary

Current owner acceptance evidence shifts the next UX work from general UX polish to MVP acceptance UI completion. The remaining acceptance issue is missing safe browser-visible workflow evidence for owner-authored source/scene selection, Story Check diagnostics, no-prose negative paths, Notes/Materials save-reload proof, raw artifact evidence, review/apply-promotion proof, and analysis runtime exposure decisions.

External SaaS reference research is allowed only as summarized design-pattern input. `PHASE8-UX-002` should use that research to improve the UI acceptance matrix and route/workflow gap map, not to copy or clone Dramatica or any other external product.

Reference boundary: `docs/roadmap/ux/PHASE8-UX-002-prepublication-reference-research-boundary.md`.

The `PHASE8-UX-002` prepublication research boundary now includes a black-box controlled-experiment method. One-variable-at-a-time observations may help map external UI panel and workflow dependencies, but only `observed`, `inferred`, and `unknown` confidence labels are allowed. Hidden algorithm, prompt, routing, ranking, model-weight, or proprietary implementation details can be known only through explicit authorized disclosure, official documentation, owner-provided evidence, or other lawful non-black-box evidence; they must not be claimed as known from black-box observations alone.

`PHASE8-UX` may retrieve authorized official documentation, owner-provided evidence, authorized disclosures, and other lawful non-black-box reference materials after that collection is explicitly scoped. The information still needs to be collected, summarized, provenance-labeled, and reviewed before use as UX/reference input.

Controlled-experiment method: `docs/roadmap/ux/PHASE8-UX-002-prepublication-controlled-experiment-method.md`.

All `PHASE8-UX-001` product boundaries remain in force: analysis-only, candidate-first, owner-controlled, evidence/provenance-backed, no generated prose, no automatic canon, and explicit owner-confirmed apply-promotion only.

## 14. Implementation Task Breakdown

### Docs-Only Tasks

- Finalize this UX proposal.
- Create detailed page specs for Candidate Detail, Raw Artifact Viewer, Review Queue workspace, Apply-Promotion workspace, and approved memory/canon pages.
- Create detailed empty-state specs.
- Create detailed warning-state specs.
- Create terminology guidance.

### Frontend-Only Tasks

- Implement dedicated Candidate Detail page or improve candidate detail panel.
- Implement dedicated Raw Artifact Viewer.
- Implement dedicated Review Queue workspace.
- Implement dedicated Apply-Promotion workspace.
- Implement approved memory/canon category pages.
- Add left-nav grouping for scenes/notes/materials.
- Add right-sidebar analysis lens selector.
- Add mobile-first review flows.

### Backend/API Tasks

- Support approved memory/canon category queries.
- Support raw artifact viewer routes/helpers.
- Support candidate detail routes/helpers.
- Support review queue filtering/sorting/search as needed.
- Preserve candidate-first and owner-confirmed mutation rules.

### Validation/Smoke Tasks

- Fix and re-run project isolation browser evidence: `node scripts/mvp-project-isolation-browser-smoke.mjs` (target exit code `0`; current FAIL-with-evidence at `artifacts/mvp-readiness/project-isolation/`).
- Re-run browser/manual smoke for notes/materials flows.
- Re-run browser/manual smoke for review queue flows.
- Re-run browser/manual smoke for apply-promotion confirmation flows.
- Re-run browser/manual smoke for approved memory/canon flows.
- Re-run roadmap validation.

### Impeccable-Assisted UI Polish Tasks

- Audit project workspace UI.
- Audit review queue UI.
- Audit apply-promotion confirmation UI.
- Audit approved memory/canon UI.
- Audit empty/error/warning states.
- Audit accessibility.
- Audit mobile/responsive behavior.

### OpenUI Prototype/Reference Spike

- Evaluate OpenUI/OpenUI Lang for prototype/reference use only.
- Do not add as production runtime dependency without explicit owner approval.
- Do not create official task IDs here unless owner explicitly requests a new roadmap task.

## 15. Open Questions

- When will project-scoped scenes and OMI/Memory/Canon navigation pass browser isolation evidence (`MVP-READINESS-BROWSER-EVIDENCE-001-C`)?
- Does OMI need a dedicated Candidate Detail page, or is panel-based detail sufficient for MVP?
- How should raw artifacts be displayed without implying canon?
- How should future Subtxt/NCP/dramatica-flow panels be separated from Story Check?
- How should mobile review flows work?
- How should evidence/provenance be summarized without hiding source details?
- Should the left navigation support collapsible groups for many scenes/notes/materials?
- What filtering/sorting/search is needed in the Review Queue for MVP?
- Which approved memory/canon categories are most important for MVP?
- How prominently should apply-promotion audit records be shown?
- Are the recommended user-facing labels clear to actual writers?
