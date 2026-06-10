# Writer Assistant Core Candidate Schemas

## 1. Purpose

This specification defines the first Writer Assistant Core candidate schemas and shared evidence/provenance model. It is documentation only. It does not implement runtime schemas, extractor code, OMI storage changes, project memory files, JSONL records, training data, model calls, or promotion behavior.

Writer Assistant Core helps the writer identify, organize, connect, annotate, and review story knowledge from owner-authored text. It follows the pre-Dramatica Project Workspace Foundation: project creation/library, chapters/scenes/notes/materials, and owner-authored prose save/edit/reload come before extraction. All extracted story knowledge is candidate-only until reviewed through OMI.

The app remains analysis-only. It must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. Base Candidate Contract

Every Writer Assistant Core candidate uses this base contract.

CORE-005 OMI review behavior is defined in `docs/roadmap/omi_story_knowledge_candidate_expansion.md`. That spec explains future OMI type filters, owner actions, merge/dedup metadata, promotion readiness, and UI requirements for these candidate classes.

WORKSPACE-011 page-structure behavior is defined in `docs/roadmap/project_memory_canon_page_structure_spec.md`. That spec defines how future Project Memory / Canon pages should keep these candidates separate from applied memory/canon records until apply-promotion succeeds.

WORKSPACE-012 OMI page behavior is defined in `docs/roadmap/omi_ideas_candidates_page_spec.md`. That spec defines the future OMI workspace page for owner raw ideas, candidate review, evidence/provenance, promotion readiness, audit-only promotion records, local filters/search, warning states, and page relationships.

WORKSPACE-013 Approved Characters page behavior is defined in `docs/roadmap/approved_characters_page_spec.md`. That spec defines the first approved-only category page: applied `character_memory_record` display, evidence/provenance panel, linked sources panel, candidate backlog snapshot, warning states, API/UI planning, and no-prose/no-silent-promotion boundaries for the characters category.

WORKSPACE-014 Approved Locations / Settings page behavior is defined in `docs/roadmap/approved_locations_settings_page_spec.md`. That spec defines the second approved-only category page: applied `location_memory_record` display, evidence/provenance panel, linked sources panel, place hierarchy placeholder, scene usage snapshot, candidate backlog snapshot, warning states including parent/child cycle detection, API/UI planning, and no-prose/no-silent-promotion boundaries for the locations/settings category.

WORKSPACE-015 Approved Timeline page behavior is defined in `docs/roadmap/approved_timeline_page_spec.md`. That spec defines the third approved-only category page: applied `timeline_event_memory_record` display, evidence/provenance panel, linked sources panel, chronology/ordering placeholder, cause/effect placeholder, scene usage snapshot, candidate backlog snapshot, warning states including sequence collisions, chronology conflicts, and cause/effect cycles, API/UI planning, and no-prose/no-silent-promotion boundaries for the timeline category.

WORKSPACE-016 Approved Plot Threads page behavior is defined in `docs/roadmap/approved_plot_threads_page_spec.md`. That spec defines the fourth approved-only category page: applied `plot_thread_memory_record` display, evidence/provenance panel, linked sources panel, linked timeline/scene snapshot, related characters/locations/objects snapshot, related open-questions and continuity-warnings placeholders, candidate backlog snapshot, warning states including thread status conflicts, API/UI planning, and no-prose/no-silent-promotion boundaries for the plot-thread category.

WORKSPACE-017 Continuity / Consistency page behavior is defined in `docs/roadmap/continuity_consistency_page_spec.md`. That spec defines the approved-only continuity/consistency page behavior and keeps continuity candidates, promotion records, and approved continuity memory/canon visibly separate.

WORKSPACE-018 Approved Open Questions page behavior is defined in `docs/roadmap/approved_open_questions_page_spec.md`. That spec defines the approved-only open-questions page behavior and keeps open-question candidates, promotion records, generated answers, and approved open-question memory/canon visibly separate.

WORKSPACE-019 Approved Relationships page behavior is defined in `docs/roadmap/approved_relationships_page_spec.md`. That spec defines the approved-only relationships page behavior and keeps relationship candidates, promotion records, generated relationship analysis, graph generation, Dramatica RS claims, and approved relationship memory/canon visibly separate.

WORKSPACE-020 Approved Organizations / Groups page behavior is defined in `docs/roadmap/approved_organizations_groups_page_spec.md`. That spec defines the approved-only organizations/groups page behavior and keeps organization/group candidates, promotion records, generated organization analysis, graph generation, faction fixes, Dramatica structural claims, and approved organization/group memory/canon visibly separate.

WORKSPACE-021 Approved Objects / Items page behavior is defined in `docs/roadmap/approved_objects_items_page_spec.md`. That spec defines the approved-only objects/items page behavior and keeps object/item candidates, promotion records, generated object analysis, graph generation, symbolic interpretation, item fixes, Dramatica structural/thematic claims, and approved object/item memory/canon visibly separate.

Required or expected fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `candidate_id` | string | Stable candidate identifier, preferably prefixed by candidate type or OMI record ID. |
| `project_id` | string | Filesystem-safe project identifier. |
| `candidate_type` | string | One of the bounded candidate types in this spec. |
| `status` | string | Candidate lifecycle status. |
| `created_at` | string | ISO-8601 timestamp. |
| `updated_at` | string | ISO-8601 timestamp. |
| `source_scene_id` | string or null | Scene ID when the candidate comes from one scene. |
| `source_reference` | object or null | Source locator when not tied to one scene. |
| `evidence` | array | Evidence span records. |
| `provenance` | object | Candidate provenance record. |
| `confidence` | string or number | Candidate confidence, not canon certainty. |
| `owner_decision` | object | Owner review decision state. |
| `promotion_status` | object | Promotion readiness and blockers. |
| `proposed_destination` | string or null | Proposed durable destination if later approved. |
| `candidate_content` | object | Candidate-type-specific content. |
| `notes` | array or string | Uncertainty, review notes, or implementation notes. |

Rules:

- Candidates are not canon.
- Schema validity does not prove story truth.
- Candidates cannot mutate `bible.json`, `storyform.json`, scenes, `project.json`, owner memory, project memory, canon, training data, or dataset manifests.
- Candidates must flow through OMI review before any promotion.
- Candidates may be approved, rejected, revised, archived, or promoted.
- Promotion requires owner approval, destination, evidence/provenance, and final confirmation.
- Extractor output, model output, NotebookLM output, and retrieved references remain candidate-only until owner-approved.
- Chapter/scene summaries are navigation-summary candidates only; they must not rewrite, continue, polish, or replace owner prose.
- Relationship candidates are not Dramatica Relationship Story proof.
- Dramatica/NCP truth claims remain deferred to the later advanced layer.

Recommended base JSON shape:

```json
{
  "candidate_id": "candidate_0001",
  "project_id": "example",
  "candidate_type": "character_candidate",
  "status": "candidate",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "source_scene_id": "scene_001",
  "source_reference": null,
  "evidence": [],
  "provenance": {},
  "confidence": "candidate_only",
  "owner_decision": {},
  "promotion_status": {},
  "proposed_destination": "project_memory_candidate",
  "candidate_content": {},
  "notes": []
}
```

## 3. Lifecycle Statuses

Allowed statuses:

- `candidate`: extracted or created but not yet owner-reviewed.
- `owner_review`: ready for owner decision.
- `approved`: owner accepts the candidate as eligible for a later promotion step.
- `rejected`: owner rejects the candidate.
- `needs_revision`: owner requests a revised candidate.
- `archived`: retained for traceability but inactive.
- `promoted`: an approved candidate has passed the future promotion flow.

Creating a candidate is not promotion. `promoted` must not be set without a promotion record and final owner confirmation.

## 4. Evidence Span Model

Evidence spans tie a candidate claim to project-local source material. Exact offsets and line numbers are preferred but optional at first if the app cannot reliably provide them yet.

Fields:

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `evidence_id` | string | Required | Stable evidence identifier. |
| `source_type` | string | Required | Source class such as `scene`, `bible`, `storyform`, `project_metadata`, `owner_note`, `omi_idea`, or `manual_review`. |
| `source_path` | string or null | Required when available | Project-relative source path. |
| `source_scene_id` | string or null | Optional | Scene ID for scene evidence. |
| `source_scene_title` | string or null | Optional | Human-readable scene title if available. |
| `source_text_excerpt` | string or null | Optional | Short excerpt for review. Do not copy long raw source text into docs or training records. |
| `start_offset` | integer or null | Optional | Character start offset in source. |
| `end_offset` | integer or null | Optional | Character end offset in source. |
| `paragraph_index` | integer or null | Optional | Paragraph locator if offsets are unavailable. |
| `line_start` | integer or null | Optional | Start line locator. |
| `line_end` | integer or null | Optional | End line locator. |
| `quote_exact` | boolean | Required | Whether `source_text_excerpt` is an exact source quote. |
| `summary` | string | Required | Short explanation of the evidence. |
| `supports_claim` | string | Required | Which candidate claim this evidence supports or qualifies. |
| `confidence` | string or number | Required | Evidence confidence, not canon certainty. |
| `notes` | array or string | Optional | Limitations, ambiguity, or owner review notes. |

Recommended evidence JSON shape:

```json
{
  "evidence_id": "evidence_0001",
  "source_type": "scene",
  "source_path": "scenes/scene_001.md",
  "source_scene_id": "scene_001",
  "source_scene_title": null,
  "source_text_excerpt": null,
  "start_offset": null,
  "end_offset": null,
  "paragraph_index": null,
  "line_start": null,
  "line_end": null,
  "quote_exact": false,
  "summary": "Candidate appears in this scene.",
  "supports_claim": "canonical_name_candidate",
  "confidence": "medium",
  "notes": []
}
```

## 5. Provenance Model

Provenance is required for candidate trust and future promotion. It records how the candidate was created and what review is still required.

Fields:

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `created_by` | string | Required | `owner`, `assistant`, `tool`, or `manual_review`. |
| `source_type` | string | Required | `owner_input`, `scene_analysis`, `manual_review`, `extractor_candidate`, `model_output`, `notebooklm_candidate`, `retrieved_reference`, or similar bounded source. |
| `tool` | string or null | Required | Tool name when a tool created or transformed the candidate. |
| `model` | string or null | Required | Model name if a model was involved. |
| `extractor` | string or null | Required | Extractor name if an extractor was involved. |
| `prompt_id` | string or null | Required | Prompt/template ID if a prompt was involved. |
| `timestamp` | string | Required | ISO-8601 timestamp. |
| `source_hash` | string or null | Optional | Hash of source snapshot where practical. |
| `snapshot_hash` | string or null | Optional | Hash of candidate snapshot where practical. |
| `human_review_required` | boolean | Required | Whether human review is required before promotion. |
| `owner_reviewed` | boolean | Required | Whether owner review has occurred. |
| `license_status` | string | Required | `owner_project`, `public_domain`, `unknown`, `review_required`, or other bounded value. |
| `notes` | array or string | Optional | Tool limitations, source caveats, or review notes. |

Model output, extractor output, NotebookLM output, and retrieved references cannot create durable story truth without owner review. External extractor dependencies require a separate spike before use.

## 6. Owner Decision Model

Owner decision model aligns with existing OMI decision concepts.

Fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `decision` | string | One of the allowed decision values. |
| `decided_by` | string or null | Owner or reviewer identifier. |
| `decided_at` | string or null | ISO-8601 timestamp. |
| `notes` | string | Owner notes. |
| `revision_request` | string or null | Requested changes when `needs_revision`. |
| `approval_confirmed` | boolean | Whether approval or promotion confirmation has been explicitly received. |

Allowed decisions:

- `undecided`
- `approve`
- `reject`
- `needs_revision`
- `archive`
- `promote`

`promote` requires prior approval, explicit destination, evidence/provenance review, and final confirmation.

## 7. Promotion Status Model

Fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `eligible` | boolean | Whether the candidate is eligible for a future promotion step. |
| `blocked_reasons` | array | Missing requirements or safety blockers. |
| `destination` | string or null | Intended destination if promoted. |
| `promotion_record_id` | string or null | Promotion audit record ID, if created. |
| `promoted_at` | string or null | ISO-8601 timestamp only after promotion. |
| `requires_confirmation` | boolean | Whether final confirmation is required. |
| `confirmation_received` | boolean | Whether confirmation was received. |

Candidate creation is not promotion. Promotion records are audit records and do not by themselves grant automatic mutation of durable truth files.

## 8. Candidate Types

The first Writer Assistant Core candidate types are listed below. Additional fields may be added later, but every type must preserve the base contract, evidence, provenance, owner decision, and promotion status.

### `character_candidate`

Candidate content fields:

- `canonical_name_candidate`
- `aliases`
- `role_notes`
- `traits`
- `goals`
- `conflicts`
- `first_seen_scene_id`
- `mentioned_in_scene_ids`
- `related_candidate_ids`

### `location_candidate`

Candidate content fields:

- `name_candidate`
- `aliases`
- `description_notes`
- `first_seen_scene_id`
- `mentioned_in_scene_ids`
- `connected_character_ids`
- `connected_event_ids`

### `object_candidate`

Candidate content fields:

- `name_candidate`
- `aliases`
- `description_notes`
- `owner_or_holder_candidate`
- `first_seen_scene_id`
- `mentioned_in_scene_ids`
- `plot_relevance_notes`

### `organization_candidate`

Candidate content fields:

- `name_candidate`
- `aliases`
- `members_candidate`
- `purpose_notes`
- `related_location_ids`
- `related_character_ids`

### `timeline_event_candidate`

Candidate content fields:

- `event_label`
- `event_summary`
- `scene_id`
- `sequence_position`
- `explicit_time_reference`
- `relative_time_reference`
- `involved_character_ids`
- `location_candidate_id`
- `causes`
- `effects`
- `uncertainty_notes`

### `relationship_candidate`

Candidate content fields:

- `subject_candidate_id`
- `object_candidate_id`
- `relationship_type`
- `relationship_summary`
- `direction`
- `status`
- `evidence_scene_ids`
- `uncertainty_notes`

Relationship candidates describe project knowledge candidates only. They are not Dramatica Relationship Story proof.

### `plot_thread_candidate`

Candidate content fields:

- `thread_label`
- `thread_summary`
- `introduced_scene_id`
- `related_scene_ids`
- `related_character_ids`
- `status`
- `unresolved_questions`
- `payoff_candidate`

### `navigation_summary_candidate`

Candidate content fields:

- `summary_label`
- `target_type`
- `target_id`
- `summary_text`
- `navigation_only`
- `source_chapter_ids`
- `source_scene_ids`
- `related_candidate_ids`
- `no_rewrite_provided`

Rules:

- `navigation_only` must be true.
- `no_rewrite_provided` must be true.
- Summary text must be compact analysis/navigation metadata, not replacement prose, continuation, polish, or authorial imitation.

### `continuity_warning_candidate`

Candidate content fields:

- `warning_type`
- `warning_summary`
- `conflicting_sources`
- `affected_candidates`
- `severity`
- `suggested_review_question`
- `no_rewrite_provided`

`no_rewrite_provided` must be true. Continuity warnings may ask diagnostic questions but must not provide replacement prose.

### `annotation_candidate`

Candidate content fields:

- `annotation_type`
- `annotation_text`
- `target_type`
- `target_id`
- `source_scene_id`
- `evidence`
- `visibility_status`

Annotation text must be analysis/metadata only, not generated story prose.

### `open_question_candidate`

Candidate content fields:

- `question`
- `question_type`
- `related_candidates`
- `source_scene_id`
- `why_it_matters`
- `status`

Questions should be diagnostic and writer-facing. They must not ask the assistant to write or rewrite story prose.

## 9. Proposed Destinations

Initial proposed destination values:

- `omi_candidate_only`
- `project_memory_candidate`
- `character_memory_candidate`
- `location_memory_candidate`
- `object_memory_candidate`
- `organization_memory_candidate`
- `timeline_memory_candidate`
- `relationship_memory_candidate`
- `plot_thread_memory_candidate`
- `summary_index_candidate`
- `annotation_index_candidate`
- `open_question_index_candidate`
- `discard`

These are candidate destinations only. CORE-004 recommends future folder-based `memory/*.json` project memory/canon storage in `docs/roadmap/project_memory_canon_storage_model.md`. Runtime apply-promotion behavior still does not exist.

## 10. Validation and Safety Rules

Future runtime validation should enforce:

- Candidate type is one of the allowed types.
- Required base fields exist.
- `evidence` is an array, even when empty.
- `provenance.human_review_required` is true for extracted/model/tool candidates.
- `owner_decision.decision` is allowed.
- `promotion_status.eligible` defaults false unless promotion requirements are met.
- No candidate type or destination requests prose generation.
- `navigation_summary_candidate` must be labeled as navigation-only and must not contain replacement prose.
- Continuity warnings do not include rewrites.
- External extractor output includes license/provenance status.
- Schema-valid candidates remain candidate-only.

## 11. Deferred Decisions

Deferred to later tasks:

- Exact runtime ID format.
- Exact source hash and snapshot hash implementation.
- Whether evidence offsets use character offsets, line ranges, paragraph indices, or a hybrid.
- Annotation storage location and UI treatment.
- First extractor strategy and dependency spike.
- Merge/deduplication behavior for duplicate candidate entities.
- Apply-promotion behavior and rollback model.
- Exact runtime implementation of the CORE-004 folder-based `memory/*.json` storage model.
