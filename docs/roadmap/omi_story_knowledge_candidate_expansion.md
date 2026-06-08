# OMI Story Knowledge Candidate Expansion

## 1. Purpose

This specification defines how Organize My Idea (OMI) should expand from its current generic raw idea / structured candidate workflow into the central review layer for Project Workspace Foundation setup candidates and Writer Assistant Core story-knowledge candidates.

This is documentation only. It does not implement runtime code, typed validation, extractors, frontend UI changes, project memory files, JSONL records, training data, model calls, candidate promotion, or apply-promotion behavior.

The app remains analysis-only. It must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. Expanded OMI Role

OMI becomes the central review layer for:

- Guided project creation from owner-provided ideas.
- Project setup candidates before the project is fully structured.
- Manually created story-knowledge candidates.
- Future extractor-created candidates.
- Future model-assisted candidates, if allowed by a later task.
- Owner-reviewed candidates.
- Promotion-record preparation.
- Future apply-promotion handoff into project memory/canon.

Core boundaries:

- OMI candidates are not canon.
- OMI promotion records are audit/intent records, not canon by themselves.
- Memory/canon records are created only by a future apply-promotion step after owner approval and final confirmation.
- OMI must not generate, rewrite, continue, imitate, polish, improve, or extend story prose.
- OMI must not directly mutate `bible.json`, `storyform.json`, scenes, `project.json`, owner memory, `memory/*.json`, training data, or `dataset_manifest.json`.
- Story-knowledge candidates may originate from scenes or project context instead of an OMI raw idea. Future runtime records should allow `idea_id: null` when `source_scene_id` or `source_reference` identifies the source.
- OMI-created project setup remains owner-controlled. OMI may organize owner-provided ideas into structured setup candidates, but blank projects and OMI-created projects must both keep pending candidates separate from project metadata and canon.
- WORKSPACE-004 dedicated planning lives in `docs/roadmap/omi_guided_project_creation_spec.md` and defines the first guided-creation handoff from staged setup state into `project.json` metadata and project-local OMI records.

Future flow:

```text
owner-authored scene/chapter/note text
  -> extraction orchestrator
  -> tool-specific adapters or manual candidate creation
  -> normalized CORE candidate schemas
  -> evidence/provenance attachment
  -> OMI candidate records
  -> owner review
  -> OMI promotion record
  -> future apply-promotion handoff
  -> memory/*.json project memory/canon record
```

## 3. Future OMI-Supported Candidate Classes

Each future candidate class uses the CORE-002/CORE-003 base candidate contract from `docs/roadmap/writer_assistant_core_candidate_schemas.md`. Current OMI runtime support remains generic until a later implementation task adds typed validation and UI behavior.

### `character_candidate`

- Purpose: candidate character identity, aliases, role notes, traits, goals, conflicts, and related records.
- Minimum required fields: `canonical_name_candidate` or owner-approved label, `source_scene_id` or `source_reference`, evidence/provenance, confidence, owner decision.
- Recommended evidence: first seen scene, name/alias evidence, role/trait evidence where available.
- Allowed proposed destinations: `character_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: approved canonical label, evidence or reason evidence is unavailable, provenance, no duplicate blocker, final confirmation.
- Likely memory target: `memory/characters.json`.
- Risks: alias overmerge, mistaking a mentioned name for a character, overclaiming goals/traits.
- UI review needs: alias editor, related candidate links, evidence preview, duplicate warning.

### `location_candidate`

- Purpose: candidate place, setting, region, or spatial context.
- Minimum required fields: `name_candidate`, source locator, evidence/provenance.
- Recommended evidence: first scene or mention, description/location evidence, connected characters/events if available.
- Allowed proposed destinations: `location_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: approved location label, source evidence, duplicate/alias check, final confirmation.
- Likely memory target: `memory/locations.json`.
- Risks: confusing generic setting terms with named locations, overconnecting characters/events.
- UI review needs: alias/location merge controls and connected event preview.

### `object_candidate`

- Purpose: candidate object, item, artifact, tool, clue, or recurring possession.
- Minimum required fields: `name_candidate`, source locator, evidence/provenance.
- Recommended evidence: first mention, holder/owner evidence if present, plot relevance evidence if present.
- Allowed proposed destinations: `object_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: approved object label, evidence/provenance, holder uncertainty noted, final confirmation.
- Likely memory target: `memory/objects.json`.
- Risks: promoting incidental props, overclaiming plot relevance or ownership.
- UI review needs: holder uncertainty label and plot relevance notes.

### `organization_candidate`

- Purpose: candidate group, faction, institution, team, family, government, company, or informal organization.
- Minimum required fields: `name_candidate`, source locator, evidence/provenance.
- Recommended evidence: membership, purpose, location, or group reference evidence where available.
- Allowed proposed destinations: `organization_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: approved organization label, membership uncertainty noted, evidence/provenance, final confirmation.
- Likely memory target: `memory/organizations.json`.
- Risks: treating a temporary group as a durable organization; overclaiming membership.
- UI review needs: member link review and purpose notes.

### `timeline_event_candidate`

- Purpose: candidate event/action with ordering, time reference, involved records, causes, and effects.
- Minimum required fields: `event_label`, `event_summary`, `scene_id` or source reference, evidence/provenance.
- Recommended evidence: scene source, explicit/relative time cues, involved characters/location if available.
- Allowed proposed destinations: `timeline_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: source scene/source, event summary, sequence/uncertainty notes, duplicate event check, final confirmation.
- Likely memory target: `memory/timeline.json`.
- Risks: overclaiming causality, order, or exact time.
- UI review needs: timeline ordering controls, uncertainty label, cause/effect review.

### `relationship_candidate`

- Purpose: candidate relationship link or state between two story-knowledge records.
- Minimum required fields: `subject_candidate_id` or record ID, `object_candidate_id` or record ID, `relationship_type`, evidence/provenance.
- Recommended evidence: scene evidence, relationship-state evidence, direction/status uncertainty.
- Allowed proposed destinations: `relationship_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: subject and object identified, uncertainty recorded, duplicate relationship check, final confirmation.
- Likely memory target: `memory/relationships.json`.
- Risks: generic interaction becoming relationship truth; relationship evidence being mistaken for Dramatica Relationship Story proof.
- UI review needs: subject/object resolver, relationship direction/status editor, explicit non-Dramatica label.

### `plot_thread_candidate`

- Purpose: candidate plot thread, unresolved thread, throughline-independent continuity thread, or payoff candidate.
- Minimum required fields: `thread_label`, `thread_summary`, source locator, evidence/provenance.
- Recommended evidence: introduced scene, related scenes/characters, unresolved questions and possible payoff notes.
- Allowed proposed destinations: `plot_thread_memory_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: approved thread label, status, related source evidence, duplicate/thread merge check, final confirmation.
- Likely memory target: `memory/plot_threads.json`.
- Risks: overclaiming narrative intent or payoff; confusing an isolated event with a plot thread.
- UI review needs: status controls, related scenes, unresolved question links.

### `navigation_summary_candidate`

- Purpose: candidate chapter/scene/project summary used for navigation, review, and project overview.
- Minimum required fields: `summary_label`, `target_type`, `target_id`, `summary_text`, `navigation_only: true`, `no_rewrite_provided: true`, source locator, provenance.
- Recommended evidence: source chapter/scene references and a short explanation of why the summary helps navigation.
- Allowed proposed destinations: `summary_index_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: owner confirms the summary is navigation-only, evidence/provenance exists, no prose rewrite is included, final confirmation.
- Likely memory target: `memory/summaries.json`.
- Risks: summary text drifting into AI-written prose or replacement scene wording.
- UI review needs: clear navigation-only label, source preview, no-rewrite boundary label.

### `continuity_warning_candidate`

- Purpose: candidate continuity issue, contradiction, missing link, or inconsistency requiring owner review.
- Minimum required fields: `warning_type`, `warning_summary`, `conflicting_sources`, `no_rewrite_provided: true`, evidence/provenance.
- Recommended evidence: both sides of conflict where available; affected candidates/records.
- Allowed proposed destinations: `continuity_warning_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: conflicting source references, severity/review status, no rewrite/prose suggestion, final confirmation.
- Likely memory target: `memory/continuity_warnings.json`.
- Risks: false contradiction; generating a fix instead of asking a diagnostic question.
- UI review needs: side-by-side evidence, severity selector, diagnostic question display, no-prose boundary label.

### `annotation_candidate`

- Purpose: candidate annotation tied to a scene, entity, record, evidence span, or project-level note.
- Minimum required fields: `annotation_type`, `annotation_text`, `target_type`, target/source locator, evidence/provenance.
- Recommended evidence: target locator and source scene or memory record.
- Allowed proposed destinations: `annotation_index_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: target exists or target uncertainty recorded, annotation is analysis/metadata only, final confirmation.
- Likely memory target: `memory/annotations.json`.
- Risks: annotation clutter; annotation text drifting into generated story prose.
- UI review needs: target preview, visibility controls, clutter filtering.

### `open_question_candidate`

- Purpose: candidate question the writer may need to answer about story knowledge, continuity, timeline, relationship, or plot.
- Minimum required fields: `question`, `question_type`, source locator or related candidates, provenance.
- Recommended evidence: why the question arose, related records/candidates, scene source.
- Allowed proposed destinations: `open_question_index_candidate`, `project_memory_candidate`, `omi_candidate_only`, `discard`.
- Promotion readiness: diagnostic question only, related source/candidate links, status, final confirmation.
- Likely memory target: `memory/open_questions.json`.
- Risks: question phrased as a writing request; vague questions without actionable source context.
- UI review needs: related candidate links, status controls, filter by question type.

## 4. Expanded Lifecycle

Existing/current OMI statuses:

- `draft`
- `candidate`
- `owner_review`
- `approved`
- `rejected`
- `archived`
- `promoted` currently appears in older OMI docs as a promotion-record lifecycle concept, but CORE-005 separates promotion audit from durable canon.

Future implementation target statuses:

- `needs_revision`
- `promotion_ready`
- `promotion_recorded`
- `superseded`

Lifecycle intent:

```text
draft
  -> candidate
  -> owner_review
  -> approved | rejected | needs_revision | archived
  -> promotion_ready
  -> promotion_recorded
  -> promoted only after future apply-promotion succeeds
```

Rules:

- `promoted` must not mean canon unless the future apply-promotion step has written an approved memory record.
- `promotion_recorded` means audit intent exists, not durable canon.
- Future docs/runtime should prefer `promotion_recorded` for OMI promotion-record completion and reserve `promoted` for successful apply-promotion into memory/canon.
- `superseded` preserves traceability for merged/replaced candidates.
- `needs_revision` returns the candidate to review after changes.

## 5. Owner Review Actions

Current or MVP-adjacent actions:

- `approve`
- `reject`
- `archive`
- `promote` to create a promotion audit record when gates pass.

Future story-knowledge review actions:

- `needs_revision`
- `merge_with_existing`
- `split_candidate`
- `mark_duplicate`
- `mark_uncertain`
- `request_more_evidence`
- `link_to_existing_memory_record`

Action rules:

- Merge/split/duplicate actions should update candidate metadata, not durable truth.
- `request_more_evidence` should block promotion readiness.
- `mark_uncertain` should preserve uncertainty through any later memory record.
- `link_to_existing_memory_record` should not mutate that memory record without apply-promotion.

## 6. Merge and Deduplication Planning

No merge logic is implemented by this spec. Future implementation should support:

- Duplicate character candidates: compare canonical name candidates, aliases, source scenes, and related candidates.
- Duplicate location candidates: compare name/alias, source scenes, and connected events.
- Alias detection: preserve alias candidates separately until owner confirms alias vs separate entity.
- Relationship duplicates: compare subject/object pair, relationship type, direction, status, and evidence scenes.
- Timeline event duplicates: compare scene ID, event label, sequence position, involved records, and summary.
- Plot thread duplicates: compare thread label, related scenes, unresolved questions, and payoff notes.
- Conflicting candidates: preserve both candidates and mark conflict rather than overwriting.
- Superseded candidates: preserve prior candidate ID, decision history, and merge/supersession note.

Recommended future metadata:

- `duplicate_of_candidate_id`
- `merged_into_candidate_id`
- `split_from_candidate_id`
- `supersedes_candidate_ids`
- `superseded_by_candidate_id`
- `conflicts_with_candidate_ids`
- `linked_memory_record_ids`

## 7. Review UI Requirements

Future OMI UI should support:

- Candidate list filtered by type and status.
- Evidence preview.
- Provenance preview.
- Confidence / uncertainty label.
- Related candidates.
- Proposed destination.
- Promotion readiness blockers.
- Approve/reject/revise/archive controls.
- Merge/split/duplicate controls.
- Request-more-evidence control.
- Link-to-existing-memory-record control.
- Final confirmation before promotion record.
- Clear candidate-only labeling.
- Clear distinction between promotion record and canon.
- No prose-generation controls.
- Project setup candidates for OMI-guided project creation.
- Separate OMI Ideas and Candidates page so pending candidates do not appear as approved memory/canon.

Continuity warnings should show conflicting sources without providing replacement prose. Relationship candidates should clearly state they are generic story-knowledge relationships, not Dramatica Relationship Story proof.

## 8. Promotion Readiness Rules

General promotion readiness requires:

- Owner approval.
- Explicit destination.
- Evidence or reason why evidence is unavailable.
- Provenance.
- Safe target type.
- No-prose validation.
- Final confirmation.
- Conflict/duplicate check.
- Source candidate snapshot.
- Candidate status `approved` or future `promotion_ready`.

Type-specific readiness examples:

- `character_candidate`: must have a canonical name or owner-approved label.
- `location_candidate`: must have a name/label and source evidence or owner note.
- `object_candidate`: must have a name/label and ownership/holder uncertainty if relevant.
- `organization_candidate`: must have a name/label and membership uncertainty if relevant.
- `timeline_event_candidate`: must identify scene/source and event summary.
- `relationship_candidate`: must identify subject/object and uncertainty.
- `plot_thread_candidate`: must include thread label, status, and source/related scene context.
- `navigation_summary_candidate`: must include `navigation_only: true`, target/source references, and `no_rewrite_provided: true`.
- `continuity_warning_candidate`: must include conflicting sources and `no_rewrite_provided: true`.
- `annotation_candidate`: must identify target type plus source scene or memory record.
- `open_question_candidate`: must be diagnostic, related to source/candidate context, and not request prose generation.

## 9. Storage Implications

Current OMI candidate records can store future candidate types as structured `candidate_content`.

Future runtime work should add:

- Candidate-type allowlist validation.
- Candidate-specific `candidate_content` validation.
- Evidence/provenance validation for promotion readiness.
- Type/status filtering in OMI index or API response.
- Promotion readiness blocker calculation.
- Merge/dedup metadata fields.
- Safe target mapping from candidate type to `memory/*.json` destination.

This spec does not implement runtime validation.

## 10. Future Test Implications

Future tests should cover:

- Creating each story-knowledge candidate type.
- Creating project setup candidates from owner-provided OMI ideas without creating canon.
- Listing/filtering candidates by type and status.
- Owner decision transitions.
- Duplicate/merge metadata safety.
- Promotion readiness blockers.
- No durable truth mutation.
- No `memory/*.json` mutation before apply-promotion.
- No JSONL/training writes.
- No prose-generation fields, destinations, or candidate types.
- Path traversal safety.
- Malformed `candidate_content` rejection.
- Evidence/provenance required for promotion readiness.
- Relationship candidates do not imply Dramatica Relationship Story proof.
- Continuity warnings do not provide rewrite text.
- Navigation summaries remain navigation-only and do not rewrite source prose.

## 11. Deferred Decisions

Deferred to later tasks:

- Runtime typed candidate validation.
- OMI API/UI implementation for type filters and review controls.
- Apply-promotion behavior.
- Runtime `memory/*.json` writes.
- Extractor implementation and dependency spikes.
- Model-assisted candidate generation policy.
- Exact merge/deduplication algorithm.
- Candidate ID/hash strategy.
- Annotation UI storage/details.
- Browser interaction design for high-volume candidate review.
