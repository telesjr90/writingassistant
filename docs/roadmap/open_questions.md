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
| No-prose enforcement point | Enforce both before model call and after model output. Future runtime implementation should use shared `backend/guardrails.py` before model calls. |
| Mock mode behavior | Start with deterministic fixture JSON for `story_check`, `throughline_classification`, `writer_questions`, and `out_of_scope_refusal`; later add malformed JSON, insufficient evidence, OS/MC confusion, IC/Antagonist confusion, and generic relationship/RS confusion fixtures. |
| UI throughline label | Use Overall Story in UI; accept Objective Story as an alias. |
| Unknown NCP fields | Hide unknown NCP fields in normal MVP UI; preserve them for advanced/raw context later. |
| Project identity | Keep filesystem-safe `project_id` separate from display title. |
| Owner memory | Include `owner_memory.json` as a design target; defer full runtime behavior until core Story Check and OMI basics. |
| Story Check artifact saving | Manual owner save only for MVP. |
| OMI location | Project-local for MVP; global idea inbox later. |
| Schema validation | Use `jsonschema` plus custom normalizer; schema validity is not story truth. |
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
5. Implement runtime no-prose guardrails in shared `backend/guardrails.py` later.
6. Implement runtime schema validation with `jsonschema` plus custom normalizers later.
7. Create deterministic mock-mode fixtures for all four supported analysis tasks.
8. Revise or create a RunPod cloud smoke config before smoke training.
9. Run the Book 1-3 cross-book coverage review before deciding on Books 4-5.
10. Define the safe derived book metadata/review artifact set that may be committed while keeping raw source text outside Git.

## Owner Questions

Sample implementation requires owner-provided content and approval:

1. What should the owner-created sample `project_id` be?
2. What should the display title be?
3. Will the owner provide the first scene text?
4. Should the first aligned sample include IC and RS evidence, or intentionally leave one or both absent for insufficient-evidence testing?
5. Is it approved to commit the owner-created sample files once provided?

Until those inputs are available, the app can proceed to Phase 2 backend safety and schema foundation.
