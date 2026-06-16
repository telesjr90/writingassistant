# PHASE8-IMPL-001 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-001`
- Title: Writer Assistant Core implementation readiness and first runtime slice plan
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE7-IMPL-010` - Workspace Validation / Browser and Manual Smoke

## 2. Why This Parent Exists

Phase 7 made the app a usable Project Workspace Foundation: project creation and selection, project-aware editing, chapter/scene compatibility, notes/materials storage, Project Overview, OMI-guided staged setup, a read-only Memory / Canon shell, and validation closeout are complete.

Phase 8 begins the Writer Assistant Core direction. The app should help identify, organize, connect, annotate, and review story knowledge from owner-authored project text, but the first parent must start with implementation readiness and context planning before runtime extraction, candidate creation, storage mutation, model calls, UI expansion, or apply-promotion behavior is added.

## 3. Scope

This parent prepares the first safe runtime slice for Writer Assistant Core. It focuses on:

- Current code, storage, and test inventory.
- Context collection planning before any context tool execution.
- Candidate schema alignment with `docs/roadmap/writer_assistant_core_candidate_schemas.md`.
- Source, evidence, and provenance boundaries.
- OMI candidate-first lifecycle and typed story-knowledge review planning.
- No-prose and no-silent-promotion boundaries.
- First runtime slice selection.
- Acceptance criteria for the first implementation task.

Near-term story knowledge categories include characters, aliases/nicknames, organizations/groups, locations/settings, objects/items, scenes, events/actions, timeline/causality notes, relationships, plot threads, open questions, continuity/consistency issues, contradictions, annotations, evidence, and provenance.

## 4. Non-Scope

This parent, and specifically `PHASE8-IMPL-001-T001`, excludes:

- Runtime extraction implementation.
- Model/Ollama calls.
- Generated prose, rewriting, continuation, style imitation, or prose improvement.
- Summarization as durable truth.
- Apply-promotion.
- Memory/canon mutation.
- OMI candidate promotion.
- Frontend extraction UI.
- Backend extraction routes.
- Package/dependency changes.
- Training, JSONL, dataset, or model artifact work.
- Context-tool execution in T001.

## 5. Risks

- Accidentally turning extraction into generation.
- Candidates being treated as canon.
- Provenance/evidence not being attached early enough.
- Context tools producing stale or overbroad context.
- Schema drift from prior CORE/OMI specs.
- Premature model/Ollama integration.
- Broad implementation tasks becoming too large.
- Runtime changes before context is collected.

## 6. Current T001 Inventory Result

`PHASE8-IMPL-001-T001` is docs/status/planning only. It publishes the Phase 8 parent, child-task sequence, inventory, enrichment JSON, and roadmap/status updates. It does not run context tools and does not change runtime code, tests, backend/frontend/package files, project runtime files, training data, JSONL records, or dataset manifests.
