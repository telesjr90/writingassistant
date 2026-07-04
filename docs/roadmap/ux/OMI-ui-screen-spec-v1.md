# OMI UI Screen Spec v1

Status: planning-only screen specification. Runtime implementation is future work.

This document turns the approved OMI Workflow Design v1 into concrete UI screens for later Impeccable shape review and low-fidelity mockups.

## 1. Purpose

OMI UI Screen Spec v1 defines the first screen-level plan for the project-local Organize My Idea workflow.

The screen set must help the owner move from owner-authored raw ideas into grouped, evidence-backed, candidate-first review packets without creating canon, writing prose, mutating Memory/Canon, calling models, creating durable project truth, or running apply-promotion.

First implementation source:

- Raw ideas only.
- Raw ideas are owner-authored project-local planning input.
- OMI can organize raw ideas into reviewable candidates in later implementation work, but this spec does not create candidates or implement extraction.

## 2. Product boundaries

OMI remains:

- Analysis-only.
- Project-local.
- Candidate-first.
- Owner-controlled.
- Evidence/provenance-backed.
- No-prose.
- Separate from approved Memory/Canon.
- Separate from apply-promotion.

OMI must not:

- Write, rewrite, continue, imitate, polish, improve, expand, revise, outline, draft, or extend story prose.
- Create durable canon.
- Mutate Memory/Canon.
- Mutate `bible.json`, `storyform.json`, scenes, notes, materials, owner memory, `memory/*.json`, training data, JSONL records, dataset manifests, or model artifacts.
- Treat candidate persistence, queue presence, confidence, extraction output, NotebookLM output, model output, or a promotion record as approval.
- Automatically promote anything.
- Hide the owner confirmation boundary.

Required standard refusal copy:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## Copy System

Preferred noun-qualified labels:

- Use noun-qualified labels that keep state and object type together, such as `Candidate: Pending Review`, `Candidate: Owner Approved`, `Promotion Audit Record`, `Not Applied to Memory/Canon`, and `Approved Memory/Canon`.
- Prefer `Owner Input` for owner-authored raw idea material in UI labels.

Candidate/canon separation language:

- Use: "OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step."
- Use: "Owner input can be used for review, but it is not Memory/Canon by itself."
- Use: "This remains a candidate until apply-promotion is separately confirmed and completed."

Handoff vs mutation wording:

- Use `handoff` for promotion readiness and apply-promotion preparation.
- Reserve `mutation`, `applied`, and `Memory/Canon changed` wording for the separate apply-promotion flow.
- Use: "Ready means the handoff packet is complete. Memory/Canon has not changed."

Disabled-state copy pattern:

- Start disabled copy with `Disabled:` when the action is present but unavailable.
- Start unavailable capability copy with `Unavailable:` when the action is out of scope for this version.
- State the missing requirement directly and avoid implying a hidden workaround.

Empty-state copy pattern:

- State what is absent.
- State the safe next source of user action.
- Reaffirm candidates, promotion audit records, and Memory/Canon boundaries when relevant.

Decision-control verb pattern:

- Use explicit owner-review verbs: `Approve Candidate for Handoff`, `Reject Candidate`, `Needs Revision`, `Archive Candidate`, `Request Evidence`, and `Mark Uncertain`.
- Use planning verbs for duplicate actions: `Treat as New Candidate`, `Plan Merge with Existing`, `Ignore as Duplicate`, and `Needs Owner Clarification`.
- Use handoff verbs for promotion actions: `Create Promotion Audit Record` and `Open Apply-Promotion Handoff`.

## 3. Screen list

Primary OMI screens and panels:

- OMI Dashboard screen.
- Raw Idea Detail screen.
- Extraction Review screen.
- Candidate Group Review screen.
- Candidate Detail screen.
- Field Approval Rows.
- Evidence Drawer.
- Duplicate / Merge / Ignore / Needs Clarification Panel.
- Promotion Readiness Panel.
- Apply-Promotion Confirmation handoff screen.
- Approved Memory/Canon Evidence View.
- Deferred / Not Included Yet Categories View.

Shared states:

- Empty states.
- Warning states.
- Disabled states.
- Required status labels and badges.

## 4. Global OMI layout

OMI should use a calm review-workspace layout, not a writing surface.

Recommended layout:

- Left project navigation: existing project/workspace navigation.
- OMI local navigation: Dashboard, Raw Ideas, Extraction Review, Candidate Groups, Promotion Readiness, Deferred Categories.
- Main review column: selected screen content.
- Right contextual rail or drawer trigger: evidence, provenance, dependencies, warnings.
- Persistent boundary banner near the top of OMI surfaces.

Global visible sections:

- Active project label.
- OMI boundary banner.
- Candidate/canon status strip.
- Project-local source indicator.
- Counts for raw ideas, candidates, grouped review packets, blocked items, promotion-ready items, promotion audit records, and approved Memory/Canon links.
- Filter/search controls where lists exist.

Global owner decision controls:

- Approve Candidate for Handoff.
- Reject Candidate.
- Needs Revision.
- Archive Candidate.
- Request Evidence.
- Mark Uncertain.
- Link candidate.
- Treat as New Candidate.
- Plan Merge with Existing.
- Ignore as Duplicate.
- Needs Owner Clarification.

Global disabled actions:

- Apply-promotion remains unavailable unless a valid apply-promotion handoff exists; use: "Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation."
- Promotion readiness disabled until owner approval, destination, evidence/provenance, candidate links/dependencies, duplicate decision, and final confirmation requirements are satisfied.
- Any prose-production or rewrite-like action absent or visibly refused.

Global candidate/canon boundary copy:

```text
OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.
```

Global mockup notes:

- Use dense but readable review tooling, with tables, rows, drawers, and segmented filters.
- Avoid marketing hero layout.
- Avoid nested cards.
- Keep status and evidence visible without decorative clutter.
- Use badges for state, not paragraphs.

Global data-testid planning targets:

- `omi-boundary-banner`
- `omi-active-project-label`
- `omi-candidate-canon-status`
- `omi-source-scope-label`
- `omi-evidence-drawer-trigger`
- `omi-no-prose-boundary-copy`

What must not happen:

- Opening OMI must not create candidates.
- Opening OMI must not mutate approved Memory/Canon.
- Switching filters must not change owner decisions.
- Confidence or grouping must not imply truth.

## 5. OMI Dashboard screen

Purpose:

- Give the owner a project-local overview of raw ideas, candidate review status, blocked work, duplicate decisions, promotion readiness, and deferred categories.

Entry point:

- Project navigation `OMI`.
- Project overview candidate/review summary links.
- Review queue link to OMI source candidate.

User goal:

- Understand what needs review and choose the next safe OMI task.

Visible sections:

- Header with active project and `OMI Dashboard`.
- Boundary banner.
- Raw idea summary.
- Candidate status summary.
- Grouped review summary.
- Duplicate/merge decision summary.
- Promotion readiness summary.
- Promotion audit records summary.
- Deferred / not included categories summary.
- Approved Memory/Canon unchanged snapshot.
- Warning and health summary.

Primary actions:

- Open raw idea.
- Review extraction output.
- Review grouped candidates.
- Open blocked candidate.
- Open promotion readiness.
- Open deferred categories.

Disabled actions:

- `Apply to Memory/Canon` remains disabled from the dashboard.
- `Run extraction` disabled unless a later implementation explicitly authorizes extraction.
- No model/Ollama action exists.

Warning copy:

```text
Dashboard counts show review status only. Candidates, groups, and promotion records are not canon.
```

Evidence/provenance display:

- Show compact counts: evidence present, evidence missing, provenance present, source locators missing.
- Preferred labels: `Evidence Linked`, evidence missing, `Provenance Linked`, source locations missing.
- Clicking a count opens the relevant filtered review list or evidence drawer.

Owner decision controls:

- None inline except quick filters. Owner decisions happen on detail/review screens.

Candidate/canon boundary copy:

```text
OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.
```

Mockup notes:

- Use a compact operational dashboard with one status row per workflow area.
- Keep category counts visually separated: raw ideas, candidates, promotion audit records, approved records.

Data-testid planning targets:

- `omi-dashboard`
- `omi-dashboard-raw-idea-count`
- `omi-dashboard-candidate-count`
- `omi-dashboard-group-count`
- `omi-dashboard-promotion-ready-count`
- `omi-dashboard-approved-memory-snapshot`

What must not happen:

- Dashboard load must not infer approved records from candidates.
- Dashboard must not display pending candidates as approved Memory/Canon.

## 6. Raw Idea Detail screen

Purpose:

- Show one owner-authored raw idea, its source status, linked candidates, and readiness for later extraction/review.

Entry point:

- Dashboard raw idea list.
- Raw Ideas tab.
- Candidate detail source link.

User goal:

- Inspect the owner-authored idea and understand what candidates, if any, are linked to it.

Visible sections:

- Raw idea header with `Owner Input` badge.
- Project-local source metadata.
- Owner-authored raw idea body.
- Linked candidates list.
- Existing owner decision/status.
- Evidence/provenance summary.
- Safety flags.
- Extraction readiness placeholder.
- Candidate/canon boundary note.

Primary actions:

- Edit owner-authored raw idea when runtime support allows owner editing.
- Open linked candidate.
- Open extraction review for this idea.
- Archive raw idea.

Disabled actions:

- Generate prose.
- Rewrite idea.
- Continue idea.
- Promote raw idea directly.
- Apply raw idea to Memory/Canon.

Warning copy:

```text
Owner input can be used for review, but it is not Memory/Canon by itself.
```

Evidence/provenance display:

- Show `created_by`, `source_type`, `created_at`, `updated_at`, source hash if present, and linked candidate IDs.
- Evidence drawer opens from linked candidate rows, not from raw idea as approved truth.

Owner decision controls:

- Archive raw idea.
- Add owner note.
- Mark not ready for extraction.
- Mark ready for future extraction review.

Candidate/canon boundary copy:

```text
Owner input can be used for review, but it is not Memory/Canon by itself.
```

Mockup notes:

- The raw idea body should read as stored owner input, not a prompt composer.
- Avoid assistant-like text areas or submit prompts.

Data-testid planning targets:

- `omi-raw-idea-detail`
- `omi-raw-idea-owner-input`
- `omi-raw-idea-linked-candidates`
- `omi-raw-idea-provenance`
- `omi-raw-idea-direct-promotion-disabled`

What must not happen:

- Saving or viewing a raw idea must not be treated as an AI request.
- Raw idea detail must not offer assistant writing controls.

## 7. Extraction Review screen

Purpose:

- Plan the review surface for candidate extraction results derived from owner raw ideas in a later implementation.

Entry point:

- Raw Idea Detail `Open extraction review`.
- Dashboard `Review extraction output`.

User goal:

- Review proposed candidate groups before any candidates are approved or promoted.

Visible sections:

- Source raw idea summary.
- Extraction status: `Not run`, `Unavailable`, `Review required`, or `Not Available Yet`.
- Proposed candidate groups.
- Deferred categories.
- Evidence/provenance summary per proposed group.
- Warning area for unsupported categories, insufficient evidence, unsafe prose-like output, or source locator gaps.

Primary actions:

- Open proposed group.
- Mark group Needs Owner Clarification.
- Mark group not included.
- Request Evidence.

Disabled actions:

- Run model/Ollama.
- Generate candidates from this screen until a later implementation task authorizes it.
- Approve all automatically.
- Apply extraction result to Memory/Canon.

Disabled-state copy:

```text
Unavailable: extraction/model actions are not part of this version.
```

Warning copy:

```text
Extraction output, when available, is candidate planning material only. It is not truth and cannot update Memory/Canon from this screen.
```

Evidence/provenance display:

- Each group row shows source raw idea ID, candidate source type, evidence count, provenance status, and unsupported/deferred status.
- Click opens Evidence Drawer scoped to the group.

Owner decision controls:

- Include for review.
- Needs Owner Clarification.
- Defer category.
- Exclude unsafe/non-supported output.

Candidate/canon boundary copy:

```text
Including a group for review creates review work only. It does not approve or promote any candidate.
```

Mockup notes:

- Treat this as a triage table with clear fail-closed unavailable states.
- Show future categories as disabled rows, not hidden capabilities.

Data-testid planning targets:

- `omi-extraction-review`
- `omi-extraction-status`
- `omi-extraction-group-row`
- `omi-extraction-deferred-category-row`
- `omi-extraction-apply-disabled`

What must not happen:

- Extraction review must not call live models in the first implementation.
- Unsafe prose-like output must not be shown as usable story text.

## 8. Candidate Group Review screen

Purpose:

- Support grouped candidate review before field-level approval or promotion readiness.

Entry point:

- Extraction Review group row.
- Dashboard grouped candidate count.
- Candidate Detail related group link.

User goal:

- Decide how a cluster of related candidates should be reviewed, linked, merged, ignored, clarified, or split before approval.

Visible sections:

- Group header with candidate type/category.
- Source raw idea and provenance summary.
- Group confidence label: `confidence is not truth`.
- Candidate rows.
- Candidate dependency/link map.
- Duplicate/merge panel.
- Evidence summary.
- Deferred/not included sibling categories.
- Group warning area.

Primary actions:

- Open candidate detail.
- Link candidates/dependencies.
- Mark duplicate decision.
- Split candidate.
- Request Evidence.
- Send candidate to field approval.
- Mark group needs clarification.

Disabled actions:

- Group approve as canon.
- Bulk promote.
- Bulk apply to Memory/Canon.
- Auto-merge without owner decision.

Warning copy:

```text
Grouping helps organize review. It does not approve candidates or create canon.
```

Evidence/provenance display:

- Group-level evidence counts plus per-candidate evidence badges.
- Original wording opens in Evidence Drawer on click.

Owner decision controls:

- Treat as New Candidate.
- Plan Merge with Existing.
- Ignore as Duplicate.
- Needs Owner Clarification.
- Link dependency.
- Mark Uncertain.

Candidate/canon boundary copy:

```text
Candidate links and duplicate decisions update review metadata only. They do not mutate approved Memory/Canon.
```

Mockup notes:

- Use a master-detail list or table with a right-side relationship panel.
- Show dependencies as simple rows/edges first; avoid complex graph visualization in v1 mockups.

Data-testid planning targets:

- `omi-candidate-group-review`
- `omi-candidate-group-row`
- `omi-candidate-dependency-row`
- `omi-candidate-group-evidence-button`
- `omi-group-bulk-promote-disabled`

What must not happen:

- A group action must not approve every field implicitly.
- Merge planning must not delete source candidates.

## 9. Candidate Detail screen

Purpose:

- Provide the full review surface for one candidate, including structured fields, evidence, provenance, owner decisions, duplicates, links/dependencies, and promotion readiness.

Entry point:

- Candidate Group Review.
- OMI Dashboard blocked/ready candidate link.
- Raw Idea Detail linked candidate.
- Review Queue candidate link.

User goal:

- Decide whether this candidate is acceptable, needs revision/evidence, should merge with something, should be rejected, or is ready for promotion handoff.

Visible sections:

- Candidate header with ID, type, status, destination, source raw idea, and project-local label.
- Candidate/canon boundary banner.
- Structured candidate fields.
- Field Approval Rows.
- Evidence/provenance panel.
- Original wording click targets.
- Duplicate / Merge / Ignore / Needs Clarification Panel.
- Candidate links/dependencies.
- Owner decision panel.
- Promotion Readiness Panel.
- Promotion audit record snapshot if present.
- Approved Memory/Canon links if already applied by a separate apply-promotion step.

Primary actions:

- Approve field.
- Reject field.
- Mark field needs evidence.
- Mark Uncertain.
- Approve Candidate for Handoff.
- Reject Candidate.
- Needs Revision.
- Archive Candidate.
- Create promotion readiness handoff when all gates pass.

Disabled actions:

- Apply-promotion until owner confirmation handoff.
- Promote without destination.
- Promote without evidence/provenance.
- Promote with unresolved duplicate choice.
- Promote with unresolved dependencies.
- Generate replacement text.

Warning copy:

```text
Owner approval prepares this candidate for a future handoff. It does not update Memory/Canon.
```

Evidence/provenance display:

- Field-level evidence status where available.
- Candidate-level provenance chain.
- Click field or evidence badge to open Evidence Drawer with original wording and source locator.

Owner decision controls:

- Per-field: approve, reject, needs evidence, uncertain.
- Candidate-level: Approve Candidate for Handoff, Reject Candidate, Needs Revision, Archive Candidate.
- Duplicate-level: Treat as New Candidate, Plan Merge with Existing, Ignore as Duplicate, Needs Owner Clarification.
- Dependency-level: add link, remove pending link, block until dependency reviewed.

Candidate/canon boundary copy:

```text
This remains a candidate until apply-promotion is separately confirmed and completed.
```

Mockup notes:

- Make the field table the main interaction.
- Keep evidence visible as drawers or expandable rows, not buried below the fold.

Data-testid planning targets:

- `omi-candidate-detail`
- `omi-candidate-boundary-copy`
- `omi-candidate-field-row`
- `omi-candidate-owner-decision`
- `omi-candidate-dependencies`
- `omi-candidate-promotion-readiness`

What must not happen:

- Field approval must not silently approve the whole candidate.
- Candidate approval must not set `promoted` or create approved memory.

## 10. Field Approval Rows

Purpose:

- Allow owner planning for field-level approval, rejection, uncertainty, and evidence requirements inside a candidate.

Entry point:

- Candidate Detail structured fields.
- Candidate Group Review inline expansion.

User goal:

- Review each candidate claim independently before candidate-level approval.

Visible sections:

- Field name.
- Proposed value.
- Field status.
- Evidence badge.
- Provenance badge.
- Duplicate/dependency badge when relevant.
- Owner note.
- Original wording trigger.

Primary actions:

- Approve field.
- Reject field.
- Mark needs evidence.
- Mark Uncertain.
- Add owner note.
- Open evidence.

Disabled actions:

- Approve field with missing required evidence unless owner explicitly records an evidence-unavailable reason.
- Promote field directly.
- Copy field to Memory/Canon.

Disabled-state copy:

```text
Disabled: this field needs evidence, or the owner must record why evidence is unavailable.
```

Warning copy:

```text
Field approval applies only inside this candidate. No field is copied to Memory/Canon from this row.
```

Evidence/provenance display:

- Evidence badge states `Evidence Linked`, `Evidence Needed`, `Insufficient Evidence`, `Original Wording Available`, or `Source Location Missing`.
- Click opens Evidence Drawer scoped to that field.

Owner decision controls:

- Segmented control: `Approve`, `Needs evidence`, `Uncertain`, `Reject`.
- Optional owner note input.

Candidate/canon boundary copy:

```text
No field becomes canon from this row.
```

Mockup notes:

- Rows should be compact and scannable.
- Long proposed values wrap without changing row controls.

Data-testid planning targets:

- `omi-field-approval-row`
- `omi-field-status-control`
- `omi-field-evidence-trigger`
- `omi-field-owner-note`
- `omi-field-direct-promote-disabled`

What must not happen:

- Field rows must not expose rewrite/improve controls.
- Field rows must not save generated prose as a value.

## 11. Evidence Drawer

Purpose:

- Show evidence, provenance, source locator, and original wording for a selected idea, group, candidate, field, promotion record, or approved Memory/Canon item.

Entry point:

- Evidence badge.
- Original wording link.
- Provenance badge.
- Approved Memory/Canon Evidence View.

User goal:

- Verify where a claim came from and what source wording or owner note supports it.

Visible sections:

- Drawer title and scope.
- Source type and source locator.
- Evidence summary.
- Original wording/excerpt when safe and short.
- Quote exactness label.
- Provenance chain.
- Confidence label.
- Limitations/ambiguity notes.
- Related candidate/promotion/approved record IDs.

Primary actions:

- Copy source locator.
- Open source record when route exists.
- Add owner evidence note.
- Mark evidence insufficient.
- Close drawer.

Disabled actions:

- Edit source prose.
- Rewrite evidence.
- Promote from drawer.
- Apply to Memory/Canon.

Warning copy:

```text
Viewing evidence does not copy source text into Memory/Canon.
```

Evidence/provenance display:

- Required fields to plan for: `evidence_id`, `source_type`, `source_path`, `source_scene_id`, `source_text_excerpt`, offsets/line locators when available, `quote_exact`, `summary`, `supports_claim`, `confidence`, and provenance fields.

Owner decision controls:

- Mark evidence accepted for review.
- Mark insufficient evidence.
- Add owner note.

Candidate/canon boundary copy:

```text
Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
```

Mockup notes:

- Drawer should be keyboard reachable and dismissible.
- Avoid long raw source dumps; show short excerpts and locators.

Data-testid planning targets:

- `omi-evidence-drawer`
- `omi-evidence-source-locator`
- `omi-evidence-original-wording`
- `omi-evidence-provenance-chain`
- `omi-evidence-insufficient-control`

What must not happen:

- Drawer must not expose source editing.
- Drawer must not invent evidence when missing.

## 12. Duplicate / Merge / Ignore / Needs Clarification Panel

Purpose:

- Make duplicate and near-duplicate choices explicit before candidate approval and promotion readiness.

Entry point:

- Candidate Detail.
- Candidate Group Review.
- Promotion Readiness blocked reason.

User goal:

- Choose whether the candidate is new, should merge into an existing candidate/approved record, should be ignored as duplicate, or needs owner clarification.

Visible sections:

- Duplicate status.
- Possible duplicate candidates.
- Possible approved Memory/Canon matches.
- Alias/same-entity warning.
- Relationship/event/thread duplicate checks where relevant.
- Owner decision controls.
- Merge target selector.
- Clarification note.

Primary actions:

- Treat as New Candidate.
- Plan Merge with Existing.
- Ignore as Duplicate.
- Needs Owner Clarification.
- Mark Uncertain.
- Open possible match.

Disabled actions:

- Merge into approved Memory/Canon directly.
- Delete candidate because duplicate is suspected.
- Approve promotion readiness with unresolved duplicate decision.

Disabled-state copy:

```text
Disabled: choose a merge target first.
```

```text
Disabled: add an owner note before ignoring a high-risk duplicate.
```

Warning copy:

```text
Duplicate decisions update review metadata only. They do not merge, overwrite, or delete approved records.
```

Evidence/provenance display:

- Show evidence/source comparison for candidate and possible match.
- Original wording available for each side when present.

Owner decision controls:

- Radio/segmented control for the four required decisions.
- Merge target picker.
- Owner note required for `Needs Owner Clarification`.

Candidate/canon boundary copy:

```text
Merge planning is not apply-promotion and does not mutate an existing approved record.
```

Mockup notes:

- Use side-by-side comparison for the selected possible match.
- Keep the four decisions visible at all times.

Data-testid planning targets:

- `omi-duplicate-panel`
- `omi-duplicate-create-new`
- `omi-duplicate-merge-existing`
- `omi-duplicate-ignore`
- `omi-duplicate-needs-clarification`
- `omi-duplicate-match-row`

What must not happen:

- No automatic merge.
- No destructive dedupe.
- No approved record overwrite.

## 13. Promotion Readiness Panel

Purpose:

- Show whether a candidate is ready for an apply-promotion handoff while preserving that readiness is not canon.

Entry point:

- Candidate Detail.
- OMI Dashboard readiness summary.
- Review Queue candidate row.

User goal:

- Understand blockers and prepare a complete handoff packet.

Visible sections:

- Readiness status: `Promotion Blocked`, `Ready for Apply-Promotion Handoff`, `Promotion Audit Record`, `Not Applied to Memory/Canon`.
- Required gates:
  - Owner approval.
  - Allowed destination.
  - Evidence reviewed.
  - Provenance present.
  - Duplicate decision resolved.
  - Candidate links/dependencies resolved or intentionally deferred.
  - No-prose boundary passed.
  - Final confirmation required.
- Blocked reasons.
- Promotion audit record snapshot if present.
- Apply-promotion handoff link when eligible.

Primary actions:

- Open blocker.
- Create Promotion Audit Record when runtime supports record-only promotion.
- Open Apply-Promotion Handoff when eligible.

Disabled actions:

- Apply promotion while any gate is missing.
- Apply promotion from OMI without separate confirmation screen.
- Promote unsupported destination.

Disabled-state copy:

```text
Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.
```

```text
Disabled: this destination is not available for apply-promotion.
```

Warning copy:

```text
Ready means the handoff packet is complete. Memory/Canon has not changed.
```

Evidence/provenance display:

- Gate rows link to evidence drawer and provenance details.

Owner decision controls:

- Confirm readiness review.
- Add owner note.
- Return to candidate decision.

Candidate/canon boundary copy:

```text
Only the separate apply-promotion flow can mutate approved Memory/Canon, and only after explicit owner confirmation.
```

Mockup notes:

- Use a checklist with clear pass/block states.
- Put the disabled apply action and explanation close together.

Data-testid planning targets:

- `omi-promotion-readiness-panel`
- `omi-promotion-readiness-gate`
- `omi-promotion-blocked-reasons`
- `omi-apply-promotion-handoff`
- `omi-apply-promotion-disabled`

What must not happen:

- Promotion readiness must not write `memory/*.json`.
- Promotion audit record must not be displayed as approved canon.

## 14. Apply-Promotion Confirmation handoff screen

Purpose:

- Plan the boundary screen that receives a ready candidate/promotion packet and requires explicit owner confirmation before durable mutation by apply-promotion.

Entry point:

- Promotion Readiness Panel handoff link.
- Review Queue apply-promotion action.

User goal:

- Confirm or cancel the future apply-promotion operation with full audit visibility.

Visible sections:

- Candidate snapshot.
- Destination and target path.
- Evidence/provenance summary.
- Source locator summary.
- Duplicate/link/dependency summary.
- Approved Memory/Canon before-state snapshot.
- Explicit owner confirmation checkbox or phrase.
- Audit record preview.
- Failure safety copy.

Primary actions:

- Confirm apply-promotion only after explicit confirmation.
- Cancel and return to candidate.

Disabled actions:

- Confirm disabled until all required confirmation controls are complete.
- Confirm disabled if candidate is not ready or destination is unsupported.

Disabled-state copy:

```text
Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.
```

```text
Disabled: this destination is not available for apply-promotion.
```

Warning copy:

```text
This is the only step that may apply an approved candidate to Memory/Canon. Review all evidence and target details before confirming.
```

Evidence/provenance display:

- Summaries must link back to Evidence Drawer or full evidence view.
- Must show source candidate ID, promotion record ID if present, destination, target file/path, owner approval, and timestamps.

Owner decision controls:

- Explicit confirmation checkbox/phrase.
- Cancel.

Candidate/canon boundary copy:

```text
Candidates, queue entries, confidence, and promotion records are not approval by themselves. This explicit confirmation is required.
```

Mockup notes:

- This should feel like a guarded confirmation page/dialog, not a routine save form.
- Put disabled/fail-closed reasons above the confirmation action.

Data-testid planning targets:

- `apply-promotion-confirmation-handoff`
- `apply-promotion-candidate-snapshot`
- `apply-promotion-owner-confirmation`
- `apply-promotion-target-summary`
- `apply-promotion-confirm-disabled`

What must not happen:

- OMI must not bypass this screen.
- Confirmation must not be inferred from review queue approval or candidate approval.

## 15. Approved Memory/Canon Evidence View

Purpose:

- Show approved Memory/Canon evidence and links without allowing OMI to treat approved records as editable candidate targets.

Entry point:

- Candidate Detail approved record link.
- Duplicate panel possible approved match.
- Project Memory/Canon category page.

User goal:

- Compare candidate claims with already approved records and inspect provenance.

Visible sections:

- Approved record header with `Approved Memory/Canon` badge.
- Record type/category.
- Approved status and timestamps.
- Source candidate IDs.
- Promotion record IDs.
- Evidence and provenance links.
- Related approved records.
- Candidate backlog link.
- Health warnings.

Primary actions:

- Open evidence drawer.
- Open source candidate.
- Open promotion audit record.
- Return to OMI duplicate/candidate review.

Disabled actions:

- Edit approved record from OMI.
- Merge candidate into approved record from OMI.
- Rewrite approved text.
- Apply candidate without confirmation.

Disabled-state copy:

```text
Disabled: approved records are read-only from OMI.
```

Warning copy:

```text
Approved Memory/Canon is read-only from OMI. Candidate changes require a separate apply-promotion flow.
```

Evidence/provenance display:

- Must preserve source candidate IDs, promotion record IDs, evidence IDs, source locators, and provenance chain.

Owner decision controls:

- Mark as possible duplicate target in OMI review metadata.
- Add OMI review note.

Candidate/canon boundary copy:

```text
Linking a candidate to this approved record does not change the approved record.
```

Mockup notes:

- This view should look distinct from candidate detail through labels and disabled editing affordances.

Data-testid planning targets:

- `approved-memory-evidence-view`
- `approved-memory-read-only-label`
- `approved-memory-source-candidate-link`
- `approved-memory-promotion-record-link`
- `approved-memory-omi-edit-disabled`

What must not happen:

- OMI must not edit approved records.
- Pending candidates must not appear inside approved record lists as approved.

## 16. Deferred / Not Included Yet Categories View

Purpose:

- Make unsupported, deferred, and post-MVP candidate categories visible without implying they are implemented.

Entry point:

- OMI Dashboard deferred summary.
- Extraction Review deferred category row.
- Candidate Group Review sibling category notice.

User goal:

- Understand which categories are not included in first OMI raw-idea implementation and why.

Visible sections:

- Included in first implementation.
- Deferred story-knowledge categories.
- Advanced analysis categories.
- Runtime/model unavailable categories.
- Reason and future dependency per category.
- Boundary warnings.

Primary actions:

- Filter OMI views to included categories.
- Open relevant roadmap reference when available.

Disabled actions:

- Enable deferred category.
- Run advanced analysis.
- Create unsupported candidate type.

Disabled-state copy:

```text
Unavailable: extraction/model actions are not part of this version.
```

Warning copy:

```text
Deferred categories are shown for planning clarity only. They are not available actions and do not create candidates.
```

Evidence/provenance display:

- None required beyond roadmap/source reference links.

Owner decision controls:

- None in v1 beyond visibility/filter preferences.

Candidate/canon boundary copy:

```text
Only unavailable categories match this view. These categories are shown for planning clarity and cannot create candidates yet.
```

Mockup notes:

- Use a plain status table, not feature cards.
- Show `Not Available Yet`, `Post-MVP`, `Unavailable in This Version`, or `Needs separate task`.

Data-testid planning targets:

- `omi-deferred-categories-view`
- `omi-deferred-category-row`
- `omi-category-not-implemented-badge`
- `omi-deferred-create-disabled`

What must not happen:

- Deferred categories must not appear as active filters with executable behavior.
- Advanced Dramatica/NCP/Subtxt/dramatica-flow execution must not be exposed.

## 17. Empty states

Required empty states:

- No owner input.
- Raw idea has no linked candidates.
- No extraction review available.
- No candidate groups.
- No candidates.
- No evidence.
- No promotion-ready candidates.
- No promotion audit records.
- No approved Memory/Canon records.
- Deferred categories only.

Empty state copy examples:

```text
No owner input yet. Add owner-authored planning material before OMI can organize review candidates.
```

```text
No candidates yet. Candidates appear only after owner-controlled review or a separately authorized extraction flow.
```

```text
No evidence linked. Add or review evidence before this can be ready for apply-promotion.
```

```text
No candidates are ready for handoff. Resolve approval, destination, evidence, provenance, duplicate, and dependency blockers first.
```

```text
No promotion audit records yet. Audit records are created only after owner approval and final confirmation.
```

```text
No approved Memory/Canon records yet. Candidates and promotion audit records are separate from approved truth.
```

```text
Only unavailable categories match this view. These categories are shown for planning clarity and cannot create candidates yet.
```

What must not happen:

- Empty states must not suggest generating prose.
- Empty states must not auto-run extraction.

## 18. Warning states

Required warning states:

- Candidate is not canon.
- Queue presence is not approval.
- Confidence is not truth.
- Promotion Audit Record.
- Not Applied to Memory/Canon.
- Insufficient evidence.
- Source location missing.
- Provenance missing.
- Duplicate unresolved.
- Dependencies unresolved.
- Destination missing or unsupported.
- Runtime/model unavailable in this version.
- Deferred category.
- Approved Memory/Canon read-only from OMI.
- Cross-project leakage warning if active project scope cannot be verified.

Required warning copy:

```text
Candidate persistence is not canon.
```

```text
Queue presence is not approval.
```

```text
Confidence is not truth.
```

```text
Promotion audit records are audit-only until apply-promotion succeeds.
```

What must not happen:

- Warnings must not be dismissible in a way that removes the safety boundary from the workflow.

## 19. Disabled states

Required disabled states:

- Apply-promotion remains unavailable until owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation gates pass.
- Candidate approval disabled when required field decisions are unresolved, unless the owner records a deliberate uncertainty/evidence-unavailable reason.
- Merge disabled without a selected target.
- Ignore as Duplicate disabled without owner note when the system marks a high-risk duplicate.
- Extraction/model controls disabled or absent in first implementation.
- Deferred categories disabled.
- Approved Memory/Canon edits disabled from OMI.
- Prose-generation controls absent or refused.

Disabled-state copy example:

```text
Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.
```

```text
Disabled: required field decisions are still unresolved.
```

```text
Disabled: this field needs evidence, or the owner must record why evidence is unavailable.
```

```text
Disabled: choose a merge target first.
```

```text
Disabled: add an owner note before ignoring a high-risk duplicate.
```

```text
Unavailable: extraction/model actions are not part of this version.
```

```text
Disabled: approved records are read-only from OMI.
```

```text
Disabled: this destination is not available for apply-promotion.
```

What must not happen:

- Disabled controls must not silently run through alternate keyboard shortcuts or secondary menus.

## 20. Required status labels and badges

OMI source labels:

- `Owner Input`
- `Project-Local`

Candidate labels:

- `Candidate`
- `Candidate: Pending Review`
- `Owner Review`
- `Candidate: Owner Approved`
- `Rejected Candidate`
- `Needs Revision`
- `Archived Candidate`
- `Uncertain`
- `Duplicate Unresolved`
- `Dependencies Unresolved`

Evidence/provenance labels:

- `Evidence Linked`
- `Evidence Needed`
- `Insufficient Evidence`
- `Original Wording Available`
- `Source Location Missing`
- `Provenance Linked`
- `Provenance Missing`

Promotion labels:

- `Promotion Blocked`
- `Ready for Apply-Promotion Handoff`
- `Promotion Audit Record`
- `Not Applied to Memory/Canon`
- `Apply-Promotion Required`

Approved Memory/Canon labels:

- `Approved Memory/Canon`
- `Read-Only from OMI`

Boundary labels:

- `Candidate persistence is not canon`
- `Queue presence is not approval`
- `Confidence is not truth`
- `Not Available Yet`
- `Unavailable in This Version`
- `Support Data, Not Canon`

## 21. Required copy boundaries

Required no-prose copy:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

Required candidate/canon copy:

```text
OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.
```

Required promotion copy:

```text
Ready means the handoff packet is complete. Memory/Canon has not changed.
```

Required apply-promotion copy:

```text
Only apply-promotion can mutate approved Memory/Canon, and only after explicit owner confirmation.
```

Required evidence copy:

```text
Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
```

Forbidden copy patterns:

- `Generate scene`
- `Rewrite`
- `Continue`
- `Improve prose`
- `Polish text`
- `Draft chapter`
- `Expand this`
- `Make canon`
- `Auto-promote`
- `Approve all as canon`
- `Fix story prose`

## 22. Accessibility requirements

Required accessibility behavior:

- Every status badge must have text, not color-only meaning.
- Every icon-only action must have an accessible name and tooltip.
- Evidence Drawer must trap focus while open and restore focus on close.
- Disabled actions must expose an explanation in adjacent text or `aria-describedby`.
- Tables/lists must have meaningful row labels.
- Field Approval Rows must be operable by keyboard.
- Warning banners must use semantic alert/status patterns where appropriate.
- Confirmation screen must make the destructive/durable nature of apply-promotion clear before the confirm control.
- Touch targets should be at least 44px on mobile.
- Body text contrast should meet WCAG AA.
- Reduced-motion preferences must be respected for drawer transitions.

What must not happen:

- Safety warnings must not rely on red/green color alone.
- Drawer content must not become unreachable by keyboard.

## 23. Mobile/responsive requirements

Mobile layout:

- Collapse OMI local navigation into tabs or a menu.
- Use stacked sections for dashboard summaries.
- Candidate lists become single-column rows.
- Field Approval Rows stack field value, status, evidence, and controls.
- Evidence Drawer becomes a full-screen sheet.
- Promotion Readiness gates become a vertical checklist.
- Apply-Promotion Confirmation must keep target, evidence, and confirmation visible before the final action.

Responsive requirements:

- No text overlap in badges, buttons, rows, or warning banners.
- Long candidate field values wrap and preserve controls.
- Data tables must support horizontal scroll only when unavoidable and with sticky primary identifiers.
- Duplicate comparison becomes stacked with clear `Candidate` and `Possible match` headings.
- Persistent boundary copy remains visible or immediately reachable on small screens.

What must not happen:

- Mobile must not hide safety copy to save space.
- Mobile must not make disabled actions look enabled.

## 24. Impeccable shape input summary

Use this document as the input for a later manual `/impeccable shape OMI UI Screen Spec v1` pass.

Shape goals:

- Turn the screen list into low-fidelity mockups.
- Preserve analysis-only, candidate-first, evidence-backed boundaries.
- Make candidate/canon separation visually obvious.
- Make grouped candidate review and field-level approval ergonomic.
- Make evidence/original wording available on click.
- Make duplicate choices explicit.
- Make promotion readiness clear without implying canon mutation.
- Make apply-promotion handoff guarded and separate.
- Make deferred categories visible without exposing unavailable actions.

Shape constraints:

- Do not implement frontend code during shape.
- Do not change backend behavior.
- Do not create candidates.
- Do not mutate Memory/Canon.
- Do not call models.
- Do not add generated prose features.
- Do not add rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.
- Only improve UI clarity, layout, accessibility, copy, empty states, warning states, and responsive behavior.

Primary mockup surfaces:

- OMI Dashboard.
- Candidate Group Review.
- Candidate Detail with Field Approval Rows and Evidence Drawer.
- Duplicate / Merge / Ignore / Needs Clarification Panel.
- Promotion Readiness Panel.
- Apply-Promotion Confirmation handoff.
- Deferred / Not Included Yet Categories View.

## 25. Open design questions

- Should Field Approval Rows live only on Candidate Detail, or should Candidate Group Review support inline field approval for small candidates?
- What is the first low-fidelity navigation model: OMI local tabs, nested sidebar, or dashboard-driven links?
- Should duplicate choices be required for every candidate type or only when possible matches exist?
- How should unresolved candidate dependencies block promotion readiness: hard block by default, or owner-overridable with an uncertainty note?
- Which raw-idea fields are editable in the first UI implementation, and which are read-only audit fields?
- What exact set of first raw-idea-derived candidate categories is included in the first implementation?
- How much original wording can be shown inline before requiring the Evidence Drawer?
- Should approved Memory/Canon evidence open inside OMI or route to approved category pages?
- What owner confirmation pattern should apply-promotion use: checkbox, typed phrase, or both?
- How should mobile handle side-by-side duplicate comparison without hiding evidence?

## 26. Validation commands

Required validation for this docs-only change:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
git diff --check
git status --short --branch
```

Expected result:

- Roadmap/enrichment validation passes.
- Markdown diff has no whitespace errors.
- Only `docs/roadmap/ux/OMI-ui-screen-spec-v1.md` is changed by this task unless unrelated pre-existing workspace changes are present.
