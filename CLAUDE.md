# Claude client guidance

This file is a thin Claude-specific overlay. It does not define product scope,
the current frontier, task status, dependencies, or acceptance.

Before acting, follow this authority order:

1. [`AGENTS.md`](AGENTS.md) for repository implementation, safety, validation,
   file-scope, and Git policy;
2. current explicit owner decisions; and
3. current roadmap/task authority, starting with
   [`docs/roadmap/roadmap_index.yaml`](docs/roadmap/roadmap_index.yaml) and the
   active task, inventory, and enrichment records it references.

[`PRODUCT.md`](PRODUCT.md) is the durable human-readable product/MVP contract.
Accepted decision records own their scoped decisions. Historical plans,
completed task records, generated context, client configuration, and old “next”
statements are reference evidence only and do not override the authority above.

## Product boundary

The application is local-first, owner-controlled, and analysis-only. It may
store, edit, and organize owner-authored prose and project materials. Claude
must never write, rewrite, continue, imitate, polish, improve, expand, outline,
draft, revise, or otherwise generate story prose.

Use the standard refusal message when applicable:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

Analysis must remain candidate-first and evidence/provenance-backed. Model,
tool, extractor, rubric, NotebookLM, and OMI output is not approved truth.
Confidence, queue presence, review status, and promotion records are not Canon.
Only the separate implemented apply-promotion workflow may update approved
project-local Memory/Canon, and only after explicit owner approval, destination
choice, blocker validation, and final confirmation. Never apply or promote
automatically.

## Task execution

- Use the exact task scope, allowlist, preflight, and validation commands.
- Do not infer implementation eligibility from this file or from
  `docs/master_plan.md`.
- Preserve unrelated owner changes and stop on an unsafe scope conflict.
- Do not stage, commit, push, amend, rebase, reset, clean, restore, or stash
  unless the owner explicitly authorizes the exact action.
- Do not call live models, external integrations, Story Check, extraction
  tools, training, or Dramatica-specific logic unless the task explicitly
  authorizes it.
- Do not use client-specific agent or skill routing to override `AGENTS.md` or
  current roadmap/task authority.

## Context and mapping tools

Repomix, Graphify, LeanCTX, MCP context tools, and context-generation scripts
may be used only in an explicitly authorized context-generation task and only
within that task's output scope. They are not automatic navigation,
implementation, validation, acceptance, or closeout steps.

For ordinary implementation and documentation tasks, use the focused direct
reads and exact searches authorized by the task. Existing saved context may be
used only as non-authoritative navigation evidence when `AGENTS.md` and the task
permit it.

## Documentation work

Documentation-only tasks do not authorize application code, tests,
dependencies, datasets, runtime project fixtures, training records, model
artifacts, or live runtime/model execution. Report exactly what changed, the
validation performed, deferred work, repository state, and whether any Git
staging or publication occurred.

## Dramatica-flow boundary

The app-owned `dramatica_flow_informed_rubric` is the approved application/MVP
boundary for permitted analysis-only concepts, rules, and structural reasoning
from the upstream reference. It is not evidence that the external
`dramatica_flow` runtime ran. That runtime is not MVP-required, and any future
integration requires separate explicit owner authorization and an analysis-only
safety review.
