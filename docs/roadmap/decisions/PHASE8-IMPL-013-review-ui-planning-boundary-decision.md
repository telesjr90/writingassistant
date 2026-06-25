# PHASE8-IMPL-013 Review UI Planning Boundary Decision

## 1. Decision Summary

- `PHASE8-IMPL-013-T004` accepts the review UI planning boundary as docs/decision only.
- Future review UI planning must happen before any frontend review UI, frontend API helper, backend route, or FastAPI endpoint implementation.
- The future review UI is an owner-facing review surface for candidate-linked queue entries. It displays workflow state, evidence, provenance, source locators, uncertainty, and owner-action controls as planning terms only.
- The review UI is not approval, canon truth, apply-promotion, memory/canon mutation, generated prose/rewrite/continuation, runtime extraction, or automatic candidate approval.
- T004 implements no UI, no routes, no frontend API helpers, no tests, no owner action execution, no apply-promotion, no memory/canon mutation, no runtime extraction, and no raw artifact persistence.

## 2. Evidence Reviewed

T004 reviewed local repository evidence only:

- `docs/roadmap/tasks/PHASE8-IMPL-013.md`
- `docs/roadmap/inventory/PHASE8-IMPL-013.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-013.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`
- `docs/roadmap/tasks/PHASE8-IMPL-012.md`
- `docs/roadmap/inventory/PHASE8-IMPL-012.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`
- `backend/story_knowledge/review_queue_storage.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `frontend/src/api.js`
- `frontend/src/App.jsx`
- `frontend/src/components/Editor.jsx`
- `frontend/src/components/ProjectNav.jsx`
- roadmap/status files and validation records.

Confirmed from local files:

- `PHASE8-IMPL-013` is active; T001, T002, and T003 are complete; T004 was ready/active; T005 is planned/next.
- `PHASE8-IMPL-012` is complete through T007.
- `backend/story_knowledge/review_queue_storage.py`, `tests/test_writer_assistant_core_review_queue_storage_contract.py`, `backend/story_knowledge/candidate_review_gate.py`, and `tests/test_writer_assistant_core_candidate_review_gate_contract.py` are tracked.
- Owner action behavior exists only as owner action record shape validation in `review_queue_storage.py`; no owner action command API or execution path exists.
- `frontend/src/api.js` has no review queue or owner action API helper.
- No frontend review UI, backend review routes, apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction exists in this pipeline.
- `backend/app.py`, `frontend/src/Editor.jsx`, and `frontend/src/ProjectNav.jsx` are not present at those exact paths in this checkout; the active route file is recorded elsewhere as `backend/main.py`, and the frontend imports `Editor` and `ProjectNav` from `frontend/src/components/`.
- `.external_sources/` remains ignored and not staged.

## 3. Review UI Purpose

The future review UI exists to let an owner inspect candidate-linked queue entries from the read-only review queue API and decide review workflow next steps through a separate command surface if later authorized.

It must display:

- workflow state;
- linked candidate summary;
- evidence and provenance;
- source document identity and source locators;
- confidence as uncertainty/support strength;
- insufficient-evidence and rejected-output states;
- owner-action controls as future planning terms only.

It must not present queue entries as approved truth, canon, promoted records, memory writes, apply-promotion, generated prose, runtime extraction, or automatic candidate approval.

## 4. UI Implementation Timing Decision

- Decision: review UI planning must happen before frontend implementation.
- T004 implements no UI.
- Future UI implementation remains deferred until tests and owner scope authorize it.
- T002 and T003 already planned the read-only API and command API contracts, but routes remain unimplemented.
- T005 may convert T002/T003/T004 into tests-first contract coverage only if authorized.

## 5. Review Queue List View Contract

Future list view should display, as planning terms only:

- `queue_entry_id` or a safe display ID;
- candidate type;
- target category;
- review status;
- lifecycle state;
- confidence as uncertainty/support strength;
- uncertainty flags;
- normalization status;
- `human_review_required`;
- evidence count or evidence summary;
- provenance/source indicators;
- insufficient-evidence or rejected-output warnings;
- `created_at` and `updated_at`.

List view must not:

- rank entries as truth;
- imply approval by position, order, grouping, or confidence;
- hide insufficient evidence;
- hide rejected output warnings;
- show approval, canon, promotion, or promoted badges;
- show apply-promotion controls;
- show generated prose controls;
- show memory/canon write controls.

## 6. Review Queue Detail View Contract

Future detail view should display:

- full queue entry workflow state;
- linked candidate record summary;
- `candidate_type` and `target_category`;
- source document identity;
- source locator;
- evidence summary and refs;
- provenance summary and refs;
- raw output refs as support-only metadata;
- confidence as uncertainty/support strength;
- normalization status;
- insufficient-evidence or rejected-output reasons;
- reviewer notes, if present;
- allowed owner action controls as planning terms only;
- visible no-promotion/no-canon warning;
- no generated prose/rewrite/continuation controls.

## 7. Evidence and Provenance Display Contract

Future UI must show:

- evidence excerpts or summaries if safe;
- evidence refs;
- provenance refs;
- source document identity;
- source locator;
- raw refs where applicable;
- normalization status;
- `human_review_required`;
- confidence as uncertainty/support strength;
- reason fields for insufficient or rejected support.

The UI must not strip evidence/provenance to make the queue look cleaner. Missing evidence/provenance is a review safety state, not a display cleanup opportunity.

## 8. Source Locator Display Contract

Future UI may show:

- source document label;
- segment label;
- character offset summary;
- line/token locator summary when available;
- safe `source_path_hint` only as debug/display metadata if already accepted by source contracts.

Future UI must not:

- expose arbitrary filesystem paths;
- accept arbitrary path input;
- make `source_path_hint` trusted;
- mutate source body;
- jump to or edit source without a separately authorized source viewer/editor boundary.

## 9. Uncertainty and Confidence Display Contract

- Confidence must be labeled as uncertainty/support strength, not truth.
- High confidence is not approval.
- Low confidence is not rejection unless a later owner action says so.
- Sorting/filtering by confidence is workflow convenience only.
- Confidence cannot hide evidence, provenance, insufficient-evidence warnings, rejected-output warnings, or source-locator problems.

## 10. Insufficient Evidence and Rejected Output Display Contract

- `needs_more_evidence` and `blocked_invalid_support` must be visually distinct.
- Rejected output must remain visible as support state, not silently deleted.
- UI must not allow blocked or rejected support to appear approved, canon, promoted, or ready for memory/canon write.
- UI must preserve reason fields and evidence/provenance/source links.

## 11. Owner Action Control Boundary

Allowed future UI controls as planning terms only:

- `request_more_evidence`
- `mark_needs_info`
- `defer_review`
- `reject_candidate`
- `mark_duplicate`
- `mark_superseded`
- `archive_without_promotion`
- `add_reviewer_note`
- `clear_reviewer_note`
- `edit_queue_metadata`
- `prepare_for_promotion_review`
- `mark_ready_for_separate_promotion_flow`

These controls are not implemented in T004. If implemented later, they must call a separate command API and must remain review-workflow-only.

Rejected UI controls:

- `approve_candidate`
- `promote_candidate`
- `apply_promotion`
- `write_to_memory`
- `write_to_canon`
- `generate_prose`
- `rewrite_source`
- `continue_scene`
- `run_extractor`
- `run_booknlp`
- `run_spacy`
- `persist_raw_artifact`

## 12. Read-Only vs Command Interaction Boundary

- Read-only screens load queue data.
- Command controls, if later implemented, must call a separate command API.
- The read-only API cannot mutate `review_status` or `lifecycle_state`.
- The command API cannot imply apply-promotion.
- UI must visually separate viewing from actions.
- Any future command control must show no-promotion/no-canon warnings.

## 13. Apply-Promotion Boundary

- No apply-promotion UI is authorized in `PHASE8-IMPL-013`.
- `ready_for_separate_promotion_review` is only a pointer to a future workflow.
- Future apply-promotion requires a separate owner-approved parent/task, explicit audit, separate tests, and memory/canon safety.
- Apply-promotion must not be hidden inside review list actions, detail actions, command responses, keyboard shortcuts, or bulk controls.

## 14. Memory/Canon Boundary

Future review UI must never write or imply writes to:

- `memory/*.json`
- `memory/index.json`
- `bible.json`
- `storyform.json`
- `project.json`
- `scenes/`
- `chapters/`
- `notes/`
- `materials/`
- owner-authored source files

The UI may display candidate-linked workflow data only. It must not label queue entries as canon, approved memory, promoted truth, or durable project truth.

## 15. Generated Prose/Rewriting/Continuation Boundary

- No generated prose controls.
- No rewrite controls.
- No continuation controls.
- No improvement, polish, expansion, or imitation controls.
- Reviewer notes are owner-authored workflow metadata only.
- Reviewer notes must not become a prompt surface for generated story prose.

## 16. Runtime Extraction and Raw Artifact Boundary

- No runtime extraction controls.
- No BookNLP/spaCy run controls.
- No raw artifact persistence controls.
- Raw refs are display/support-only metadata.
- The UI cannot install, import, run, or trigger extractor dependencies.

## 17. Accessibility and Usability Planning Requirements

Future UI tests should encode:

- keyboard navigability;
- visible focus states;
- clear headings and labels;
- readable status labels;
- non-color-only status differentiation;
- warnings that are perceivable and persistent;
- status messages for empty/error/quarantine states;
- accessible action labels;
- confirmation language for destructive workflow actions like reject/archive;
- no hidden evidence/provenance behind inaccessible controls;
- mobile and desktop readability;
- no horizontal-only workflows for core review tasks.

## 18. Empty, Error, and Quarantine State Requirements

Future UI should display:

- empty queue state;
- no matching filters state;
- invalid queue entry state;
- missing candidate record state;
- malformed entry state;
- insufficient evidence state;
- rejected output state;
- unavailable evidence/provenance state;
- safe error message with no write/repair side effect;
- no silent deletion or auto-repair.

## 19. Mobile/Desktop Layout Planning Boundary

Plan only; no layout implementation is authorized in T004.

Future UI should support:

- desktop list/detail review workflow;
- mobile stacked list/detail workflow;
- evidence/provenance visibility on small screens;
- controls separated from evidence display;
- no accidental command execution through cramped controls;
- safe review status visibility without relying only on color.

## 20. T005 Handoff

T005 should create review API/UI contract tests only if authorized.

Expected future test scope:

- read-only API contract expected-red if routes are absent;
- owner action command API contract expected-red if routes are absent;
- UI planning/component contract expected-red only if owner authorizes frontend tests;
- no route/UI implementation;
- no apply-promotion;
- no memory/canon mutation;
- no generated prose;
- no runtime extraction;
- no package changes.

## 21. T006/T007 Handoff

- T006 should validate or harden API/UI safety boundaries only if prior tests authorize it.
- T006 must not implement routes, UI, owner action execution, apply-promotion, memory/canon mutation, runtime extraction, raw persistence, or generated prose unless a prior tests-first scope explicitly authorizes a narrow safety hardening.
- T007 closes the parent and records final status.

## 22. Explicit Rejections

T004 rejects:

- frontend review UI implementation;
- frontend API helper implementation;
- backend route implementation;
- FastAPI endpoint implementation;
- owner action command API implementation;
- owner action execution;
- apply-promotion UI;
- memory/canon mutation UI;
- generated prose/rewrite/continuation UI;
- runtime extraction UI;
- raw artifact persistence UI;
- package/dependency changes;
- model calls;
- training/JSONL/dataset work;
- automatic candidate approval;
- approved/canon/promoted UI states.

## 23. Accepted Decision

- ACCEPT review UI planning before implementation.
- ACCEPT evidence/provenance/uncertainty as mandatory display requirements.
- ACCEPT list/detail view planning as owner-facing workflow support only.
- ACCEPT owner action controls only as future planning terms.
- ACCEPT visible no-promotion/no-canon warnings.
- ACCEPT accessibility/usability requirements for future tests.
- ACCEPT T005 as tests-first only if authorized.
- REJECT UI/routes/API implementation, apply-promotion, memory/canon mutation, runtime extraction, raw persistence, and generated prose.
