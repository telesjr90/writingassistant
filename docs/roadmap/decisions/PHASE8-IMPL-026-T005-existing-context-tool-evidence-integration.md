# PHASE8-IMPL-026-T005 — Existing Context-Tool Evidence Integration

## Result

T005: **complete/PASS**.

Existing Repomix, Graphify, and CCE output can now be imported through a
standard-library-only, deterministic, read-only adapter. The integration does
not install or execute a context tool. Imported output remains
`generated_evidence` and cannot become roadmap truth, project truth, Memory,
Canon, or an approved registry amendment.

## Scope decision

T005 implements import adapters, not live tool runners.

- `scripts/project_memory/context_tool_evidence.py` discovers, inspects,
  normalizes, packages, and validates existing context-tool evidence.
- `scripts/project_memory/build_context_tool_evidence.py` exposes the bounded
  CLI used for a clean-HEAD post-commit evidence run.
- Source artifacts are read-only.
- The package is written under ignored
  `.codex-context/project-memory/PHASE8-IMPL-026-T005/<RUN_ID>/` output.
- Project Memory packages below `.codex-context/project-memory/` are excluded
  from discovery to prevent recursively nested evidence.
- No new dependency, tool installation, indexing operation, collector, MCP
  server, model, network client, or retrieval system is introduced.

Read-import approval is separate from approval to install or execute Repomix,
Graphify, or CCE. T005 approves only deterministic inspection of existing
artifacts. Live execution remains unapproved.

## Existing surfaces

Tracked policy and conventions identify these generated roots:

- `.codex-context/` — task/baseline context packages and bounded CCE evidence;
- `ai_context/` — Repomix output created by tracked configuration/script
  conventions;
- `graphify-out/` — Graphify graph output.

At implementation time, `ai_context/` and `graphify-out/` were absent in this
checkout. `.codex-context/` contained only prior Project Memory evidence, which
is explicitly excluded from recursive import. Tracked Repomix, Graphify, and
CCE conventions remain available for future ignored artifacts and are covered
with temporary fixture-generated packages.

## Attribution contract

Tool attribution requires deterministic evidence:

- tool-specific manifest or metadata fields;
- a recorded collector command;
- a tracked configuration output path;
- a tracked script output convention; or
- a tracked context-execution convention combined with the expected bounded
  package structure.

A filename alone is never sufficient. Conflicting tool identities are not
resolved by precedence. Unknown and ambiguous origins are normalized as
`unknown_generated_context` and quarantined.

## Normalized envelope

Every discovered artifact receives one deterministic envelope containing, when
the source provides the information:

- adapter and envelope versions;
- tool identity and version;
- source package path and attribution evidence;
- recorded repository, branch, commit, and generation time;
- current branch and commit;
- included and excluded scope;
- bounded file inventory and declared checksum validation;
- fixed `generated_evidence` authority and trust class;
- freshness, safety, validation, eligibility, and quarantine state;
- findings and limitations.

Absent metadata remains absent. The adapter does not infer commit identity from
modification time and does not fabricate version, repository, scope, checksum,
or provenance claims.

## Freshness and eligibility

Freshness classifications are deterministic:

- `current` — full recorded commit and branch match the current repository and
  validation passes;
- `stale` — a valid recorded commit differs from current HEAD;
- `historical` — source metadata explicitly preserves past evidence;
- `unknown` — commit or branch cannot be established;
- `unusable` — metadata is malformed, contradictory, unsafe, authority-claiming,
  or checksum-invalid.

Default consumption requires safe location, strong attribution,
`generated_evidence`, current commit and branch, valid declared checksums,
bounded scope, non-authoritative behavior, and no blocking finding. Stale,
historical, unknown, ambiguous, unsafe, and provenance-incomplete artifacts
remain inventoried but quarantined.

Checksum absence is reported as a limitation. A declared checksum must validate;
absence alone is not fabricated into failure. Scope must still be explicit and
bounded for default eligibility.

## Safety contract

Discovery is limited to generated roots named by tracked policy. The adapter
rejects or quarantines traversal, external absolute paths, escaping symlinks,
special files, secrets, `.env` files, credentials, `.git`, `node_modules`,
virtual environments, caches, model files, training datasets, recursively
nested Project Memory packages, oversized metadata, checksum traversal, and
packages claiming authority.

Only bounded manifests, metadata, command records, inventories, checksum files,
summaries, and a small file-header sample required for attribution are read.
Generated source-pack bodies are not broadly loaded.

## Generated package contract

The atomic, overwrite-refusing CLI writes exactly:

1. `run-metadata.json`
2. `tool-inventory.json`
3. `artifact-inventory.json`
4. `artifact-envelopes.json`
5. `findings.json`
6. `summary.md`
7. `FILE-INVENTORY.txt`
8. `SHA256SUMS`

The package records:

```text
authority_class: generated_evidence
tool_execution_performed: false
network_access_performed: false
model_call_performed: false
registry_mutation_performed: false
```

Output is canonical JSON with stable ordering. It is assembled in a temporary
sibling directory, validated before atomic rename, cleaned after failure, and
never overwrites an existing run.

## Public APIs

- `discover_context_artifacts`
- `inspect_context_artifact`
- `normalize_context_artifact`
- `build_context_evidence_package`
- `validate_context_evidence_package`

## Validation

T005 adds 45 focused tests using temporary repositories and fixture-generated
packages only. Coverage includes strong attribution for all three supported
tools; unknown and ambiguous origin; all five freshness states; branch and
commit mismatch; checksum success, absence, and mismatch; unsafe paths,
symlinks, special files, sensitive/excluded content, and oversized metadata;
authority self-claim rejection; eligibility and quarantine; execution-approval
separation; deterministic byte-identical output; exact inventory and checksums;
atomic cleanup and overwrite refusal; source and registry immutability; JSON CLI
output; empty roots; and roadmap preservation.

The full Project Memory suite is green: 290 passed, comprising the 245
pre-existing tests plus 45 focused T005 tests. Registry, roadmap, enrichment,
JSON, checksum, and diff validation are required before the T005 commit. The
real T005 package is intentionally generated only from the clean committed T005
HEAD and remains ignored/uncommitted; its run ID is reported with post-commit
evidence rather than embedded in tracked truth before it exists.

## Registries

- T005 is complete/PASS.
- The internal context-tool evidence importer is an approved repository-owned
  tool.
- Existing Repomix and Graphify records now distinguish approved read import
  from unapproved installation/live execution.
- CCE configuration is recorded with the same separation.
- T005 depends on T004.
- The automated fixture-only validation record is accepted evidence.

The schema and registry manifest are unchanged.

## Roadmap preservation

- T006 (Serena) remains planned, contingent, and inactive.
- T007 (LlamaIndex/local embedding/Qdrant Local) remains planned, contingent,
  and inactive.
- T008–T011 remain planned.
- T006 is next in the accepted sequence but is not activated; provenance and
  benchmark approval remain prerequisites.
- The application frontier remains `PHASE8-IMPL-024-T003A`.
- PHASE8-IMPL-025 remains published/planned and inactive.
- Q151–Q154 remain open.

## Product and execution boundaries

No application backend, frontend, application data, owner-authored prose,
dataset, model artifact, dependency file, environment file, prior generated
evidence, agent configuration, plugin configuration, or MCP configuration is
modified. No context tool, collector, network operation, model call, registry
mutation, authority promotion, staging shortcut, or push is performed by the
adapter.
