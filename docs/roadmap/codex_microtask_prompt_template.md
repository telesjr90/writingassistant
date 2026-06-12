# Codex Micro-Task Prompt Template

Use this shape for strict Codex implementation tasks.

## Task ID

`PHASE7-IMPL-000-T000`

## Goal

State the single deliverable Codex must complete.

## Context

- Current track:
- Parent task:
- Relevant roadmap source:
- Required files to read:

## Allowed Files to Modify

- `path/to/file`

## Must Not Modify

- Application runtime code outside the allowed list.
- `backend/**` unless explicitly allowed.
- `frontend/**` unless explicitly allowed.
- `tests/**` unless explicitly allowed.
- Dependency files unless explicitly allowed.
- Project prose.
- Training data, generated context packs, OMI implementation files, and model artifacts.

## Product Boundaries

- No generated prose.
- No rewriting.
- No continuation.
- No imitation.
- No polishing.
- No prose improvement.
- No silent promotion to project truth.
- No model calls unless explicitly allowed.

## Required Validation

- `python scripts/validate_roadmap.py`
- Additional focused command, if task-specific:

## Final Response Format

- Result: PASS, PARTIAL, or BLOCKED.
- Files changed:
- Summary:
- Validation run and result:
- Deferred work:
- Confirmation that nothing was staged, committed, or pushed.

