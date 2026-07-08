# Roadmap Context Execution Standard

## Purpose

This document defines the standard context-maintenance workflow for roadmap implementation work.

The goal is to keep implementation prompts small, accurate, and bounded while preserving a durable context baseline for the full codebase. Context tools are planning and evidence tools only. They must not be embedded inside Codex, Cursor, Claude Code, or other implementation micro-task prompts.

Generated context artifacts are evidence. They are not roadmap truth, not product decisions, and not task-completion records.

Roadmap truth remains controlled by:

1. `docs/roadmap/roadmap_index.yaml`
2. `docs/roadmap/implementation_status.md`
3. `docs/roadmap/validation/latest_roadmap_validation.md`

## Product Boundary

All context collection and implementation work must preserve the project boundary:

* Analysis-only.
* Candidate-first.
* Evidence/provenance-backed.
* Owner-controlled.
* Owner-authored prose storage/editing is allowed.
* AI-generated prose is permanently forbidden.
* The app must never generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or produce story prose.
* Queue presence is not approval.
* Confidence is not truth.
* Candidate persistence is not canon.
* Raw artifacts are support data, not canon.
* Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.

## Tooling Directory

Roadmap enrichment tooling lives here:

Windows path:

```text
\\wsl$\Ubuntu\home\tjrpirateking\projects\WritingAssistantApplication\scripts\roadmap_enrichment
```

WSL path:

```text
/home/tjrpirateking/projects/WritingAssistantApplication/scripts/roadmap_enrichment
```

Important files:

```text
scripts/roadmap_enrichment/README.md
scripts/roadmap_enrichment/enrich_task.py
scripts/roadmap_enrichment/enrich_all.py
scripts/roadmap_enrichment/render_task_record.py
scripts/roadmap_enrichment/tool_commands.md
scripts/roadmap_enrichment/task_enrichment.schema.json
scripts/roadmap_enrichment/templates/cce_queries.yaml
scripts/roadmap_enrichment/templates/graphify_queries.yaml
scripts/roadmap_enrichment/templates/task_record.md.j2
scripts/roadmap_enrichment/templates/tool_command_probe.md
scripts/check_enrichment.py
scripts/validate_roadmap.py
scripts/context_health_check.sh
scripts/generate_ai_context.sh
```

## Context Tool Boundary

The following tools are planning/context tools only:

* CCE
* Graphify
* Repomix
* LeanCTX
* AI Context / `scripts/generate_ai_context.sh`
* MCP tools
* Roadmap enrichment scaffold / collect-plan

They must not run inside normal implementation micro-task prompts.

Implementation prompts may reference already-created context artifacts, but must not run context tooling unless the task is explicitly a context collection or validation task.

Do not run CCE, Graphify, Repomix, LeanCTX, MCP, or broad context collection inside normal implementation prompts unless the task is explicitly a context collection task.

## OMI MVP Live-Runtime Rule

Fixture/mock adapter contracts are scaffolding only. They validate schema, safety, no-prose boundaries, and candidate normalization, but they do not prove that the application can run real analysis.

For PHASE8-IMPL-023 MVP completion, OMI and analysis must connect to real local/runtime tools and validate them through automated and manual tests.

A tool is MVP-complete only after:

* real local/runtime adapter connection,
* runtime preflight or health check,
* automated adapter/orchestrator test,
* manual OMI test on real raw idea text,
* evidence-backed candidate output or explicit safe fail-closed behavior,
* no Memory/Canon mutation,
* no promotion/apply-promotion,
* no generated story prose.

Implementation prompts must distinguish:

1. fixture/mock adapter contract validation,
2. real live/runtime integration,
3. automated runtime testing,
4. manual OMI validation,
5. owner-review UI,
6. MVP closeout.

Do not describe fixture-only adapter contracts as live integration.
Do not describe UI display of fixture outputs as MVP completion.
Do not mark PHASE8-IMPL-023 complete until selected live tools are connected/tested or explicitly owner-blocked.

## Standard Context Artifacts

Parent-level context artifacts should use:

```text
.codex-context/<PARENT_TASK_ID>/
```

For example:

```text
.codex-context/PHASE8-IMPL-014/
```

Expected collect-plan files:

```text
.codex-context/<PARENT_TASK_ID>/task_manifest.json
.codex-context/<PARENT_TASK_ID>/collection_plan.md
.codex-context/<PARENT_TASK_ID>/cce-queries.md
.codex-context/<PARENT_TASK_ID>/graphify-queries.md
.codex-context/<PARENT_TASK_ID>/repomix-include-candidates.txt
.codex-context/<PARENT_TASK_ID>/ai-context-command-candidates.md
.codex-context/<PARENT_TASK_ID>/evidence_manifest.json
```

Expected collected evidence files, when explicit collection is authorized:

```text
.codex-context/<PARENT_TASK_ID>/cce-findings.md
.codex-context/<PARENT_TASK_ID>/graphify-output.md
.codex-context/<PARENT_TASK_ID>/repomix-output.md
```

Repo-wide baseline artifacts should use:

```text
.codex-context/baseline/<YYYY-MM-DD-codebase-baseline>/
```

Repomix generated packs should also remain under ignored/generated context paths such as:

```text
ai_context/
.codex-context/baseline/<BASELINE_ID>/repomix/
```

## Before Running Any Implementation Task Prompt

Complete these context checks before running a task prompt.

### 1. Confirm Roadmap Frontier

Run or inspect:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication

git status --short --branch
sed -n '1,80p' docs/roadmap/implementation_status.md
python3 scripts/validate_roadmap.py
python3 scripts/check_enrichment.py
```

Confirm:

* Current active parent.
* Current child task.
* Last completed child.
* Last completed parent.
* Whether the task is docs-only, runtime, validation, or closeout.
* Whether the working tree is clean or intentionally dirty.
* Whether uncommitted changes belong to the previous completed task.

Do not proceed if the active child in the prompt does not match the roadmap truth layer.

### 2. Confirm `context_pack` Exists for the Active Parent

The active parent task in `docs/roadmap/roadmap_index.yaml` must include:

```json
"context_pack": ".codex-context/<PARENT_TASK_ID>/"
```

Example:

```json
"context_pack": ".codex-context/PHASE8-IMPL-014/"
```

If missing, add the pointer to the parent task entry in `docs/roadmap/roadmap_index.yaml`, then run:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
```

### 3. Run Scaffold and Collect-Plan

Run this outside implementation prompts:

```bash
python3 scripts/roadmap_enrichment/enrich_task.py \
  --task <PARENT_TASK_ID> \
  --mode scaffold

python3 scripts/roadmap_enrichment/enrich_task.py \
  --task <PARENT_TASK_ID> \
  --mode collect-plan
```

This writes planned context files only. It does not run CCE, Graphify, Repomix, AI Context, LeanCTX, MCP tools, tests, app servers, or implementation work.

### 4. Inspect Generated Context Questions

Read:

```text
.codex-context/<PARENT_TASK_ID>/cce-queries.md
.codex-context/<PARENT_TASK_ID>/graphify-queries.md
.codex-context/<PARENT_TASK_ID>/repomix-include-candidates.txt
.codex-context/<PARENT_TASK_ID>/ai-context-command-candidates.md
```

Decide whether explicit collection is needed.

For docs-only decision tasks, collection may be light or skipped if roadmap context is already sufficient.

For runtime implementation tasks, collect at least task-relevant CCE, Graphify, and Repomix evidence unless the task is intentionally narrow and already has a complete allowlist.

### 5. Run CCE Collection Only When Authorized

CCE may be used only as explicit owner-run context collection.

Do not run:

```bash
cce init
```

Do not run CCE inside implementation prompts.

Safe pattern:

```bash
cce search --top-k 8 "<query from .codex-context/<PARENT_TASK_ID>/cce-queries.md>"
```

Save results to:

```text
.codex-context/<PARENT_TASK_ID>/cce-findings.md
```

### 6. Run Graphify Collection Only When Authorized

Graphify query/path/explain may be used against an existing graph during explicit context collection.

Safe pattern:

```bash
graphify query "<query from .codex-context/<PARENT_TASK_ID>/graphify-queries.md>" \
  --graph graphify-out/graph.json \
  --budget 3000
```

Save results to:

```text
.codex-context/<PARENT_TASK_ID>/graphify-output.md
```

Run `graphify update .` only when:

* Starting a repo-wide baseline,
* Ending a phase or parent with code changes,
* The existing graph is stale relative to backend/frontend/test code,
* Or the owner explicitly authorizes graph refresh.

Do not run Graphify update/extract inside implementation prompts.

### 7. Run Repomix / AI Context Collection Only When Authorized

Repomix may be used for explicit context packs only.

Preferred packs:

```text
ai_context/repomix-workspace-docs-context.xml
ai_context/repomix-workspace-context.xml
ai_context/repomix-current-task-context.xml
.codex-context/baseline/<BASELINE_ID>/repomix/*.xml
.codex-context/<PARENT_TASK_ID>/repomix-output.md or .xml
```

For task packs, prefer exact file lists from:

```text
.codex-context/<PARENT_TASK_ID>/repomix-include-candidates.txt
```

Task-specific AI Context packs must be verified after generation before use in
implementation prompts. If a task-specific pack includes broad unrelated repo
files or repo-wide token counts, do not use it for implementation prompts;
repair the script/config or use a temporary exact-file staged pack before
relying on it. Generated AI Context packs remain evidence only and must not be
staged.

Do not run Repomix or `scripts/generate_ai_context.sh` inside implementation prompts.

### 8. Snapshot Context Collection Results

After collection, record:

```text
.codex-context/<PARENT_TASK_ID>/cce-findings.md
.codex-context/<PARENT_TASK_ID>/graphify-output.md
.codex-context/<PARENT_TASK_ID>/repomix-output.md
.codex-context/<PARENT_TASK_ID>/evidence-collection-addendum.md
```

The addendum should include:

* Date/time.
* Commands run.
* Files generated.
* Files intentionally not generated.
* Whether tools failed or were skipped.
* Git status.
* Confirmation that no implementation task was executed.

### 9. Update the Task Prompt With References Only

Implementation task prompts may reference:

```text
.codex-context/<PARENT_TASK_ID>/collection_plan.md
.codex-context/<PARENT_TASK_ID>/cce-findings.md
.codex-context/<PARENT_TASK_ID>/graphify-output.md
.codex-context/<PARENT_TASK_ID>/repomix-output.md
.codex-context/baseline/<BASELINE_ID>/
```

But implementation prompts must not include commands that run:

* CCE
* Graphify
* Repomix
* LeanCTX
* AI Context generation
* MCP tools
* collect-plan
* scaffold
* context health scripts

### 10. Final Pre-Prompt Gate

Before running a task prompt, capture:

```bash
git status --short --branch
git diff --check
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
```

If the working tree is dirty, the task prompt must explicitly state whether the dirty tree is accepted and which previous task caused it.

## During Implementation Tasks

Implementation prompts must include:

* One task ID only.
* Active parent and active child.
* Strict boundaries.
* Allowed files.
* Disallowed files.
* Validation commands.
* Required final report format.
* No staging.
* No commit.
* No push.
* No context tool execution.
* No MCP tool execution unless explicitly authorized for a non-mutating context task.
* No generated prose or prose-production paths.

Implementation prompts must not include:

* CCE commands.
* Graphify commands.
* Repomix commands.
* AI Context generation commands.
* LeanCTX commands.
* MCP commands.
* collect-plan/scaffold commands.
* broad repository exploration.
* unrelated cleanup.
* task collapsing.
* parent skipping.
* commit/push instructions.

## After Each Child Task

After a child task completes:

1. Review the final report.
2. Verify changed files match the prompt allowlist.
3. Run task-specific validation commands if needed.
4. Capture final status:

```bash
git status --short --branch
git diff --check
```

5. If accepted, update the next prompt using:

   * Final report.
   * Roadmap truth files.
   * Existing context artifacts.
   * New task outputs.
6. Do not rerun full baseline unless code structure changed or context became stale.

## Before Closing a Parent Task

Before parent closeout, verify:

* All child tasks are complete.
* All expected task records are updated.
* Roadmap status matches actual completion.
* Validation files reflect the latest completed child.
* Decision log, risk register, and open questions are updated if needed.
* Generated context evidence remains untracked/ignored.
* No source-cache or external-source directories are staged.
* No context tool artifacts are mistaken for roadmap truth.

Run:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
git diff --check
git status --short --branch
git status --short -- .external_sources
git status --short --ignored -- .external_sources | head -50
```

## End-of-Phase or Major Parent Boundary Context Tasks

At the end of a parent or major phase, complete a broader context refresh.

### 1. Repo-State Snapshot

Save:

```bash
pwd
git branch --show-current
git remote -v
git log --oneline -15
git status --short --branch
git diff --stat
git diff --check
```

### 2. Roadmap Snapshot

Save:

```bash
python3 scripts/validate_roadmap.py
python3 scripts/check_enrichment.py
sed -n '1,120p' docs/roadmap/implementation_status.md
sed -n '1,160p' docs/roadmap/roadmap_governance.md
sed -n '1,140p' docs/roadmap/validation/latest_roadmap_validation.md
```

### 3. Repomix Baseline Refresh

Refresh as appropriate:

* Full repo pack at major phase boundaries.
* Docs/roadmap pack after roadmap status changes.
* Backend pack after backend parents.
* Frontend pack after frontend parents.
* Tests pack after test-contract parents.
* Phase-specific pack after parent publication and closeout.
* Task-specific pack before implementation prompts when useful.

### 4. Graphify Refresh

Run `graphify update .` at the end of a parent or phase when backend/frontend/test code changed.

Do not run Graphify update only for docs/status/context metadata changes unless the owner wants a timestamp-perfect baseline.

### 5. CCE Collection

Run CCE searches at parent or phase boundaries when:

* New modules were added.
* Call graphs changed.
* A future task depends on unfamiliar files.
* You need caller/callee context before generating implementation prompts.

Save results under:

```text
.codex-context/<PARENT_TASK_ID>/cce-findings.md
```

or:

```text
.codex-context/baseline/<BASELINE_ID>/cce/
```

### 6. MCP Snapshot

Snapshot MCP availability only.

Do not run mutation-capable MCP tools as part of baseline maintenance unless explicitly authorized.

### 7. Baseline Addendum

Write:

```text
.codex-context/baseline/<BASELINE_ID>/addendum.md
```

Include:

* What changed.
* What was refreshed.
* What was not refreshed and why.
* Generated files.
* Validation results.
* Git status.
* Boundary confirmation.

## Generated Artifact Tracking Policy

Keep these untracked/ignored unless a future explicit docs task says otherwise:

```text
.codex-context/
ai_context/
graphify-out/
.external_sources/
training/reports/
```

Never stage:

```text
.external_sources/
model artifacts
training datasets
JSONL files
raw source books
generated context packs
runtime extraction artifacts
```

unless an explicit future task authorizes a safe derived artifact.

## Standard Decision Rule

Use the smallest context refresh that matches the change:

* Documentation-only task: roadmap snapshot + docs/roadmap pack.
* Backend code task: backend pack + relevant tests pack + Graphify refresh after completion.
* Frontend code task: frontend pack + relevant tests/smoke context.
* Contract-test task: tests pack + relevant implementation files.
* Parent/phase boundary: repo-wide baseline refresh.
* Context metadata repair: delta refresh only.

For any task-specific AI Context pack, verify generated scope against the
requested file list before using it. A broad pack is a tooling defect, not task
evidence.

## Required Boundary Language for Future Prompts

Every implementation prompt must state:

```text
Do not run CCE, Graphify, Repomix, LeanCTX, AI Context generation, MCP tools, scaffold, collect-plan, or broad context collection inside this implementation task. Use only the already-generated context artifacts listed in this prompt.
```

Every context collection prompt must state:

```text
This is explicit owner-run context collection only. Do not edit app code, do not mutate roadmap status, do not mark tasks complete, do not stage, do not commit, do not push, and do not execute implementation work.
```

## Current Recommended Standard

Before running an implementation task prompt:

1. Verify roadmap truth.
2. Verify `context_pack`.
3. Run scaffold/collect-plan if missing.
4. Inspect generated CCE/Graphify/Repomix candidates.
5. Run explicit context collection only if needed.
6. Save context evidence under `.codex-context/<PARENT_TASK_ID>/`.
7. Run roadmap/enrichment validators.
8. Capture git status.
9. Generate or update the implementation prompt.
10. Keep implementation prompt free of context-tool execution commands.

At parent or phase closeout:

1. Validate roadmap and enrichment.
2. Refresh appropriate context packs.
3. Refresh Graphify only if code changed or owner requests a full baseline.
4. Run targeted CCE questions only if future implementation needs caller/callee context.
5. Save a baseline addendum.
6. Confirm ignored/generated artifacts remain unstaged.
7. Commit only source/roadmap changes that belong to the completed task.
