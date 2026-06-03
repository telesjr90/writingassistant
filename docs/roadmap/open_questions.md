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

## Remaining Verification / Setup Tasks

1. Push the safe local `main` branch to GitHub in a separate task.
2. Declare Node `>=22.12.0 <23` in package metadata in a later implementation task.
3. Replace the sample fixture with one aligned owner-created project for MVP.
4. Define exact OMI API/storage implementation without assuming current endpoints exist.
5. Reuse shared `backend/guardrails.py` request and output guard helpers when future freeform/model routes are implemented without treating scene text as user request intent.
6. Extend runtime schema validation patterns beyond Story Check when new analysis routes are implemented.
7. Add broader route tests where useful without live Ollama.
8. Create remaining deterministic mock-mode fixtures beyond Story Check: `throughline_classification`, `writer_questions`, `out_of_scope_refusal`, malformed JSON, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion.
9. Continue frontend hardening after FE-001, App-4, and App-5; rich Story Check UI sections, scene editor dirty-state handling, and owner-controlled bible/storyform JSON editing are implemented.
10. Begin bounded OMI implementation planning with storage/runtime design that preserves owner approval and no-prose boundaries.
11. Revise or create a RunPod cloud smoke config before smoke training.
12. Run the Book 1-3 cross-book coverage review before deciding on Books 4-5.
13. Define the safe derived book metadata/review artifact set that may be committed while keeping raw source text outside Git.

## Owner Questions

No additional owner decisions are required before Phase 2 backend safety and schema foundation.

Resolved sample/source roles:

1. `project_id`: `example`, kept for MVP compatibility with the current hard-coded frontend project ID.
2. Display title: `The Princess and the Pea`, from `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt`.
3. First scene text: copied verbatim from `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt` into the local ignored fixture.
4. `/mnt/e/WritingAssistantApplication/docs/owner_sample_input.md`: reserved for future OMI raw idea/candidate-planning tests only, not Story Check fixture prose or project truth.
5. MC, IC, RS, CIPS, and dynamics evidence: not asserted for the public-domain fixture, so these remain unresolved for insufficient-evidence behavior.
6. Commit status: project fixture changes remain unstaged/uncommitted until explicitly requested.
