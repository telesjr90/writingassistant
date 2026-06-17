# PHASE8-IMPL-002 Candidate Storage and Evidence/Provenance Contract Decision

## 1. Decision Identity

- Parent: `PHASE8-IMPL-002`
- Child: `PHASE8-IMPL-002-T002`
- Title: Candidate storage and evidence/provenance contract decision
- Track: Writer Assistant Core
- Status: accepted
- Date: 2026-06-16
- Dependencies: completed `PHASE8-IMPL-002-T001` and completed `PHASE8-IMPL-001`

## 2. Decision Summary

The first `PHASE8-IMPL-002` runtime direction is:

- **T003**: tests-only candidate storage/evidence contract coverage
- **T004**: tiny pure validation helpers
- **T005**: project-local storage path contract tests
- **T006**: conditional storage helper skeleton only if T005 authorizes it

No storage writes are authorized before T005/T006.

No extraction, routes, UI, model calls, apply-promotion, or memory/canon mutation are authorized by this decision.

This decision defines the typed Writer Assistant Core **storage record contract** that T003 will test and T004 will validate. It builds on the constants-only vocabulary in `backend/story_knowledge/candidate_schema.py` from `PHASE8-IMPL-001` and does not change that module in T002.

## 3. Candidate Record Contract

The canonical typed Writer Assistant Core candidate **storage record** shape is a JSON object with these top-level fields.

### Required now

| Field | Type | Purpose |
| --- | --- | --- |
| `candidate_id` | string | Stable, path-safe, project-local identifier. |
| `project_id` | string | Filesystem-safe project identifier. |
| `candidate_type` | string | One of `CORE_CANDIDATE_TYPES`. |
| `status` | string | Candidate lifecycle status (see section 11). |
| `target_category` | string | Review destination category aligned with `CORE_CANDIDATE_TARGET_CATEGORIES`. |
| `source_locator` | object | Project-local source reference (see section 7). |
| `evidence` | array | Evidence records supporting the candidate (see section 8). |
| `provenance` | object | Origin and review trail (see section 9). |
| `owner_decision` | string | Owner review metadata (see section 12). |
| `destination` | string | Candidate routing hint (see section 13). |
| `confidence` | number | Numeric confidence in `[0.0, 1.0]` (see section 10). |
| `created_at` | string | ISO-8601 timestamp for record creation. |
| `updated_at` | string | ISO-8601 timestamp for last record update. |

### Optional now

| Field | Type | Purpose |
| --- | --- | --- |
| `uncertainty` | string or array of strings | Human-readable uncertainty notes. |
| `links` | array | Future cross-links to other candidate or source records. |
| `notes` | string or array | Review or implementation notes. |
| `owner_review_notes` | string or array | Owner-specific review notes. |
| `schema_version` | string | Optional record schema version label. |
| `source_snapshot_hash` | string or null | Optional hash of source snapshot at record creation. |

### Rules

- The record is candidate-only. Valid shape does not create approved memory/canon.
- `evidence` must exist and may be an empty array before extraction exists.
- `target_category` must match the mapped category for `candidate_type`.
- Records must remain project-local JSON under the future storage path (section 14).

Recommended minimal record example:

```json
{
  "candidate_id": "core_candidate_scene_character_001",
  "project_id": "example",
  "candidate_type": "character_candidate",
  "status": "candidate",
  "target_category": "characters",
  "source_locator": {
    "project_id": "example",
    "source_document_type": "scene",
    "source_document_id": "scene_001"
  },
  "evidence": [],
  "provenance": {
    "origin": "manual",
    "extraction_method": "owner_entry",
    "timestamp": "2026-06-16T00:00:00Z",
    "human_review_required": true
  },
  "owner_decision": "undecided",
  "destination": "omi_candidate_only",
  "confidence": 0.0,
  "created_at": "2026-06-16T00:00:00Z",
  "updated_at": "2026-06-16T00:00:00Z"
}
```

## 4. Candidate Identity Contract

- IDs must be stable strings.
- IDs must be path-safe.
- IDs must not contain slashes, backslashes, traversal sequences, absolute paths, or Windows drive prefixes.
- IDs must be project-local identifiers, not host filesystem paths.
- ID generation is deferred to later helpers; T003/T004 validate shape only.

Recommended format: `core_candidate_<safe-token>` or an equivalent safe slug prefixed by type or scope.

UUID format is not required unless a later task adopts it for consistency with other project IDs.

## 5. Candidate Type Contract

Candidate records must use exactly one value from `CORE_CANDIDATE_TYPES` in `backend/story_knowledge/candidate_schema.py`:

- `character_candidate`
- `location_candidate`
- `object_candidate`
- `organization_candidate`
- `timeline_event_candidate`
- `relationship_candidate`
- `plot_thread_candidate`
- `navigation_summary_candidate`
- `continuity_warning_candidate`
- `contradiction_candidate`
- `annotation_candidate`
- `open_question_candidate`
- `scene_event_causality_review_candidate`

T003 must test that stored records accept only these known types.

No new candidate type may imply prose generation, rewriting, continuation, automatic promotion, or approved truth.

Forbidden type labels include: `generated_prose`, `rewrite`, `continuation`, `style_imitation`, `prose_improvement`, `summary_as_canon`, `apply_promotion`.

## 6. Target Category Contract

`target_category` must align with `CORE_CANDIDATE_TARGET_CATEGORIES` in `candidate_schema.py`.

Rules:

- Target categories are review destinations/categories, not approved memory/canon.
- A candidate with a target category remains candidate-only.
- Category alignment does not create approved truth.
- `target_category` must equal the mapped value for the record's `candidate_type`.

## 7. Source Locator Contract

The canonical `source_locator` object uses field names from `CORE_SOURCE_LOCATOR_FIELDS`.

Recommended shape:

```json
{
  "project_id": "example",
  "source_document_type": "scene",
  "source_document_id": "scene_001",
  "section_id": null,
  "chapter_id": null,
  "scene_id": null,
  "start_offset": null,
  "end_offset": null,
  "line_start": null,
  "line_end": null,
  "source_hash": null
}
```

### Required now

- `project_id`
- `source_document_type`
- `source_document_id`

### Optional now

- `section_id`
- `chapter_id`
- `scene_id`
- `start_offset`
- `end_offset`
- `line_start`
- `line_end`
- `source_hash`

### Allowed `source_document_type` values

- `scene`
- `note`
- `material`
- `bible`
- `storyform`
- `omi`

### Rules

- Do not allow arbitrary filesystem paths, absolute host paths, training paths, or dataset manifest paths.
- Forbidden locator field names include: `external_book_path`, `training_file_path`, `dataset_manifest_path`, `absolute_filesystem_path`.
- Locators must remain project-local references by document type and ID.

## 8. Evidence Contract

Evidence supports the candidate claim. It is not generated prose.

Each evidence item is an object. The top-level `evidence` field is an array of such objects.

Recommended evidence item shape:

```json
{
  "evidence_id": "evidence_001",
  "source_locator": {},
  "source_text_excerpt": "",
  "summary": "",
  "supports_claim": "",
  "confidence": 0.0,
  "notes": ""
}
```

Field names align with `CORE_EVIDENCE_FIELDS` in `candidate_schema.py`.

### Required per evidence item now

- `source_locator` (nested object meeting section 7 minimum requirements)
- `confidence` (numeric in `[0.0, 1.0]` or bounded string label until extraction exists)

### Optional per evidence item now

- `evidence_id`
- `source_text_excerpt`
- `summary`
- `supports_claim`
- `notes`
- `line_start`
- `line_end`
- `start_offset`
- `end_offset`

### Rules

- The top-level `evidence` array must exist. It may be empty before extraction exists.
- Evidence text, if present, must be owner-authored excerpt/support, not AI-generated prose.
- Evidence must remain project-local.
- Evidence does not approve or promote the candidate.

## 9. Provenance Contract

Provenance records origin and review trail. It supports review; it does not grant authority.

Recommended shape using `CORE_PROVENANCE_FIELDS` names:

```json
{
  "origin": "manual",
  "extraction_method": "owner_entry",
  "timestamp": "2026-06-16T00:00:00Z",
  "human_review_required": true,
  "updated_at": null,
  "source_hash": null,
  "snapshot_hash": null,
  "created_by": "owner",
  "source_type": "owner_input"
}
```

### Required now

- `origin` — bounded values: `manual`, `extractor`, `model_assisted`, `imported`
- `extraction_method` — bounded values include `owner_entry`, `future_extractor`, `future_model_adapter`
- `timestamp` — ISO-8601 creation timestamp for provenance
- `human_review_required` — boolean review requirement

### Optional now

- `updated_at`
- `source_hash`
- `snapshot_hash`
- `created_by`
- `source_type`
- `owner_reviewed`
- `license_status`
- future adapter fields such as `adapter_name`, `adapter_version`, `reviewed_at`, `reviewed_by`

### Rules

- `origin` must not imply authority or approved truth.
- `model_assisted` and `future_model_adapter` remain future-only until model routes exist.
- Provenance supports review only; it does not apply promotion or mutate memory/canon.

## 10. Confidence and Uncertainty Contract

- Top-level `confidence` must be numeric with suggested range `0.0 <= confidence <= 1.0`.
- Evidence-item `confidence` may be numeric or a bounded string label until extraction normalizes values.
- Top-level `uncertainty` is optional and may be a string or list of strings in T003/T004.
- Structured uncertainty objects may be added later without breaking the optional string/list contract.

## 11. Status Contract

Stored records must use values from `CORE_CANDIDATE_STATUS_VALUES` except where this decision forbids a value before apply-promotion exists.

Allowed for stored Writer Assistant Core records now:

- `candidate`
- `owner_review`
- `approved`
- `rejected`
- `needs_revision`
- `archived`

Optional future extension:

- `draft` — may be added by T003/T004 if tests need a pre-candidate state; not required in T003.

Forbidden on stored records until explicit apply-promotion work exists:

- `promoted` — may remain in schema constants vocabulary but must not appear on stored typed Writer Assistant Core records in T003/T004/T005/T006.

Rules:

- `approved` means approved as candidate/review state only.
- It does not mean applied durable memory/canon.
- Status changes do not mutate bible, storyform, scenes, notes, materials, or `memory/*.json`.

## 12. Owner Decision Contract

Stored records must use string values from `CORE_OWNER_DECISION_VALUES`:

- `undecided`
- `approve`
- `reject`
- `needs_revision`
- `archive`

Forbidden on stored records until explicit apply-promotion work exists:

- `promote`

Rules:

- Owner decision is review metadata.
- Owner decision alone does not mutate memory/canon.
- Durable truth remains future apply-promotion work.

## 13. Destination Contract

Stored records must use values from `CORE_DESTINATION_VALUES`:

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
- `contradiction_memory_candidate`
- `discard`

Forbidden destination labels:

- `apply_promotion`
- `auto_promote`
- `write_to_canon`
- `mutate_memory`
- `rewrite_scene`

Rules:

- Destinations are candidate routing hints only.
- They do not write to bible, storyform, scenes, notes, materials, or approved memory/canon files.
- Destination labels ending in `_memory_candidate` name a future review target, not applied truth.

## 14. Storage Path Decision

Future typed Writer Assistant Core candidate records may live in a separate project-local folder distinct from existing generic OMI MVP candidate storage.

Recommended future paths:

- Record file: `projects/{project_id}/writer_assistant/candidates/{candidate_id}.json`
- Optional future index: `projects/{project_id}/writer_assistant/index.json`

Rationale:

- Separates typed Writer Assistant Core candidate records from existing OMI generic candidate MVP files.
- Keeps future extraction candidates candidate-only.
- Avoids writing to `memory/`, `bible.json`, `storyform.json`, scenes, notes, or materials.
- Avoids confusing candidate records with approved canon.

Important:

- This decision does not authorize storage writes in T002, T003, or T004.
- T005 should test the path contract and storage boundaries.
- T006 may implement a storage helper skeleton only if T005 authorizes it.

## 15. Path-Safety Decision

Path-safety requirements for IDs, locators, and future storage helpers:

- Project IDs and candidate IDs must pass existing safe ID patterns or equivalent validation used elsewhere in the project backend.
- No absolute paths in IDs or locators.
- No traversal sequences (`..`, encoded traversal, or mixed separators used to escape project roots).
- No slashes or backslashes in candidate IDs.
- No Windows drive prefixes in IDs or locators.
- No hidden filesystem expansion outside the selected project root.
- Future writes must remain inside `projects/{project_id}/writer_assistant/candidates/`.
- Future reads/lists must be side-effect free.
- T004 validation helpers must not create files or directories.

## 16. T003 Scope Decision

`PHASE8-IMPL-002-T003` — Candidate storage/evidence contract tests.

**Decision: T003 is tests-only.**

T003 should add tests for:

- Candidate record required and optional fields
- Candidate type allowed values
- Target category alignment with `candidate_type`
- Source locator required/optional fields and forbidden path fields
- Evidence required/optional fields and empty-array allowance
- Provenance required/optional fields
- Confidence numeric range
- Status, owner decision, and destination allowed values
- Forbidden destination mutation labels
- Forbidden `promoted` status and `promote` owner decision on stored records until apply-promotion exists
- Storage path contract as a future expectation (no writes in T003)
- No memory/canon mutation behavior
- No extraction, model, or import behavior
- No backend routes or frontend files

Expected red or explicit pending behavior:

- T003 may be expected red if it imports future validation helpers not yet implemented in T004.
- Alternatively, T003 may use local test fixtures and mark helper-dependent expectations as explicit `xfail` or pending.
- T003 must not require production validation helper code.

Likely test file: `tests/test_writer_assistant_core_candidate_record_contract.py` (exact name chosen in T003).

## 17. T004 Scope Decision

`PHASE8-IMPL-002-T004` — Candidate record validation helpers.

Allowed:

- Tiny pure validation helpers
- Static schema/contract metadata if needed
- No file I/O
- No storage writes
- No routes
- No UI
- No model calls
- No extraction
- No apply-promotion
- No memory/canon mutation

Likely future modules (T003 may select through imports):

- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_validation.py`

T004 implements only enough helper surface to satisfy T003 contract tests.

## 18. T005/T006 Storage Boundary Decision

- T005 tests path contract and storage boundaries before any storage helper skeleton.
- T005 verifies that future candidate storage stays under `projects/{project_id}/writer_assistant/` and never writes to memory/canon/bible/storyform/scene/note/material truth paths.
- T006 may implement a minimal storage helper skeleton only if T005 explicitly authorizes it.
- If T005 finds storage writes too risky, T005/T006 remain decision/test-only and defer writes to a later parent such as `PHASE8-IMPL-003`.
- No storage writes are authorized in T002, T003, or T004 regardless of T005 outcome.

## 19. Deferred Work

- Extraction runtime
- Model/Ollama integration
- Candidate creation from owner text
- Backend extraction routes
- Frontend extraction UI
- Semantic search
- Story Check auto-runs
- Apply-promotion
- Memory/canon mutation
- Candidate-to-canon promotion application
- Package/dependency additions
- Training/JSONL/dataset work
- Browser/manual validation
- Storage writes before T005/T006 authorization

## 20. Acceptance Criteria

T002 is complete when:

- This decision file exists and records the contract shape explicitly enough for T003 tests.
- T003 tests-only scope is clear.
- T004 helper scope is clear.
- Storage write boundary is explicit.
- Roadmap/status files mark T002 complete and T003 ready/active.
- Validators pass.
- No code, tests, or runtime files changed in T002.
