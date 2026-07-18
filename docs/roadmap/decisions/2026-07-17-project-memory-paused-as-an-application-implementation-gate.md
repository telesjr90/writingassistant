# Project Memory Paused as an Application Implementation Gate

## Decision record

- Date: 2026-07-17
- Status: accepted/current
- Decision type: owner-authorized repository implementation policy

## Decision

Implementation-only mode is active.

Project Memory remains preserved in the repository, but it is paused and
nonblocking for ordinary application implementation, validation, acceptance,
and closeout. Project Memory freshness, supervision, handoffs, Project Source
rotations, continuation packages, tests, scripts, validators, publication
state, and the Project Memory GitHub workflow are not application gates while
this decision remains current.

Plan Integrity and execution routing are likewise not application gates while
Project Memory is paused. Ordinary application agents must not invoke Project
Memory scripts or tests or attempt to repair Project Memory failures.

Application implementation authority is, in order:

1. current explicit owner decisions;
2. current roadmap and task documents;
3. tracked application code, schemas, fixtures, and tests;
4. saved context-tool outputs as non-authoritative navigation aids; and
5. focused direct file reads.

Application acceptance is based on the current task requirements, relevant
application tests, required integration or runtime evidence, reviewed file
scope, and repository state.

## Context tools

Context tools remain active under the repository's existing mode separation.
Repomix, Graphify, LeanCTX, `scripts/generate_ai_context.sh`, and
`scripts/context_health_check.sh` may run only in an explicitly authorized
context-generation task. Ordinary implementation agents consume saved context
outputs and do not regenerate them. Generated context remains supporting
evidence, never authority.

## Preserved boundaries

Product and Git safety are unchanged:

- the application remains analysis-only;
- presentation remains candidate-first, evidence/provenance-backed, and
  owner-controlled;
- generated story prose is prohibited;
- automatic promotion and automatic apply-promotion are prohibited;
- automatic Memory/Canon mutation is prohibited;
- generated or model output never becomes project truth automatically;
- destructive Git operations are prohibited; and
- staging, committing, or pushing requires explicit owner authorization.

## Historical and roadmap preservation

Historical Project Memory records, task results, frontier identities, commit
bindings, workflow runs, failures, and acceptance evidence remain historically
accurate. This decision does not rewrite those records.

This decision creates no new task. It changes no task status, dependency,
application frontier, structured routing assignment, or completed-task record.
It pauses only the current applicability of Project Memory, Plan Integrity, and
execution routing as ordinary application gates.

Project Memory may still be consulted, maintained, published, or used for
governance when the owner explicitly requests that bounded work. Reactivating
Project Memory as an application implementation, validation, acceptance, or
closeout gate requires a later explicit owner decision.
