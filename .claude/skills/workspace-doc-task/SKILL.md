---
name: workspace-doc-task
description: Use this skill when creating or updating WORKSPACE roadmap/spec documentation tasks for this project.
effort: high
---

# Workspace Documentation Task Skill

Use this workflow for WORKSPACE documentation tasks.

## Required constraints

Documentation-only unless explicitly told otherwise.

Do not modify:

* backend runtime code
* frontend runtime code
* tests
* package/dependency files
* dataset files
* JSONL files
* training/data/dataset_manifest.json
* runtime project files under projects/
* OMI runtime records
* memory/canon runtime files

Do not run:

* training
* fine-tuning
* Ollama/live model calls
* package installs

Do not stage, commit, or push.

## Required inspection

Inspect:

* docs/master_plan.md
* docs/plan.md
* related docs/roadmap/*.md files
* task_backlog.md
* phase_map.md
* open_questions.md
* risk_register.md
* decision_log.md
* mvp_completion_test_matrix.md

Inspect runtime files only if needed for context. Do not edit them.

## Required report

Create a local ignored report:

`training/reports/<task_id>_<short_name>.md`

Include:

* date/time
* files inspected
* files modified
* spec created/updated
* summary of main decisions
* future tests
* deferred decisions
* safety confirmations

## Required validation

Run:

```bash
git status --short --branch
git diff --stat
git diff --check
git diff --cached --name-only
```

If unexpected runtime/test/package/dataset/runtime project changes appear, stop and report BLOCKED.

## Final response

Use the project's standard final response format from CLAUDE.md.
