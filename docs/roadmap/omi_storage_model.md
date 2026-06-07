# OMI MVP Storage Model

## 1. Executive Summary

This specification defines the target MVP storage model for Organize My Idea (OMI). It is a design target only. It does not create runtime OMI files, backend endpoints, frontend UI, candidate records, promotion behavior, or generated prose.

OMI storage must keep raw ideas, structured candidates, owner decisions, destinations, provenance, statuses, and promotion records separate from owner-approved project truth. OMI records are candidate planning material until an explicit owner-controlled promotion flow approves a destination and records provenance.

OMI storage has a no prose generation boundary: OMI records may store structural planning candidates, diagnostic questions, evidence/provenance, and owner decisions, but they must not store generated story prose as an output or promotion target.

Current implementation status:

- OMI MVP backend/frontend slices now exist for raw idea and structured candidate creation/list/load, owner decision/status/destination updates, record-only promotion creation, and UI lifecycle/status/provenance display.
- OMI still does not apply promotions to durable truth files.
- Existing ignored local OMI artifacts may exist under `projects/example/omi/`, but tracked fixture files remain clean unless owner-approved separately.
- `docs/roadmap/omi_mvp_schema_lifecycle.md` defines the OMI lifecycle and field boundary.
- This storage model remains the design source for expanding OMI into the central Writer Assistant Core candidate review/promotion system.
- CORE-002/CORE-003 schema reference: `docs/roadmap/writer_assistant_core_candidate_schemas.md` defines future typed story-knowledge candidates and shared evidence/provenance models. This storage document keeps the record layout; the new schema document defines candidate content contracts.

## 2. Target Storage Layout

Target project-local layout:

```text
projects/{project_id}/
  omi/
    ideas/
      {idea_id}.json
    candidates/
      {candidate_id}.json
    promotions/
      {promotion_id}.json
    index.json
```

This layout is not implemented yet. Future runtime tasks must create these folders only through safe project path helpers and only after the owner starts using OMI.

Storage boundaries:

- `omi/ideas/` stores owner-authored raw ideas and their lifecycle state.
- `omi/candidates/` stores structured candidate planning material derived from ideas, owner project text, model output, NotebookLM output, retrieved references, extractor output, or owner review.
- `omi/promotions/` stores explicit owner-approved promotion attempts and records before any future target mutation.
- `omi/index.json` stores references and summary metadata for OMI records.
- OMI files cannot overwrite `bible.json`, `storyform.json`, `owner_memory.json`, `project.json`, or `scenes/`.

Writer Assistant Core candidate types planned for future OMI expansion:

- `character_candidate`
- `location_candidate`
- `object_candidate`
- `organization_candidate`
- `timeline_event_candidate`
- `relationship_candidate`
- `plot_thread_candidate`
- `continuity_warning_candidate`
- `annotation_candidate`
- `open_question_candidate`

All extracted story knowledge remains candidate-only until owner approval, destination selection, evidence/provenance review, and final confirmation. OMI promotion records are not automatic canon mutation.

These candidate classes are future OMI expansion targets. They are not runtime extractor implementations, project memory/canon files, or durable truth mutations.

## 3. OMI Idea Record

An OMI idea record captures owner-authored raw idea input. It is not durable project truth by itself.

Required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `idea_id` | string | Stable single-record identifier. |
| `project_id` | string | Filesystem-safe project identifier. |
| `raw_idea` | string | Owner-authored source idea. It is not an assistant request when being saved. |
| `status` | string | Lifecycle status. |
| `created_at` | string | ISO-8601 creation timestamp. |
| `updated_at` | string | ISO-8601 update timestamp. |
| `provenance` | object | Source and authorship trail. |
| `owner_decision` | object | Current owner review decision. |
| `linked_candidate_ids` | array | Candidate records derived from this idea. |

Schema-like example:

```json
{
  "idea_id": "idea_20260602_001",
  "project_id": "example",
  "raw_idea": "Owner-authored idea text stored as candidate planning input.",
  "status": "draft",
  "created_at": "2026-06-02T00:00:00Z",
  "updated_at": "2026-06-02T00:00:00Z",
  "provenance": {
    "source_type": "owner_input",
    "source_path": null,
    "source_label": "manual OMI idea",
    "created_by": "owner",
    "tool": "omi",
    "model": null,
    "prompt_id": null,
    "timestamp": "2026-06-02T00:00:00Z",
    "source_hash": null,
    "snapshot_hash": null,
    "confidence": null,
    "notes": []
  },
  "owner_decision": {
    "approved": false,
    "decision": "undecided",
    "decided_at": null,
    "decided_by": null,
    "notes": ""
  },
  "linked_candidate_ids": []
}
```

Rules:

- `raw_idea` may contain fragmentary owner text, planning language, or quoted owner notes.
- Saving `raw_idea` must not be blocked as request intent.
- `raw_idea` must not be copied into bible, storyform, owner memory, scenes, or analysis artifacts without a candidate and promotion record.
- The idea record can link to candidate IDs, but linked candidates remain candidate-only.

## 4. OMI Candidate Record

An OMI candidate record stores structured planning material. It can be owner-authored, model-assisted, NotebookLM-assisted, reference-informed, or manually edited, but it remains candidate-only until promoted.

Required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `candidate_id` | string | Stable candidate identifier. |
| `project_id` | string | Filesystem-safe project identifier. |
| `idea_id` | string | Source idea identifier. |
| `candidate_type` | string | Candidate class such as planning note or storyform context candidate. |
| `candidate_content` | object | Structured candidate material, not story prose. |
| `status` | string | Lifecycle status. |
| `destination` | string | Proposed destination. |
| `provenance` | object | Source and generation/review trail. |
| `evidence` | array | Evidence, references, or owner notes supporting review. |
| `owner_decision` | object | Owner decision state. |
| `promotion_status` | object | Promotion eligibility and blocking state. |
| `created_at` | string | ISO-8601 creation timestamp. |
| `updated_at` | string | ISO-8601 update timestamp. |

Schema-like example:

```json
{
  "candidate_id": "omi_candidate_20260602_001",
  "project_id": "example",
  "idea_id": "idea_20260602_001",
  "candidate_type": "storyform_context_candidate",
  "candidate_content": {
    "summary": "Structural planning candidate only.",
    "fields": [],
    "diagnostic_questions": [],
    "insufficient_evidence": []
  },
  "status": "candidate",
  "destination": "storyform_context_candidate",
  "provenance": {
    "source_type": "model_output",
    "source_path": "omi/ideas/idea_20260602_001.json",
    "source_label": "OMI candidate from owner idea",
    "created_by": "assistant",
    "tool": "omi",
    "model": "qwen3:8b",
    "prompt_id": "omi_candidate_v1",
    "timestamp": "2026-06-02T00:00:00Z",
    "source_hash": null,
    "snapshot_hash": "sha256:...",
    "confidence": "candidate_only",
    "notes": []
  },
  "evidence": [],
  "owner_decision": {
    "approved": false,
    "decision": "undecided",
    "decided_at": null,
    "decided_by": null,
    "notes": ""
  },
  "promotion_status": {
    "eligible": false,
    "blocked_reasons": [
      "owner approval required",
      "final confirmation required"
    ],
    "promotion_id": null
  },
  "created_at": "2026-06-02T00:00:00Z",
  "updated_at": "2026-06-02T00:00:00Z"
}
```

Rules:

- `candidate_content` must be structured planning material, not generated scene prose.
- Model-authored `candidate_content` must be output-sanitized before display or save.
- Candidate records cannot overwrite durable project truth.
- Candidate records can reference evidence, but evidence does not establish story truth without owner approval.
- Positive OS/MC/IC/RS/CIPS/dynamics claims remain candidate-only unless owner-approved and evidence-backed.
- Character, location, object, organization, event, relationship, plot, continuity, annotation, and open-question candidates must preserve uncertainty and evidence locators where practical.
- Relationship candidates are generic story-knowledge candidates by default and must not be treated as Dramatica Relationship Story proof.

## 5. OMI Promotion Record

An OMI promotion record stores the owner-approved intent to move a candidate into a chosen target. It must exist before any future target mutation.

Required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `promotion_id` | string | Stable promotion identifier. |
| `project_id` | string | Filesystem-safe project identifier. |
| `candidate_id` | string | Candidate being promoted. |
| `destination` | string | Explicit chosen destination. |
| `owner_approval` | object | Approval and final confirmation details. |
| `provenance` | object | Source trail from raw idea through candidate. |
| `evidence` | array | Supporting evidence or owner notes required for the destination. |
| `source_snapshot` | object | Immutable candidate snapshot at promotion time. |
| `target_file` | string | Explicit target file, when future implementation allows mutation. |
| `target_path` | string | Explicit JSON path or insertion path, when applicable. |
| `created_at` | string | ISO-8601 creation timestamp. |
| `confirmed_at` | string or null | Final owner confirmation timestamp. |
| `status` | string | Promotion lifecycle status. |

Schema-like example:

```json
{
  "promotion_id": "omi_promotion_20260602_001",
  "project_id": "example",
  "candidate_id": "omi_candidate_20260602_001",
  "destination": "storyform_context_candidate",
  "owner_approval": {
    "approved": true,
    "approved_by": "owner",
    "approved_at": "2026-06-02T00:00:00Z",
    "final_confirmation": true,
    "confirmation_text": "owner confirmed promotion"
  },
  "provenance": {
    "source_type": "omi_candidate",
    "source_path": "omi/candidates/omi_candidate_20260602_001.json",
    "source_label": "owner-approved OMI candidate",
    "created_by": "owner",
    "tool": "omi",
    "model": null,
    "prompt_id": null,
    "timestamp": "2026-06-02T00:00:00Z",
    "source_hash": "sha256:...",
    "snapshot_hash": "sha256:...",
    "confidence": "owner_approved",
    "notes": []
  },
  "evidence": [],
  "source_snapshot": {},
  "target_file": "storyform.json",
  "target_path": "/story/narratives/0/subtext/storypoints",
  "created_at": "2026-06-02T00:00:00Z",
  "confirmed_at": "2026-06-02T00:00:00Z",
  "status": "approved"
}
```

Rules:

- Promotion records are audit records, not automatic mutation permission by themselves.
- Future target mutation must be atomic or rollback-safe.
- Promotion records must snapshot the candidate before mutation.
- Promotion to scene prose is forbidden.
- Promotion into `bible.json`, `storyform.json`, or `owner_memory.json` is future-only and must be explicit.

## 6. OMI Index

`omi/index.json` is a project-local lookup file for OMI record IDs and summary metadata.

Required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `project_id` | string | Filesystem-safe project identifier. |
| `idea_ids` | array | Known idea record IDs. |
| `candidate_ids` | array | Known candidate record IDs. |
| `promotion_ids` | array | Known promotion record IDs. |
| `last_updated` | string | ISO-8601 timestamp. |

Schema-like example:

```json
{
  "project_id": "example",
  "idea_ids": [],
  "candidate_ids": [],
  "promotion_ids": [],
  "last_updated": "2026-06-02T00:00:00Z"
}
```

Rules:

- The index is derived convenience state.
- Missing index entries must not make records unreachable if individual files exist.
- Future writes should update record file and index consistently.
- The index must not contain full raw idea or candidate content.

## 7. Status Model and Transitions

Allowed statuses:

- `draft`: captured but not ready for candidate review.
- `candidate`: structured candidate planning material exists.
- `owner_review`: ready for owner decision.
- `approved`: owner approved a record for a specific destination.
- `rejected`: owner rejected a record.
- `promoted`: approved candidate has passed the promotion gate and the future target mutation completed.
- `archived`: inactive but retained for traceability.

Idea transitions:

- `draft` -> `candidate`
- `draft` -> `owner_review`
- `draft` -> `archived`
- `owner_review` -> `approved`
- `owner_review` -> `rejected`
- `owner_review` -> `candidate`
- `approved` -> `archived`
- `rejected` -> `archived`

Candidate transitions:

- `candidate` -> `owner_review`
- `candidate` -> `rejected`
- `candidate` -> `archived`
- `owner_review` -> `approved`
- `owner_review` -> `rejected`
- `owner_review` -> `candidate`
- `approved` -> `promoted` only through the promotion gate
- `approved` -> `archived`
- `rejected` -> `archived`
- `promoted` -> `archived`

Promotion transitions:

- `draft` -> `owner_review`
- `owner_review` -> `approved`
- `owner_review` -> `rejected`
- `approved` -> `promoted` only after target mutation succeeds
- `approved` -> `archived`
- `rejected` -> `archived`
- `promoted` -> `archived`

Blocked transitions:

- `candidate` -> `promoted` without owner approval.
- `draft` -> `promoted`.
- `owner_review` -> `promoted` without approved status and final confirmation.
- `rejected` -> `promoted`.
- `archived` -> `promoted`.
- Raw model output -> `bible.json`, `storyform.json`, `owner_memory.json`, `project.json`, or `scenes/` without candidate record and approval.
- NotebookLM output -> durable truth without provenance and owner approval.
- `raw_idea` -> durable truth without candidate record and promotion record.
- Any OMI output -> scene prose generation destination.

## 8. Destination Model

Allowed MVP destinations:

| Destination | Role | Future promotable? |
| --- | --- | --- |
| `planning_notes` | Candidate planning note storage or owner memory note. | Yes, with owner approval and target path. |
| `project_bible_candidate` | Candidate fact, relationship, place, object, or continuity context. | Yes, to `bible.json` after approval. |
| `storyform_context_candidate` | Candidate NCP/storyform context. | Yes, to `storyform.json` after approval and evidence. |
| `scene_prompt_context_candidate` | Candidate context for owner-authored scene planning. | Candidate-only for MVP; cannot write scene prose. |
| `template_starter_candidate` | Structural scaffold, checklist, or empty field starter. | Candidate-only for MVP; cannot include story prose. |
| `discard` | Rejected or unwanted material. | No. |

Destination rules:

- No destination may write generated story prose.
- No destination may create scene, dialogue, chapter, paragraph, opening, ending, or continuation text.
- Scene-related destinations can only store structural context for the owner to use while writing their own text.
- Destination choice is required before approval or promotion.

## 9. Provenance Model

Every OMI idea, candidate, and promotion record must include provenance.

Required provenance fields:

| Field | Purpose |
| --- | --- |
| `source_type` | Source category such as owner_input, model_output, notebooklm_candidate, retrieved_reference, story_check_candidate, manual_owner_edit, or omi_candidate. |
| `source_path` | Project-relative path or external/local path when safe to store. |
| `source_label` | Human-readable source label. |
| `created_by` | owner, assistant, system, import, or tool identifier. |
| `tool` | Tool or app path that produced the record. |
| `model` | Model name if model-assisted; null for owner/manual-only records. |
| `prompt_id` | Prompt/template identifier if model-assisted. |
| `timestamp` | Source capture timestamp. |
| `source_hash` | Hash of source content where practical. |
| `snapshot_hash` | Hash of stored candidate or promotion snapshot where practical. |
| `confidence` | Candidate confidence/status label, not story truth certainty. |
| `notes` | Additional provenance notes. |

Source role rules:

- `docs/owner_sample_input.md` may be a future raw idea source only. It is not project truth.
- NotebookLM output is candidate-only.
- Model output is candidate-only.
- Retrieved definitions are reference-only and cannot establish story-specific truth.
- The public-domain scene fixture is not the OMI source for owner ideas.
- Schema validity and model confidence do not prove story truth.

## 10. Promotion Gate

Promotion requires all of the following:

- Candidate record exists.
- Candidate status is `approved`.
- `owner_decision.approved` is `true`.
- Destination is selected and allowed.
- Provenance is present.
- Evidence is present where required by the destination.
- Final owner confirmation is present.
- Target file is explicitly chosen.
- Target path is explicitly chosen when mutating structured JSON.
- Promotion record is created before target mutation.
- Future mutation is atomic or rollback-safe.
- No generated prose destination is involved.

Promotion must fail closed when any requirement is missing.

Promotion cannot target:

- Scene prose generation.
- Generated dialogue.
- Generated chapters, paragraphs, monologues, openings, endings, or continuations.
- Raw model output as durable truth.
- NotebookLM candidate output as durable truth without owner approval and provenance.
- Retrieved reference definitions as story-specific truth.

## 11. Storage Safety Rules

Future implementation must enforce:

- Safe project path handling.
- OMI record IDs as single path components.
- No path traversal.
- JSON object only for OMI records.
- Deterministic pretty JSON formatting.
- UTF-8 writes.
- No silent overwrite.
- Save failures preserve existing files.
- Candidate records cannot overwrite bible, storyform, owner memory, project metadata, scenes, or analysis artifacts.
- Promotions require a separate promotion record before any target mutation.
- Deleted or archived records remain traceable unless explicit owner action safely removes them.
- Runtime OMI storage must not write to `training/data`.
- Runtime OMI storage must not modify `dataset_manifest.json`.

Recommended future write behavior:

- Write candidate/promotion records to a temporary file first.
- Validate JSON object shape before replacing existing record.
- Replace atomically where platform support allows.
- Update `omi/index.json` only after record write succeeds.
- Surface write errors without losing owner-entered text.

## 12. Guardrail Implications

Future OMI request fields:

- Freeform assistant/model instruction fields must call `guard_freeform_request` before model calls.
- Owner-authored content fields such as `raw_idea`, planning notes, scene content, bible JSON, and storyform JSON must not be blocked as request intent while being saved.

Future OMI output fields:

- Model-authored `candidate_content` must pass output sanitization before display or save.
- Output guard failures should block unsafe candidate display/save or replace unsafe text with safe diagnostics.
- OMI model outputs remain candidate-only after sanitization.
- No OMI path may write, rewrite, continue, imitate, polish, improve, or extend story prose.

Promotion guard:

- Request/output guard success is necessary but not sufficient for promotion.
- Owner approval, destination, provenance, evidence, status, and final confirmation are still required.

## 13. Runtime Implementation Implications

Future tasks and likely files:

### OMI-003 Candidate Creation Backend API

Expected scope:

- Add storage helpers for ideas, candidates, promotions, and index.
- Add backend routes to create/list/read OMI ideas and candidates.
- Keep owner-authored `raw_idea` separate from freeform assistant request intent.

Likely files:

- `backend/project_manager.py`
- `backend/main.py`
- `backend/guardrails.py`
- `tests/test_omi_storage.py`
- `tests/test_omi_routes.py`

### OMI-004 Owner Decision and Destination Selection UI

Expected scope:

- Add owner decision and destination controls.
- Show candidate-only, provenance, and status labels.
- Preserve unsaved owner edits and visible errors.

Likely files:

- `frontend/src/App.jsx`
- `frontend/src/api.js`
- future `frontend/src/components/OMI*.jsx`
- `frontend/src/styles.css`
- UI smoke/build tests if a frontend test runner exists later.

### OMI-005 Promotion Gate Enforcement

Expected scope:

- Enforce promotion requirements before any target mutation.
- Create promotion record before target mutation.
- Keep future mutation atomic or rollback-safe.

Likely files:

- `backend/project_manager.py`
- `backend/main.py`
- `tests/test_omi_promotion.py`

### OMI-006 OMI UI

Expected scope:

- Add raw idea input, candidate list, candidate detail view, status/provenance display, destination selector, and final confirmation UI.
- Keep no-prose boundary copy visible.

Likely files:

- `frontend/src/App.jsx`
- `frontend/src/api.js`
- future `frontend/src/components/OMI*.jsx`
- `frontend/src/styles.css`

### OMI-007 Tests for No-Prose and No-Silent-Promotion

Expected scope:

- Cover request guard, output guard, owner-authored content saves, candidate lifecycle, promotion blocking, path traversal, and owner decision gates.

Likely files:

- `tests/test_omi_storage.py`
- `tests/test_omi_routes.py`
- `tests/test_request_guards.py`
- `tests/test_output_guards.py`

## 14. Testing Implications

Future tests should cover:

- Storage helper tests for ideas, candidates, promotions, and index.
- Route tests for create/list/read/update paths.
- No path traversal for project IDs and OMI record IDs.
- Candidate lifecycle transitions.
- Blocked transitions.
- No silent promotion.
- No-prose request guard on freeform OMI instruction fields.
- Output guard on model-authored candidate fields.
- Owner-authored `raw_idea` save is not overblocked.
- Owner decision gate.
- Destination gate.
- Evidence/provenance requirements.
- Atomic or rollback-safe target mutation.
- UI smoke/build tests.

## 15. Acceptance Checklist

- [x] Target storage layout defined.
- [x] OMI idea record required fields defined.
- [x] OMI candidate record required fields defined.
- [x] OMI promotion record required fields defined.
- [x] OMI index required fields defined.
- [x] Statuses and transitions defined.
- [x] Blocked transitions defined.
- [x] Destinations defined.
- [x] Provenance model defined.
- [x] Promotion gate requirements defined.
- [x] Storage safety rules defined.
- [x] Guardrail implications defined.
- [x] Future runtime tasks listed.
- [x] Test implications listed.
- [x] Spec states this is design-only and not implemented.

## 16. Recommended Next Task

Recommended next App MVP task: OMI-003 candidate creation flow, starting with backend storage helpers and route preflight while preserving the no-prose, candidate-only, and no-silent-promotion boundaries in this spec.
