# PHASE8-IMPL-026-T002 — Schema and Normalized-Registry Architecture

## Decision

```
JSON as the canonical tracked Project Memory registry format.
JSON Schema Draft 2020-12 as the formal machine-readable data contract.
One schema bundle with typed $defs; 12 separate normalized tracked registry files.
Dependency-free standard-library Python validator.
Tracked source registries separate from generated commit-bound snapshots.
Stable namespaced identifiers; enforced trust classes, lifecycle values, and cross-record references.
```

## Result

Complete/PASS.

## Rationale

Project Memory needs a deterministic, tracked, extensible data model before any scanner,
renderer, or retrieval tool exists. JSON was chosen over YAML as the canonical tracked
format because it:
- requires no new dependency (Python standard-library `json` module);
- is directly compatible with JSON Schema Draft 2020-12;
- provides deterministic serialization;
- has exact value types (no ambiguous `yes`/`no`/`on`/`off` coercion);
- enables straightforward automated validation.

A single schema bundle with typed `$defs` was chosen over many small schema files because
it:
- keeps the formal data contract in one reviewable location;
- allows each `$def` to reference shared types (trust classes, lifecycle, source locator, provenance);
- avoids proliferation of schema files before scanners and renderers exist.

## JSON as Canonical Tracked Registry Format (Q149 resolved)

Q149 asked: "What exact registry storage format should Project Memory use?"

Resolution: **JSON** as the canonical tracked Project Memory registry format.

Reasons:
- Python standard-library parsing (`json` module);
- direct compatibility with JSON Schema Draft 2020-12;
- deterministic serialization (sorted keys, no trailing comma ambiguity);
- no new YAML dependency (avoiding PyYAML installation and its associated C-extension issues);
- exact value types (booleans, integers, floats are unambiguous);
- easier automated validation (type checking does not require YAML schema coercion).

Human-readable Markdown will be generated later by T004 (MkDocs rendering) and is not
an authority source by itself.

## Schema Decomposition (Q150 resolved)

Q150 asked: "What schema decomposition and normal form should Project Memory registries adopt?"

Resolution: **One JSON Schema Draft 2020-12 bundle with typed `$defs`; 12 separate
normalized tracked registry files; one registry manifest; one dependency-free
standard-library Python validator.**

The schema bundle at `docs/project-memory/schemas/project-memory.schema.json` defines
all record types in `$defs`:
- `StableId`, `GitSha`, `IsoTimestamp` — shared value types;
- `TrustClass`, `LifecycleStatus`, `TaskLifecycleStatus`, `DecisionLifecycleStatus` — enumerations;
- `SourceLocator`, `ProvenanceMetadata`, `LifecycleMetadata` — shared metadata records;
- `BaseRecord` — common fields for all records;
- `ProjectRecord`, `FeatureRecord`, `BoundaryRecord`, `TaskRecord`, `DecisionRecord`,
  `CapabilityRecord`, `AssetRecord`, `EvidenceRecord`, `DependencyRecord`,
  `ToolRecord`, `OwnerDecisionRecord` — typed record schemas;
- `RegistryManifest`, `RegistryContainer`, `GeneratedSnapshotManifest`,
  `ValidationFinding` — infrastructure schemas.

Each registry file is a `RegistryContainer` with `registry_type`, `schema_version`,
and `records`.

## Tracked Source vs. Generated Snapshot Separation

**Tracked normalized registries** (`docs/project-memory/registries/`):
- express accepted normalized records;
- carry source locators and authority/lifecycle metadata;
- are changed only through owner-approved implementation tasks;
- do not need to be rewritten solely because repository HEAD advances.

**Generated commit-bound snapshots** (future `.codex-context/project-memory/`):
- bind tracked registries and discovered repository state to an exact commit;
- carry `bound_commit`, source hashes, tool/version, generation time, scope, exclusions, freshness;
- are generated evidence (`generated_evidence`), not `authoritative`;
- are not created in T002.

The generated snapshot manifest schema is defined in the schema bundle but no
snapshot is instantiated by T002.

## Stable ID Rules

Stable namespaced identifiers follow the pattern:

```text
project:<slug>
feature:<slug>
boundary:<slug>
task:<authoritative-task-id>
decision:<authoritative-decision-id>
capability:<slug>
asset:<slug>
evidence:<slug>
dependency:<slug>
tool:<slug>
owner-decision:<slug>
```

Requirements enforced by the validator:
- IDs are unique across all registries;
- IDs are immutable after acceptance;
- Display labels may change without changing IDs;
- Task records preserve the authoritative roadmap task ID;
- Decision records preserve the authoritative decision identifier and path;
- Records may reference other records only by stable ID;
- Unknown references are validation failures;
- IDs cannot contain path traversal, whitespace, control characters, absolute paths,
  or platform-specific separators.

## Registry Decomposition

12 tracked registry files plus the manifest:

| Registry | Record type | Record count (seed) |
| --- | --- | --- |
| `manifest.json` | manifest | 1 (declaration set) |
| `projects.json` | project | 2 |
| `features.json` | feature | 5 |
| `boundaries.json` | boundary | 10 |
| `tasks.json` | task | 7 |
| `decisions.json` | decision | 2 |
| `capabilities.json` | capability | 5 |
| `assets.json` | asset | 4 |
| `evidence.json` | evidence | 3 |
| `dependencies.json` | dependency | 4 |
| `tools.json` | tool | 6 |
| `owner-decisions.json` | owner_decision | 6 |

Total: 56 seed records across 12 registries.

## Validator Contract

`scripts/project_memory/validate_registries.py`:
- Uses only Python standard-library modules (`json`, `os`, `re`, `sys`, `pathlib`);
- Discovers registry files through `manifest.json`;
- Parses all registry JSON files;
- Enforces expected top-level shapes;
- Enforces schema version `1.0.0` and architecture version `1.0.0`;
- Enforces unique global IDs across all registries;
- Enforces record type matches the containing registry;
- Enforces the eight exact T001 trust classes;
- Enforces lifecycle values;
- Validates repository-relative source locators (rejects traversal, absolute paths);
- Validates full Git SHAs where a field requires one;
- Validates ISO 8601 timestamps where a field requires one;
- Validates all cross-record references (supersedes, superseded_by, owner_decision_ref,
  parent_task_id, depends_on, source_id, target_id);
- Detects direct task dependency cycles;
- Validates supersession symmetry;
- Rejects current records that are simultaneously superseded;
- Ensures generated and untrusted records are not default-authority eligible;
- Verifies manifest registry filenames exist;
- Rejects undeclared registry files;
- Returns deterministic, sorted findings;
- Exits zero only when there are no errors;
- Supports human-readable default report;
- Supports `--json` for machine-readable output.

The validator does not call Git, network services, models, MCP servers, package
managers, or external tools.

## Representative Seed Scope

The seed registries contain a minimal representative set, not a complete repository
inventory. Only facts provable from accepted current files are included.

Key seed design choices:
- PHASE8-IMPL-025 remains published/planned and inactive;
- T003A is the application frontier;
- Elena assets are mixed-role (historical/training/evaluation), not obsolete;
- Princess and the Pea is a committed fixture, not a durable owner-approved fixture;
- `generated_evidence` records in the evidence registry document generated context
  artifacts without claiming authority;
- No Serena, LlamaIndex, Qdrant, or other proposed tools are marked as installed;
- External tool provenance fields may remain `owner_pending` or `uncertain`;
- OMI content under `projects/example/omi/` is not inspected or registered.

## No External Dependency Installation

No JSON Schema package, YAML parser, or other external dependency was installed.
The schema file is the formal machine-readable contract. The repository-owned
validator enforces all critical structural and cross-registry invariants using
only Python standard-library modules. A later task may approve a third-party
JSON Schema implementation after provenance review.

## No Scanners or Repository Discovery Yet

T002 provides the schema and normalized-registry architecture only. No read-only
deterministic scanners, repository walkers, or file-inventory collectors were implemented.
Scanner implementation is deferred to T003.

## No Generated Snapshot Yet

The generated snapshot manifest schema is defined (`GeneratedSnapshotManifest` in the
schema bundle) but no snapshot JSON file was created. Snapshot generation requires
scanners (T003) to produce bound-commit evidence.

## No Renderer

No MkDocs, Markdown, or HTML renderer was created. Human-readable Project Memory
documentation is deferred to T004.

## No Retrieval or AI Agents

No retrieval system, embedding model, vector store, agent skill, or MCP server was
implemented. All retrieval and agent integration is deferred to T005-T008.

## Open Questions

### Resolved

- **Q149** — canonical registry format: **JSON**.
- **Q150** — schema decomposition: **one JSON Schema Draft 2020-12 bundle with typed `$defs`,
  12 separate normalized tracked registry files, one manifest, one dependency-free validator**.

### Remaining

- **Q151** — convergence criteria beyond the structural foundation:
  not prematurely resolved. T003 will define exact convergence criteria for
  plan-vs-implementation comparison.
- **Q152** — Serena adoption criteria: not prematurely resolved.
  Requires T005 (context-tool integration) and provenance/benchmark approval.
- **Q153** — embedding model selection: not prematurely resolved.
  Requires T007 (LlamaIndex pilot) after deterministic foundation exists.
- **Q154** — synchronization cadence: not prematurely resolved.
  T001 defined the complete-commit synchronization policy; operational cadence
  is deferred to T011.

## Risk Handling

T002 provides real mitigations but does not falsely close risks:

| Risk | T002 Impact |
| --- | --- |
| Competing authority systems | Mitigated by schema and trust-class enforcement. Not closed — remains active until retrieval implementation. |
| Stale memory | Remains active until T003 snapshots and freshness checks. |
| Generated-evidence promotion | Mitigated by schema/validator (generated records cannot claim authoritative). Not closed. |
| Prompt injection | Remains active until retrieval implementation (T008). |
| Tool provenance | Remains active. Tools registry captures known state; external provenance fields remain `owner_pending`/`uncertain`. |
| Partial branch synchronization | Governed by T001; operational enforcement remains future. |
| Duplicate context systems | Remains active. Registries provide a single normal form but don't prevent multiple tools from producing conflicting evidence. |
| Model-generated amendments | Remains active. Schema enforcement prevents stale data but doesn't prevent model-generated proposals. |

## Next Task

`PHASE8-IMPL-026-T003` — Deterministic scanners and convergence. Will implement
read-only deterministic scanners that inspect repository state (code, tests,
roadmap decisions, task records, enrichment data) and produce normalized
evidence records. Define convergence criteria that detect when plan and
implementation agree, disagree, or have insufficient evidence.

## Unchanged

- Application frontier remains: `PHASE8-IMPL-024-T003A`.
- PHASE8-IMPL-025 remains published/planned and inactive.
- No external tool pilot is active.
- Broad owner acceptance and MVP readiness remain governed by the application roadmap.
- T003A is the immediate next implementation task for the application.
- T002 status: complete/PASS.

## Validation

```bash
python3 -m py_compile scripts/project_memory/__init__.py scripts/project_memory/validate_registries.py
python3 scripts/project_memory/validate_registries.py
python3 scripts/project_memory/validate_registries.py --json
python3 -m pytest tests/project_memory/test_validate_registries.py -q -p no:cacheprovider
python3 -m json.tool docs/project-memory/schemas/project-memory.schema.json >/dev/null
find docs/project-memory/registries -maxdepth 1 -type f -name '*.json' -print0 | while IFS= read -r -d '' file; do python3 -m json.tool "$file" >/dev/null; done
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json >/dev/null
python3 scripts/validate_roadmap.py
python3 scripts/check_enrichment.py
git diff --check
```
