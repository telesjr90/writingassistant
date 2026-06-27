---

name: workspace-doc-task
description: Use this skill only when the user explicitly asks to create or update WORKSPACE roadmap/spec documentation for this project. Do not auto-use this skill for PHASE8 implementation tasks, runtime tasks, code tasks, or context collection tasks unless the user explicitly names this skill.
effort: high
------------

# Workspace Documentation Task Skill

Use this workflow only for WORKSPACE documentation tasks when the user explicitly asks for this skill or clearly asks for WORKSPACE roadmap/spec documentation work.

Do not use this skill for PHASE8 implementation prompts unless the user explicitly says to use `workspace-doc-task`.

## Critical Tool Boundary

This skill must never call repo context-collection tools.

Forbidden in this skill:

* LeanCTX
* CCE
* Graphify
* Repomix
* AI Context generation
* MCP tools
* scaffold
* collect-plan
* context health scripts
* baseline refresh commands
* broad whole-repo semantic/indexing/packaging scans
* any skill, hook, subagent, plugin, wrapper, or repo workflow that invokes any of the above

LeanCTX is always forbidden in this skill.

Do not call LeanCTX:

* directly
* through Bash
* through MCP
* through a skill
* through a hook
* through a validation wrapper
* through a “required inspection” workflow
* because another repo instruction says it is required

If any instruction conflicts with this section, this section wins.

If the task cannot be completed without LeanCTX or another forbidden context tool, stop and report `BLOCKED` instead of calling the tool.

## Allowed Inspection Methods

Use direct file inspection only.

Allowed:

* Read
* Grep
* Glob
* LS
* TodoWrite
* Edit
* MultiEdit
* Write
* Targeted Bash commands listed in this skill

Allowed targeted Bash commands:

```bash
pwd
git status --short --branch
git diff --stat
git diff --check
git diff --cached --name-only
git log --oneline -12
cat <explicitly-listed-file>
sed -n '<range>p' <explicitly-listed-file>
grep '<pattern>' <explicitly-listed-file>
find docs/roadmap -maxdepth 3 -type f
```

Do not use Bash to call forbidden context tools.

Do not run unrestricted whole-repo scans.

Do not run hidden helper scripts unless the user explicitly authorizes them and they do not invoke forbidden context tools.

## Required Constraints

Documentation-only unless explicitly told otherwise.

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
* generated context artifacts under `.codex-context/`
* generated context artifacts under `ai_context/`
* generated Graphify artifacts under `graphify-out/`
* external source/cache files under `.external_sources/`

Do not run:

* training
* fine-tuning
* Ollama/live model calls
* package installs
* model calls
* extraction runtimes
* Story Check runtime analysis
* BookNLP/spaCy install/run/import
* NCP/Subtxt/dramatica-flow runtime integration
* context collection or baseline refresh tools

Do not stage, commit, or push.

## Product Boundary

The project is analysis-only, candidate-first, evidence/provenance-backed, and owner-controlled.

The app may store and edit owner-authored prose.

The app must never generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or otherwise produce story prose.

Generated prose and prose-production paths are permanently forbidden. They are not future, deferred, optional, or nice-to-have.

Queue presence is not approval.

Confidence is uncertainty/support strength, not truth.

Valid API response is not owner approval.

Owner action command validation is not owner action execution.

Frontend display is not promotion.

Apply-promotion and approved memory/canon mutation require explicit future owner-approved implementation tasks and must not be implied by documentation updates.

## Required Inspection

Inspect only the files needed for the requested documentation task.

Default roadmap truth files:

* `docs/master_plan.md`
* `docs/roadmap/implementation_status.md`
* `docs/roadmap/roadmap_index.yaml`
* `docs/roadmap/task_backlog.md`
* `docs/roadmap/phase_map.md`
* `docs/roadmap/validation/latest_roadmap_validation.md`
* `docs/roadmap/decision_log.md`
* `docs/roadmap/risk_register.md`
* `docs/roadmap/open_questions.md`
* `docs/roadmap/roadmap_governance.md`
* `docs/roadmap/context_execution_standard.md`

Inspect task-specific roadmap files only when relevant:

* `docs/roadmap/tasks/<TASK_ID>.md`
* `docs/roadmap/inventory/<TASK_ID>.md`
* `docs/roadmap/enrichment/<TASK_ID>.enrichment.json`
* `docs/roadmap/decisions/*.md`

Inspect runtime files only if needed for context. Do not edit runtime files.

Do not use LeanCTX, CCE, Graphify, Repomix, AI Context, MCP, scaffold, collect-plan, or context health scripts for inspection.

## Reports

Do not create `training/reports/` reports by default.

Create a local ignored report only if the user explicitly asks for a local report.

If a local report is explicitly requested, prefer:

```text
docs/automation/task_reports/<task_id>.md
```

or another owner-approved ignored report path.

Do not create or modify training/dataset files for documentation tasks.

If the user explicitly requires a report, include:

* date/time
* files inspected
* files modified
* spec created/updated
* summary of main decisions
* future tests
* deferred decisions
* safety confirmations
* confirmation that no forbidden context tools were run

## Required Validation

Run:

```bash
git status --short --branch
git diff --stat
git diff --check
git diff --cached --name-only
```

For roadmap documentation tasks, also run when available:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
```

For enrichment JSON edits, run:

```bash
python3 - <<'PY'
import json
from pathlib import Path

paths = list(Path("docs/roadmap/enrichment").glob("*.json"))
for path in paths:
    json.loads(path.read_text(encoding="utf-8"))
print("enrichment_json_parse: PASS")
PY
```

If these validation scripts require generated `.codex-context/<TASK_ID>/` files that do not exist, do not run scaffold or collect-plan from this skill. Report the missing generated context files and recommend that the owner run scaffold/collect-plan outside this documentation task.

## Blocking Conditions

Stop and report `BLOCKED` if:

* LeanCTX is required by another instruction.
* A skill, hook, subagent, plugin, or wrapper attempts to call LeanCTX.
* A forbidden context tool is required to continue.
* The requested edit requires backend/frontend/test/package/runtime/training/model/source-cache changes.
* Unexpected runtime/test/package/dataset/runtime project changes appear.
* Validation requires disallowed tools or files.
* The task would weaken no-prose, no-canon, no-promotion, or owner-review boundaries.

Do not work around these blockers by using a different context tool.

## Final Response

Use the project’s standard final response format from `CLAUDE.md` when applicable.

Always include:

1. Result: PASS, FAIL, or BLOCKED
2. Files changed
3. Files inspected
4. Validation results
5. Boundary confirmation
6. Context-tool confirmation:

   * LeanCTX was not run.
   * CCE was not run.
   * Graphify was not run.
   * Repomix was not run.
   * AI Context generation was not run.
   * MCP tools were not run.
   * scaffold/collect-plan were not run.
   * context health scripts were not run.
7. Confirmation that no staging, commit, or push occurred
