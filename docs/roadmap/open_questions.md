# Open Questions

Owner decisions have answered the original roadmap questions. Remaining items below are implementation or verification follow-ups, not unresolved product decisions.

## Accepted Answers

| Original question | Accepted owner decision |
| --- | --- |
| Canonical product and repository name | Canonical repo: `telesjr90/writingassistant`. Product working name: Dramatica-Informed Writing Assistant. |
| License | MIT for app source code only. Training data, book sources, packet evidence, model artifacts, and datasets are excluded pending separate provenance/license review. |
| Git initialization/repair | Local Git is initialized/repaired on `main`; `origin` is `https://github.com/telesjr90/writingassistant`; first safe local baseline commit is `25ef64d chore: initialize safe project baseline`. Push safe local `main` to GitHub later, but do not push during App-3a. |
| Python dependency strategy | Use simple requirements files now. `backend/requirements.txt` exists and remains separate from `training/requirements-unsloth.txt`. Revisit `pyproject.toml`/`uv` later. |
| Node version | Target Node `>=22.12.0 <23`. Use both `.nvmrc` and `frontend/package.json` engines later; do not edit package metadata in this documentation task. |
| Example fixture identity | Replace the Elena/Ember Crown mismatch later with a small owner-created aligned sample for MVP. Public-domain material can be used later for broader evaluation. |
| Minimum OMI schema | OMI is in the App MVP as bounded analysis-only candidate planning. Design target fields are `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`. OMI may propose candidate storyform slots plus diagnostic questions, but candidate-only until owner approval. |
| Promotion action | Owner must explicitly approve, choose destination, attach evidence/provenance, and confirm promotion. |
| No-prose enforcement point | Enforce both before model call and after model output. Shared guard location is `backend/guardrails.py`; GUARD-001 has implemented the reusable module, GUARD-002 has implemented request-field policy for future freeform routes, and GUARD-003 has implemented post-normalization Story Check output sanitization. |
| Mock mode behavior | Story Check deterministic fixture JSON is implemented for `ANALYSIS_MODE=mock`; `throughline_classification`, `writer_questions`, `out_of_scope_refusal`, malformed JSON, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion fixtures remain future work. |
| UI throughline label | Use Overall Story in UI; accept Objective Story as an alias. |
| Unknown NCP fields | Hide unknown NCP fields in normal MVP UI; preserve them for advanced/raw context later. |
| Project identity | Keep filesystem-safe `project_id` separate from display title. |
| Owner memory | Include `owner_memory.json` as a design target; defer full runtime behavior until core Story Check and OMI basics. |
| Story Check artifact saving | Manual owner save only for MVP. |
| OMI location | Project-local for MVP; global idea inbox later. |
| Schema validation | Use `jsonschema` plus custom normalizer; schema validity is not story truth. BE-002 implements the reusable Story Check normalizer with schema diagnostics and safe fallback behavior. |
| Story Check prompt schema | SC-001 aligns `backend/prompts/story_check.txt` to the rich Story Check schema, JSON-only output, no-prose boundaries, and insufficient-evidence reporting. |
| Story Check compatibility | SC-002 verifies minimal, rich, fallback, diagnostic, missing-rich-field, unknown-field, and error-shaped Story Check reports through the current route and sidebar compatibility path. |
| GitHub Issues/Projects | Not yet; wait until Phase 1 and early Phase 2 task structure are approved. |
| Reference repo role | Prose-generation and autonomous-agent repos remain documentation-only. NCP may inform structure. |
| qwen25 cloud config | Revise/create cloud smoke config before RunPod smoke. |
| Books 4-5 need | Conditional only after cross-book coverage review. |
| Book folders in Git | Keep raw source text outside Git. Store only safe derived metadata/review artifacts in repo. |
| IC/RS threshold | Require owner-approved exact evidence per record. Target at least 15-20 strong IC and 15-20 strong RS examples, preferably 30+ each. |
| Book evidence approval format | Use a consolidated owner-review worksheet with candidate answer, excerpt IDs, evidence, weak/contradicting evidence, confidence, owner decision, and final training status. |
| Book 1-3 owner-answer inventory | Owner supplied final row decisions for Books 1-3. These have been implemented as local prep reports and a mapping queue only; positive, insufficient-evidence, needs-revision, and context-only rows remain separated. |
| Fine-tuning prep pause | Fine-tuning/book-backed prep is paused after the Book 1-3 review JSONL mapping dry-run. No JSONL records were created, no records were promoted, the manifest was not updated, and no training ran. |

## Remaining Verification / Setup Tasks

1. Push the safe local `main` branch to GitHub in a separate task.
2. Declare Node `>=22.12.0 <23` in package metadata in a later implementation task.
3. Optionally replace the public-domain sample fixture with an owner-created aligned project in a later task.
4. Extend OMI runtime beyond the OMI-003/OMI-004/OMI-005/OMI-006 raw idea/candidate/review/promotion-record/status-provenance slices only through separately approved tasks; apply-promotion behavior remains unimplemented.
5. Reuse shared `backend/guardrails.py` request and output guard helpers when future freeform/model routes are implemented without treating scene text as user request intent.
6. Extend runtime schema validation patterns beyond Story Check when new analysis routes are implemented.
7. Add broader route tests where useful without live Ollama.
8. Create remaining deterministic mock-mode fixtures beyond Story Check: `throughline_classification`, `writer_questions`, `out_of_scope_refusal`, malformed JSON, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion.
9. Continue frontend hardening after FE-001, App-4, and App-5; rich Story Check UI sections, scene editor dirty-state handling, and owner-controlled bible/storyform JSON editing are implemented.
10. Record owner acceptance/documentation of the current committed public-domain `projects/example` fixture state. Phase 6 Step 1 refresh found no dirty tracked fixture files; ignored local `projects/example/omi/` artifacts remain local-only.
11. Revise or create a RunPod cloud smoke config before smoke training in a future training task; this is not current while fine-tuning prep is paused.
12. Fine-tuning is paused pending P0 evidence extraction/verification before any Book 1-3 JSONL drafting.
13. Define the safe derived book metadata/review artifact set that may be committed while keeping raw source text outside Git.
14. Re-run the repo safety portion of the MVP completion test matrix after the dirty fixture files are resolved before declaring MVP exit; this is the next active project task.
15. Evaluate optional analysis extractors only after MVP exit; any segram, fabula, silverfish, AI-Reader-V2, or narrative-blueprint work remains candidate-only and routed through OMI.
16. Books 4-5 remain conditional and should not start while the fine-tuning/book-backed track is paused.
17. Decide whether to accept the Step 2 sandbox limitation for localhost backend/frontend server smokes or rerun those smokes in a local environment where socket binding is permitted.

## Writer Assistant Core Follow-Up Questions

These are implementation follow-ups for the new product direction, not blockers to recording the pivot.

1. What durable project memory/canon file structure should be used: separate `memory/*.json` files, a single `project_memory.json`, or another layout?
2. Which candidate types are required for the first Writer Assistant Core release: character, location, object, organization, timeline event, relationship, plot thread, continuity warning, annotation, open question, or a smaller subset?
3. What is the minimum evidence-span format: exact text span, scene-relative character offsets, line/paragraph locators, source hashes, or a hybrid?
4. Should annotations be stored per scene, per entity, globally, or in a combined index?
5. Should the first extractor be deterministic/rule-based, LLM-assisted, `segram`-assisted, or hybrid?
6. What UI should approve, reject, revise, merge, or annotate candidate story knowledge?
7. What qualifies a relationship or timeline event for owner-approved promotion to canon?
8. When should Dramatica analysis return as an advanced layer after Writer Assistant Core?

## Writer Assistant Core Follow-Up Questions

These are implementation follow-ups for the new product direction, not blockers for the completed MVP foundation:

1. What durable project memory/canon file structure should be used: `memory/*.json`, one `project_memory.json`, or another layout?
2. Which candidate types are required for the first Writer Assistant Core release: characters, aliases, locations, objects, organizations, events, relationships, plot threads, open questions, continuity warnings, annotations, or a smaller subset?
3. What is the minimum evidence-span format: file path plus character offsets, line ranges, excerpt IDs, source hashes, or a hybrid?
4. Should annotations be stored per scene, per entity, globally, or in an OMI-linked annotation store?
5. Should the first extractor be deterministic/rule-based, LLM-assisted, `segram`-assisted, or hybrid?
6. What UI should approve, reject, revise, and annotate candidate story knowledge?
7. What qualifies a relationship, timeline event, or plot-thread item for promotion to canon?
8. When should Dramatica analysis return as an advanced layer after Writer Assistant Core is stable?
9. Which extractor spike should be first once schemas and OMI candidate flow are ready?

## Book 1-3 Owner-Answer Status

Resolved by owner inventory and implemented locally:

- Book 1 parent rows and split/local candidates have final owner decisions recorded.
- Book 2 parent rows and split candidates have final owner decisions recorded, with B2-010a Optionlock replacing the contradicted Timelock parent.
- Book 3 parent/review rows and split candidates have final owner decisions recorded, with Book 3 RS validity retained as insufficient evidence.

Still unresolved or blocked for direct conversion:

- Parent rows marked `needs_revision` remain blocked from direct conversion.
- Context-only master packet rows remain do-not-convert.
- Insufficient-evidence rows remain negative calibration only.
- P0 evidence extraction/verification remains required before any JSONL draft.
- Later review JSONL conversion, promotion, manifest update, and training remain pending and paused.
- App MVP Phase 6 / MVP exit matrix preflight is the next active project task.

## Owner Questions

No additional owner decisions are required for the completed App MVP slices. The current owner decision needed for local MVP readiness is whether to accept/document the current committed public-domain `projects/example` fixture state and leave ignored local `projects/example/omi/` artifacts as local-only state. The current product-direction decision has shifted: after Phase 6 owner acceptance, the next roadmap priority is Writer Assistant Core, while Dramatica, Books 4-5, and fine-tuning remain deferred.

Phase 6 Step 2 adds one MVP exit decision: true backend/frontend dev-server smokes are blocked by this sandbox's socket/listen restrictions, while in-process mock route smoke passed. The owner can either accept this as an environment limitation for documentation purposes or request a rerun in a socket-enabled local environment.

Resolved sample/source roles:

1. `project_id`: `example`, kept for MVP compatibility with the current hard-coded frontend project ID.
2. Display title: `The Princess and the Pea`, from `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt`.
3. First scene text: copied verbatim from `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt` into the local ignored fixture.
4. `/mnt/e/WritingAssistantApplication/docs/owner_sample_input.md`: reserved for future OMI raw idea/candidate-planning tests only, not Story Check fixture prose or project truth.
5. MC, IC, RS, CIPS, and dynamics evidence: not asserted for the public-domain fixture, so these remain unresolved for insufficient-evidence behavior.
6. Commit status: tracked project fixture files are clean in `HEAD` as of the Phase 6 Step 1 refresh; no revert is needed unless the owner rejects the committed fixture state.
