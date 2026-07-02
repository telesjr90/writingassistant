# PHASE8-UX-001 - Impeccable UI/UX QA Workflow

## Purpose

Impeccable is a UI/UX design QA, critique, and polishing layer for frontend work.

It is not a backend/runtime implementation tool, not a crawler, not a source of external research captures, not a context collection tool, and not a source of roadmap truth.

External crawler/browser-automation research for `PHASE8-UX-002`, if later approved, remains separate from Impeccable UI polish. Impeccable may critique or polish an approved frontend/design task, but it does not authorize crawler runs, raw captures, roadmap structure, implementation scope, or product requirements.

Black-box controlled experiments for future `PHASE8-UX-002-T002A` are research input only. Impeccable remains frontend UI/UX critique and polish only; it is not a crawler, not a reverse-engineering tool, not a context collection tool, and not a source of roadmap truth.

Use Impeccable to improve how users understand and navigate:

- Project workspace
- Scene editor
- Story Check analysis
- OMI ideas and candidates
- Review Queue
- Candidate detail pages
- Apply-promotion confirmation
- Approved memory/canon pages
- Future raw artifact viewer
- Future Subtxt / NCP / dramatica-flow analysis lens UI

## Placement in the Workflow

Recommended frontend task sequence:

1. Implement the frontend feature.
2. Run tests.
3. Run frontend build.
4. Run Impeccable audit, critique, or polish commands.
5. Apply only UI-safe improvements.
6. Re-run tests and build.
7. Review diff.
8. Commit only after owner acceptance.

Impeccable must not be run inside backend-only implementation tasks.

## Product Boundaries

All Impeccable usage must preserve the app boundaries:

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Owner-authored prose storage/editing is allowed.
- AI-generated prose is permanently forbidden.
- No generated story prose.
- No rewrite controls.
- No continuation controls.
- No imitation controls.
- No polish/improve prose controls.
- No expansion controls.
- No outline/draft story controls.
- Queue presence is not approval.
- Confidence is not truth.
- Candidate persistence is not canon.
- Raw artifacts are support data, not canon.
- Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.

## Good Uses

Use Impeccable for:

- Project selector/library
- Project overview
- Chapters/scenes page
- Notes/materials page
- Analysis sidebar
- OMI candidate panel
- Review queue
- Apply-promotion confirmation
- Approved memory/canon pages
- Empty states
- Error states
- Warning states
- Mobile/responsive layout
- Accessibility
- UX copy clarity

## Commands to Use

Useful commands:

- /impeccable audit
- /impeccable critique the review queue
- /impeccable clarify the apply-promotion confirmation screen
- /impeccable harden the raw artifact viewer
- /impeccable adapt the project workspace for mobile
- /impeccable polish the memory canon pages

## Where Not to Use Impeccable

Do not use Impeccable in:

- Backend-only tasks
- Raw artifact persistence helper implementation
- Extraction/runtime implementation
- Model integration tasks
- BookNLP/spaCy runtime tasks
- Roadmap context collection tasks
- Validation-only backend tasks
- Dataset/training tasks
- Any task where UI/UX changes are not explicitly authorized

## Installation Policy

Use project-local installation only.

Recommended command:

npx impeccable install --providers=codex --scope=project

For Codex, after install or update, open:

/hooks

Approve the Impeccable project hook only if the hook change is expected and project-local.

## Impeccable Init Context

When running:

/impeccable init

Choose:

- product
- app UI
- dashboard/tool
- local-first writing assistant
- calm workspace
- analysis/review workflow

Use this design context:

This is a local-first Writer Assistant Core application.

The UI must clearly separate:

- owner-authored prose
- raw artifacts / support data
- candidate records
- review queue state
- approved memory/canon
- apply-promotion audit records

The app must never offer generated prose, rewriting, continuation, imitation, polishing, story drafting, story outlining, or prose improvement.

Design priority:

- clarity over decoration
- evidence/provenance visibility
- strong warning states
- explicit owner confirmation
- calm project workspace UI
- accessible review workflows
- candidate versus canon separation
- confidence-is-not-truth messaging
- queue-presence-is-not-approval messaging
- mobile-safe review flows
- safe empty/error/quarantine states

## Required Prompt Boundary for Impeccable Tasks

Every future prompt that uses Impeccable must include:

Do not change backend behavior.
Do not create candidates.
Do not mutate canon.
Do not call models.
Do not add generated prose features.
Do not add rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.
Only improve UI clarity, layout, accessibility, copy, empty states, warning states, and responsive behavior.
Preserve analysis-only, candidate-first, evidence/provenance-backed, owner-controlled boundaries.

## Recommended Roadmap Placement

Use Impeccable in future frontend/UX task types:

- Review Queue UI audit/polish
- OMI candidate review UI audit/polish
- Apply-promotion confirmation UI audit/polish
- Approved memory/canon UI audit/polish
- Raw Artifact Viewer UI audit/polish
- MVP UI/UX audit and polish

## Validation After Impeccable-Assisted Frontend Work

After any Impeccable-assisted frontend change, run:

npm --prefix frontend run build
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
git diff --check
git status --short --branch

If the task has frontend tests or smoke tests, run those too.

## Final Rule

Use Impeccable to make the app easier and safer to understand.

Do not use Impeccable to implement core logic, mutate project truth, bypass OMI/review gates, create model calls, or introduce generated prose features.
