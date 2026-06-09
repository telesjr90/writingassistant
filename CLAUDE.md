# CLAUDE.md — Dramatica-Informed Writing Assistant

## Project identity

Working directory:

`/home/tjrpirateking/projects/WritingAssistantApplication`

Repository:

`telesjr90/writingassistant`

Working product name:

`Dramatica-Informed Writing Assistant`

The near-term roadmap is **not Dramatica-first**. The current priority is the **Pre-Dramatica Project Workspace Foundation**.

The app should first become a usable local writing-project workspace:

1. Create projects.
2. Select projects from a library.
3. Create projects through OMI-guided idea capture.
4. Organize chapters, scenes, notes, and materials.
5. Store and edit owner-authored prose.
6. Show Project Overview, Chapters/Scenes, Notes/Materials, OMI Ideas/Candidates, and Project Memory/Canon pages.
7. Keep pending candidates visibly separate from approved project truth.

Dramatica/NCP analysis is a later advanced layer.

## Non-negotiable product boundary

This product is analysis-only.

The app may store, edit, and organize owner-authored prose, notes, research, references, metadata, and materials.

The AI must never:

* write story prose
* rewrite story prose
* continue story prose
* imitate style
* polish prose
* improve prose
* expand a scene
* generate dialogue
* generate chapters
* generate story passages

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## Candidate/canon boundary

Never treat model output, OMI output, NotebookLM output, extractor output, reference material, or generated summaries as approved truth.

Important distinctions:

* Owner-authored source material is source/evidence, not canon by default.
* OMI raw ideas are owner input, not canon.
* OMI candidates are candidate planning records, not canon.
* Approved candidates are still not durable memory/canon until future apply-promotion explicitly applies them.
* Promotion records are audit records only, not canon by themselves.
* Applied memory/canon must require explicit owner-controlled future promotion.
* Pending, rejected, archived, and needs-revision candidates are not canon.
* Notes/materials are not training data by default.
* Reference/copyrighted material is not owner-authored story truth unless explicitly marked by a future owner-controlled policy.

## Current architecture

Backend:

* Python FastAPI
* Local project files under `projects/{project_id}/`
* Ollama-backed Story Check path through `backend/analysis_engine.py`
* Current baseline model: `qwen3:8b`
* Mock mode exists through `ANALYSIS_MODE=mock`

Frontend:

* React/Vite
* Existing editor/sidebar style interface
* Existing OMI panel slice
* Future workspace pages are being documented before implementation

Project docs:

* `docs/master_plan.md`
* `docs/plan.md`
* `docs/roadmap/*`

Important roadmap specs include:

* `docs/roadmap/project_workspace_foundation_spec.md`
* `docs/roadmap/project_creation_flow_spec.md`
* `docs/roadmap/project_selector_library_spec.md`
* `docs/roadmap/omi_guided_project_creation_spec.md`
* `docs/roadmap/chapter_scene_data_model_spec.md`
* `docs/roadmap/notes_materials_data_model_spec.md`
* `docs/roadmap/user_authored_document_editor_workflow_spec.md`
* `docs/roadmap/project_overview_page_spec.md`
* `docs/roadmap/chapters_scenes_page_spec.md`
* `docs/roadmap/notes_materials_page_spec.md`
* `docs/roadmap/project_memory_canon_page_structure_spec.md`
* `docs/roadmap/omi_storage_model.md`
* `docs/roadmap/omi_mvp_schema_lifecycle.md`
* `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
* `docs/roadmap/project_memory_canon_storage_model.md`
* `docs/roadmap/writer_assistant_core_candidate_schemas.md`
* `docs/roadmap/task_backlog.md`
* `docs/roadmap/phase_map.md`
* `docs/roadmap/open_questions.md`
* `docs/roadmap/risk_register.md`
* `docs/roadmap/decision_log.md`
* `docs/roadmap/mvp_completion_test_matrix.md`

## Default task mode

Default to documentation-only unless the user explicitly asks for implementation.

For documentation-only tasks:

Do not modify:

* backend runtime code
* frontend runtime code
* tests
* package/dependency files
* dataset files
* JSONL files
* training/data/dataset_manifest.json
* runtime project files under `projects/`
* OMI runtime records
* memory/canon runtime files

Do not run:

* training
* fine-tuning
* Ollama/live model calls
* package installs

Do not stage, commit, or push unless the user explicitly asks.

For each documentation task, create or update only the requested roadmap docs and related planning docs.

Local reports under `training/reports/` are expected to be ignored by Git unless specifically whitelisted.

## Required safety checks for documentation tasks

Before final response, run:

```bash
git status --short --branch
git diff --stat
git diff --check
git diff --cached --name-only
```

If runtime code, tests, dependency files, dataset files, JSONL files, runtime project files, OMI records, or memory/canon files were modified by mistake, stop and report BLOCKED.

## Documentation task final response format

Use this format unless the user gives a different one:

1. Result:

   * PASS / BLOCKED / PARTIAL

2. Files created/modified:

   * list every file
   * include local report path

3. Main spec summary:

   * summarize the target

4. Key model/flow decisions:

   * summarize core recommendations

5. Safety boundaries:

   * summarize no-prose, candidate/canon, no-silent-promotion boundaries

6. API/UI planning:

   * summarize future route groups and frontend components, if applicable

7. Future tests:

   * summarize key future test categories

8. Roadmap updates:

   * summarize docs updated and why

9. Deferred decisions:

   * list what remains open

10. Safety confirmations:

* no backend runtime code changed
* no frontend runtime code changed
* no tests changed
* no package/dependency files changed
* no dataset files changed
* no JSONL/training records created
* dataset_manifest.json unchanged
* no training/fine-tuning run
* no Ollama/live model call
* no packages installed
* no Dramatica-specific logic implemented
* no runtime project files created
* no OMI records created
* no memory/canon files created when applicable
* no staging/commit

11. Recommended next task:

* recommend review/commit if PASS, otherwise recommend smallest corrective task

## Commit policy

Do not commit automatically.

When the user asks for commit commands, provide commands rather than committing.

Use this pattern:

```bash
git status --short --branch
git diff --stat
git diff --name-only
git diff --check
git add <explicit expected files only>
git status --short
git diff --cached --stat
git diff --cached --check
git commit -m "<message>"
git status --short --branch
git log -1 --oneline
```

Never stage ignored local reports unless the user explicitly asks.

## Preferred Claude Code model settings

For WORKSPACE planning/docs:

* Preferred model: `sonnet`
* Preferred effort: `high`

For broad roadmap reconciliation or hard architecture decisions:

* Preferred model: `opusplan`
* Preferred effort: `high`

For very difficult one-off reasoning:

* Preferred model: `opus`
* Preferred effort: `xhigh`

For quick doc cleanup:

* Preferred model: `sonnet`
* Preferred effort: `medium`

Avoid `max` unless the user explicitly approves the cost/token risk.

## Local/free model fallback

If using Ollama with Claude Code or another local agent:

Preferred fallback order:

1. `qwen3-coder:30b` if the machine can run it.
2. `devstral-small-2` if it runs better.
3. `qwen3:8b` only for drafts, review, summarization, and low-risk cleanup.

Do not rely on a small local model for unsupervised repo-wide edits. Require manual review.

## Skills and agents

Use project subagents from `.claude/agents/` for isolated review/planning roles.

Use project skills from `.claude/skills/` for repeatable workflows.

Prefer these roles:

* roadmap-docs-orchestrator: multi-file roadmap/spec planning
* safety-boundary-reviewer: no-prose/candidate-canon review
* implementation-planner: future implementation sequencing and acceptance criteria

Use skills for:

* workspace-doc-task
* review-and-commit-docs
* no-prose-boundary

## Default behavior for next roadmap tasks

For future WORKSPACE tasks:

* inspect relevant existing specs
* create one new spec file if needed
* update only related docs
* create an ignored local report
* run safe documentation checks only
* do not implement runtime code
* do not stage or commit
