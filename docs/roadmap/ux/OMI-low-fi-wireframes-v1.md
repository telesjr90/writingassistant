# OMI Low-Fi Wireframes v1

Status: planning-only low-fidelity wireframe artifact. Runtime implementation is future work.

## 1. Purpose

This document defines the first low-fidelity mockup plan for four OMI screens:

- OMI Dashboard
- Candidate Detail
- Evidence Drawer
- Apply-Promotion Confirmation

The goal is to give Impeccable a concrete, safety-bounded mockup brief that can prove layout, information hierarchy, warning copy, disabled risky actions, and responsive behavior before frontend implementation.

OMI remains analysis-only, candidate-first, evidence/provenance-backed, owner-controlled, project-local, and no-prose. These wireframes do not create candidates, mutate Memory/Canon, run apply-promotion, call models, or initialize Impeccable.

## 2. Source inputs

Source documents read for this artifact:

- `docs/roadmap/ux/OMI-ui-screen-spec-v1.md`
- `docs/roadmap/ux/PHASE8-UX-001-impeccable-ui-ux-qa-workflow.md`
- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_memory_canon_storage_model.md`

Impeccable direction source:

- Dense operational tool UI, not marketing UI.
- Calm review workspace with strong warnings, evidence/provenance visibility, accessible controls, and candidate/canon separation.
- No generated story-prose affordances.
- No frontend/backend/runtime implementation in this task.

## 3. Global wireframe rules

- Use a dense operational layout with tables, rows, status badges, drawers, checklists, and compact filters.
- Keep raw ideas, candidates, promotion audit records, and approved Memory/Canon visually separated.
- Keep the OMI boundary banner visible on every OMI route and route-backed confirmation.
- Treat evidence as review support, not canon truth.
- Treat readiness as handoff completeness, not mutation.
- Evidence summary, supports-claim note, proposed value, structured field summary, original wording excerpt, and evidence/provenance summary areas display stored review metadata only. They must not trigger newly generated summaries, assistant-composed text, prose rewriting, model calls, or source-text transformation.
- Show risky actions disabled with adjacent reasons instead of hiding the safety boundary.
- Every blocked reason or disabled action reason must be programmatically associated with the disabled control, not only visually adjacent. Implementation should plan for `aria-describedby` or equivalent semantic association.
- Keep owner decisions explicit and separate from automated status or confidence.
- Keep candidate-level actions separate from field-level actions.
- Use noun-qualified labels such as `Candidate: Pending Review`, `Promotion Audit Record`, `Not Applied to Memory/Canon`, and `Approved Memory/Canon`.
- Use stable layout zones that can survive empty, blocked, corrupt, and missing-evidence states.
- Use compact browser mockup density: row height should support dense review without becoming metric-card UI; badges should be short text badges, not color-only chips; long values should wrap inside value columns without moving decision controls; tables should favor stable columns on desktop and stacked rows on mobile.
- Long candidate IDs, source locations, Memory/Canon target paths, proposed field values, and owner notes need wrapping or truncation with accessible full-value access. Do not hide critical path or ID data only in tooltips; preserve copyable source and target paths where useful.
- Avoid metric-card dashboards, hero sections, nested cards, decorative visuals, and assistant prompt-composer patterns.
- Do not show controls for write, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, or story-prose production.

## 4. OMI Dashboard wireframe

### Purpose

Give the owner a project-local operational overview of owner input, candidate review, blockers, duplicate decisions, promotion handoff readiness, promotion audit records, deferred categories, approved Memory/Canon snapshot, and warnings.

### What the mockup must prove

- The dashboard reads as a review operations surface, not a metric dashboard.
- Counts for candidates and promotion audit records do not blend into approved Memory/Canon.
- Every workflow row has one safe navigation action, not inline approval.
- `Apply to Memory/Canon` appears only disabled with a visible reason.
- The owner can scan blockers, evidence gaps, provenance gaps, and deferred categories without opening a detail page.

### Desktop wireframe

```text
+------------------------------------------------------------------------------+
| Project: {Project Name}                                      OMI Dashboard    |
| OMI stores review material only. Nothing becomes Memory/Canon until the owner |
| explicitly confirms a separate apply-promotion step.                          |
| Candidate status: 18 total | 6 blocked | 2 handoff ready | Canon unchanged    |
+------------------------------------------------------------------------------+
| Filters: [Status v] [Evidence missing] [Provenance missing] [Blockers]        |
|          [Deferred] [Clear filters]                                           |
+------------------------------------------------------------------------------+
| Workflow area        Count  Status      Blockers  Evidence / Provenance Action |
| Owner Input          12     Reviewable  1         10 linked / 2 gap     Open   |
| Candidates           18     Mixed       6         14 linked / 4 gap     Review |
| Grouped Review       7      Needs work  2         5 groups sourced      Open   |
| Duplicate Decisions  5      Pending     3         5 with provenance     Resolve|
| Promotion Readiness  2      Ready       0         packets complete      Open   |
| Promotion Audits     4      Audit only  0         not applied           View   |
| Deferred Categories  3      Deferred    0         source retained       Open   |
| Disabled risky action / reason: Apply to Memory/Canon disabled; dashboard     |
| cannot mutate Memory/Canon.                                                   |
+------------------------------------------------------------------------------+
| Approved Memory/Canon Snapshot                                                |
| Characters 0 | Locations 0 | Timeline 0 | Plot Threads 0 | Health: unchanged |
| Action: Open Approved Memory/Canon                                             |
+------------------------------------------------------------------------------+
| Warnings / Health                                                             |
| - Dashboard counts show review status only. Candidates, groups, and promotion |
|   records are not canon.                                                       |
| - Ready means the handoff packet is complete. Memory/Canon has not changed.   |
| [Disabled: Apply to Memory/Canon requires owner approval, destination,         |
| evidence/provenance review, duplicate resolution, dependency review, and final |
| confirmation.]                                                                |
+------------------------------------------------------------------------------+
```

### Mobile wireframe

```text
+--------------------------------------+
| Project: {Project Name}              |
| OMI Dashboard                        |
| Boundary banner                      |
| Candidate status strip               |
+--------------------------------------+
| Filters                              |
| [Status v] [Evidence] [Provenance]   |
| [Blockers] [Deferred]                |
+--------------------------------------+
| Owner Input                          |
| Count 12 | Reviewable | 1 blocker    |
| Evidence/provenance: 10 linked / 2   |
| [Open owner input]                   |
+--------------------------------------+
| Candidates                           |
| Count 18 | Mixed | 6 blockers        |
| [Review candidates]                  |
+--------------------------------------+
| ...same row pattern...               |
+--------------------------------------+
| Approved Memory/Canon Snapshot       |
| Visually separated from OMI counts   |
+--------------------------------------+
| Warnings / disabled apply reason     |
+--------------------------------------+
```

### Layout zones

- Top stack: active project label, `OMI Dashboard`, persistent boundary banner, candidate/canon status strip.
- Filter strip: compact status/evidence/provenance/blocker/deferred filters.
- Main status table: one row per workflow area.
- Dashboard row columns must be `Workflow area`, `Count`, `Status`, `Blockers`, `Evidence / Provenance`, `Action`, and `Disabled risky action / reason, if applicable`.
- Each workflow row has exactly one safe primary navigation action. The action navigates to a review surface or filtered list; it does not approve, promote, merge, ignore, mutate Memory/Canon, or call a model.
- Approved Memory/Canon snapshot: separate band below OMI workflow rows.
- Warnings/health band: boundary reminders, corrupt/missing state warnings, disabled apply reason.

### Required visible labels

- `OMI Dashboard`
- `Owner Input`
- `Candidates`
- `Grouped Review`
- `Duplicate Decisions`
- `Promotion Handoff Readiness`
- `Promotion Audit Records`
- `Deferred Categories`
- `Approved Memory/Canon Snapshot`
- `Warnings / Health`
- `Evidence Linked`
- `Provenance Linked`
- `Not Applied to Memory/Canon`

### Required warning/boundary copy

```text
OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.
```

```text
Dashboard counts show review status only. Candidates, groups, and promotion records are not canon.
```

```text
Ready means the handoff packet is complete. Memory/Canon has not changed.
```

### Primary safe action

Open the next relevant review surface from a status row, such as `Review candidates`, `Resolve duplicates`, or `Open handoff queue`.

### Disabled risky action, if applicable

`Apply to Memory/Canon` must appear only as disabled:

```text
Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.
```

### Missing states

- No owner input: show zero-count owner input row and safe navigation back to project workspace.
- No candidates: show candidate row with `0` and copy that raw ideas may remain unstructured.
- Missing evidence: row badge `Evidence Required`; safe action opens filtered candidate list.
- Missing provenance: row badge `Provenance Missing`; safe action opens filtered candidate list.
- No approved Memory/Canon: approved snapshot shows zero records and `Canon unchanged`.
- Corrupt OMI index: warnings/health row shows degraded state and disables readiness/apply actions.

### Accessibility notes

- Use a real table or accessible row group for workflow rows.
- Each row action must include the row label in its accessible name.
- Status badges must not rely on color alone.
- Filter controls need labels, visible focus, and keyboard order before the table.
- The disabled apply control needs adjacent explanatory text reachable by screen reader.
- The disabled apply reason must be programmatically associated with the disabled dashboard apply control using `aria-describedby` or an equivalent semantic association.

### Mobile/responsive notes

- Collapse the status table into stacked row summaries.
- Keep the top stack and boundary banner above filters.
- Keep Approved Memory/Canon as a separate stacked section, not an item inside candidate counts.
- Row actions stay full-width touch targets.
- Avoid horizontal scrolling except for optional advanced tables hidden behind detail routes.

### What must not appear

- Metric cards that imply success scores or canon totals.
- Inline candidate approval controls.
- Enabled apply-promotion or Memory/Canon mutation controls.
- Model/Ollama controls.
- Generated prose, rewrite, continue, outline, draft, polish, improve, expand, imitate, or revise controls.
- Pending candidates displayed as approved Memory/Canon.

## 5. Candidate Detail wireframe

### Purpose

Provide the full review workspace for one candidate, including structured fields, field decisions, evidence, provenance, duplicate/dependency state, owner notes, and promotion readiness.

### What the mockup must prove

- The field table is the main workspace.
- Candidate-level actions are separate from field-level actions.
- Promotion readiness is a checklist, not a primary action cluster.
- Duplicate, merge, clarification, and dependency state is visible before candidate approval.
- Approved Memory/Canon links are read-only references.
- Field approval does not silently approve the candidate.

### Desktop wireframe

```text
+------------------------------------------------------------------------------+
| Project: {Project Name}                                                       |
| Candidate: {candidate_id} | Type: {candidate_type} | Status: Pending Review   |
| Destination: {destination} | Source: Owner Input {idea_id or source locator}  |
| This remains a candidate until apply-promotion is separately confirmed and    |
| completed.                                                                    |
+------------------------------------------------------------------------------+
| Candidate actions                                                             |
| [Approve Candidate for Handoff] [Reject Candidate] [Needs Revision]           |
| [Archive Candidate]                                                           |
| Disabled: apply-promotion requires completed handoff gates and final owner     |
| confirmation.                                                                 |
+--------------------------------------------------------------+---------------+
| Field review table                                           | Right rail     |
| Field | Proposed value | Decision | Evidence | Provenance    | Evidence      |
|       |                |          |          |               | summary       |
| Name  | {structured}   | Pending  | 2 linked | owner input   | [Open drawer] |
| Type  | {structured}   | Needs ev | 0 linked | source gap    |               |
| Link  | {structured}   | Uncertain| 1 linked | extractor     | Provenance    |
|       |                |          |          |               | chain         |
| Duplicate/dependency | Owner note | row action buttons       |               |
| Possible duplicate: {approved/candidate id} | {note}          | Duplicate /   |
| [Approve field] [Reject field] [Request Evidence] [Uncertain] | dependency    |
+--------------------------------------------------------------+ panel         |
| Duplicate / Merge / Clarification                            | - Treat as new|
| Candidate has unresolved duplicate/dependency review.         | - Plan merge  |
| [Treat as New Candidate] [Plan Merge with Existing]           | - Ignore dup  |
| [Ignore as Duplicate] [Needs Owner Clarification]             | - Clarify     |
+--------------------------------------------------------------+---------------+
| Promotion readiness checklist                                                |
| [ ] Owner approved candidate                                                  |
| [ ] Destination selected and allowed                                          |
| [ ] Evidence reviewed or insufficiency accepted                               |
| [ ] Provenance reviewed                                                       |
| [ ] Duplicate decision complete                                               |
| [ ] Dependencies reviewed                                                     |
| [ ] Promotion audit record preview available                                  |
| Ready means the handoff packet is complete. Memory/Canon has not changed.     |
+------------------------------------------------------------------------------+
| Read-only references                                                          |
| Approved Memory/Canon links: read-only, separated from this candidate.         |
| Promotion Audit Record: Not Applied to Memory/Canon                           |
+------------------------------------------------------------------------------+
```

### Mobile wireframe

```text
+--------------------------------------+
| Candidate: {candidate_id}            |
| Status / destination / source        |
| Boundary banner                      |
+--------------------------------------+
| Candidate actions                    |
| [Approve Candidate for Handoff]      |
| [Reject] [Needs Revision] [Archive]  |
| Disabled apply reason                |
+--------------------------------------+
| Tabs: [Fields] [Evidence] [Readiness]|
+--------------------------------------+
| Fields tab                           |
| Field: Name                          |
| Proposed value: {structured value}   |
| Decision: Pending                    |
| Evidence: 2 linked [Open drawer]     |
| Provenance: owner input              |
| Duplicate/dependency: none           |
| Owner note: {note}                   |
| [Approve field] [Request Evidence]   |
+--------------------------------------+
| Readiness tab                        |
| Checklist, links/dependencies,       |
| duplicates, read-only references     |
+--------------------------------------+
```

### Layout zones

- Header/status area: candidate ID, type, status, destination, source, project-local label, boundary copy.
- Candidate-level action bar: approve handoff, reject, needs revision, archive, disabled apply reason.
- Main field table: field-level review columns.
- Right rail or lower panel: evidence/provenance summary, duplicate/dependency controls, read-only references.
- Promotion readiness checklist: gate status only.
- Read-only references: approved Memory/Canon and promotion audit record links.
- Mobile uses exactly three sections/tabs: `Fields`, `Evidence`, and `Readiness`. Links, dependencies, duplicates, and approved Memory/Canon references are folded into those panels: links/dependencies appear in `Readiness`; duplicate state appears in `Readiness` and relevant field rows; approved Memory/Canon references appear in `Evidence` or `Readiness` as read-only references.
- Proposed values, structured field summaries, original wording excerpts, evidence summaries, supports-claim notes, and evidence/provenance summaries display stored review metadata only. They must not trigger newly generated summaries, assistant-composed text, prose rewriting, model calls, or source-text transformation.
- Candidate Detail should label confidence near the Evidence/Provenance summary or field table legend as: `Confidence indicates support strength, not truth.`

### Required visible labels

- `Candidate: Pending Review`
- `Destination`
- `Source`
- `Field`
- `Proposed value`
- `Decision`
- `Evidence`
- `Provenance`
- `Confidence indicates support strength, not truth.`
- `Duplicate/dependency`
- `Owner note`
- `Duplicate / Merge / Clarification`
- `Promotion readiness checklist`
- `Approved Memory/Canon links`
- `Read-only reference`
- `Not Applied to Memory/Canon`

### Required warning/boundary copy

```text
This remains a candidate until apply-promotion is separately confirmed and completed.
```

```text
Owner approval prepares this candidate for a future handoff. It does not update Memory/Canon.
```

```text
Evidence supports review; it is not canon truth until owner approval and apply-promotion are complete.
```

### Primary safe action

`Approve Candidate for Handoff`, only when field decisions, evidence/provenance, duplicate/dependency state, and destination are reviewable. This action prepares a handoff; it does not apply to Memory/Canon.

### Disabled risky action, if applicable

`Apply to Memory/Canon` must be disabled or absent from Candidate Detail. If shown for boundary clarity:

```text
Disabled: apply-promotion requires a completed route-backed confirmation and every handoff gate.
```

### Missing states

- Candidate missing: show `Candidate not found` with return to candidate list.
- Unsupported schema: disable owner approval and show blocking warning.
- Missing evidence: field row shows `Evidence Required`; readiness gate remains unchecked.
- Missing provenance: field row shows `Provenance Missing`; readiness gate remains unchecked.
- Duplicate unresolved: duplicate panel blocks candidate approval for handoff.
- Dependency unresolved: dependency panel blocks handoff readiness.
- No approved Memory/Canon links: show `No applied Memory/Canon links`.

### Accessibility notes

- Field table must support keyboard traversal and row-level actions with clear labels.
- Each field action must include the field name in accessible text.
- Right rail drawer triggers need `aria-expanded` or equivalent state in implementation.
- Checklist items must expose checked/unchecked state and blocker text.
- Read-only references must not look like editable controls.
- Disabled Candidate Approval, Field Approval, Merge, Ignore Duplicate, Unsupported Destination, Approved Memory/Canon edit, and extraction/model unavailable controls need programmatically associated reasons, not only adjacent visual copy.

### Mobile/responsive notes

- Convert the field table into per-field stacked rows or tabs.
- Move the right rail into the `Fields`, `Evidence`, and `Readiness` mobile panels.
- Keep candidate-level actions above field-level actions.
- Keep readiness as a checklist section below field review, not a sticky confirm bar.
- Preserve the disabled apply reason near the action area.

### What must not appear

- Enabled apply-promotion.
- A single `Approve all fields and promote` action.
- Generated replacement text or story prose suggestions.
- Editable approved Memory/Canon records.
- Duplicate merge that deletes or overwrites candidates.
- Confidence labels that imply truth.

## 6. Evidence Drawer wireframe

### Purpose

Show source evidence, original wording/excerpt, provenance, related IDs, timestamps, and review decisions for a candidate, field, group, promotion audit record, or approved Memory/Canon item without offering edit, rewrite, promote, or apply controls.

### What the mockup must prove

- The drawer is scoped and contextual.
- Evidence exactness, source location, confidence/support, and limitations are visible before acceptance.
- Evidence review actions are safe metadata actions.
- There is no path from the drawer to mutation or generated prose.
- Desktop uses a right-side drawer; mobile uses a full-screen sheet.

### Desktop wireframe

```text
Main screen content                                              Evidence Drawer
+------------------------------------------------------------+ +----------------+
| Candidate Detail / Dashboard / Audit screen                | | Evidence       |
|                                                            | | Scope: field   |
| [Evidence linked: 2] -------------------------------------->| | Candidate: ... |
+------------------------------------------------------------+ +----------------+
                                                               | Source type    |
                                                               | Source location|
                                                               | Quote exactness|
                                                               | Support label  |
                                                               | Confidence     |
                                                               +----------------+
                                                               | Original       |
                                                               | wording/excerpt|
                                                               | {short stored  |
                                                               | excerpt}       |
                                                               | Evidence       |
                                                               | summary        |
                                                               | Supports-claim |
                                                               | note           |
                                                               | Limitations /  |
                                                               | ambiguity      |
                                                               +----------------+
                                                               | Provenance     |
                                                               | chain          |
                                                               | Related IDs    |
                                                               | Timestamps     |
                                                               | Source hash    |
                                                               | Snapshot hash  |
                                                               +----------------+
                                                               | [Copy source]  |
                                                               | [Open source]  |
                                                               | [Mark accepted]|
                                                               | [Insufficient] |
                                                               | [Add owner note]|
                                                               | [Close]        |
                                                               +----------------+
```

### Mobile wireframe

```text
+--------------------------------------+
| Evidence                             |
| Scope: Candidate field               |
| [Close]                              |
+--------------------------------------+
| Source type                          |
| Source location                      |
| Quote exactness                      |
| Confidence/support label             |
+--------------------------------------+
| Original wording/excerpt             |
| Evidence summary                     |
| Supports-claim note                  |
| Limitations / ambiguity              |
+--------------------------------------+
| Provenance chain                     |
| Related IDs                          |
| Timestamps                           |
| Source hash / snapshot hash          |
+--------------------------------------+
| [Copy source location]               |
| [Open source record]                 |
| [Mark evidence accepted for review]  |
| [Mark insufficient evidence]         |
| [Add owner note]                     |
| [Close]                              |
+--------------------------------------+
```

### Layout zones

- Header: scope, candidate/field/group/promotion/approved item identifier, close control.
- Top metadata: source type, source location, quote exactness, confidence/support label.
- Middle evidence body: short original wording/excerpt, evidence summary, supports-claim note, limitations/ambiguity.
- Lower provenance: provenance chain, related IDs, timestamps, source hash, snapshot hash.
- Footer actions: grouped by risk and intent:
  - Navigation / copy: `Copy source location`, `Open source record`.
  - Review marking: `Mark evidence accepted for review`, `Mark insufficient evidence`.
  - Owner note: `Add owner note`.
  - Close: `Close drawer`.
- Evidence summary, supports-claim note, original wording excerpt, source location summary, and evidence/provenance summary display stored review metadata only. They must not trigger newly generated summaries, assistant-composed text, prose rewriting, model calls, or source-text transformation.

### Required visible labels

- `Evidence`
- `Scope`
- `Source type`
- `Source location`
- `Quote exactness`
- `Confidence/support`
- `Original wording/excerpt`
- `Evidence summary`
- `Supports claim`
- `Limitations / ambiguity`
- `Provenance chain`
- `Related IDs`
- `Timestamps`
- `Source hash`
- `Snapshot hash`
- `Copy source location`
- `Open source record`
- `Mark evidence accepted for review`
- `Mark insufficient evidence`
- `Add owner note`
- `Close`

### Required warning/boundary copy

```text
Evidence supports review; it is not canon truth until owner approval and apply-promotion are complete.
```

```text
Opening evidence does not edit candidates, promotion records, or approved Memory/Canon.
```

### Primary safe action

`Mark evidence accepted for review`, which marks review metadata only and does not approve the candidate or mutate Memory/Canon.

### Disabled risky action, if applicable

No edit, rewrite, promote, or apply-to-Memory/Canon action should appear. If a disabled boundary marker is necessary:

```text
Unavailable: evidence review cannot apply to Memory/Canon from this drawer.
```

### Missing states

- No source location: show `Source location missing`; disable copy/open source actions.
- No excerpt: show `No excerpt stored`; keep provenance visible.
- Ambiguous support: show `Support uncertain`; do not allow readiness gate to complete unless owner marks insufficiency accepted.
- Broken related ID: show warning and disable unsafe navigation to missing record.
- Missing hash: show `Hash not recorded`; do not invent hash values.
- Source record loading: show `Source record loading`; keep review actions available only if they do not depend on the source open action.
- Source record missing: show `Source record missing`; disable open source action.
- Source location unsafe: show `Source location unsafe`; disable open source action and preserve source locator text for review.
- Source location out of range: show `Source location out of range`; disable open source action.
- Source record corrupt: show `Source record corrupt`; disable open source action and unsafe navigation.
- Source record belongs to another project: show `Source belongs to another project`; disable open source action.
- Source open action unavailable: show `Source open unavailable`; keep stored metadata visible.
- Source open action failed closed: show `Source open failed closed`; do not infer replacement evidence.
- Source-opening failures must not create fallback generated summaries, inferred evidence, transformed source text, or assistant-composed substitutes.

### Accessibility notes

- Desktop drawer needs focus trap, labelled close button, and return focus to opener.
- Mobile full-screen sheet needs a route/dialog title and clear close path.
- Footer actions need consistent order and large hit areas.
- Original wording/excerpt must preserve readable line length.
- Status labels must be text, not color-only.
- Disabled source-opening controls need programmatically associated reasons, not only adjacent visual copy.

### Mobile/responsive notes

- Use a full-screen sheet on mobile instead of a narrow side drawer.
- Keep footer actions sticky only if they do not cover evidence text.
- Collapse lower provenance into grouped rows, not hidden accordions by default.
- The close action must be visible at the top and bottom.

### What must not appear

- Edit candidate content.
- Rewrite source.
- Generate summary from source.
- Promote candidate.
- Apply to Memory/Canon.
- Mark canon truth.
- Story prose production controls.

## 7. Apply-Promotion Confirmation wireframe

### Purpose

Provide a guarded, explicit owner-confirmed apply-promotion handoff screen or route-backed dialog. This surface must make candidate/canon separation, blocked gates, before-state, audit preview, and failure safety unmistakable.

### What the mockup must prove

- This is not a routine modal; it is a guarded confirmation route/dialog.
- Blocked reasons appear above confirmation.
- Candidate snapshot, destination, evidence/provenance, duplicate/dependency state, approved Memory/Canon before-state, and audit preview are all visible before confirmation.
- Final action is disabled until every gate is complete.
- Cancel/return is clear and less risky than confirm.
- Owner action is explicit.

### Desktop wireframe

```text
+------------------------------------------------------------------------------+
| Apply-Promotion Confirmation                                  Guarded Handoff |
| Breadcrumbs: OMI Dashboard > Candidates > Candidate Detail > Apply-Promotion  |
| Handoff                                                                      |
| Strong boundary warning: Candidates are not Memory/Canon. Promotion audit     |
| records are not Memory/Canon. Applying requires explicit owner confirmation.  |
+------------------------------------------------------------------------------+
| Blocked reasons                                                               |
| - Evidence review incomplete                                                  |
| - Duplicate decision unresolved                                               |
| - Approved Memory/Canon before-state not loaded                               |
+------------------------------------------------------------------------------+
| Candidate snapshot                                                            |
| Candidate: {candidate_id} | Type: {candidate_type} | Status: Owner Approved   |
| Proposed fields: {structured field summary only}                              |
| Source candidate snapshot timestamp: {timestamp}                              |
+------------------------------------------------------------------------------+
| Destination / target path                                                     |
| Destination: {memory category}                                                |
| Target file: memory/{category}.json                                           |
| Target path / record ID: {target path or new record id}                       |
+------------------------------------------------------------------------------+
| Evidence / provenance summary       | Source location summary                 |
| Evidence linked: {n}                | Owner input / scene / source refs       |
| Provenance reviewed: yes/no         | Hash/snapshot status                    |
| Support limitations: {summary}      |                                        |
+------------------------------------------------------------------------------+
| Duplicate / link / dependency summary                                         |
| Duplicate decision: {complete or blocked}                                     |
| Dependencies: {reviewed or blocked}                                           |
| Related candidate links: {ids}                                                |
+------------------------------------------------------------------------------+
| Approved Memory/Canon before-state snapshot                                   |
| Existing matching records: {n}                                                |
| Current target state: read-only preview                                       |
| This is the state before apply-promotion.                                     |
+------------------------------------------------------------------------------+
| Audit record preview                                                          |
| Promotion Audit Record: will record candidate ID, owner approval, destination,|
| evidence, provenance, target path, timestamp, and confirmation.                |
| Promotion audit records are audit-only until apply-promotion succeeds.        |
+------------------------------------------------------------------------------+
| Failure safety                                                                |
| If apply-promotion fails, Memory/Canon must remain unchanged and the audit     |
| trail must show the failure state.                                             |
+------------------------------------------------------------------------------+
| Explicit owner confirmation                                                   |
| [ ] I understand this applies the approved candidate to Memory/Canon.          |
| [Cancel / Return to Candidate]              [Disabled: Apply to Memory/Canon] |
| Disabled reason is associated with the control and shown because blockers     |
| remain visible.                                                              |
+------------------------------------------------------------------------------+
```

### Mobile wireframe

```text
+--------------------------------------+
| Apply-Promotion Confirmation         |
| Guarded handoff                      |
| Boundary warning                     |
+--------------------------------------+
| Blocked reasons                      |
| - Evidence incomplete                |
| - Duplicate unresolved               |
+--------------------------------------+
| Step 1 Candidate snapshot            |
| Step 2 Destination / target path     |
| Step 3 Evidence / provenance         |
| Step 4 Duplicate / dependency        |
| Step 5 Before-state snapshot         |
| Step 6 Audit record preview          |
| Step 7 Failure safety                |
+--------------------------------------+
| Explicit owner confirmation          |
| [ ] I understand this applies...     |
| [Cancel / Return]                    |
| [Disabled: Apply to Memory/Canon]    |
+--------------------------------------+
```

### Layout zones

- Guarded header: title, route/dialog status, strong warning copy.
- Blocked reasons: top of page, before all confirmation controls.
- Candidate snapshot: immutable source candidate summary.
- Destination/target path: explicit future memory target.
- Evidence/provenance summary and source location summary.
- Duplicate/link/dependency summary.
- Approved Memory/Canon before-state snapshot.
- Audit record preview.
- Failure safety copy.
- Explicit owner confirmation and final actions.
- Enabled final action appears only when all blockers are absent. Mockups must not show blocked examples beside an enabled-looking final Apply-Promotion button. If any blocker is visible, the final action must be disabled and its reason programmatically associated with the control.
- Structured field summary, evidence/provenance summary, source location summary, support limitations, candidate snapshot, and before-state preview display stored review metadata only. They must not trigger newly generated summaries, assistant-composed text, prose rewriting, model calls, or source-text transformation.

### Required visible labels

- `Apply-Promotion Confirmation`
- `Guarded Handoff`
- `Blocked reasons`
- `Candidate snapshot`
- `Destination / target path`
- `Evidence / provenance summary`
- `Source location summary`
- `Duplicate / link / dependency summary`
- `Approved Memory/Canon before-state snapshot`
- `Audit record preview`
- `Failure safety`
- `Explicit owner confirmation`
- `Cancel / Return to Candidate`
- `Apply to Memory/Canon`

### Required warning/boundary copy

```text
Candidates are not Memory/Canon. Promotion audit records are not Memory/Canon. Applying requires explicit owner confirmation.
```

```text
Ready means the handoff packet is complete. Memory/Canon has not changed.
```

```text
If apply-promotion fails, Memory/Canon must remain unchanged and the audit trail must show the failure state.
```

### Primary safe action

`Cancel / Return to Candidate`. This must be visually clear and available at all times.

### Disabled risky action, if applicable

`Apply to Memory/Canon` is disabled until every gate is complete:

```text
Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, before-state review, audit preview, and explicit owner confirmation.
```

### Missing states

- Blocked gates: show above confirmation; final action disabled.
- Missing before-state: block confirmation.
- Missing target path: block confirmation.
- Missing evidence/provenance: block confirmation.
- Unresolved duplicate/dependency: block confirmation.
- Audit preview unavailable: block confirmation.
- Candidate no longer approved: block confirmation and return to Candidate Detail.

### Accessibility notes

- Route-backed dialog/page title must be the first heading.
- Blocked reasons must be announced before confirmation controls.
- Final checkbox must have explicit label text, not only visual text nearby.
- Disabled final action needs programmatic disabled state and adjacent reason.
- Every blocked reason or disabled final action reason must be programmatically associated with the final disabled control using `aria-describedby` or equivalent semantic association.
- Cancel/return must precede confirm in keyboard order.

### Mobile/responsive notes

- Use a route-backed full-screen confirmation or full-screen sheet, not a tiny modal.
- Stack confirmation sections in the same order as desktop.
- Keep blocked reasons pinned near the top.
- Keep final actions visible after the explicit checkbox.
- Avoid dense two-column summaries on mobile; use labelled rows.

### What must not appear

- Routine modal styling that makes the action feel casual.
- Enabled confirm with blocked gates.
- Hidden before-state.
- Apply action without explicit owner checkbox.
- Any action to generate, rewrite, continue, outline, draft, polish, improve, expand, imitate, or revise prose.
- Claims that audit records are canon.

## 8. Cross-screen navigation model

- Dashboard row actions navigate to filtered review lists, Candidate Detail, audit records, deferred categories, or approved Memory/Canon pages.
- Candidate Detail opens Evidence Drawer from field evidence, candidate evidence, provenance, duplicate/dependency references, and read-only approved references.
- Evidence Drawer closes back to the exact originating row/control.
- Candidate Detail opens Apply-Promotion Confirmation only when a handoff packet exists.
- Apply-Promotion Confirmation cancel returns to Candidate Detail with no mutation.
- Approved Memory/Canon links from OMI are read-only references and must not make candidate content appear approved.
- Promotion audit records are navigable as audit records, not editable canon.
- Candidate Detail breadcrumb: `OMI Dashboard > Candidates > Candidate Detail`.
- Apply-Promotion Confirmation breadcrumb: `OMI Dashboard > Candidates > Candidate Detail > Apply-Promotion Handoff`.

## 9. Cross-screen boundary copy

Required recurring copy:

```text
OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.
```

```text
Owner input can be used for review, but it is not Memory/Canon by itself.
```

```text
This remains a candidate until apply-promotion is separately confirmed and completed.
```

```text
Ready means the handoff packet is complete. Memory/Canon has not changed.
```

```text
Evidence supports review; it is not canon truth until owner approval and apply-promotion are complete.
```

Standard refusal copy for any future freeform request surface:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 10. Cross-screen disabled/risky action rules

- `Apply to Memory/Canon` is disabled everywhere except a completed Apply-Promotion Confirmation surface.
- Disabled actions must include adjacent `Disabled:` reason copy.
- Disabled and blocked reasons must be programmatically associated with disabled controls, not only visually adjacent. This applies to disabled Apply-Promotion, Candidate Approval, Field Approval, Merge, Ignore Duplicate, Unsupported Destination, Approved Memory/Canon edit, and extraction/model unavailable controls.
- Unavailable future capabilities must include adjacent `Unavailable:` reason copy.
- Candidate approval must not apply Memory/Canon.
- Field approval must not approve the whole candidate.
- Evidence acceptance must not approve the candidate.
- Promotion audit record creation must not apply Memory/Canon.
- Duplicate/merge planning must not delete, overwrite, or silently merge source candidates.
- Read-only approved Memory/Canon references must not expose edit controls from OMI.
- No screen may expose model/Ollama execution controls in these mockups.

## 11. Accessibility checklist

- Page title is a real heading on every route/screen.
- Boundary banner is reachable by keyboard and screen reader.
- Status badges include text labels.
- Disabled risky actions include nearby reason text.
- Disabled risky actions and blocked reasons include programmatic reason association such as `aria-describedby` or equivalent semantic association.
- Tables have labelled columns and row-specific actions.
- Drawers/sheets trap focus and restore focus to opener.
- Confirmation screen announces blocked reasons before final actions.
- Touch targets are large enough on mobile.
- Copy is concise and does not rely on color alone.
- Keyboard order follows visual order: header, warning, filters, content, safe actions, risky disabled actions.

## 12. Mobile/responsive checklist

- Dashboard table collapses into stacked workflow rows.
- Candidate field table collapses into per-field review rows inside exactly three Candidate Detail mobile sections/tabs: `Fields`, `Evidence`, and `Readiness`.
- Right rail becomes lower panel or tab group.
- Evidence Drawer becomes a full-screen sheet.
- Apply-Promotion Confirmation becomes a full-screen route/sheet, not a small modal.
- Boundary banner remains visible near the top of every screen.
- Approved Memory/Canon snapshot remains visually separated from candidate and audit counts.
- Disabled apply reason remains adjacent to disabled action.
- No horizontal overflow for required labels.
- Final confirmation controls remain reachable without covering content.

## 13. Missing states checklist

- No owner input.
- No candidates.
- No selected candidate.
- Candidate not found.
- Unsupported candidate schema.
- Missing evidence.
- Missing provenance.
- Broken source location.
- Missing source hash or snapshot hash.
- Unresolved duplicate.
- Unresolved dependency.
- No promotion audit records.
- Promotion audit record exists but is not applied.
- No approved Memory/Canon records.
- Approved Memory/Canon before-state unavailable.
- Corrupt OMI index or corrupt record.
- Unsafe/prose-like candidate content quarantined or blocked.

## 14. Low-fidelity mockup acceptance checklist

- The four target screens are represented: OMI Dashboard, Candidate Detail, Evidence Drawer, Apply-Promotion Confirmation.
- Each screen includes purpose, proof goal, desktop wireframe, mobile wireframe where applicable, layout zones, labels, warning copy, safe action, risky disabled action, missing states, accessibility notes, responsive notes, and exclusions.
- Dashboard is a dense operational overview, not metric cards.
- Candidate Detail uses a three-zone review workspace and field table.
- Evidence Drawer has no edit, rewrite, promote, or apply controls.
- Apply-Promotion Confirmation is guarded and route/dialog backed.
- Candidate/canon separation is visible on every screen.
- Approved Memory/Canon is visually separated from candidate and promotion audit material.
- Disabled risky actions include reasons.
- Disabled risky actions include programmatically associated reasons.
- No generated prose controls appear.
- The artifact remains docs-only.

## 15. Recommended implementation order

1. OMI Dashboard
2. Candidate Detail
3. Evidence Drawer
4. Apply-Promotion Confirmation

## 16. What must not appear

- Generated prose controls.
- Rewrite controls.
- Continue controls.
- Outline controls.
- Draft controls.
- Polish controls.
- Improve controls.
- Expand controls.
- Imitate controls.
- Revise story-prose controls.
- Story-prose-production controls.
- Model/Ollama controls.
- Enabled dashboard apply-to-Memory/Canon.
- Candidate approval that mutates Memory/Canon.
- Evidence acceptance that creates canon.
- Promotion audit records presented as approved Memory/Canon.
- Owner input presented as Memory/Canon.
- Pending candidates presented as approved Memory/Canon.
- Metric-card dashboard as the primary dashboard form.
- Decorative hero layout.
- Nested card-heavy UI.
- Hidden blocked reasons on confirmation.

## 17. Next Impeccable prompt

Use this prompt for the first Impeccable mockup pass:

```text
Create low-fidelity mockups for the first OMI screens using docs/roadmap/ux/OMI-low-fi-wireframes-v1.md as the source of truth.

Targets:
1. OMI Dashboard
2. Candidate Detail
3. Evidence Drawer
4. Apply-Promotion Confirmation

Do not change backend behavior.
Do not create candidates.
Do not mutate Memory/Canon.
Do not call models/Ollama.
Do not run apply-promotion.
Do not add generated prose features.
Do not add rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.
Only improve UI clarity, layout, accessibility, copy, empty states, warning states, and responsive behavior.
Preserve analysis-only, candidate-first, evidence/provenance-backed, owner-controlled boundaries.

Design direction:
- Build dense operational review UI, not marketing UI.
- Use a calm app/tool workspace.
- Keep OMI review material, candidates, promotion audit records, and approved Memory/Canon visually separate.
- Show disabled risky actions with reasons.
- Make evidence/provenance and owner confirmation unmistakable.
- Treat apply-promotion confirmation as a guarded route-backed confirmation, not a routine modal.
```
