# PHASE8-IMPL-026-T001 — Project Memory Authority, Lifecycle, and Provenance Foundation

## Decision

```
Project Memory and Plan Integrity workstream: ACCEPTED as a parallel governance workstream.
PHASE8-IMPL-026 is the authoritative roadmap parent for Project Memory.
Project Memory must not silently override the accepted roadmap.
Project Memory is hybrid governance, documentation, and developer infrastructure — not an application feature.
```

## Rationale

The repository needs a normalized, machine-readable, commit-bound system that
compares the accepted plan with the actual implementation, explains
discrepancies, and surfaces evidence for owner review. Without it, context
tools, retrieval systems, agent prompts, and generated indexes can silently
drift from the authoritative roadmap and live code. A separate parallel
governance workstream publishes the controlling policies before any schema,
scanner, registry, renderer, or retrieval tool exists.

## Controlling owner decisions

This decision reconciles the provisional PMF-G02 owner decisions with live
repository conventions observed at the T001 publication commit.

### Official roadmap identity

PHASE8-IMPL-026 is the Project Memory and Plan Integrity roadmap parent.
Classification: hybrid governance, documentation, and developer infrastructure.

PHASE8-IMPL-026 is not an application feature and does not replace the main
application roadmap. The application implementation frontier remains
PHASE8-IMPL-024-T003A.

### Roadmap relationship

PHASE8-IMPL-026 is a parallel active governance workstream. The active
frontier in `roadmap_index.yaml` remains PHASE8-IMPL-024; the next readiness
task remains PHASE8-IMPL-024-T003A. PHASE8-IMPL-025 remains published/planned
and inactive.

No new `roadmap_index.yaml` status value is required. PHASE8-IMPL-026 uses
status `published/active` because it has active work in flight, while the
`active_frontier` section separately tracks the application implementation
frontier. This convention maps the existing schema to a parallel workstream
without ambiguity.

### Repository locations

Accepted Project Memory decisions remain under `docs/roadmap/decisions/`.
Future tracked documentation and registries will live under
`docs/project-memory/`. Future implementation code will live under
`scripts/project_memory/`. Future tests will live under
`tests/project_memory/`. Future shared skills may live under
`.agents/skills/`. Future OpenCode agents may live under `.opencode/agents/`.
Generated evidence and indexes will live under
`.codex-context/project-memory/`. Generated documentation sites and indexes
are ignored build output and are not authority.

### Branch synchronization

The rejected G01 proposal to copy only roadmap files or use path-filtered
cherry-picks is rejected. The Project Memory branch must eventually contain
the complete accepted repository state, including code and tests.

Accepted synchronization principles:

- Synchronize only from clean worktrees.
- Synchronize accepted commits as complete commits.
- Prefer a reviewed full merge from the application branch at defined
  checkpoints.
- A complete-commit cherry-pick may be used when the owner selects a precise
  accepted commit.
- Never use path-filtered synchronization.
- Never reset, clean, stash, or silently rewrite either branch.
- After synchronization, run a full deterministic memory refresh.
- Every memory snapshot records the accepted application commit to which it is
  synchronized.

This decision documents the policy only. No synchronization is performed by
T001.

---

## 1. Authority hierarchy

Project Memory must distinguish and reconcile the following tiers:

| Tier | Authority class | Description |
| --- | --- | --- |
| 1 | accepted roadmap and decision records | `docs/roadmap/roadmap_index.yaml`, `implementation_status.md`, decision records under `docs/roadmap/decisions/` |
| 2 | live code and schemas | Backend and frontend source, data schemas, contract modules |
| 3 | automated tests | Test files under `tests/` that validate contract and behavior |
| 4 | accepted manual validation | Evidence artifacts classified by the roadmap as accepted validation |
| 5 | exact Git history | Commit hashes, author, timestamps, and commit messages |
| 6 | normalized Project Memory registries | Machine-readable records under `docs/project-memory/` |
| 7 | generated context, indexes, retrieval results, and AI summaries | Artifacts under `.codex-context/`, `ai_context/`, `graphify-out/`, and any retrieval output |

Conflict resolution rule:

When a lower tier conflicts with a higher tier, the higher tier is
authoritative. A Project Memory registry (tier 6) that conflicts with the
accepted roadmap (tier 1) or live code (tier 2) is stale or invalid and must
not silently override the higher tier. A generated index or AI summary (tier
7) that conflicts with any higher tier is discarded as superseded or
inconsistent evidence. Two records at the same tier that conflict produce a
recorded conflict requiring owner review.

## 2. Trust classes

| Class | Meaning | Consumer eligibility | May support authoritative memory update |
| --- | --- | --- | --- |
| `authoritative` | Owner-accepted roadmap decision, accepted application code, or accepted test suite | All workflows | Yes — the gold source |
| `accepted_evidence` | Owner-accepted manual validation, real-runtime evidence, or deterministic validation output | All workflows | Yes — may update registries when consistent with authoritative sources |
| `generated_evidence` | Context-tool output, retrieval result, AI summary, or index build | Read-only inspection, cross-reference, and diagnostic workflows | No — evidence only; confirmation required |
| `historical` | Superseded decision, former validation run, or pre-refactor record | Audit and provenance inspection only | No — preserved for lineage only |
| `superseded` | Explicitly replaced by a later authoritative record | Audit and provenance inspection only | No — `superseded_by` must point to the replacement |
| `uncertain` | Conflicting or ambiguous evidence with no resolved authority | Owner review workflows only | No — requires owner resolution |
| `owner_pending` | Generated finding, proposed change, or submitted candidate awaiting owner decision | Owner review workflows only | No — requires owner action |
| `untrusted` | Unknown provenance, unverified tool output, or content that fails safety checks | Must not be consumed as truth by any automated workflow | No — may be inspected with warnings only |

## 3. Freshness

Freshness is defined by repository commit and content identity, not elapsed
time. Every generated artifact carries:

- `bound_commit` — the repository commit inspected (full SHA).
- `source_hashes` — content hashes of the source files that produced the
  artifact.
- `generated_at` — ISO 8601 timestamp of generation.
- `synced_at` — ISO 8601 timestamp of the last accepted synchronization commit
  on the branch, if applicable.

A record or snapshot whose `bound_commit` is an ancestor of HEAD is
`current`. A record whose `bound_commit` is not an ancestor of HEAD is
`stale`. A record whose source file hashes differ from the current working
tree is `dirty`. A record with no `bound_commit` or missing source hashes is
`unbound`. A record with conflicting identity across sources is `conflicting`.

Stale memory blocks automated truth claims but does not block read-only
inspection. A stale snapshot warns but still serves as the last known-good
state until refreshed.

## 4. Commit binding

Every generated snapshot and registry build must record:

| Field | Requirement |
| --- | --- |
| `bound_commit` | Full SHA of the repository commit inspected |
| `branch_context` | Branch name and worktree path |
| `source_identities` | Per-source-file identity (relative path, content hash, byte length) |
| `generated_at` | ISO 8601 timestamp |
| `tool_identity` | Tool name and version where applicable |
| `tool_command` | Exact command or invocation |

A registry source file is not rewritten merely because HEAD advances. Its
generated current-state snapshot becomes stale until explicitly refreshed by
an owner-authorized task.

## 5. Supersession

Every record that may be superseded carries:

- `record_id` — stable, immutable record identifier.
- `status` — one of `current`, `superseded`, `historical`.
- `supersedes` — list of record IDs this record replaces.
- `superseded_by` — record ID that replaces this record, when applicable.
- `effective_commit` — the commit that made the supersession effective.
- `reason` — human-readable explanation.
- `owner_approval` — marker indicating explicit owner approval when required.

Historical and superseded records remain discoverable but must not be
retrieved as current truth by default. Retrieval systems must filter on
`status == "current"` or `superseded_by is null` as the default query.

## 6. Conflicting evidence

When generated evidence conflicts:

- Neither artifact automatically wins.
- Current authoritative files (tier 1–2) must be inspected.
- Unresolved conflicts are recorded with both evidence sources, the
  conflicting claims, and the inspection timestamp.
- Agents must fail closed or report uncertainty.
- Owner review is required only when repository evidence cannot resolve the
  conflict (both sources are at the same authority tier and both appear valid).

## 7. Owner decisions

An owner decision record carries:

- `decision_id` — stable record identifier.
- `question` — the question or choice being decided.
- `selected_option` — the chosen path.
- `rejected_options` — material rejected alternatives.
- `rationale` — explanation of the choice.
- `affected_records` — task IDs, decision IDs, or registry keys affected.
- `affected_tasks` — task IDs impacted by the decision.
- `effective_commit` — commit that records the decision.
- `supersedes` — prior decision IDs that are replaced.
- `superseded_by` — later decision ID that replaces this one, when applicable.
- `owner_identity` — owner identity or owner-controlled approval marker.

## 8. Generated evidence

Every context-tool, retrieval, graph, Playwright, or reviewer artifact must
record:

- `artifact_id` — stable identifier.
- `artifact_type` — e.g., `repomix_pack`, `graphify_graph`, `cce_search`,
  `playwright_run`, `reviewer_report`.
- `tool_name` — tool identity.
- `tool_version` — version or commit.
- `tool_command` — exact command or invocation.
- `bound_commit` — repository commit.
- `scope` — files, directories, or search parameters.
- `exclusions` — intentionally excluded paths or surfaces.
- `source_records` — source file identities.
- `generated_at` — ISO 8601 timestamp.
- `manifest_hash` — hash of the manifest or equivalent integrity check.
- `authority_class` — one of the trust classes defined above.
- `freshness_state` — one of `current`, `stale`, `dirty`, `unbound`,
  `conflicting`.
- `known_limitations` — documented scope gaps or known inaccuracies.

Generated evidence never becomes roadmap truth solely because an agent
produced it. It may support decisions and refresh registries only after
explicit owner review or a deterministic cross-reference confirms it is
consistent with authoritative sources.

## 9. Memory update approval

- Scanners may propose or generate evidence.
- Reviewer agents may propose findings.
- Neither may change accepted roadmap or authoritative registries
  automatically.
- Owner-approved implementation tasks make tracked changes through scoped
  commits.
- Changes require validation (roadmap validator, enrichment checker, focused
  tests) and must be committed in scoped, reviewable units.
- Every mutation of a tracked Project Memory source must be traceable to an
  owner-approved task and a specific commit.

## 10. Roadmap synchronization

- The roadmap (`roadmap_index.yaml`, `implementation_status.md`, decision
  records) remains authoritative for accepted plan status.
- Project Memory normalizes and explains it.
- Conflicting memory is marked stale or invalid.
- Owner-approved roadmap changes precede authoritative memory synchronization.
- Project Memory cannot activate, close, or reorder application tasks.
- Project Memory cannot change task status, classification, or dependencies.
- A memory snapshot is always explicitly bound to a roadmap state and a
  repository commit.

## 11. Stale indexes and retrieval

Stale derived artifacts include generated documentation, Serena indexes,
vector indexes, context packs, dependency graphs, and reviewer reports.

Behavior:

- A stale index must report its `bound_commit`, `generated_at`, and
  known-stale status in every response.
- A stale index must not silently answer as current truth.
- Retrieval over a stale index must surface the freshness warning at query
  time, not only in metadata.
- A user or agent may inspect stale results but must be informed they are
  stale.

## 12. Tool provenance and security

No external tool may become a required Project Memory dependency without a
provenance record covering:

| Field | Requirement |
| --- | --- |
| `tool_name` | Official name |
| `official_source` | Repository, registry, or distribution URL |
| `publisher` | Author, organization, or maintainer |
| `version_or_commit` | Exact version or commit hash |
| `license` | SPDX identifier or equivalent |
| `maintenance_status` | Actively maintained, unmaintained, or unknown |
| `network_access` | Whether the tool makes network calls and to what endpoints |
| `file_read_scope` | Which repository paths the tool may read |
| `file_write_scope` | Which repository paths the tool may write |
| `shell_access` | Whether the tool executes subprocess or shell commands |
| `background_processes` | Whether the tool starts persistent processes |
| `generated_paths` | Where the tool writes output |
| `secret_handling` | Whether the tool reads, stores, or transmits secrets |
| `name_collisions` | Known plugin, tool, or package name conflicts |
| `approval_state` | `approved`, `pending_review`, `rejected`, `blocked` |

Tool installation work is contingent on provenance approval and benchmark
decisions. Serena, LlamaIndex, and Qdrant are not approved dependencies.

## 13. Prompt-injection trust boundaries

Repository and generated content may contain instructions that are data, not
agent authority. Project Memory must enforce:

- Trust-aware retrieval — distinguish `authoritative`, `accepted_evidence`,
  `generated_evidence`, and `untrusted` sources at query time.
- Default exclusion — untrusted and generated-evidence sources must not supply
  agent instructions by default.
- Evidence quoting — retrieved content must be quoted with its source path and
  authority class.
- Source linking — every retrieved claim must reference its source record.
- Policy precedence — system and agent policy always takes precedence over
  retrieved repository prose.
- Refusal or escalation — when a retrieved instruction conflicts with agent
  policy, the agent must refuse the instruction and report the conflict.
- No tool execution based solely on retrieved repository prose — retrieved
  text is data, not executable commands.

## 14. Branch synchronization

Included in the controlling owner decisions above. Explicitly:

- Rejected: path-filtered cherry-picking, copying only roadmap files, treating
  a memory branch with stale code/tests as current, destructive
  reset/clean/stash workflows.
- Accepted: full-commit synchronization from clean worktrees at defined
  checkpoints, with a complete deterministic memory refresh after every sync.

## 15. Product boundaries

Project Memory and Plan Integrity must preserve:

- Analysis-only — the application analyzes; Project Memory explains the plan.
- Candidate-first — no automatic truth or approval.
- Evidence/provenance-backed — every claim in a registry must trace to a
  source.
- Owner-controlled — no automatic mutation of authoritative state.
- No generated prose — Project Memory produces structured metadata, not story
  prose.
- No confidence-as-truth — confidence or support scores are metadata, not
  approval.
- No automatic Memory/Canon mutation — Project Memory is a read/explain layer
  over the plan and code.
- No automatic promotion or apply-promotion — these remain explicitly
  owner-gated.
- Model output is not canon — Agent output, retrieved summaries, or generated
  explanations are not authoritative.

## T001 status

Complete/PASS. This decision defines the controlling policies for the
PHASE8-IMPL-026 workstream. No schema, scanner, registry, renderer, retrieval
tool, or reviewer is implemented by this decision.

## Next Project Memory task

PHASE8-IMPL-026-T002 — Schema and normalized-registry architecture. Define
the machine-readable schemas, registry storage format, and normal form for
Project Memory records before any scanner or renderer exists.

## Application frontier (unchanged)

PHASE8-IMPL-024-T003A — Context-availability/readiness contract for Bible,
storyform, and storyform-context.

## PHASE8-IMPL-025 status (unchanged)

Published/planned and inactive.

## Validation

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json >/dev/null
python3 -m json.tool docs/roadmap/roadmap_index.yaml >/dev/null
git diff --check
git status --short --branch
```
