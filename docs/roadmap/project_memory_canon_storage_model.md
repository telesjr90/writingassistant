# Project Memory / Canon Storage Model

## 1. Purpose

This specification defines the future Writer Assistant Core project memory/canon storage model. It is documentation only. It does not create runtime project memory files, backend code, frontend code, extractors, OMI candidates, promotion records, JSONL records, training data, model calls, or apply-promotion behavior.

Project memory/canon is the durable owner-approved story knowledge layer that may exist after Project Workspace Foundation save/edit flows, OMI candidate review, and a future owner-confirmed apply-promotion step. It comes after project creation, chapters/scenes/notes/materials, owner-authored prose storage, candidate extraction, and owner approval.

WORKSPACE-011 page-structure planning lives in `docs/roadmap/project_memory_canon_page_structure_spec.md`. That spec defines the future Project Memory / Canon page, approved-vs-candidate labels, category cards, promotion-record snapshots, empty states before apply-promotion exists, health warnings, API/UI planning, and page-level no-silent-promotion boundaries.

WORKSPACE-012 OMI page planning lives in `docs/roadmap/omi_ideas_candidates_page_spec.md`. That spec defines the future OMI raw idea, candidate review, evidence/provenance, promotion readiness, promotion audit records, local filter/search, and OMI health warning page.

WORKSPACE-013 Approved Characters page planning lives in `docs/roadmap/approved_characters_page_spec.md`. That spec defines the first approved-only category page: applied `character_memory_record` display, evidence/provenance panel, linked sources panel, candidate backlog snapshot, warning states, API/UI planning, and no-prose/no-silent-promotion boundaries for the characters category.

WORKSPACE-014 Approved Locations / Settings page planning lives in `docs/roadmap/approved_locations_settings_page_spec.md`. That spec defines the second approved-only category page: applied `location_memory_record` display, evidence/provenance panel, linked sources panel, place hierarchy placeholder, scene usage snapshot, candidate backlog snapshot, warning states including parent/child cycle detection, API/UI planning, and no-prose/no-silent-promotion boundaries for the locations/settings category.

WORKSPACE-015 Approved Timeline page planning lives in `docs/roadmap/approved_timeline_page_spec.md`. That spec defines the third approved-only category page: applied `timeline_event_memory_record` display, evidence/provenance panel, linked sources panel, chronology/ordering placeholder, cause/effect placeholder, scene usage snapshot, candidate backlog snapshot, warning states including sequence collisions, chronology conflicts, and cause/effect cycles, API/UI planning, and no-prose/no-silent-promotion boundaries for the timeline category.

WORKSPACE-016 Approved Plot Threads page planning lives in `docs/roadmap/approved_plot_threads_page_spec.md`. That spec defines the fourth approved-only category page: applied `plot_thread_memory_record` display, evidence/provenance panel, linked sources panel, linked timeline/scene snapshot, related characters/locations/objects snapshot, related open-questions and continuity-warnings placeholders, candidate backlog snapshot, warning states including thread status conflicts, API/UI planning, and no-prose/no-silent-promotion boundaries for the plot-thread category.

WORKSPACE-017 Continuity / Consistency page planning lives in `docs/roadmap/continuity_consistency_page_spec.md`. That spec defines the approved-only continuity/consistency page: applied `continuity_warning_memory_record` or `consistency_issue_memory_record` display, evidence/provenance panel, linked sources panel, affected story-knowledge snapshot, resolution placeholder, candidate backlog snapshot, warning states, API/UI planning, and no-prose/no-silent-promotion boundaries.

WORKSPACE-018 Approved Open Questions page planning lives in `docs/roadmap/approved_open_questions_page_spec.md`. That spec defines the approved-only open-questions page: applied `open_question_memory_record` or `unresolved_question_memory_record` display, evidence/provenance panel, linked sources panel, linked story-knowledge snapshot, owner-answer/resolution placeholder, candidate backlog snapshot, warning states, API/UI planning, and no-prose/no-silent-promotion boundaries.

WORKSPACE-019 Approved Relationships page planning lives in `docs/roadmap/approved_relationships_page_spec.md`. That spec defines the approved-only relationships page: applied `relationship_memory_record` display, participant snapshot, linked story-knowledge snapshot, related plot/timeline/open-question/continuity snapshots, evidence/provenance panel, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica Relationship Story boundaries.

The app remains analysis-only. It must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. Recommended Storage Layout

CORE-004 recommends Option B: folder-based memory.

Recommended future target:

```text
projects/{project_id}/
  memory/
    characters.json
    locations.json
    objects.json
    organizations.json
    timeline.json
    relationships.json
    plot_threads.json
    summaries.json
    annotations.json
    open_questions.json
    continuity_warnings.json
    index.json
```

Why Option B is recommended:

- It keeps each story-knowledge category human-readable and easier to review.
- It reduces accidental overwrite risk compared with one large file.
- It supports safer incremental writes and smaller diffs.
- It is more compatible with future relationship graph, timeline, and search/query work.
- It maps cleanly from CORE-002/CORE-003 candidate types to durable memory record groups.
- It lets OMI promotion records point to explicit target files and record IDs.
- It keeps index/search data derived and separate from approved records.
- It is easier to archive, supersede, or rollback one record category without rewriting the whole memory model.
- It supports project-specific pages for approved characters, locations/settings, timeline, plot threads, continuity/consistency, navigation summaries, and approved canon/memory.

Rejected alternatives:

| Option | Layout | Reason not recommended as default |
| --- | --- | --- |
| Option A | `projects/{project_id}/project_memory.json` | Simplest initial file, but it can become large, harder to review, more conflict-prone, and riskier for incremental writes. |
| Option C | `project_memory.json` plus `memory/index.json` and detailed files only when needed | Flexible, but adds ambiguous ownership between the aggregate file and detailed files. It is better as a later migration path if the folder model proves too granular. |

## 3. Storage Boundaries

The future memory model must keep these roles separate:

| Store | Role | Boundary |
| --- | --- | --- |
| Scene text | Owner-authored story prose in `scenes/` | Never overwritten by candidate, model, extractor, or memory output. |
| `bible.json` | Existing owner-approved project bible context | Durable truth for current app context, but not a dumping ground for raw candidate output. |
| `storyform.json` | Existing owner-approved NCP/storyform context | Dramatica/NCP layer; deferred from Writer Assistant Core and owner-gated. |
| `project.json` | Project identity and metadata | Not story truth and not candidate storage. |
| `owner_memory.json` | Existing/future owner preference and decision target | Separate from story canon unless a later task explicitly merges roles. |
| OMI candidate records | Candidate-only review material | Not canon. Shape-valid candidates do not prove story truth. |
| OMI promotion records | Owner-approved promotion audit intent | Not canon by themselves unless a future apply step writes approved content to memory/canon. |
| Project memory/canon records | Durable owner-approved story knowledge | Canon only after owner confirmation and successful future apply-promotion. |
| Navigation summaries | Approved or candidate chapter/scene summaries for navigation | Must remain structural/navigation aids; they must not become AI-written replacement prose. |
| Analysis artifacts | Transient or saved diagnostics | Candidate analysis, not durable truth. |
| Training data | SFT/evaluation dataset material under `training/data` | Must never be written from project memory/canon automatically. |

Rules:

- OMI candidates are not canon.
- Promotion records are not canon by themselves.
- Approved memory/canon records are durable project truth after owner confirmation and future apply-promotion success.
- No model, extractor, NotebookLM output, retrieved reference, or raw analysis output can directly mutate project memory/canon.
- Project memory/canon must not write to `training/data`, JSONL files, or `dataset_manifest.json`.
- Raw book/source text and training artifacts must not be stored in project memory files.
- Pending, rejected, archived, duplicate, or uncertain candidates must not be displayed as approved canon.
- Approved memory/canon is project-local. Selecting a different project must load that project's approved memory only.

## 4. Shared Memory Record Contract

Every memory record should include these fields.

| Field | Type | Purpose |
| --- | --- | --- |
| `record_id` | string | Stable durable memory record ID. |
| `project_id` | string | Filesystem-safe project ID. |
| `record_type` | string | One of the memory record types in this spec. |
| `canonical_name` or `label` | string | Human-readable primary name/label. |
| `status` | string | `active`, `needs_review`, `superseded`, `archived`, or `deleted_by_owner`. |
| `created_at` | string | ISO-8601 creation timestamp. |
| `updated_at` | string | ISO-8601 update timestamp. |
| `approved_at` | string | ISO-8601 owner approval timestamp. |
| `approved_by` | string | Owner/reviewer identifier. |
| `source_candidate_ids` | array | OMI candidate IDs that led to this record. |
| `promotion_record_ids` | array | OMI promotion records that authorized this record or revision. |
| `evidence_ids` | array | Referenced evidence IDs from candidate/promotion material. |
| `evidence_summaries` | array | Optional compact evidence summaries for review. |
| `provenance` | object | Source trail from candidate through promotion. |
| `confidence_at_promotion` | string or number | Confidence at the time owner approved promotion, not objective truth certainty. |
| `revision_history` | array | Append-only change notes and prior snapshots where practical. |
| `supersedes_record_ids` | array | Older records replaced by this one. |
| `superseded_by_record_id` | string or null | Newer record that replaced this one. |
| `notes` | array or string | Owner notes, ambiguity, or implementation notes. |

Schema-like base example:

```json
{
  "record_id": "character_0001",
  "project_id": "example",
  "record_type": "character_memory_record",
  "canonical_name": "Example Character",
  "status": "active",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "approved_at": "2026-06-07T00:00:00Z",
  "approved_by": "owner",
  "source_candidate_ids": ["omi_candidate_0001"],
  "promotion_record_ids": ["omi_promotion_0001"],
  "evidence_ids": ["evidence_0001"],
  "evidence_summaries": [],
  "provenance": {},
  "confidence_at_promotion": "owner_approved",
  "revision_history": [],
  "supersedes_record_ids": [],
  "superseded_by_record_id": null,
  "notes": []
}
```

## 5. Memory Record Types

### `character_memory_record`

Additional fields:

- `canonical_name`
- `aliases`
- `description_notes`
- `traits`
- `goals`
- `conflicts`
- `first_seen_scene_id`
- `mentioned_in_scene_ids`
- `related_character_ids`
- `related_location_ids`
- `related_plot_thread_ids`

### `location_memory_record`

Additional fields:

- `canonical_name`
- `aliases`
- `description_notes`
- `first_seen_scene_id`
- `mentioned_in_scene_ids`
- `connected_character_ids`
- `connected_event_ids`

### `object_memory_record`

Additional fields:

- `canonical_name`
- `aliases`
- `description_notes`
- `current_holder_character_id`
- `first_seen_scene_id`
- `mentioned_in_scene_ids`
- `plot_relevance_notes`

### `organization_memory_record`

Additional fields:

- `canonical_name`
- `aliases`
- `members_character_ids`
- `purpose_notes`
- `related_location_ids`
- `related_plot_thread_ids`

### `timeline_event_memory_record`

Additional fields:

- `event_label`
- `event_summary`
- `scene_id`
- `sequence_position`
- `explicit_time_reference`
- `relative_time_reference`
- `involved_character_ids`
- `location_id`
- `causes`
- `effects`
- `uncertainty_notes`

### `relationship_memory_record`

Additional fields:

- `subject_record_id`
- `object_record_id`
- `relationship_type`
- `relationship_summary`
- `direction`
- `status`
- `evidence_scene_ids`
- `uncertainty_notes`

Relationship memory records are project story-knowledge records. They are not Dramatica Relationship Story proof.

### `plot_thread_memory_record`

Additional fields:

- `thread_label`
- `thread_summary`
- `introduced_scene_id`
- `related_scene_ids`
- `related_character_ids`
- `status`
- `unresolved_questions`
- `payoff_notes`

### `annotation_memory_record`

Additional fields:

- `annotation_type`
- `annotation_text`
- `target_type`
- `target_id`
- `source_scene_id`
- `visibility_status`
- `owner_notes`

Annotation text must remain analysis/metadata only. It must not contain generated story prose, replacement prose, or continuation text.

### `open_question_memory_record`

Additional fields:

- `question`
- `question_type`
- `related_record_ids`
- `source_scene_id`
- `why_it_matters`
- `status`

Questions should be diagnostic and writer-facing.

### `continuity_warning_memory_record`

Additional fields:

- `warning_type`
- `warning_summary`
- `conflicting_record_ids`
- `conflicting_sources`
- `affected_record_ids`
- `severity`
- `review_status`
- `resolution_notes`
- `no_rewrite_provided`

`no_rewrite_provided` must be true. A continuity warning may identify a contradiction and ask a diagnostic question, but it must not provide replacement prose.

### `navigation_summary_memory_record`

Additional fields:

- `summary_label`
- `target_type`
- `target_id`
- `summary_text`
- `navigation_only`
- `source_scene_ids`
- `source_chapter_ids`
- `no_rewrite_provided`

Navigation summaries must remain analysis/navigation metadata. They are not replacement scene prose, continuation text, polish suggestions, or generated story passages.

## 6. Proposed File Shapes

Each category file should use a small envelope rather than a bare array, so schema/version/index metadata can evolve.

Example:

```json
{
  "schema_version": "0.1.0",
  "project_id": "example",
  "record_type": "character_memory_record",
  "records": [],
  "updated_at": "2026-06-07T00:00:00Z",
  "notes": []
}
```

Recommended file-to-record mapping:

| File | Record type |
| --- | --- |
| `memory/characters.json` | `character_memory_record` |
| `memory/locations.json` | `location_memory_record` |
| `memory/objects.json` | `object_memory_record` |
| `memory/organizations.json` | `organization_memory_record` |
| `memory/timeline.json` | `timeline_event_memory_record` |
| `memory/relationships.json` | `relationship_memory_record` |
| `memory/plot_threads.json` | `plot_thread_memory_record` |
| `memory/summaries.json` | `navigation_summary_memory_record` |
| `memory/annotations.json` | `annotation_memory_record` |
| `memory/open_questions.json` | `open_question_memory_record` |
| `memory/continuity_warnings.json` | `continuity_warning_memory_record` |

## 7. Promotion Path From OMI to Memory/Canon

Future intended flow:

```text
owner-authored scene/chapter/note text
  -> extraction orchestrator
  -> tool-specific adapters
  -> normalized CORE candidate schemas
  -> evidence/provenance attachment
  -> OMI candidate records
  -> owner review
  -> OMI promotion record
  -> future apply-promotion step
  -> memory/*.json project memory/canon record
```

CORE-004 only designs the target. It does not implement apply-promotion.

CORE-005 OMI review behavior is defined in `docs/roadmap/omi_story_knowledge_candidate_expansion.md`. That spec defines the future OMI-side owner review, merge/deduplication, and promotion-readiness behavior before any apply-promotion implementation exists.

Future apply-promotion must fail closed if any of these are missing:

- Approved OMI candidate.
- Explicit owner approval.
- Final confirmation.
- Destination and safe target file/path.
- Evidence/provenance.
- Promotion record.
- Valid memory record shape.
- Atomic write/rollback-safe behavior.

Promotion records should snapshot the source candidate. Memory records should reference both candidate IDs and promotion record IDs.

Approved project-specific pages should read from memory/canon records only:

- Project Overview approved-memory summary.
- Approved Characters.
- Approved Locations/Settings.
- Approved Timeline.
- Approved Plot Threads.
- Continuity/Consistency.
- Approved Open Questions.
- Approved Relationships.
- Approved Navigation Summaries.
- Approved Project Memory/Canon.

The OMI Ideas and Candidates page should show pending/rejected/uncertain candidates separately from these approved pages.

## 8. Index and Search Implications

Recommended future index:

```text
projects/{project_id}/memory/index.json
```

Suggested fields per index entry:

- `record_id`
- `record_type`
- `label`
- `aliases`
- `status`
- `source_scene_ids`
- `related_record_ids`
- `updated_at`
- `search_keywords`

Index rules:

- `memory/index.json` is recommended for first implementation, but it should be treated as derived convenience state.
- Individual category files remain the source of durable memory truth.
- Missing or stale index entries must not make records unreachable.
- The index should not store full raw scene text or long evidence excerpts.
- Future search/query features can start with the index and load full records on demand.

## 9. Revision and Rollback Strategy

Documentation-level rules:

- Records should not be silently overwritten.
- Changes should append `revision_history`.
- Superseded records should remain traceable.
- Delete should be archive-first unless the owner explicitly deletes.
- Apply-promotion should write atomically or fail closed.
- Failed promotion must not corrupt memory files.
- A promotion record should remain traceable even if the apply step fails.
- Rollback should restore the prior category file and index state together.

Future implementation should define exact atomic write mechanics and tests.

## 10. Relationship and Timeline Graph Implications

The folder model supports later graph/timeline UI without adopting graph libraries now.

Design implications:

- `relationship_memory_record` should use stable `subject_record_id` and `object_record_id`.
- `timeline_event_memory_record` should use `sequence_position`, scene IDs, causal fields, and related character/location IDs.
- `plot_thread_memory_record` should reference related scene and character IDs.
- `navigation_summary_memory_record` should reference source chapters/scenes and mark `navigation_only: true`.
- The future index can provide lightweight relationship/timeline lookup.
- Graph visualization is future-only.
- Storage should not require graph libraries now.
- `AI-Reader-V2` remains UI inspiration only.
- Relationship/timeline extraction tools remain future adapter spikes only.

## 11. Safety and Validation Rules

Future runtime validation should enforce:

- Memory records only come from owner-approved OMI promotion flows.
- Required base fields exist.
- Record IDs are unique within their category.
- Cross-record references either resolve or are explicitly marked unresolved.
- `no_rewrite_provided` is true for continuity warnings.
- Annotation text remains analysis/metadata, not story prose.
- Navigation summary text remains analysis/navigation metadata, not story prose.
- Relationship records do not imply Dramatica Relationship Story proof.
- Timeline/relationship/plot records preserve uncertainty where needed.
- Memory writes do not touch `training/data`, JSONL files, model artifacts, or dataset manifests.
- Memory writes do not mutate scenes, `project.json`, `storyform.json`, or `bible.json` unless a later explicit task adds a separate owner-approved bridge.

## 12. Deferred Decisions

Deferred to later tasks:

- Runtime implementation of `memory/` files.
- Atomic apply-promotion behavior.
- Rollback tests and failure-mode tests.
- Candidate merge/deduplication rules.
- Exact runtime ID and hash generation.
- Exact evidence locator strategy.
- Annotation UI and storage refinements.
- First extractor strategy and dependency spike.
- Whether `bible.json` should eventually mirror a subset of approved project memory.
- Whether memory records should have per-record files if category files become too large.
