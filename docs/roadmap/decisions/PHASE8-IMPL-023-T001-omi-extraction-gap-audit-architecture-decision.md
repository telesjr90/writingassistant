# PHASE8-IMPL-023-T001 OMI Extraction Gap Audit and Architecture Decision

## Result

PASS for audit and architecture decision only.

`PHASE8-IMPL-023-T001` is complete/PASS. The next child is `PHASE8-IMPL-023-T002 - Expected-red raw idea to candidate listing tests`.

No extraction implementation, backend route change, frontend code change, test edit, runtime extraction, model/Ollama call, candidate creation, Memory/Canon mutation, apply-promotion run, or generated story prose occurred for this decision.

## Current OMI Gap

The current OMI raw idea workflow stores owner-authored planning input, then requires manual candidate creation through a separate candidate form. It does not analyze the raw idea text and does not produce identified candidates from that raw idea.

Current backend behavior:

- `backend/main.py` exposes `GET /api/projects/{project_name}/omi`, `POST /api/projects/{project_name}/omi/ideas`, `GET /api/projects/{project_name}/omi/ideas/{idea_id}`, `POST /api/projects/{project_name}/omi/candidates`, `GET /api/projects/{project_name}/omi/candidates/{candidate_id}`, decision PATCH routes, and promotion-record routes.
- `backend/main.py` request models accept `OMIIdeaCreate.raw_idea` and manual `OMICandidateCreate.candidate_content`; there is no extraction request/response model.
- `backend/project_manager.py` persists OMI ideas under `omi/ideas/`, candidates under `omi/candidates/`, promotions under `omi/promotions/`, and indexes IDs in `omi/index.json`.
- `create_omi_idea` validates non-empty raw idea text and stores it as status `draft` with owner-input provenance and empty `linked_candidate_ids`.
- `create_omi_candidate` validates only a narrow manual candidate type/destination allowlist plus JSON-object `candidate_content` and array `evidence`; it does not derive fields from `raw_idea`.
- Current candidate types are `planning_note`, `project_bible_candidate`, `storyform_context_candidate`, `scene_prompt_context_candidate`, and `template_starter_candidate`, which do not directly cover the MVP candidate categories.

Current frontend behavior:

- `frontend/src/api.js` has OMI CRUD/decision/promotion helpers only; no extraction helper exists.
- `frontend/src/components/OMIPanel.jsx` lets the owner create a raw idea, then manually create a candidate with default empty JSON: `{"summary": "", "fields": []}` and empty evidence.
- `OMIPanel.jsx`, `OMICandidateDetail.jsx`, `OMICandidateFieldTable.jsx`, and `OMIPromotionReadinessChecklist.jsx` explicitly label this as a manual shell and state that automatic extraction is unavailable.
- Candidate display is currently a flat list plus selected detail; it is not grouped by extracted candidate type and does not show extraction result status.

Current tests:

- `tests/test_omi_routes.py` covers idea/candidate CRUD, status transitions, decision validation, promotion-record boundaries, no Ollama/model calls, and no apply-promotion shortcut.
- `tests/test_project_manager.py` covers OMI storage/index helpers, manual candidate creation, decision updates, promotion-record creation, and project-truth non-mutation.
- `tests/test_omi_boundaries.py` covers no prose destinations, owner-authored raw idea acceptance, no silent promotion, no model-path calls, no automatic sample-input reads, path safety, and frontend boundary copy.
- `tests/test_omi_manual_workflow_source.py` intentionally asserts manual-shell and extraction-unavailable labels.

The gap exists because the only candidate creation path is explicit manual candidate creation. There is no deterministic extractor, no extraction route, no extraction output contract, no evidence-span generation, no fail-closed empty extraction result, and no UI state that renders extracted candidates grouped by MVP type.

## Architecture Decision

The MVP extraction architecture will use a deterministic/rule-based baseline first. The first MVP extractor must not depend on models, Ollama, Story Check, BookNLP, spaCy runtime execution, NCP/Subtxt/dramatica-flow runtime, or any generated prose path unless a later task separately authorizes and tests that layer.

Accepted architecture:

- Add tests first in T002 for raw idea input producing visible extracted candidate records where evidence exists.
- Define the backend extraction contract/schema in T003 before implementation.
- Implement a deterministic/rule-based MVP extractor in T004 that reads only the submitted raw idea text and emits candidate drafts/records supported by direct source evidence.
- Persist extracted candidates in T005 only after schema validation, evidence/provenance validation, and fail-closed write guards.
- Add frontend extracted-candidate review UI in T006 after the backend contract and persistence behavior exist.
- Run safety validation in T007 to prove no Memory/Canon mutation, no apply-promotion, no model/Ollama call, no runtime extraction creep, and no generated prose.
- Complete browser/manual evidence in T008.

The extractor may identify candidate categories from explicit textual signals in the raw idea. It must preserve source excerpts or source locators for every emitted candidate. It must not infer unsupported facts, expand the idea creatively, outline scenes, rewrite text, continue prose, or settle canon.

Empty extraction must fail closed. If no evidence-backed candidates are found, the system returns a clear `empty`/`fail_closed` extraction result with an explanation and zero candidate writes. It must not create placeholder candidates, empty shells, or records that imply extraction succeeded.

## Candidate Output Contract

T002/T003 should define and test an extraction result contract with:

- `extraction_status`: `succeeded`, `empty`, or `fail_closed`.
- `explanation`: required for `empty` or `fail_closed`.
- `source_idea_id`: the OMI idea ID used as source.
- `source_locator`: a locator into the raw idea record or raw idea text.
- `candidates`: an array of candidate objects; empty only for explicit `empty`/`fail_closed` results.

Each candidate object must include:

- `candidate_type`: one of the MVP extraction categories, such as `character`, `location`, `timeline_event`, `relationship`, `organization`, `object`, `plot_thread`, `story_fact`, `open_question`, or supportable `storyform_context`.
- `label` or `name`: the short owner-review label for the candidate.
- `extracted_claim`: the specific analysis claim being presented for review.
- `evidence`: source excerpt and/or source locator tied to the raw idea.
- `provenance`: at minimum source type, source idea ID, extractor name/version, timestamp, model `null`, prompt ID `null`, and source hash or snapshot hash where available.
- `confidence` or `support_strength`: optional bounded support signal only; confidence is not truth.
- `status`: candidate/review status, defaulting to candidate/review-pending, never approved/promoted/canon.
- `owner_decision`: default pending owner decision state.
- `candidate_status`: explicit candidate lifecycle state if separate from `status`.

The contract must preserve existing safety fields and allow future mapping into review queue and apply-promotion flows without treating extraction output as approved Memory/Canon.

## UI/UX Requirements for T006

The T006 UI should provide:

- Raw idea intake with an explicit extraction action or state transition after save.
- Extraction status/progress/result states: idle/ready, running, succeeded, empty, fail-closed, and error.
- Grouped candidate list by candidate type with counts and clear review status.
- Empty/fail-closed state that explains no evidence-backed candidates were created and does not show placeholder shells.
- Candidate detail showing type, label/name, extracted claim, evidence/source excerpt or locator, provenance, confidence/support strength if present, status, and owner decision state.
- Owner review actions for candidate workflow metadata only, such as approve for review, reject, needs revision, defer/request more evidence where supported by the existing owner-action boundary.
- Persistent separation between extracted candidates, review queue state, approved Memory/Canon, and apply-promotion.
- No UI wording that implies queue presence, extraction success, confidence, or approval has mutated canon or memory.

## Safety Invariants

- Candidate persistence is not canon.
- Queue presence is not approval.
- Candidate approval does not mutate Memory/Canon.
- Apply-promotion remains separate, guarded, audited, owner-confirmed, and outside extraction.
- Extraction output, confidence, model output if ever separately authorized, and raw artifacts are not truth.
- No automatic Memory/Canon mutation occurs.
- No automatic apply-promotion occurs.
- No generated story prose, rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, revision, or prose-production path is authorized.
- Empty extraction fails closed and creates no misleading candidate shells.
- Storyform/context candidates are emitted only when supportable by direct raw-idea evidence.

## T002-T008 Touchpoints

- T002 tests: expected-red route/helper/UI-contract coverage for raw idea input returning evidence-backed extracted candidates and fail-closed empty extraction.
- T003 backend contract/schema: extraction request/response models, candidate type allowlist, candidate field validation, evidence/provenance/source locator validation, fail-closed result contract.
- T004 extractor: deterministic/rule-based baseline only, no model/Ollama dependency.
- T005 persistence: reuse or reconcile current OMI storage helpers with evidence-backed extracted candidate records; no empty-shell writes.
- T006 frontend: `frontend/src/api.js`, `OMIPanel.jsx`, `OMICandidateDetail.jsx`, `OMICandidateFieldTable.jsx`, and `OMIPromotionReadinessChecklist.jsx` need extraction-state and extracted-candidate review behavior after tests/contract authorize it.
- T007 safety: existing OMI route/project-manager/boundary tests need expansion to prove no canon/memory mutation, no apply-promotion, no model/Ollama call, no generated prose, and fail-closed empty extraction.
- T008 evidence: browser/manual proof after implementation.

## Deferred Work

Implementation is deferred to T002-T008. Model-assisted extraction, runtime BookNLP/spaCy extraction, Story Check integration, NCP/Subtxt/dramatica-flow runtime, apply-promotion changes, and Memory/Canon mutation remain outside this T001 decision.
