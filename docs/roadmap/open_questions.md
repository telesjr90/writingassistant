# Open Questions

Owner decisions have answered the original roadmap questions. Remaining items below are implementation or verification follow-ups, not unresolved product decisions.

## Accepted Answers

| Original question | Accepted owner decision |
| --- | --- |
| Canonical product and repository name | Canonical repo: `telesjr90/writingassistant`. Product working name: Dramatica-Informed Writing Assistant. |
| License | MIT for app source code only. Training data, book sources, packet evidence, model artifacts, and datasets are excluded pending separate provenance/license review. |
| Git initialization/repair | Initialize or repair local Git later as the next setup task. Do not initialize Git as part of this documentation update. |
| Python dependency strategy | Use simple requirements files now. Keep backend requirements separate from `training/requirements-unsloth.txt`. Revisit `pyproject.toml`/`uv` later. |
| Node version | Target Node `>=22.12.0 <23`. Do not edit `frontend/package.json` in this documentation task. |
| Example fixture identity | Replace the Elena/Ember Crown mismatch later with one clean aligned fixture, preferably public-domain or owner-created. |
| Minimum OMI schema | Design-only schema fields: raw idea, candidates, owner decision, destination, provenance, and status. |
| Promotion action | Owner must explicitly approve, choose destination, attach evidence/provenance, and confirm promotion. |
| No-prose enforcement point | Enforce both before model call and after model output. |
| Mock mode behavior | Deterministic fixture JSON for `story_check`, `throughline_classification`, `writer_questions`, and `out_of_scope_refusal`. |
| Reference repo role | Prose-generation and autonomous-agent repos remain documentation-only. NCP may inform structure. |
| qwen25 cloud config | Revise/create cloud smoke config before RunPod smoke. |
| Books 4-5 need | Conditional only after cross-book coverage review. |
| Book folders in Git | Keep raw source text outside Git. Store only safe derived metadata/review artifacts in repo. |
| IC/RS threshold | Require owner-approved exact evidence per record. Target at least 15-20 strong IC and 15-20 strong RS examples, preferably 30+ each. |
| Book evidence approval format | Use a consolidated owner-review worksheet with candidate answer, excerpt IDs, evidence, weak/contradicting evidence, confidence, owner decision, and final training status. |

## Remaining Verification / Setup Tasks

1. Initialize or repair the local Git repository in a later setup task.
2. Add safe repo metadata files after Git is ready, including license/readme/gitignore decisions that respect the app-source-only MIT scope.
3. Add backend requirements in a simple requirements file without changing `training/requirements-unsloth.txt`.
4. Declare Node `>=22.12.0 <23` in package metadata in a later implementation task.
5. Replace the sample fixture with one aligned public-domain or owner-created project.
6. Draft the OMI design schema without implementing OMI runtime endpoints.
7. Create deterministic mock-mode fixtures for all four supported analysis tasks.
8. Revise or create a RunPod cloud smoke config before smoke training.
9. Run the Book 1-3 cross-book coverage review before deciding on Books 4-5.
10. Define the safe derived book metadata/review artifact set that may be committed while keeping raw source text outside Git.

## Project Model Owner Questions

1. Should `project_id` remain filesystem-oriented, with display title fully separate from `project_id`?
2. Should `owner_memory.json` be included in MVP, or deferred until after Story Check and OMI basics?
3. Should analysis artifacts be saved automatically after every Story Check, or only when the owner chooses to save them?
4. Should OMI candidates live inside each project, or can there be a global idea inbox later?
5. For the aligned sample project, should we use owner-created material or public-domain material?
