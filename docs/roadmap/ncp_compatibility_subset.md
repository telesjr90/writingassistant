# App MVP NCP Compatibility Subset

## 1. Executive Summary

This specification defines the Narrative Context Protocol (NCP) and storyform subset that the Dramatica-Informed Writing Assistant App MVP may safely support. Its purpose is to let Story Check and future OMI use structural context without claiming full Dramatica verifier parity or turning candidate analysis into durable project truth.

Product pivot status: NCP/Dramatica remains useful for future structural analysis, but it is no longer the main near-term app backbone. The next product track is Writer Assistant Core, which should use a simpler writer-assistant story knowledge model first: characters, aliases, locations, objects, organizations, events, timelines, relationships, plot threads, open questions, continuity issues, contradictions, annotations, and evidence spans. Dramatica-specific truth claims remain owner-gated and deferred to a later advanced analysis layer.

What exists now:

- `projects/{project_name}/storyform.json` is loaded by `backend/storyform.py`.
- The file is validated against the JSON schema copied in `docs/repo_knowledge.md`.
- `Storyform.to_prompt_context()` converts valid storyform data into prompt text for Story Check.
- Story Check receives storyform context, bible JSON, and scene text, then returns normalized candidate diagnostics.
- The current example project still mixes Elena/Whispering Woods bible and scene material with Quest for the Ember Crown storyform material.

The App MVP should support a bounded NCP subset:

- Story identity and one or more narrative records.
- Four-throughline separation for Overall Story / Objective Story, Main Character, Influence Character, and Relationship Story.
- Players, dynamics, storypoints, perspectives, and storybeats as owner-approved structural context.
- Explicit unresolved or insufficient-evidence handling for missing or unsupported fields.

Unsupported or owner-gated:

- Full Dramatica Story Engine or verifier parity.
- Automatic proof of RS, IC, CIPS, dynamics, signposts, or issue/variation claims from scene text.
- Any storyform update based on raw model output, OMI output, NotebookLM output, retrieved definitions, or generic thematic language without owner approval.

Immediate next task after this spec: App-3a / OMI-001 OMI MVP schema and lifecycle, then sample project alignment, then Phase 2 backend safety and schema foundation.

## 2. Current NCP/Storyform Inventory

Current loading path:

- `analysis_engine.run_story_check(project_name, scene_id)` calls `Storyform.from_file(project_name).to_prompt_context()`.
- `Storyform.from_file()` reads `projects/{project_name}/storyform.json`.
- `Storyform.validate_data()` validates the JSON object against the NCP schema extracted from `docs/repo_knowledge.md`.
- `GET /api/projects/{project_name}/storyform-context` returns the same prompt context string.

Current validation behavior:

- Validation is JSON Schema validation only.
- A syntactically valid storyform file does not prove the storyform is complete, correct, owner-approved, or evidence-grounded.
- The current `Storyform.from_file()` path does not reuse `project_manager` path validation.

Current prompt context behavior:

- `to_prompt_context()` includes story title, logline, narrative title/status, players, dynamics, grouped throughlines, storybeats, and overviews.
- Throughlines are grouped from `storypoints[].throughline` or inferred from storypoint `appreciation` prefix.
- The current output is plain text, not a structured API contract.

`docs/repo_knowledge.md` contributes:

- The copied NCP JSON schema from `narrative-context-protocol`.
- Field constraints for `schema_version`, `story`, `narratives`, `subtext`, `perspectives`, `players`, `dynamics`, `storypoints`, `storybeats`, and `storytelling`.
- It is reference documentation and schema source, not story-specific evidence.

Tests currently cover:

- `Storyform.from_questionnaire({})` returns a schema-valid sample storyform.
- `Storyform.from_file()` loads and validates a project storyform.
- Invalid storyform data raises a validation error.
- `to_prompt_context()` includes story title, throughlines, concern/issue content, and storybeats.
- Project manager tests cover bible/scene load/save and path safety for project and scene IDs.

Current example mismatch:

- `projects/example/storyform.json` describes Quest for the Ember Crown, Mara Vell, and Sir Calen Rook.
- `projects/example/bible.json` describes Elena, The Stranger, Whispering Woods, and Elena's Village.
- `projects/example/scenes/scene_001.md` is an Elena/Whispering Woods scene.
- This mismatch blocks reliable Story Check demo/evaluation and must be fixed separately.

## 3. NCP Compatibility Goals

- Support Story Check context safely without overclaiming structural certainty.
- Keep NCP/Dramatica available as reference context while the near-term app prioritizes Writer Assistant Core story knowledge workflows.
- Preserve OS/MC/IC/RS separation in storage, prompt context, diagnostics, and future UI.
- Preserve owner-approved truth boundaries: `storyform.json` is durable only when owner-approved.
- Preserve unresolved, absent, or unsupported fields instead of guessing.
- Avoid full Dramatica verifier parity claims.
- Keep the subset compatible with mock mode, qwen3/Ollama baseline mode, future `dramatica-analyst:8b`, and OMI candidate planning.
- Keep retrieved Dramatica/NCP definitions as reference-only material.
- Keep raw model output, OMI output, NotebookLM output, and external reference output as candidate material until owner-approved.
- Avoid forcing every story knowledge candidate into a Dramatica schema. Character, timeline, relationship, plot, continuity, and annotation candidates may use simpler project-memory schemas first.

## 4. MVP-Supported NCP/Storyform Fields

The App MVP may support these fields as the safe compatibility subset. Support here means the field may be loaded, validated syntactically, preserved, summarized, or used as owner-approved context after implementation. It does not mean the field is proven true by the app.

Story-level fields:

- `schema_version`
- `story.id`
- `story.title`
- `story.genre`
- `story.logline`
- `story.narratives`

Narrative fields:

- `narrative.id`
- `narrative.title`
- `narrative.status`

Perspective fields:

- `subtext.perspectives`
- `perspectives.id`
- `perspectives.author_structural_pov`
- `perspectives.summary`
- `perspectives.storytelling`

Player fields:

- `subtext.players`
- `players.id`
- `players.name`
- `players.role`
- `players.summary`
- `players.bio`
- `players.storytelling`
- `players.perspectives`

Dynamic fields:

- `subtext.dynamics`
- `dynamics.id`
- `dynamics.dynamic`
- `dynamics.vector`
- `dynamics.summary`
- `dynamics.storytelling`

Storypoint fields:

- `subtext.storypoints`
- `storypoints.id`
- `storypoints.appreciation`
- `storypoints.narrative_function`
- `storypoints.illustration`
- `storypoints.summary`
- `storypoints.storytelling`
- `storypoints.throughline`
- `storypoints.perspectives`

Optional but safe to preserve:

- `story.settings`
- `story.ideation`
- `players.visual`
- `players.audio`
- `players.motivations`
- `storybeats`
- `storytelling.overviews`
- `storytelling.moments`
- `custom_*` schema fields

Optional fields may be preserved or displayed as advanced context later, but they should not drive MVP Story Check claims unless a later implementation explicitly supports them.

## 5. Throughline Subset

Canonical UI recommendation:

- Use `Overall Story` in user-facing UI.
- Treat `Objective Story` as an accepted alias because the current NCP data and prompt use `Objective Story`.
- Internally normalize to stable keys: `overall_story`, `main_character`, `influence_character`, and `relationship_story`.

Allowed labels and aliases:

| Canonical key | Preferred UI label | Accepted aliases |
| --- | --- | --- |
| `overall_story` | Overall Story | Objective Story, OS |
| `main_character` | Main Character | MC |
| `influence_character` | Influence Character | IC, Impact Character |
| `relationship_story` | Relationship Story | RS, Subjective Story |

Separation rules:

- Overall Story / Objective Story is the external or shared problem context.
- Main Character is the personal viewpoint or personal problem.
- Influence Character is the pressure, challenge, or alternative viewpoint that bears on the MC.
- Relationship Story is the relationship itself as conflict or transformation, not merely the existence of a relationship.
- A scene may involve more than one throughline, but diagnostics must report them separately.
- A generic relationship, romance, banter, alliance, or conversation is not Relationship Story proof.
- An antagonist, rival, mentor, or love interest is not automatically the Influence Character.

## 6. Players Subset

Safe MVP player use:

- Use `players.name`, `players.role`, `players.summary`, `players.bio`, `players.storytelling`, and `players.perspectives` as context.
- Use player data to help compare scene evidence against owner-approved character context.
- Use perspective links as hints, not proof.

Boundaries:

- Player role is useful context, not automatic throughline evidence.
- `role: Antagonist` is not automatically Influence Character.
- `role: Main Character` is not sufficient proof that a scene is an MC throughline scene.
- Relationship presence is not Relationship Story proof.
- Player motivations can inform diagnostics only when the storyform is owner-approved and the scene provides evidence.

## 7. Dynamics Subset

The NCP schema currently allows these `dynamics.dynamic` values:

- `main_character_resolve`
- `influence_character_resolve`
- `main_character_growth`
- `main_character_approach`
- `problem_solving_style`
- `story_limit`
- `story_driver`
- `story_outcome`
- `story_judgment`

App MVP naming aliases:

| MVP label | NCP dynamic value |
| --- | --- |
| main_character_resolve | `main_character_resolve` |
| story_outcome | `story_outcome` |
| story_judgment | `story_judgment` |
| driver | `story_driver` |
| limit | `story_limit` |
| growth | `main_character_growth` |
| approach | `main_character_approach` |
| problem-solving style | `problem_solving_style` |

Current sample support:

- Existing sample data includes `main_character_resolve`, `story_outcome`, and `story_judgment`.
- Existing schema supports the broader set above.
- Existing tests only assert prompt-context output from the sample storyform; they do not validate every dynamic value.

Rules:

- Dynamics claims require owner-approved storyform context.
- Missing dynamics remain unresolved.
- Story Check may compare a scene's apparent direction to an owner-approved dynamic.
- Story Check must report insufficient evidence when a dynamic is absent or unsupported.
- Dynamics cannot be inferred into `storyform.json` from a scene, model output, OMI candidate, or NotebookLM candidate without owner approval.

## 8. Story Points Subset

Safe storypoint support:

- `throughline`
- `concern`
- `issue`
- `problem`
- `solution`
- `goal`
- `requirements`
- `consequences`
- signposts/beats if present

Mapping approach:

- Use `storypoints.throughline` when present.
- Otherwise infer grouping only from supported `appreciation` prefixes such as `Objective Story`, `Main Character`, `Influence Character`, and `Relationship Story`.
- Treat `appreciation` suffixes such as `Concern`, `Issue`, `Problem`, `Solution`, `Goal`, `Requirements`, and `Consequences` as labels only after schema validation.

Boundaries:

- A generic theme is not an Issue/Variation proof.
- A general conflict is not a Problem proof.
- A satisfying resolution is not automatically a Solution proof.
- CIPS, Problem, and Solution claims must be owner-approved and evidence-grounded.
- Missing story points should be reported as insufficient evidence.
- Story Check may ask diagnostic questions about missing storypoints, but must not fill them as truth.

## 9. Prompt-Context Subset

Future `to_prompt_context()` behavior should remain deterministic and should eventually include:

- Project/story identity: story ID, title, genre, and logline.
- Narrative ID, title, and status.
- Four throughline summaries, using canonical UI labels and stable internal keys.
- Relevant players and perspective links.
- Relevant dynamics with known vectors.
- Relevant storypoints grouped by throughline and appreciation.
- Unresolved or missing fields.
- Owner-approved status/provenance if available in future project metadata.

Do not implement changes in this task. The current prompt context is a useful starting point, but it is not yet the final App MVP context contract.

## 10. Story Check Usage Rules

Story Check may:

- Compare scene evidence to owner-approved storyform and bible context.
- Report throughline alignment separately for Overall Story, Main Character, Influence Character, and Relationship Story.
- Report `insufficient_evidence` when the scene or storyform lacks support.
- Ask writer-focused diagnostic questions.
- Preserve raw model output as candidate diagnostics only if saved later as an analysis artifact.

Story Check must not:

- Mutate `storyform.json`, `bible.json`, owner memory, OMI files, or scene text.
- Infer unsupported storyform fields as truth.
- Treat schema-valid storyform data as proof of story correctness.
- Treat retrieved definitions as story evidence.
- Claim verifier-level certainty.
- Write, rewrite, continue, imitate, polish, improve, or extend story prose.

## 11. OMI Usage Rules

OMI may use this NCP subset:

- As candidate planning structure.
- As prompts or diagnostic questions for the owner.
- As candidate `storyform_context` material after owner review.
- To help the owner decide where a raw idea might belong.

OMI must not:

- Treat NCP candidates as automatic story truth.
- Generate story prose.
- Write scenes, chapters, paragraphs, dialogue, endings, or continuations.
- Rewrite, improve, polish, imitate, or extend prose.
- Promote candidate material into `bible.json`, `storyform.json`, `owner_memory.json`, planning notes, or scenes without explicit owner approval, destination, provenance, status, and final confirmation.

No prose generation is allowed in OMI or Story Check paths.

## 12. Unsupported or Future Fields

Future-only or unsupported for App MVP:

- Full storyform questionnaire.
- Complete Dramatica Story Engine/verifier.
- Full CIPS verification.
- Automatic signpost validation.
- Full NCP authoring UI.
- Automatic proof of RS/IC/CIPS/dynamics from scene text.
- Automatic proof of Issue/Variation from generic theme language.
- Automatic proof of Relationship Story from any generic relationship.
- Any field not present in owner-approved storyform context.
- Any update to durable truth from raw model output, OMI output, NotebookLM output, or retrieved definitions.

Unsupported fields can be preserved as data where schema allows, but should not be interpreted by App MVP Story Check unless later implementation explicitly supports them.

## 13. Validation and Normalization Expectations

Future implementation expectations:

- Schema validation should be separate from semantic certainty.
- Syntactically valid storyform data does not prove story truth.
- Unsupported fields can be preserved but not interpreted.
- Invalid files should fail safely with bounded errors.
- Prompt context should be deterministic for the same project files.
- Normalized Story Check output should label insufficient evidence.
- No-prose guardrails should apply before model calls and after model output.
- Storyform context should expose enough unresolved-field information that models do not guess missing structure.

## 14. Current Sample Mismatch Implications

The current `projects/example` files are internally inconsistent:

- `storyform.json` is Quest for the Ember Crown, Mara Vell, Sir Calen Rook, and the Ember Crown quest.
- `bible.json` is Elena, The Stranger, Whispering Woods, and Elena's Village.
- `scene_001.md` is an Elena scene in Whispering Woods.

Why this matters:

- Story Check receives mismatched owner-approved context.
- Throughline alignment results cannot be trusted as a demo or evaluation signal.
- Apparent model errors may be caused by inconsistent fixture data.

Fixing this is a separate sample alignment task. App-3 documents the risk and subset rules only; it does not edit files under `projects/`.

## 15. API/Frontend Implications

Future design targets only:

- Backend should expose safe storyform context as a structured contract, not only prompt text.
- Backend should preserve unsupported fields while restricting MVP interpretation.
- Frontend should display owner-approved vs candidate labels later.
- Frontend should display unresolved/insufficient-evidence state separately from confirmed structure.
- OMI UI should surface candidate/provenance/status and destination before promotion.
- No API, frontend, or runtime behavior changes are made in this task.

## 16. Test Implications

Future tests should cover:

- Accepted NCP subset validates.
- Unsupported fields are preserved or ignored safely.
- Invalid storyform fails safely.
- OS/MC/IC/RS separation appears in prompt context or structured context.
- Antagonist is not auto-IC.
- Generic relationship is not auto-RS.
- Generic theme is not auto-Issue.
- Missing CIPS/dynamics becomes `insufficient_evidence`.
- OMI cannot promote NCP candidates without owner approval.
- Story Check cannot mutate storyform truth.
- No-prose guard applies to NCP-informed Story Check and OMI paths when implemented.

## 17. App-3 Acceptance Checklist

- [x] Defines the App MVP NCP/storyform compatibility subset.
- [x] Documents current storyform loading, validation, prompt-context behavior, and tests.
- [x] Defines MVP-supported story, narrative, perspective, player, dynamic, and storypoint fields.
- [x] Defines Overall Story / Objective Story, Main Character, Influence Character, and Relationship Story separation rules.
- [x] Documents dynamics and storypoint boundaries.
- [x] Defines Story Check usage rules and no-mutation boundaries.
- [x] Defines OMI usage rules and no-prose/no-silent-promotion boundaries.
- [x] Lists unsupported and future-only fields.
- [x] Documents the current sample mismatch without modifying project files.
- [x] Lists future validation, API/frontend, and test implications.
- [x] Lists owner questions separately from engineering tasks.

## 18. Recommended Next Tasks

1. App-3a / OMI-001 OMI MVP schema and lifecycle, using App-2 and App-3 boundaries.
2. Sample project alignment decision.
3. Phase 2 backend safety and schema foundation.
4. GUARD-001 runtime no-prose guard.
5. BE-002 Story Check normalizer.

## 19. Owner Questions

1. Which canonical throughline labels should the UI show: Overall Story or Objective Story?
2. Should unknown NCP fields be hidden from the MVP UI or shown as advanced raw context?
3. Should the sample project be owner-created or public-domain?
4. Should OMI propose candidate storyform slots, or only ask diagnostic questions until the owner fills them?
