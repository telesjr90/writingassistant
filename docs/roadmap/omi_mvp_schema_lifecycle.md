# OMI MVP Schema and Lifecycle

## 1. Executive Summary

This specification defines the App MVP design target for Organize My Idea (OMI). OMI is for capturing a writer's raw idea, organizing it into structured planning candidates, asking diagnostic questions, preparing owner-review packets, and later supporting guided project creation without taking over authorship.

OMI is not allowed to write, rewrite, continue, imitate, polish, improve, or extend story prose. It must not generate scenes, chapters, paragraphs, dialogue, monologues, openings, endings, or prose passages. It must not silently mutate `bible.json`, `storyform.json`, `owner_memory.json`, planning notes, analysis artifacts, or scenes.

What exists now:

- OMI MVP runtime slices now exist for owner-authored raw idea and structured candidate records, owner decisions, destination/status updates, record-only promotion creation, and UI lifecycle/status/provenance display.
- OMI still has no apply-promotion behavior and does not mutate durable project truth.
- App-2 defines the project file model target, including project-local OMI folders.
- App-3 defines the safe NCP/storyform subset that OMI may use as candidate planning context, now as a later advanced layer rather than the next product backbone.
- Story Check remains the only model-backed analysis path; Writer Assistant Core extraction is future work.
- Project Workspace Foundation is the next product milestone before expanded extraction or Dramatica-specific work. OMI should support guided project creation and idea capture as owner-controlled setup candidates.
- WORKSPACE-004 dedicated planning for guided setup lives in `docs/roadmap/omi_guided_project_creation_spec.md`; it recommends staged setup state before project creation, then project-local OMI records after owner confirmation.

MVP target:

- OMI is project-local, analysis-only, candidate-first, owner-controlled, and no-prose.
- OMI records `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`.
- OMI can capture project ideas before a project is fully structured and organize owner-provided ideas into setup candidates.
- OMI may propose candidate storyform slots and diagnostic questions, but those slots remain candidate-only until explicit owner approval.
- Promotion requires owner approval, destination, provenance, status, source candidate ID, timestamp, and final confirmation.
- For Writer Assistant Core, OMI becomes the central review/promotion system for extracted story knowledge. Extracted characters, aliases, locations, objects, organizations, events, relationships, plot threads, annotations, open questions, continuity warnings, and contradiction warnings must enter OMI as candidates before any durable project memory/canon promotion.
- CORE-002/CORE-003 schema reference: `docs/roadmap/writer_assistant_core_candidate_schemas.md` defines the future Writer Assistant Core candidate types, shared base candidate contract, evidence model, provenance model, owner decision model, and promotion status model. Those candidate types are future OMI-supported classes; this spec does not make them runtime-implemented by itself.
- CORE-004 storage reference: `docs/roadmap/project_memory_canon_storage_model.md` recommends future folder-based `memory/*.json` files as the durable project memory/canon target after OMI review and a later apply-promotion step.
- CORE-005 OMI expansion reference: `docs/roadmap/omi_story_knowledge_candidate_expansion.md` defines future OMI typed review behavior for story-knowledge candidates, including candidate type filters, owner actions, merge/dedup planning, promotion-readiness rules, and review UI needs.
- WORKSPACE-011 page-structure reference: `docs/roadmap/project_memory_canon_page_structure_spec.md` defines how future Project Memory / Canon pages should display applied memory separately from OMI candidates and promotion records before apply-promotion exists.

Immediate next task after this spec: review and commit App-3a / OMI-001 outputs, then decide/spec the owner-created aligned sample project before Phase 2 backend safety and schema foundation.

## 2. OMI MVP Scope

OMI is:

- Project-local for MVP. OMI ideas and candidates belong under one project; a global idea inbox is future-only.
- Analysis-only. It can classify, summarize structurally, ask diagnostic questions, and identify missing information.
- Candidate-first. OMI output starts as candidate planning material, not durable truth.
- Owner-controlled. The owner decides whether to reject, revise, approve, archive, or promote a candidate.
- No-prose. OMI must never produce story prose or replacement prose.
- No silent promotion. OMI output cannot update durable project truth without explicit approval and confirmation.
- Project-setup capable. OMI may help create a project from owner-provided ideas by organizing metadata/setup candidates, but it must not generate premise prose, scene prose, chapter prose, dialogue, or canon automatically.
- Compatible with Story Check, the App-3 NCP subset, and the App-2 project file model.
- Independent from fine-tuning, RunPod, book-backed review, and dataset gates.

## 3. OMI Non-Goals

OMI does not do any of the following in the MVP:

- Write prose.
- Rewrite prose.
- Continue scenes.
- Draft chapters, dialogue, paragraphs, monologues, endings, or passages.
- Imitate style.
- Polish or improve text.
- Generate storyform data as truth.
- Generate project prose, premise prose, scene text, chapter text, dialogue, or sample passages for a new project.
- Mutate `bible.json`, `storyform.json`, `owner_memory.json`, planning notes, analysis artifacts, or scenes automatically.
- Provide full Dramatica verifier behavior.
- Provide a full NCP authoring UI.
- Provide a global idea inbox.
- Behave as an autonomous agent that decides project truth or edits project files without owner action.

## 4. Required OMI MVP Data Fields

| Field | Type expectation | Required | Purpose |
| --- | --- | --- | --- |
| `raw_idea` | string | Required on idea records | Owner-entered source idea. It may be fragmentary and is not story truth by itself. |
| `candidates` | array of candidate summaries or IDs | Required, can be empty | Structured candidate planning outputs derived from the idea. |
| `owner_decision` | enum/string object | Required | Owner review state such as `undecided`, `approve`, `reject`, `revise`, `archive`, or `promote`. |
| `destination` | enum/string | Required before approval or promotion | Proposed destination such as planning notes, bible candidate, storyform candidate, scene prompt context candidate, template starter candidate, or discard. |
| `provenance` | object | Required | Source trail showing whether content came from owner input, OMI, Story Check, NotebookLM, retrieved reference, manual owner edit, or import. |
| `status` | enum/string | Required | Lifecycle state: `draft`, `candidate`, `owner_review`, `approved`, `rejected`, `promoted`, or `archived`. |

Schema validation confirms shape only. It does not prove story truth.

## 5. Proposed OMI Idea Schema

Design target only; not implemented.

```json
{
  "idea_id": "idea_20260531_001",
  "project_id": "example_project",
  "raw_idea": "Owner-entered idea text.",
  "created_at": "2026-05-31T00:00:00Z",
  "updated_at": "2026-05-31T00:00:00Z",
  "status": "draft",
  "provenance": {
    "sources": ["owner_input"],
    "created_by": "owner",
    "notes": []
  },
  "owner_decision": {
    "decision": "undecided",
    "decided_at": null,
    "decided_by": null,
    "notes": ""
  },
  "candidates": [],
  "notes": [],
  "linked_candidate_ids": [],
  "safety_flags": {
    "contains_prose_request": false,
    "requires_refusal": false,
    "promotion_blocked": true
  }
}
```

Field notes:

- `idea_id`: stable ID for the raw idea within the project.
- `project_id`: filesystem-safe project ID, separate from display title.
- `raw_idea`: owner input; it can be analyzed, but it is not automatically promoted.
- `status`: current lifecycle state for the idea.
- `provenance`: required source and authorship trail.
- `owner_decision`: required even when undecided.
- `candidates` and `linked_candidate_ids`: references to derived OMI candidates.
- `safety_flags`: records no-prose and promotion-blocking concerns.

## 6. Proposed OMI Candidate Schema

Design target only; not implemented.

```json
{
  "candidate_id": "omi_candidate_20260531_001",
  "project_id": "example_project",
  "idea_id": "idea_20260531_001",
  "candidate_type": "storyform_context_candidate",
  "candidate_summary": "Brief structural summary, not prose.",
  "candidate_fields": {
    "throughline": "overall_story",
    "story_point": "Concern",
    "value": "candidate structural label",
    "diagnostic_questions": []
  },
  "destination": "storyform_context_candidate",
  "status": "candidate",
  "provenance": {
    "sources": ["owner_input", "omi_candidate"],
    "source_idea_id": "idea_20260531_001",
    "notes": []
  },
  "owner_decision": {
    "decision": "undecided",
    "decided_at": null,
    "decided_by": null,
    "notes": ""
  },
  "evidence_links": [],
  "promotion_requirements": {
    "requires_owner_approval": true,
    "requires_destination": true,
    "requires_provenance": true,
    "requires_status": true,
    "requires_final_confirmation": true
  },
  "created_at": "2026-05-31T00:00:00Z",
  "updated_at": "2026-05-31T00:00:00Z",
  "safety_flags": {
    "no_prose_generated": true,
    "candidate_only": true,
    "promotion_blocked": true
  }
}
```

Candidate types:

- `planning_note`: structural planning note candidate.
- `bible_candidate`: possible bible fact, relationship, place, object, or rule candidate.
- `storyform_context_candidate`: possible NCP/storyform slot candidate.
- `scene_prompt_context_candidate`: structural context for later owner-authored scene work; not scene prose.
- `template_starter_candidate`: structural scaffolding only, such as fields to fill or diagnostic slots. It is not prose and must not contain sample scene text.
- `diagnostic_question_set`: owner-facing structural questions.
- `character_candidate`: candidate character identity, traits, aliases, or role notes.
- `location_candidate`: candidate place or setting note.
- `object_candidate`: candidate object/item note.
- `organization_candidate`: candidate group, faction, institution, or team note.
- `timeline_event_candidate`: candidate event/action with time/order context.
- `relationship_candidate`: candidate relationship link or relationship-state note; not Dramatica Relationship Story proof.
- `plot_thread_candidate`: candidate plot thread, unresolved thread, or thread status note.
- `continuity_warning_candidate`: candidate continuity issue or contradiction warning.
- `annotation_candidate`: candidate scene/entity/global annotation with evidence.
- `open_question_candidate`: candidate open question for owner review.

The Writer Assistant Core candidate types above are future expansion targets. Runtime support remains limited to the OMI slices explicitly listed in the current implementation status until a later implementation task adds typed validation, extraction, and UI behavior.

Future durable memory/canon begins only after OMI candidate review, promotion record creation, and a later apply-promotion step. OMI promotion records are audit intent, not canon by themselves.

CORE-005 status clarification: future OMI work should distinguish `promotion_recorded` from `promoted`. `promotion_recorded` means an OMI promotion audit record exists; `promoted` should be reserved for successful future apply-promotion into `memory/*.json`.

## 7. OMI Status Lifecycle

Statuses:

- `draft`: raw idea is being captured or edited; no candidate claim is ready.
- `candidate`: OMI has produced candidate planning material for review.
- `owner_review`: candidate is ready for owner decision.
- `approved`: owner accepts the candidate as eligible for promotion to a specific destination.
- `rejected`: owner rejects the candidate; it must not be promoted.
- `promoted`: approved candidate has been explicitly promoted with required metadata and final confirmation.
- `archived`: inactive record retained for traceability.

Allowed transitions:

- `draft` -> `candidate`
- `draft` -> `archived`
- `candidate` -> `owner_review`
- `candidate` -> `rejected`
- `candidate` -> `archived`
- `owner_review` -> `approved`
- `owner_review` -> `rejected`
- `owner_review` -> `candidate` for revision
- `approved` -> `promoted` only after final confirmation
- `approved` -> `archived`
- `rejected` -> `archived`
- `promoted` -> `archived`

Blocked transitions:

- `draft` -> `approved`
- `draft` -> `promoted`
- `candidate` -> `promoted`
- `owner_review` -> `promoted`
- `rejected` -> `approved` without a new revision cycle
- `rejected` -> `promoted`
- `archived` -> `promoted`

Only approved candidates can be promoted, and promotion requires explicit owner confirmation.

## 8. OMI Destinations

MVP destinations:

- `planning_notes`: candidate planning note destination. It may become durable planning material only after owner approval.
- `project_bible_candidate`: candidate bible fact or context. It can eventually feed `bible.json` after owner approval and confirmation.
- `storyform_context_candidate`: candidate NCP/storyform context. It can eventually feed `storyform.json` after owner approval and confirmation.
- `scene_prompt_context_candidate`: candidate scene-planning context for owner-authored work. It must not write to scenes as prose.
- `template_starter_candidate`: structural scaffold candidate, such as fields, checklists, or diagnostic prompts. It is not prose.
- `discard`: rejected or unwanted candidate.

All destinations are candidate-only until approval. Only `planning_notes`, `project_bible_candidate`, and `storyform_context_candidate` can eventually feed durable project truth, and only after approval, provenance, status, source candidate ID, timestamp, destination, and final confirmation. OMI must not write prose into scene files.

## 9. Owner Decision Model

Owner decision values:

- `undecided`: no owner decision has been made.
- `approve`: owner accepts the candidate for a specific destination but has not necessarily promoted it yet.
- `reject`: owner rejects the candidate.
- `revise`: owner wants a revised candidate; status returns to candidate after revision.
- `archive`: owner removes the candidate from active review while retaining traceability.
- `promote`: owner confirms promotion of an approved candidate to the selected destination.

Required fields for promotion:

- `owner_decision`: must be `promote` at final confirmation.
- `destination`: must be explicit and allowed.
- `provenance`: must include source trail.
- `status`: must be `approved` before promotion and `promoted` after promotion.
- `final_confirmation`: explicit owner confirmation.
- `timestamp`: promotion timestamp.
- `source_candidate_id`: the candidate being promoted.

Promotion must be blocked if any required field is absent.

## 10. Provenance Model

Provenance sources:

- `owner_input`: owner supplied the raw idea or instruction. This can establish owner intent, but not structural truth by itself.
- `omi_candidate`: OMI organized or proposed candidate planning material. This is candidate-only.
- `story_check_candidate`: Story Check produced candidate analysis. It can support review, but cannot mutate durable truth automatically.
- `notebooklm_candidate`: NotebookLM or similar aggregation output. It is candidate-only and cannot establish story truth by itself.
- `retrieved_reference`: retrieved Dramatica/NCP definitions or reference material. It can support interpretation, but cannot establish story-specific truth by itself.
- `manual_owner_edit`: owner manually edited durable project material. This can become owner-approved truth when saved intentionally.
- `imported_project_data`: data imported from a project source. It requires owner review before being treated as durable truth.

Every OMI record should preserve provenance. Retrieved references and NotebookLM output cannot establish story truth without owner approval and evidence.

## 11. OMI and NCP/Storyform Interaction

Product pivot note: NCP/Dramatica is no longer the main near-term app backbone. OMI may still use NCP/storyform as reference context, but Writer Assistant Core should use a simpler story-knowledge model first. Dramatica-specific truth claims remain owner-gated and deferred to a later advanced analysis layer.

OMI follows the App-3 NCP compatibility rules:

- UI should use `Overall Story`; `Objective Story` is an accepted alias.
- Unknown NCP fields are hidden in normal MVP UI and preserved for advanced/raw context later.
- OMI may propose candidate storyform slots plus diagnostic questions.
- OMI candidate storyform slots remain candidate-only until owner approval.
- Missing storyform fields remain unresolved, not guessed.
- Generic relationships are not Relationship Story proof.
- Generic theme is not Issue/Variation proof.
- Antagonist is not automatically Influence Character.
- Positive OS/MC/IC/RS/CIPS/dynamics claims require owner-approved context and evidence.
- OMI must not claim full Dramatica verifier parity.

## 12. OMI and Project File Model Interaction

OMI follows the App-2 project file model:

- `project_id` remains filesystem-safe and separate from display title.
- OMI candidates are project-local for MVP.
- `owner_memory.json` is a design target, but full runtime behavior is deferred until core Story Check and OMI basics.
- Story Check artifacts are manually saved by owner choice only for MVP.
- OMI cannot mutate `bible.json`, `storyform.json`, `owner_memory.json`, planning notes, analysis artifacts, or scenes without explicit owner approval, destination, provenance, status, source candidate ID, timestamp, and final confirmation.
- Project-local future storage may use `omi/ideas/{idea_id}.json` and `omi/candidates/{candidate_id}.json`, but no storage files are created in this task.

## 13. OMI No-Prose Safety Requirements

Prohibited request types:

- write
- draft
- compose
- generate prose
- rewrite
- revise prose
- polish
- improve
- continue
- finish
- extend
- imitate style
- create dialogue
- create scene/chapter/paragraph/ending

Allowed OMI outputs:

- Structural candidate summaries.
- Diagnostic questions.
- Field checklists.
- Candidate labels with confidence/status.
- Missing-information lists.
- Owner-review packets.
- Provenance summaries.
- Destination recommendations.
- Project setup metadata candidates from owner-provided ideas.
- Navigation summaries labeled as analysis/navigation aids, not rewritten prose.

No prose generation is allowed in OMI. Allowed outputs must not include story prose. The standard refusal message is:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 14. OMI API/Storage Design Implications

Future backend design only; not implemented in this task:

- Create OMI idea.
- Create project setup idea before a full project structure exists.
- Create owner-controlled project setup candidates.
- List OMI ideas.
- Get OMI idea.
- Update OMI idea status.
- Create candidate from idea.
- List candidates.
- Update candidate decision.
- Promote candidate.
- Archive candidate.

Future implementation should introduce shared `backend/guardrails.py` before any model call. Guardrails should reject or redirect prose-generation, rewrite, continuation, imitation, polish, and improvement requests before model invocation and check model output before returning or saving candidate material.

Future OMI-guided project creation must keep owner-provided setup input, setup candidates, and approved project metadata separate. It must not silently create canon, memory, storyform truth, scene text, chapter text, or prose passages.

## 15. OMI Frontend Design Implications

Future frontend design only; not implemented in this task:

- Raw idea input.
- Candidate list.
- Candidate detail view.
- Status badge.
- Provenance badge.
- Destination selector.
- Owner decision controls.
- Promotion confirmation dialog.
- No-prose boundary copy.
- Advanced/raw context view for preserved unknown NCP fields.

The normal MVP UI should hide unknown NCP fields. Advanced/raw context can expose preserved unknown fields later with clear labels.

## 16. OMI Mock Fixture Implications

Fixture needs:

- `story_check`
- `throughline_classification`
- `writer_questions`
- `out_of_scope_refusal`
- OMI idea candidate.
- OMI rejected prose-generation request.
- OMI promotion-blocked-without-owner-approval.
- OMI candidate storyform slot marked candidate-only.

Initial mock mode should start with the four existing analysis task fixtures: `story_check`, `throughline_classification`, `writer_questions`, and `out_of_scope_refusal`. Later fixtures should cover malformed JSON, insufficient evidence, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion.

## 17. OMI Test Implications

Future tests should prove:

- OMI cannot generate story prose.
- OMI cannot silently promote candidates.
- Promotion requires owner approval.
- Candidate storyform slots remain candidate-only.
- Destination is required.
- Provenance is required.
- Status is required.
- Project-local storage is enforced.
- No raw model output mutates durable truth.
- Unknown NCP fields are preserved but not interpreted.
- Shared guardrails block prose requests before model calls.

## 18. Sample Project Implication

Recommended answer:

- Use the public-domain `public_domain_scene_002.txt` source for the main `projects/example` MVP Story Check fixture.
- Reserve `owner_sample_input.md` for future OMI raw idea and candidate-planning tests.
- Do not modify `projects/example` in this task.

The owner idea input is not accepted story truth, not Story Check scene prose, and not a source for `bible.json` or `storyform.json` unless a future owner-controlled OMI promotion explicitly approves a candidate destination.

## 19. App-3a / OMI-001 Acceptance Checklist

- [x] Required fields defined: `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`.
- [x] OMI idea schema proposed.
- [x] OMI candidate schema proposed.
- [x] Lifecycle statuses and transitions defined.
- [x] Destinations defined.
- [x] Owner decision model defined.
- [x] Provenance model defined.
- [x] No-prose boundary explicit.
- [x] No-silent-promotion boundary explicit.
- [x] NCP/storyform interactions documented.
- [x] Project file model interactions documented.
- [x] Future API/storage, frontend, fixture, and test implications listed.
- [x] Spec states this is design only and not implemented.

## 20. Recommended Next Tasks

1. Review and commit App-3a / OMI-001 outputs.
2. Sample project alignment decision/spec using the public-domain main fixture and OMI-only owner idea input split.
3. Phase 2 backend safety and schema foundation.
4. GUARD-001 runtime no-prose guard in shared `backend/guardrails.py`.
5. BE-002 Story Check normalizer using `jsonschema` plus custom normalizer.

## 21. Owner Questions

The recommended answers supplied for App-3a resolve the open product decisions needed for this spec. No additional owner decisions are required before reviewing and committing App-3a.

Future implementation may still need tactical choices, such as exact endpoint names, UI layout, and file naming conventions, but those are engineering follow-ups rather than owner-blocking product questions.
