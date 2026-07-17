# PHASE8-IMPL-026-T011 Operational Maintenance — Project Memory Gate Decoupling and GitHub Handoff

## Result

Accepted/complete as PASS. This is one owner-authorized bounded operational-
maintenance event under the existing T011 event-driven procedure. It is not a
new T013 roadmap child, does not reopen T012, creates no Project Memory
implementation frontier, and changes no application task, dependency, status,
frontier, code, test, or data.

The application frontier remains `PHASE8-IMPL-024-T003B`, active/in progress.
`PHASE8-IMPL-024-T003C` remains planned and dependency-ineligible. This event
does not complete T003B or activate T003C.

## Accepted gate profiles

Application implementation, task closeout, and governance use separate
profiles. Implementation supervision retains normal repository, task,
dependency, frontier, routing, product-safety, changed-path, validator, and
evidence gates. It may report `READY_WITH_ADVISORIES` with
`project_memory_commit_lag_application_only` only when the accepted package is
an ancestor on the same branch, the same task remains eligible and unchanged,
all intervening paths are bounded application code or directly related tests,
Plan Integrity has no blocker, and no authority, routing, registry, schema,
workflow, Project Instructions, shared skill/agent, task, dependency,
frontier, or Project Memory protocol path changed. Stale memory is never called
`FRESH`, and implementation mode never performs a full refresh.

Closeout remains exact-commit strict. It requires explicitly synchronized task
and dependency state, expected frontier advancement, passing scoped tests,
clean Git state, zero Plan Integrity blockers, and exact-commit `FRESH`
snapshot/report/render/quality/semantic/authority/inventory/checksum evidence.
Governance is likewise exact-commit strict and additionally fails closed on
authority, routing, schema, registry, guidance, workflow-security, task,
dependency, or source-generation-policy conflict. Validation never performs
the synchronization it checks.

## Deterministic supervisor and handoff

`scripts/project_memory/supervise.py` is the single standard-library core. It
extends the T011 status/refresh system and T012 routing resolver rather than
duplicating them. It accepts only enumerated modes, validated task IDs, and an
optional bounded evidence JSON file; it never accepts a shell command from CLI
arguments, workflow inputs, PR text, branch names, or repository content.

Every evaluated run produces generated evidence under
`.codex-context/project-memory/handoff/<task>/<full-sha>/<mode>/` with canonical
JSON, bounded Markdown, and SHA-256 coverage. Publication is atomic,
overwrite-refusing for different same-binding content, symlink/path-escape
safe, stably ordered, network-independent, and free of automatic tracked-state
or Git mutation. The payload explicitly denies task acceptance and authority,
application, Git, candidate, promotion, apply-promotion, Memory/Canon, and
frontier mutation.

## GitHub publication boundary

The existing Project Memory workflow is extended. Pull requests and pushes use
implementation mode by default; manual dispatch may choose implementation,
closeout, or governance with a validated task ID. The supervision job has
read-only contents permission and publishes the complete handoff artifact and
step summary. A separate same-repository-only comment job has only contents
read and pull-request write permission, does not check out PR code, and updates
one comment identified by `<!-- project-memory-supervision -->`. Comment
failure is advisory. There is no PAT, `pull_request_target`, repository write,
commit, push, arbitrary PR command, secret-bearing step, or automatic roadmap
mutation.

## ChatGPT and Project Sources

A live GitHub repository/PR at an exact SHA plus a deterministic passing
handoff may satisfy ordinary same-task application binding. Tracked files
remain authority; checks, artifacts, comments, summaries, and local handoffs
remain generated evidence. Mid-task 25-file Project Source rotations are not
required for qualifying application-only commits. Local unpushed commits use
the same local handoff. New branches/tasks/owner decisions or changes to
routing, authority, schemas, Project Instructions, shared guidance, workflows,
or Project Memory protocols require strict rebinding. Project Sources remain a
fallback/bootstrap mechanism and are still required for a new full authority
baseline. Conflicts fail closed.

## Preserved boundaries

No generated evidence may activate, complete, accept, reorder, or mutate an
application task or dependency. Passing code tests are not acceptance. No
automatic candidate promotion, apply-promotion, approved Memory/Canon mutation,
story-prose generation, commit, or push is authorized. T012 remains closed and
its routing registry remains the current application executor authority.
