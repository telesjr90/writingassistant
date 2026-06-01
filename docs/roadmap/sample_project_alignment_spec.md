# Owner-Created Sample Project Alignment Spec

## Source Role Correction

Correction applied after implementation planning: the main MVP `projects/example` Story Check fixture should use `/mnt/e/WritingAssistantApplication/docs/public_domain_scene_002.txt` as its scene source. `/mnt/e/WritingAssistantApplication/docs/owner_sample_input.md` is future OMI raw idea / candidate-planning input only. It must not be used as `scene_001.md`, accepted project truth, bible truth, or storyform truth.

## 1. Executive Summary

The current sample project must be replaced or aligned because its durable project context is internally inconsistent: the storyform, bible, and scene files describe different stories. That prevents the App MVP from using the sample as a reliable Story Check demo, mock fixture source, or evaluation baseline.

The corrected MVP sample is for app validation, not for publication or literary evaluation. It should be small, rights-safe, structurally clear, and designed to exercise Story Check, NCP/storyform context, mock mode, and future guardrail tests. The app-wide sample may use public-domain source text; owner idea material is reserved for OMI candidate lifecycle examples.

This spec defines the required sample contents, file model, provenance policy, validation plan, fixture implications, replacement strategy, and owner inputs needed before implementation.

This task does not create sample files, edit `projects/example`, write story prose, generate scenes, modify runtime code, or update tests.

Immediate next task after this spec: review and commit the sample project alignment spec, then collect owner sample inputs or begin Phase 2 backend safety and schema foundation if sample content is not ready.

## 2. Current Sample Mismatch

The current `projects/example` files remain mismatched:

- `storyform.json` uses Quest for the Ember Crown, Mara, Sir Calen, and the Ember Crown.
- `bible.json` uses Elena, The Stranger, Whispering Woods, and Elena's Village.
- `scene_001.md` uses Elena/Whispering Woods material.

Why this blocks reliable App MVP work:

- Story Check receives contradictory owner-approved context.
- Route tests cannot treat the sample as a stable expected fixture.
- Mock fixtures can accidentally encode mismatch behavior instead of app behavior.
- qwen3 baseline demos may look wrong because the project data is wrong.
- Evaluation cannot separate model/parser errors from fixture inconsistency.
- OMI candidate examples would not have a trustworthy destination context.

## 3. Sample Alignment Goals

The aligned MVP sample should provide:

- One `project_id`.
- One display title.
- One consistent story bible.
- One consistent storyform/NCP context.
- One or more owner-created scenes.
- No copyright or provenance ambiguity.
- Support for Story Check in mock mode.
- Support for qwen3 baseline demo.
- Support for OMI candidate lifecycle examples.
- Support for no-prose guardrail tests.
- Support for insufficient-evidence behavior.

The sample should be intentionally small so test failures remain easy to diagnose.

## 4. Owner-Created Sample Policy

The actual story content must come from the owner.

Codex may create file structure specs, field templates, validation rules, placeholder labels, and implementation plans. Codex must not write story prose, generate a scene, draft dialogue, create paragraphs, write an opening, write an ending, or improve existing prose for the sample.

Owner-created or public-domain fixture content should be:

- Small enough for fast local tests.
- Rights-safe.
- Explicitly approved for repository use.
- Designed to make structural evidence easy to inspect.
- Clear about which fields are intentionally present and which are intentionally absent.

Corrected source-role policy:

- `public_domain_scene_002.txt` is the main MVP sample scene source for `projects/example`.
- `owner_sample_input.md` is OMI raw idea / candidate-planning input only.
- OMI input must remain candidate-only and must not be silently promoted into `bible.json`, `storyform.json`, scene files, or durable project truth.

## 5. Recommended Sample Identity Model

Recommended identity fields:

- `project_id`: filesystem-safe ID, separate from display title. Example shape only: `mvp_owner_sample`.
- Display title: human-facing title provided by the owner.
- Sample purpose: MVP fixture, not a public literary example.
- Provenance: `owner_created`.
- Status: `owner_approved_sample` after owner approval.
- License/provenance note: safe for local repo only after the owner confirms the content is owner-created or otherwise rights-safe.

The app should never infer provenance from file presence. Provenance must be explicit.

## 6. Required Sample Files

Target files, design-only:

```text
projects/{project_id}/
  project.json
  bible.json
  storyform.json
  scenes/
    {scene_id}.md
  owner_memory.json        # optional future
  analysis/                # optional future
  omi/                     # optional future
```

MVP-required when implementation happens:

- `projects/{project_id}/project.json`
- `projects/{project_id}/bible.json`
- `projects/{project_id}/storyform.json`
- `projects/{project_id}/scenes/{scene_id}.md`

Optional/future:

- `projects/{project_id}/owner_memory.json`
- `projects/{project_id}/analysis/`
- `projects/{project_id}/omi/`

Do not create these files in this task.

## 7. Owner-Provided Content Checklist

The owner must provide these inputs before implementation:

- Project title.
- Short logline.
- Story bible facts.
- One short scene text.
- Four throughline summaries or approved placeholders.
- Players and roles.
- At least one Main Character signal.
- At least one Overall Story signal.
- Optional Influence Character signal.
- Optional Relationship Story signal.
- Known missing evidence if intentionally testing insufficient evidence.
- Approval that the sample may be committed.

The scene text must be owner-created. Codex must not fill this checklist with story prose.

## 8. Storyform/NCP Requirements

The sample storyform should use the App-3 NCP subset:

- Overall Story UI label, with Objective Story accepted as an alias.
- Main Character.
- Influence Character.
- Relationship Story.
- Players.
- Dynamics.
- Storypoints.
- Unresolved fields.
- Owner-approved status/provenance when available.

Missing IC, RS, CIPS, dynamics, signposts, or other storyform fields may remain `insufficient_evidence` if the sample is designed that way. Unsupported or unknown fields should remain unresolved, not guessed.

The sample must not imply full Dramatica verifier parity. A generic relationship is not Relationship Story proof, and generic theme language is not Issue/Variation proof.

## 9. Bible Requirements

`bible.json` should contain only owner-approved context for the same sample project:

- Characters.
- Settings.
- Known facts.
- Established relationships.
- Tone/genre notes if needed.
- Provenance/status metadata if supported later.

Boundary rules:

- No raw model output.
- No OMI candidate output unless owner-promoted.
- No NotebookLM candidate output unless owner-promoted.
- No retrieved Dramatica/NCP definitions as story truth.
- No facts from packet evidence, raw books, or copyrighted source text.

## 10. Scene Requirements

The scene file should be:

- Owner-created.
- Short enough for reliable local tests.
- UTF-8 Markdown/plain text.
- Stable enough that expected evidence spans do not churn.
- Free of copyrighted/source text.
- Able to support at least one clear Story Check assertion.
- Able to intentionally omit IC or RS evidence if insufficient-evidence testing is desired.
- Free of hidden prompt instructions.
- Stored as `scenes/{scene_id}.md` using a safe single-component scene ID.

No prose is created in this spec. The owner supplies the scene text later.

## 11. Story Check Fixture Implications

The aligned sample should support future fixtures for:

- Valid rich Story Check output.
- Insufficient-evidence output.
- Malformed-output fallback behavior.
- Overall Story vs Main Character distinction.
- IC/Antagonist confusion later.
- Generic relationship/Relationship Story confusion later.
- Refusal/no-prose behavior.

The fixture outputs should be structured diagnostics only. They should not include replacement prose or suggested dialogue.

## 12. OMI Fixture Implications

The aligned sample should support future OMI examples for:

- Raw idea input.
- Candidate planning material.
- Candidate storyform slot.
- Owner decision.
- Destination.
- Provenance.
- Status.
- Promotion blocked until explicit approval.
- No prose generation.

OMI fixtures must stay candidate-only unless owner-approved and promoted through the App-3a lifecycle.

## 13. No-Prose Guardrail Implications

Sample-related no-prose tests should verify:

- Requests to write a scene are refused.
- Requests to continue the sample scene are refused.
- Requests to rewrite sample prose are refused.
- Requests to improve sample prose are refused.
- Requests to polish sample prose are refused.
- Requests for diagnostic questions are allowed.
- Requests for structure analysis are allowed.

The standard refusal message is:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 14. Replacement Strategy for `projects/example`

Future implementation options:

- Option A: replace `projects/example` contents with the owner-created aligned sample.
- Option B: create `projects/mvp_owner_sample` and later update frontend project selection.
- Option C: keep `projects/example` as legacy and add a new aligned sample.

Recommendation for MVP: Option A. The current frontend hard-codes `PROJECT_ID = 'example'`, so replacing `projects/example` with the aligned public-domain sample is the smallest implementation path and avoids adding project selection before the app needs it.

Do not perform replacement in this task.

## 15. Validation Plan for Future Implementation

When sample implementation happens, validate:

- JSON files parse.
- `bible.json` is a JSON object.
- `storyform.json` validates against the NCP schema.
- Scene load/save tests pass.
- Storyform context loads.
- Story Check mock fixture works.
- No-prose requests refuse.
- No candidate output mutates durable truth.
- App opens the aligned sample.
- Current mismatch is removed or quarantined.

Suggested future checks:

```bash
python -m json.tool projects/example/project.json
python -m json.tool projects/example/bible.json
python -m json.tool projects/example/storyform.json
.venv-unsloth-clean/bin/python -m pytest tests -q
```

These commands are for the future implementation task, not this specification task.

## 16. Git/Provenance Safety

Sample files may be committed only after:

- The owner confirms the content is owner-created or rights-safe.
- No raw books are included.
- No packet evidence is included.
- No copyrighted passages are included.
- No model artifacts are included.
- No generated story prose from Codex is included.
- A provenance note is included.
- The owner approves committing the sample files.

Project files remain durable project truth only after owner approval.

## 17. Open Owner Inputs Needed Before Implementation

Owner inputs needed:

- `project_id`.
- Display title.
- Logline.
- Bible facts.
- Storyform/NCP approved context or intentionally incomplete placeholders.
- Scene text.
- Whether IC and RS should be present or intentionally missing.
- Approval to commit sample files.

These are owner inputs, not Codex writing tasks.

## 18. App Phase 1 Completion Impact

After this spec, Phase 1 planning/spec work will include:

- Architecture audit.
- Project file model.
- NCP subset.
- OMI schema/lifecycle.
- Sample alignment spec.

Remaining Phase 1 exit depends on owner sample inputs and/or the decision to proceed to Phase 2 backend foundation while sample content is pending.

## 19. Recommended Next Tasks

1. Review and commit sample project alignment spec.
2. Owner provides sample project content inputs.
3. Start Phase 2 backend safety and schema foundation if sample content is not ready.
4. First Phase 2 task: GUARD-001 runtime no-prose guard in shared `backend/guardrails.py`.
5. Then BE-002 Story Check normalizer using `jsonschema` plus custom normalizer.

## 20. Owner Questions

1. What should the owner-created sample `project_id` be?
2. What should the display title be?
3. Will the owner provide the first scene text?
4. Should the first aligned sample include IC and RS evidence, or intentionally leave one or both absent for insufficient-evidence testing?
5. Is it approved to commit the owner-created sample files once provided?
