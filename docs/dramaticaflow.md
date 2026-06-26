Yes — **dramatica-flow can be constrained to analysis-only**, but **not safely by using the repo as-is**. The official repo is built as an AI novel-creation system with outline generation, chapter generation, revision, export, and a five-layer writing pipeline; for your app, you should treat it as a **tool-evaluation source / extractable analysis library**, not as a drop-in runtime. The safe path is an **allowlisted adapter** that imports or reimplements only the diagnostic/extraction parts and blocks all prose/outline generation paths. The repo itself exposes both analysis/tracking features and explicit generation/rewrite endpoints. ([GitHub][1])

## Bottom line

**Recommended use:** yes, but only as an **analysis-only extraction/evaluation module** that produces OMI-style candidate records.

**Do not use:** the default `WritingPipeline`, `WriterAgent`, `ReviserAgent`, `df write`, outline generation, chapter-content generation, rewrite endpoints, or “continue writing” features.

**Best MVP role:** feed owner-authored text into a constrained adapter that extracts or diagnoses:

* causal links
* continuity risks
* information-boundary violations
* relationship/emotional changes
* foreshadowing/hook candidates
* timeline/thread events
* audit issues
* candidate summaries

Those outputs should become **candidate records with evidence/provenance**, not canon.

---

## Why it cannot be used as-is

The repo’s default flow is explicitly a **single-chapter writing pipeline**: Architect plans a blueprint, Writer generates chapter prose, validator checks it, Auditor audits it, Reviser fixes critical issues, final text is saved, causal links are extracted, a summary is generated, and world state is updated. That is useful architecture, but it violates your non-negotiable boundary because it includes prose generation, revision, final-draft saving, and automatic state updates. ([GitHub][2])

The public API/CLI also exposes generation and rewrite actions: `ai-generate/outline`, `ai-continue/outline`, `ai-generate/chapter-outlines`, `continue-writing`, `ai-generate/chapter-content`, `ai-rewrite-segment`, `action/write`, and `action/revise`. Those must be blocked in your app. ([GitHub][1])

---

## Safe / unsafe feature map

| Repo feature/module                                                                         |                         Use in your app? | Why                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------- | ---------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `PostWriteValidator` / hard-rule validation                                                 |                                 **Safe** | It checks existing text for issues such as AI-marker density, forbidden phrases, and meta-narrative patterns; it does not need to create prose. ([GitHub][3])                                                                                                |
| `AuditorAgent.audit_chapter`                                                                |                    **Safe with wrapper** | It audits an existing chapter against blueprint/truth context and returns structured JSON issues: severity, dimension, description, location, suggestion. Use only the report; never call revision afterward. ([GitHub][4])                                  |
| `NarrativeEngine.extract_causal_links`                                                      |                    **Safe with wrapper** | It analyzes supplied chapter content and extracts cause → event → consequence records, affected decisions, and triggered events as JSON. This maps well to candidate extraction. ([GitHub][5])                                                               |
| Story tracking views: causal chain, emotional arcs, hooks, relationships, threads, timeline | **Safe as read-only display/candidates** | The repo exposes story-tracking endpoints for causal chain, emotional arcs, hooks, relationships, narrative threads, and global timeline. Keep them read-only and candidate-first. ([GitHub][1])                                                             |
| Information-boundary model                                                                  |                    **Safe and valuable** | The repo models what each character knows, when they learned it, and source type such as witnessed, hearsay, deduced, or document. That is directly useful for POV leakage and continuity warnings. ([GitHub][1])                                            |
| Timeline swimlane visualization                                                             |                 **Safe as UI reference** | The timeline page shows multi-thread lanes, chapter filters, event highlighting, character activity, zoom, and act-structure background. This can guide your future UI without generating text. ([GitHub][1])                                                |
| `SummaryAgent`                                                                              |                   **Conditionally safe** | It summarizes existing chapter content into structured summary, key events, characters, state changes, hook updates, and emotional note. Safe only if stored as candidate summary, never canon or prose. ([GitHub][4])                                       |
| `ArchitectAgent.plan_chapter`                                                               |           **Mostly block / narrow only** | It creates a chapter blueprint with conflict, hooks to plant, emotional journey, ending hook, pace notes, and checklist. That is creative planning, not just analysis. Only reuse if rewritten to evaluate an existing owner-authored outline. ([GitHub][4]) |
| `NarrativeEngine.generate_outline`                                                          |                                **Block** | It generates a complete story outline from seed event, protagonist, world context, target chapters, and genre. That creates story structure/content. ([GitHub][5])                                                                                           |
| `NarrativeEngine.generate_chapter_outlines`                                                 |                                **Block** | It expands sequences into chapter outlines, beats, emotional arcs, and mandatory tasks. That is generated outline content. ([GitHub][5])                                                                                                                     |
| `WriterAgent.write_chapter`                                                                 |                           **Hard block** | It is explicitly a novel-writing agent that outputs chapter body text plus a settlement table. ([GitHub][4])                                                                                                                                                 |
| `ReviserAgent.revise`                                                                       |                           **Hard block** | It supports spot-fix, rewrite-section, and polish modes; all modify prose. ([GitHub][4])                                                                                                                                                                     |
| Full `WritingPipeline`                                                                      |                           **Hard block** | It orchestrates planning, prose generation, validation, auditing, revision, saving final draft, extraction, summary, and world-state update. ([GitHub][2])                                                                                                   |

---

## Candidate-record fit: yes

The safe outputs can fit your OMI model very well **if you enforce candidate-first storage**.

A good candidate record shape would be:

```json
{
  "candidate_id": "cand_causal_000123",
  "candidate_type": "causal_link",
  "source_tool": "dramatica-flow.extract_causal_links",
  "source_module": "core.narrative.NarrativeEngine",
  "status": "candidate",
  "confidence": "model_reported_or_app_assigned",
  "claim": {
    "cause": "...",
    "event": "...",
    "consequence": "...",
    "affected_decisions": []
  },
  "evidence": [
    {
      "project_id": "example",
      "document_id": "chapter_003",
      "span_start": 1204,
      "span_end": 1518,
      "quote": "short owner-authored excerpt only"
    }
  ],
  "provenance": {
    "created_by": "analysis_tool",
    "created_at": "ISO timestamp",
    "input_hash": "hash of analyzed owner-authored text",
    "tool_version": "dramatica-flow commit/version if recorded"
  },
  "promotion": {
    "is_canon": false,
    "requires_owner_approval": true
  }
}
```

That approach matches your existing safety boundary: the tool may **suggest extracted facts**, but it never directly writes canon, never promotes automatically, and never creates story prose.

---

## Practical implementation recommendation

Use dramatica-flow as a **reference/fork candidate**, not as a direct dependency at first.

For the MVP, create a small adapter like:

```text
writer_assistant/integrations/dramatica_flow_analysis/
  adapter.py
  schemas.py
  safety.py
  provenance.py
  tests/
```

The adapter should expose only:

```python
analyze_causal_links(owner_text) -> list[CandidateRecord]
audit_continuity(owner_text, approved_context) -> list[CandidateRecord]
detect_information_boundary_issues(owner_text, character_knowledge_context) -> list[CandidateRecord]
extract_timeline_events(owner_text) -> list[CandidateRecord]
extract_relationship_changes(owner_text) -> list[CandidateRecord]
extract_hook_candidates(owner_text) -> list[CandidateRecord]
summarize_as_candidate(owner_text) -> CandidateRecord
```

And explicitly forbid:

```python
generate_outline(...)
continue_outline(...)
generate_chapter_outline(...)
write_chapter(...)
rewrite_segment(...)
revise(...)
export_full_book(...)
apply_to_world_state(...)
promote_to_canon(...)
```

## Final answer

**Yes, dramatica-flow can help you reach the MVP faster, but only if you constrain it to analysis-only through an allowlisted adapter.** The safest modules/features are the validator, auditor, causal-link extractor, timeline/story-tracking concepts, information-boundary model, and possibly summary extraction. The features that must be blocked are outline generation, outline continuation, chapter outline generation, chapter prose generation, rewrite/revise/polish, full writing pipeline execution, final draft saving, export, and automatic world-state/canon updates.

For your app, dramatica-flow should produce **OMI candidate records with evidence and provenance**, never canon.

[1]: https://github.com/ydsgangge-ux/dramatica-flow "GitHub - ydsgangge-ux/dramatica-flow: 深度集成 Dramatica 理论与 5 层 Agent 写作管线的下一代 AI 自动写小说引擎，支持因果链管理、多线叙事与伏笔追踪。A causal-driven AI novel creation system based on Dramatica theory, featuring a 5-layer Agent pipeline for deep narrative logic. · GitHub"
[2]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/core/pipeline.py "dramatica-flow/core/pipeline.py at main · ydsgangge-ux/dramatica-flow · GitHub"
[3]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/core/validators/__init__.py "dramatica-flow/core/validators/__init__.py at main · ydsgangge-ux/dramatica-flow · GitHub"
[4]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/core/agents/__init__.py "dramatica-flow/core/agents/__init__.py at main · ydsgangge-ux/dramatica-flow · GitHub"
[5]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/core/narrative/__init__.py "dramatica-flow/core/narrative/__init__.py at main · ydsgangge-ux/dramatica-flow · GitHub"
-------------------------------------------------------------------------

I searched the official `ydsgangge-ux/dramatica-flow` repo and treated your boundary as: **no authored prose, no AI continuation, no rewriting, no AI-created outline/plan/world seed, and no direct mutation of canon/truth/world-state files.** The repo is explicitly built around AI-assisted long-form novel creation, with an Architect → Writer → Validator → Auditor → Reviser pipeline, causal extraction, summaries, and world-state settlement. ([GitHub][1])

## Decision key

**Block** = do not expose or call in your app.
**Wrap** = only allow behind a dry-run adapter that returns candidate records with evidence/provenance and performs **zero writes**.
**Ignore** = do not integrate; leave as upstream UI/app functionality outside your analysis-only MVP.

## Features/APIs/modules that cross the analysis-only boundary

| Feature / API / module                                                       | What it appears to do                                                                                                                                                                                                 | Decision for your app                                                                                                                 |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `core/pipeline.py` / `WritingPipeline.run`                                   | Full writing pipeline: plans a chapter, writes draft prose, validates/audits, revises, saves final text, extracts causal links, generates summary, and applies settlement into world state/truth files. ([GitHub][2]) | **Block.** This is the central prose-generation and truth-mutation pipeline. Do not call it.                                          |
| `ArchitectAgent.plan_chapter`                                                | Generates a chapter blueprint: core conflict, hooks to advance/plant, emotional journey, ending hook, risks, and chapter planning material. ([GitHub][3])                                                             | **Block by default.** It authors future story structure. Only a heavily rewritten “risk scan only” adapter could be considered later. |
| `WriterAgent.write_chapter`                                                  | The prompt identifies the agent as a novel writer and instructs it to directly produce chapter body text plus a settlement table. ([GitHub][3])                                                                       | **Block.** Direct prose generation.                                                                                                   |
| `ReviserAgent.revise`                                                        | Supports `spot-fix`, `rewrite-section`, and `polish`; outputs revised full prose and a changelog. ([GitHub][3])                                                                                                       | **Block.** This rewrites/polishes owner prose.                                                                                        |
| `SummaryAgent.generate_summary` / `format_for_truth_file`                    | Generates a structured chapter summary, key events, state changes, hook updates, and formats it for `chapter_summaries.md`. ([GitHub][3])                                                                             | **Wrap.** Summaries can be useful only as candidate extraction outputs. Do not write them to truth files. Require evidence spans.     |
| `AuditorAgent.audit_chapter`                                                 | Audits OOC, information boundaries, causality, emotional arc, outline deviation, continuity, hook management, AI-ish language, conflict quality, etc. ([GitHub][3])                                                   | **Wrap / allow as analysis-only.** Safe only if it cannot trigger revise/write actions and returns diagnostics, not fixes.            |
| Causal-chain extraction / state settlement layer                             | README says causal extraction writes to world state, summary generation injects truth files, and settlement writes positions/emotions/relationships/hooks to `world_state.json`. ([GitHub][1])                        | **Wrap.** Candidate-only extraction is useful; direct mutation is not.                                                                |
| `core/state/*` world state and truth-file writers                            | Repo structure includes `core/state` for world state and truth files; pipeline applies settlements and writes relationship/hook/info/timeline changes. ([GitHub][4])                                                  | **Wrap at storage boundary.** For your app, replace writes with candidate records requiring owner approval.                           |
| `POST /api/action/write`                                                     | Listed in the API reference as an AI writing action. ([GitHub][4])                                                                                                                                                    | **Block.**                                                                                                                            |
| `POST /api/action/revise`                                                    | Listed as a revision action. ([GitHub][4])                                                                                                                                                                            | **Block.**                                                                                                                            |
| `POST /api/action/audit`                                                     | Listed as audit action. ([GitHub][4])                                                                                                                                                                                 | **Wrap.** Audit is acceptable only as read-only diagnostics, with no auto-revision.                                                   |
| `POST /api/books/{id}/ai-generate/chapter-content`                           | Listed as AI generation for chapter content. ([GitHub][4])                                                                                                                                                            | **Block.** Direct prose generation.                                                                                                   |
| `POST /api/books/{id}/ai-rewrite-segment`                                    | Listed as AI rewrite endpoint. ([GitHub][4])                                                                                                                                                                          | **Block.** Direct rewrite.                                                                                                            |
| `POST /api/books/{id}/ai-generate/outline`                                   | Generates a story outline. README says the UI supports AI outline generation and sequence planning. ([GitHub][4])                                                                                                     | **Block.** Authored story planning content.                                                                                           |
| `POST /api/books/{id}/ai-continue/outline`                                   | Server code includes an outline-continuation endpoint and prompts the model to continue chapter outlines based on unexpanded story sequences. ([GitHub][5])                                                           | **Block.** Story continuation.                                                                                                        |
| `POST /api/books/{id}/ai-generate/chapter-outlines`                          | Listed as AI chapter-outline generation. ([GitHub][4])                                                                                                                                                                | **Block.** Authored outline content.                                                                                                  |
| `POST /api/books/{id}/ai-generate/detailed-outline`                          | Listed as AI detailed-outline generation. ([GitHub][4])                                                                                                                                                               | **Block.** Authored outline content.                                                                                                  |
| `POST /api/books/{id}/continue-writing`                                      | Server code has a `continue-writing` route that asks the LLM to continue chapter outlines and then appends new chapter outlines to `chapter_outlines.json`. ([GitHub][5])                                             | **Block.** Continuation plus file mutation.                                                                                           |
| `POST /api/books/{id}/ai-generate/setup`                                     | Generates a complete story setup/worldview JSON: characters, world, locations, factions, rules, and events. ([GitHub][5])                                                                                             | **Block.** It creates story truth/world seed material.                                                                                |
| `POST /api/books/{id}/ai-generate/arc-events`                                | Server prompt generates arc event lists, then appends those generated events into setup/event files. ([GitHub][5])                                                                                                    | **Block.** AI-created plot events plus truth mutation.                                                                                |
| `POST /api/books/{id}/extract-from-novel`                                    | Extracts characters/world/events from uploaded novel text; code prompt allows inference/guessing when information is insufficient. ([GitHub][5])                                                                      | **Wrap.** Useful for candidate extraction only. Must prohibit guessing and require evidence/provenance.                               |
| `POST /api/books/{id}/extract-story-state`                                   | Extracts positions, emotions, relationships, hooks, info, key events, causal links, then writes to world state and truth files. ([GitHub][5])                                                                         | **Wrap.** Analysis part is valuable; all writes must be disabled and converted to candidate records.                                  |
| `POST /api/books/{id}/extract-story-state/batch`                             | Batch version of story-state extraction; server code iterates through draft/final chapters and updates state/thread outputs. ([GitHub][5])                                                                            | **Wrap.** Same as above, but higher risk because it can mass-mutate story state.                                                      |
| `POST /api/books/{id}/setup/load`                                            | API reference lists setup loading into world state. ([GitHub][4])                                                                                                                                                     | **Wrap.** Loading owner-authored data may be okay, but it must not silently become canon.                                             |
| `PUT /api/books/{id}/setup/{file_type}`                                      | Updates setup files. ([GitHub][4])                                                                                                                                                                                    | **Wrap.** Manual truth mutation; require owner approval/audit trail.                                                                  |
| `PUT /api/books/{id}/outline`                                                | Saves outline data to `outline.json`. Server code includes `save_outline` behavior. ([GitHub][5])                                                                                                                     | **Wrap.** Allowed only as owner-authored document editing, not AI-generated canon.                                                    |
| `PUT /api/books/{id}/chapter-outlines`                                       | Saves chapter outlines to `chapter_outlines.json`. ([GitHub][5])                                                                                                                                                      | **Wrap.** Same rule: owner-authored only, no AI generation.                                                                           |
| Outline/chapter-outline import endpoints                                     | Server code normalizes and saves imported outlines/chapter outlines, and updates config/current chapter targets. ([GitHub][5])                                                                                        | **Wrap.** Import can be safe only as user-supplied material; no automatic canon promotion.                                            |
| Chapter import / draft/final save behavior                                   | Server code imports chapters, saves draft/final files, and updates chapter/config state. ([GitHub][5])                                                                                                                | **Wrap.** Ingestion of owner text is okay, but it must not trigger extraction, promotion, or truth mutation automatically.            |
| Chapter promotion / finalization behavior                                    | Server code includes `promote_chapter`, and pipeline saves final chapters. ([GitHub][5])                                                                                                                              | **Wrap or ignore.** For your app, owner-authored prose storage is okay; AI-generated “final” promotion is not.                        |
| Hook resolve/reopen endpoints                                                | Server code exposes hook resolution/reopen behavior. ([GitHub][5])                                                                                                                                                    | **Wrap.** This mutates story truth. In your app, represent as owner-approved canon change or candidate status change.                 |
| Thread create/update/delete/auto-generate behavior                           | Server code exposes thread management and batch extraction can create new threads. ([GitHub][5])                                                                                                                      | **Wrap.** Manual owner edits may be allowed; auto-generated threads must be candidate-only.                                           |
| Novel-plan arc/event add/update/delete/switch behavior                       | Server code writes novel plan, arcs, and events. ([GitHub][5])                                                                                                                                                        | **Wrap.** Treat as owner-authored planning docs only; AI-generated arc events are blocked.                                            |
| Web UI “AI Writing / Manual Revision / Audit” chapter creation flow          | README describes chapter creation with AI writing, manual revision, audit, and story tracking. ([GitHub][1])                                                                                                          | **Ignore.** Do not reuse the UI flow; it is built around authorial generation.                                                        |
| Web UI “AI Generate Story Outline / Sequence Planning / Linked Continuation” | README describes AI outline generation, sequence planning, and continuation. ([GitHub][1])                                                                                                                            | **Ignore / block equivalent routes.** This is outside the analysis-only MVP.                                                          |
| Export endpoint / full-book export                                           | API reference lists export. ([GitHub][4])                                                                                                                                                                             | **Ignore or allow read-only.** Export itself is not generation, but it should never compile AI-generated prose as if owner-authored.  |

## Practical denylist for your app

For the MVP, I would explicitly denylist these route families:

```text
/api/action/write
/api/action/revise
/api/books/*/ai-generate/*
/api/books/*/ai-continue/*
/api/books/*/continue-writing
/api/books/*/ai-rewrite-segment
```

Then separately put a **write guard** around anything touching:

```text
world_state.json
chapter_summaries.md
current_state.md
thread_status.md
outline.json
chapter_outlines.json
setup_state.json
setup/events.json
drafts/
final/
```

## What can be salvaged safely

The safest useful parts are the **audit/extraction ideas**, not the writing pipeline. The `AuditorAgent` style checks, causal-chain extraction, story-state extraction, and summary extraction can become candidate producers, but only if your wrapper enforces:

1. no prose generation or rewrite,
2. no continuation or outline creation,
3. no direct writes to truth/canon files,
4. evidence spans for every claim,
5. candidate status such as `suggested`, `needs_review`, `rejected`, or `owner_approved`,
6. no promotion without explicit owner action.

So the answer is: **do not integrate dramatica-flow as a runtime engine wholesale.** Use it as a reference repo for analysis patterns, but block its Writer/Reviser/Architect/generation endpoints and wrap extraction/audit behavior into your existing candidate-first OMI architecture.

[1]: https://github.com/ydsgangge-ux/dramatica-flow "GitHub - ydsgangge-ux/dramatica-flow: 深度集成 Dramatica 理论与 5 层 Agent 写作管线的下一代 AI 自动写小说引擎，支持因果链管理、多线叙事与伏笔追踪。A causal-driven AI novel creation system based on Dramatica theory, featuring a 5-layer Agent pipeline for deep narrative logic. · GitHub"
[2]: https://github.com/ydsgangge-ux/dramatica-flow/raw/main/core/pipeline.py "raw.githubusercontent.com"
[3]: https://github.com/ydsgangge-ux/dramatica-flow/raw/main/core/agents/__init__.py "raw.githubusercontent.com"
[4]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/README_EN.md "dramatica-flow/README_EN.md at main · ydsgangge-ux/dramatica-flow · GitHub"
[5]: https://github.com/ydsgangge-ux/dramatica-flow/raw/main/core/server.py "raw.githubusercontent.com"
------------------------------------------------------

Yes — **dramatica-flow is useful here as an analysis-concept reference**, not as a runtime engine. The repo’s own model is built around causal chains, hook tracking, emotional arcs, relationship graphs, multi-thread timelines, information boundaries, and narrative audit dimensions; the unsafe part is that its pipeline writes these into `world_state.json` and truth files, so your app should convert them into **candidate records only**. ([GitHub][1])

## Baseline candidate wrapper for every concept

Every extracted concept should share this provenance envelope:

```json
{
  "candidate_id": "cand_...",
  "candidate_type": "...",
  "status": "suggested",
  "source": {
    "project_id": "...",
    "document_id": "...",
    "document_type": "chapter|scene|note|material|imported_text",
    "chapter_id": "...",
    "scene_id": "...",
    "span_start": 0,
    "span_end": 0,
    "excerpt": "...",
    "source_file_hash": "...",
    "source_modified_at": "..."
  },
  "extraction": {
    "extractor": "dramatica_flow_inspired_adapter",
    "extractor_version": "...",
    "model_id": "...",
    "prompt_version": "...",
    "run_id": "...",
    "created_at": "...",
    "confidence": 0.0,
    "claim_basis": "explicit|strong_inference|weak_inference",
    "requires_owner_review": true
  },
  "links": {
    "related_candidate_ids": [],
    "depends_on_candidate_ids": [],
    "conflicts_with_candidate_ids": []
  }
}
```

The important rule: **no candidate updates canon, truth files, memory pages, relationship pages, timeline pages, or world state directly.** The repo’s own pipeline includes causal extraction, summary injection, and state settlement into world state/truth files; in your app, that same shape should stop at candidate creation. ([GitHub][1])

## Concept-to-candidate map

| Analysis concept from dramatica-flow                 | What to borrow                                                                                                                                                                                                                                             | Candidate types in your app                                                                                                                                                                                                                                      | Required concept-specific evidence/provenance                                                                                                                                                                                                                              |          |                                                                                                                                                                        |                                                                            |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Causal chains**                                    | The repo models each event as cause → event → effect/consequence → decision; its state types also define `CausalLink` with `cause`, `event`, `consequence`, affected decisions, triggered events, and thread IDs. ([GitHub][1])                            | `causal_link_candidate`, `timeline_event_candidate`, `character_decision_candidate`, `plot_thread_connection_candidate`, `continuity_warning_candidate`                                                                                                          | Evidence spans for the cause, event, consequence, and decision separately; source chapter/scene; involved character IDs; affected thread ID; downstream event references; confidence per link, not just global confidence.                                                 |          |                                                                                                                                                                        |                                                                            |
| **Foreshadowing / promises / mysteries / conflicts** | The repo’s hook system distinguishes four narrative commitments: foreshadow, promise, mystery, and conflict, and tracks overdue/unresolved status. ([GitHub][1])                                                                                           | `foreshadow_candidate`, `promise_candidate`, `mystery_candidate`, `conflict_candidate`, `hook_resolution_candidate`, `unresolved_hook_warning_candidate`                                                                                                         | Evidence span where the hook is planted; optional span where it is advanced or resolved; hook type; planted chapter/scene; expected resolution window if inferable; status candidate: `open                                                                                | advanced | resolved                                                                                                                                                               | possibly_abandoned`; why it matters; whether type is explicit or inferred. |
| **Emotional arcs**                                   | The repo tracks emotion intensity from 1–10 per character and supports a dual external-goal/internal-need model. Its state model includes `EmotionalSnapshot` with character, emotion, intensity, chapter, and trigger. ([GitHub][1])                      | `character_emotion_candidate`, `emotional_arc_point_candidate`, `character_goal_candidate`, `internal_need_candidate`, `arc_shift_warning_candidate`                                                                                                             | Evidence span for the emotion; trigger span; character ID/name; emotion label; intensity; chapter/scene; before/after emotion if comparing; whether the internal need is explicit or inferred; confidence and alternative readings.                                        |          |                                                                                                                                                                        |                                                                            |
| **Relationship networks**                            | The repo models relationship strength from -100 to +100 and stores relationship deltas with reason/history. ([GitHub][1])                                                                                                                                  | `relationship_candidate`, `relationship_change_candidate`, `relationship_conflict_candidate`, `relationship_knowledge_candidate`                                                                                                                                 | Evidence span for the interaction; character A/B IDs; relationship type candidate; delta candidate; reason; prior relationship candidate ID if known; who knows about the relationship; whether the change is shown by action, dialogue, narration, or inference.          |          |                                                                                                                                                                        |                                                                            |
| **Timeline / thread activity**                       | The repo’s multi-thread system supports main plot, subplot, parallel, and flashback threads, with POV characters, goal arcs, last-active tracking, dormancy warnings, and a global timeline of who did what, where, and when. ([GitHub][1])                | `timeline_event_candidate`, `plot_thread_candidate`, `thread_activity_candidate`, `thread_dormancy_warning_candidate`, `cross_thread_effect_candidate`, `flashback_event_candidate`                                                                              | Evidence span for event/action; physical or relative time marker; time order if inferable; chapter/scene; character ID; location ID; thread ID; affected threads/characters; POV character; whether event is present-time, flashback, reported, remembered, or inferred.   |          |                                                                                                                                                                        |                                                                            |
| **Information boundaries**                           | The repo’s `KnownInfoRecord` records who knows what, when they learned it, and source type: witnessed, hearsay, deduced, or document; the feature is designed to prevent characters from knowing things they have not plausibly learned. ([GitHub][1])     | `known_info_candidate`, `info_reveal_candidate`, `information_boundary_warning_candidate`, `knowledge_source_candidate`, `continuity_warning_candidate`                                                                                                          | Evidence span where information is learned; character ID; info key/content; learned chapter/scene; source type; source character/document if hearsay/document; later evidence span where character appears to use the info; warning reason if no learning source is found. |          |                                                                                                                                                                        |                                                                            |
| **Audit diagnostics**                                | The repo’s auditor dimensions include OOC behavior, information boundaries, causality, emotional arc, outline deviation, pacing, hook management, AI-ish language, continuity, conflict quality, ending hooks, and cross-thread consistency. ([GitHub][2]) | `diagnostic_candidate`, `continuity_warning_candidate`, `causality_warning_candidate`, `ooc_warning_candidate`, `information_boundary_warning_candidate`, `hook_warning_candidate`, `conflict_quality_warning_candidate`, `thread_consistency_warning_candidate` | Diagnostic dimension; severity candidate: `info                                                                                                                                                                                                                            | warning  | critical`; exact triggering excerpt; location; explanation; affected candidates; rule/prompt version; suggested diagnostic question, not rewrite advice; no prose fix. |                                                                            |
| **Structured chapter summaries**                     | The repo’s summary agent extracts key events, characters appeared, state changes, hook updates, and emotional notes, then formats them for truth files. For your app, this should become a reviewable summary candidate only. ([GitHub][2])                | `summary_candidate`, `chapter_event_summary_candidate`, `state_change_candidate`, `hook_update_candidate`, `character_presence_candidate`                                                                                                                        | Summary source span range; chapter/scene coverage; list of cited event spans; characters mentioned with evidence; state-change evidence; hook-update evidence; whether it summarizes explicit text or inferred continuity.                                                 |          |                                                                                                                                                                        |                                                                            |
| **Story-state extraction bundle**                    | The repo’s `extract-story-state` prompt extracts position changes, emotional changes, relationship changes, planted/resolved hooks, revealed information, key events, main characters, and a causal link. ([GitHub][3])                                    | `extraction_batch_candidate_set`, plus child candidates: `location_change_candidate`, `emotion_candidate`, `relationship_change_candidate`, `hook_candidate`, `info_reveal_candidate`, `timeline_event_candidate`, `causal_link_candidate`                       | Parent extraction run ID; child candidate IDs; source chapter/scene; per-child evidence span; per-child confidence; parse/validation status; whether any field was dropped because it lacked evidence.                                                                     |          |                                                                                                                                                                        |                                                                            |

## Recommended candidate type set for your app

I would implement these as a compact first version:

```text
causal_link_candidate
timeline_event_candidate
plot_thread_candidate
thread_activity_candidate
thread_dormancy_warning_candidate
foreshadow_candidate
promise_candidate
mystery_candidate
conflict_candidate
hook_resolution_candidate
character_emotion_candidate
emotional_arc_point_candidate
relationship_candidate
relationship_change_candidate
known_info_candidate
info_reveal_candidate
diagnostic_candidate
continuity_warning_candidate
summary_candidate
state_change_candidate
```

That set covers the useful dramatica-flow analysis ideas while staying aligned with your OMI principle: **extract → evidence → candidate → owner review → optional promotion**.

## Fields I would require per category

### `causal_link_candidate`

```json
{
  "candidate_type": "causal_link_candidate",
  "payload": {
    "cause": "...",
    "event": "...",
    "consequence": "...",
    "affected_decisions": [
      {"character_ref": "...", "decision": "..."}
    ],
    "triggered_events": [],
    "thread_ref": "...",
    "source_thread_ref": "..."
  },
  "evidence": {
    "cause_span": {...},
    "event_span": {...},
    "consequence_span": {...},
    "decision_spans": []
  }
}
```

### `hook_candidate`

```json
{
  "candidate_type": "foreshadow_candidate|promise_candidate|mystery_candidate|conflict_candidate",
  "payload": {
    "hook_type": "foreshadow|promise|mystery|conflict",
    "description": "...",
    "status": "open|advanced|resolved|possibly_abandoned",
    "planted_in": "...",
    "expected_resolution_range": null,
    "resolved_in": null
  },
  "evidence": {
    "plant_span": {...},
    "advance_spans": [],
    "resolution_span": null
  }
}
```

### `character_emotion_candidate`

```json
{
  "candidate_type": "character_emotion_candidate",
  "payload": {
    "character_ref": "...",
    "emotion": "...",
    "intensity": 7,
    "trigger": "...",
    "arc_direction": "ascending|descending|plateau|unknown",
    "external_goal_ref": null,
    "internal_need_ref": null
  },
  "evidence": {
    "emotion_span": {...},
    "trigger_span": {...}
  }
}
```

### `relationship_change_candidate`

```json
{
  "candidate_type": "relationship_change_candidate",
  "payload": {
    "character_a_ref": "...",
    "character_b_ref": "...",
    "relationship_type": "ally|enemy|neutral|family|mentor|rival|romantic|unknown",
    "strength_delta": 10,
    "reason": "...",
    "known_to": []
  },
  "evidence": {
    "interaction_span": {...},
    "reason_span": {...}
  }
}
```

### `timeline_event_candidate`

```json
{
  "candidate_type": "timeline_event_candidate",
  "payload": {
    "chapter_ref": "...",
    "scene_ref": "...",
    "physical_time": "...",
    "time_order": null,
    "character_ref": "...",
    "location_ref": "...",
    "action": "...",
    "thread_ref": "...",
    "affected_threads": [],
    "affected_characters": [],
    "event_kind": "position|emotion|info|conflict|key|other"
  },
  "evidence": {
    "action_span": {...},
    "time_span": null,
    "location_span": null
  }
}
```

### `known_info_candidate`

```json
{
  "candidate_type": "known_info_candidate",
  "payload": {
    "character_ref": "...",
    "info_key": "...",
    "content": "...",
    "learned_in_chapter_ref": "...",
    "source_type": "witnessed|hearsay|deduced|document",
    "source_ref": null
  },
  "evidence": {
    "learning_span": {...},
    "source_span": {...}
  }
}
```

### `diagnostic_candidate`

```json
{
  "candidate_type": "diagnostic_candidate",
  "payload": {
    "dimension": "information_boundary|causality|emotional_arc|continuity|hook_management|relationship|thread_consistency|conflict_quality|ooc",
    "severity": "info|warning|critical",
    "description": "...",
    "diagnostic_question": "...",
    "affected_candidate_refs": []
  },
  "evidence": {
    "trigger_span": {...},
    "comparison_spans": []
  }
}
```

## The clean extraction strategy

Use dramatica-flow as a **taxonomy and schema inspiration source**, not as an execution dependency. The safest path is:

```text
owner-authored text
→ read-only analyzer
→ candidate records with evidence
→ validation: reject candidates without source spans
→ UI review queue
→ owner approves/rejects/edits
→ approved memory pages update only through explicit owner action
```

The most valuable concepts to copy first are **causal links, hook/promises/mysteries/conflicts, relationship changes, known-info records, timeline events, and audit diagnostics**. Those line up directly with the repo’s analysis structures and with the features you already want: characters, relationships, timeline events, plot threads, contradictions, continuity warnings, summaries, and canon facts.

[1]: https://github.com/ydsgangge-ux/dramatica-flow/blob/main/README_EN.md "dramatica-flow/README_EN.md at main · ydsgangge-ux/dramatica-flow · GitHub"
[2]: https://raw.githubusercontent.com/ydsgangge-ux/dramatica-flow/main/core/agents/__init__.py "raw.githubusercontent.com"
[3]: https://raw.githubusercontent.com/ydsgangge-ux/dramatica-flow/main/core/server.py "raw.githubusercontent.com"
