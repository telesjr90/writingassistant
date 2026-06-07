# Product Pivot: Writer Assistant Core Plan Update

Date/time: 2026-06-07 America/Los_Angeles

## Scope

This documentation-only update records the product pivot from a Dramatica-first analyzer roadmap to a Writer Assistant Core roadmap.

The working product name can remain Dramatica-Informed Writing Assistant. The near-term implementation priority is now a local, analysis-only writer assistant that identifies, organizes, connects, annotates, and reviews story knowledge from the writer's own text.

## Files Inspected

- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/tooling_decisions.md`
- `docs/roadmap/optional_analysis_extractors.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/ncp_compatibility_subset.md`
- `docs/roadmap/mvp_completion_test_matrix.md`
- `docs/roadmap/app_mvp_architecture_audit.md`

## Files Modified

- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/tooling_decisions.md`
- `docs/roadmap/optional_analysis_extractors.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/ncp_compatibility_subset.md`
- `training/reports/product_pivot_writer_assistant_core_plan_update.md`

## Product Pivot Summary

The app roadmap now prioritizes Writer Assistant Core after the current MVP foundation / Phase 6 exit-preflight is owner-accepted.

Writer Assistant Core is focused on:

- Characters, aliases, nicknames, locations, objects/items, and organizations/groups.
- Scenes, events/actions, timelines, relationships, plot threads, and open questions.
- Continuity issues, contradictions, annotations, evidence spans, and provenance.
- Candidate-first review and promotion through OMI before durable project memory/canon changes.

The product remains analysis-only and must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message remains:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## Updated Priority Order

1. Complete/record App MVP Phase 6 foundation acceptance.
2. Phase 7: Writer Assistant Core Planning and Schemas.
3. Phase 8: OMI Expansion for Story Knowledge Candidates.
4. Phase 9: Story Knowledge Extraction Pipeline.
5. Phase 10: Annotation, Evidence, and Review UI.
6. Phase 11: Project Memory / Canon Promotion.
7. Phase 12: Continuity, Relationship, Timeline, and Plot Assistance.
8. Later: Advanced Dramatica Analysis.
9. Later: Fine-tuning / `dramatica-analyst` model.

## Dramatica Demotion Summary

Dramatica/NCP remains allowed as a future advanced analysis layer for storyform analysis, throughline classification, CIPS/dynamics, IC/RS analysis, and possible fine-tuned model evaluation.

It is no longer the next implementation priority. Dramatica-specific truth claims remain owner-gated, evidence-backed, and deferred. Fine-tuning remains paused and outside the MVP/core critical path.

## OMI Priority Change

OMI is now the central candidate review and promotion system for future extracted story knowledge.

Future OMI candidate types documented:

- `character_candidate`
- `location_candidate`
- `object_candidate`
- `organization_candidate`
- `timeline_event_candidate`
- `relationship_candidate`
- `plot_thread_candidate`
- `continuity_warning_candidate`
- `annotation_candidate`
- `open_question_candidate`

Extracted knowledge must remain candidate-only until owner approval, destination selection, evidence/provenance review, and final confirmation. Candidates cannot mutate `bible.json`, `storyform.json`, scenes, `project.json`, owner memory, project memory, or canon without owner approval.

## Extractor / Tooling Priority Change

Optional extractors are reclassified from vague post-MVP tooling to future Writer Assistant Core implementation research.

Tool roles now recorded:

- `segram`: first future extractor spike candidate for semantic/action/entity extraction.
- `fabula`: second-stage graph/entity/event/relationship extraction candidate.
- `silverfish`: later relationship/evidence-cluster candidate.
- `AI-Reader-V2`: visualization/UI reference for maps, timelines, and relationship graphs.
- `narrative-blueprint`: future batch/evaluation pipeline inspiration after at least one extractor exists.
- `narrative-context-protocol`: later structural/Dramatica reference and optional schema inspiration, not the near-term backbone.
- `NovelClaw`: future memory-bank inspiration only.
- `dramatron`, `ai-story-writer`, and Inkos/story-engine-style systems: not runtime implementation templates; generation-heavy systems remain blocked or deferred.

No extractor dependency should be installed until a dedicated spike evaluates license, maintenance, runtime cost, safety, candidate-only behavior, and OMI integration.

## New Phases / Tasks Added

The roadmap now includes a Writer Assistant Core phase sequence from Phase 7 through Phase 12.

The backlog now includes CORE tasks:

- CORE-001 through CORE-005 for product pivot docs, schemas, evidence/provenance, project memory/canon, and OMI candidate type expansion.
- CORE-006 through CORE-013 for extraction pipelines, annotation UI, owner promotion flow, continuity/contradiction checks, and search/query assistance.
- CORE-014 through CORE-018 for extractor evaluation and visualization research.

## Risks Added / Updated

The risk register now tracks:

- Extracted candidates mistaken for canon.
- Relationship/timeline/plot extraction overclaiming certainty.
- Annotation clutter overwhelming the writer.
- External extractor dependency license/security/maintenance/runtime risk.
- Scope creep from assistant/annotation into prose generation.
- Dramatica-first roadmap distraction from core writer-assistant value.

Mitigations center on candidate-only OMI flow, evidence spans, provenance, owner review, no-prose guardrails, staged implementation, UI status labels, and extractor spikes before dependency adoption.

## Open Questions Added

Future owner/implementation choices now include:

- Durable project memory/canon file structure.
- First-release candidate type set.
- Minimum evidence-span format.
- Annotation storage location.
- First extractor strategy.
- Candidate annotation review UI.
- Relationship/timeline promotion criteria.
- When Dramatica analysis should return as an advanced layer.

## Commands Run

- `pwd`
- `git status --short --branch`
- `ls docs/roadmap`
- `test -f docs/roadmap/optional_analysis_extractors.md && echo "optional_analysis_extractors.md exists" || echo "optional_analysis_extractors.md missing"`
- `grep -RInE "Dramatica-first|Dramatica|optional extractor|extractor|OMI|Phase 6|fine-tuning|Fine-Tuning|MVP" ...`
- `sed -n ...` inspections for roadmap and planning docs
- `grep -n ...` targeted inspections for pivot terms
- Final validation commands are recorded in the task response after execution.

## Items Deliberately Not Done

- No backend runtime code changed.
- No frontend runtime code changed.
- No packages installed.
- No `package.json` edits made.
- No JSONL records created.
- No review JSONL records created.
- No SFT records created.
- `training/data/dataset_manifest.json` not updated.
- No training run.
- No smoke training run.
- No Ollama/qwen3 live call made.
- No optional extractors implemented.
- No Books 4-5 work started.
- No files staged.
- No files committed.
- No files pushed.
