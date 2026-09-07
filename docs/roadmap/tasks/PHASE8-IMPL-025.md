# PHASE8-IMPL-025 — Layered Analysis Architecture and Tool Integration Expansion

## Status

Published/active. T001-T003 implementation milestones and the T005 contract are
complete/PASS. The T004 and T006 implementation commits remain accepted, but
their overall external-tool completion gates remain open: T004 requires real
expanded BookNLP execution through the current layered path, and T006 requires
a verified official Subtxt runner plus current-layer real execution. T006 is
the immediate active execution frontier. T007 and T008 remain planned and not
begun.

Activation had one explicit boundary: `PHASE8-IMPL-024` fully complete/closed
with application closeout validation PASS. That boundary is satisfied by the
accepted PHASE8-IMPL-024-T008 closeout, so this parent is published/active.
Project Memory is not an activation gate while the accepted 2026-07-17 pause
decision remains current. The current application frontier is
`PHASE8-IMPL-025-T006`: application adapter implementation accepted; real
official-runtime connection and execution pending. T007 and T008 remain
planned/not begun. T004's separate current-layer real BookNLP validation debt
must be satisfied before downstream acceptance relies on that contributor.

The owner-authorized T001 context prerequisite is satisfied by the generated,
read-only supporting pack at
`.codex-context/PHASE8-IMPL-025/T001-tool-role-layered-orchestration/20260830T175126Z/`.
The pack is navigation evidence only, is not roadmap authority, and is not a
tracked deliverable.

Controlling decision:
`docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`.

Controlling T001 contract:
`docs/roadmap/decisions/PHASE8-IMPL-025-T001-tool-role-and-layered-orchestration-contract.md`.

## Goal

Expand the implemented independent-adapter/fusion/candidate-review foundation
into a layered-plus-parallel architecture with stable source identity,
immutable run evidence, evidence-bounded interpretation, semantic guardrails,
full authorized Subtxt runtime integration, richer BookNLP extraction, a full
NCP gateway, bounded owner-correction workflows, and isolated end-to-end
validation.

## Current foundation, not completion

The following remain accepted historical or implementation foundation within
their recorded scopes and must not be erased or described as failed:

- real local spaCy extraction;
- real Ollama/qwen3:8b structured candidate extraction;
- real Story Check execution through the analysis engine and Ollama, with the
  P0 grounding repair complete/PASS and available for layered reuse;
- real BookNLP character/location findings and compatibility repair;
- explicit owner-selected NCP JSON validation/import to candidate-only
  findings;
- app-owned `subtxt_informed_rubric` and
  `dramatica_flow_informed_rubric` contracts, evaluators, adapters, and manual
  validation;
- deterministic normalized IDs, fingerprints, duplicate/conflict/uncertainty
  metadata, candidate-only persistence, and grouped review;
- `PHASE8-IMPL-023-T023A` and T023B.

Persisted findings remain pending, unapproved, promotion-ineligible,
candidate-only, and non-canon. The app-owned Subtxt-informed rubric remains a
valid fallback and supplemental semantic guardrail. It is not official/full
Subtxt runtime execution.

## Accepted architecture

The target layers are:

0. Owner source and source identity.
1. Raw extraction.
2. Raw artifact and evidence ledger.
3. Interpretation and diagnostics.
4. Grounding and semantic guardrails.
5. Fusion.
6. Candidate persistence and owner review.
7. Explicit promotion and approved context.
8. NCP gateway.

Independent contributors may run in parallel when their inputs are satisfied.
Sequential consumers may run only after their declared source, artifact,
normalized-evidence, or approved-context dependencies exist. No adapter may
silently substitute raw text for a normalized-evidence dependency or silently
fall back across roles.

## Child task hierarchy

Indexed workstreams are registered as `T001` through `T012`. Lettered slices
below are bounded publication/execution slices and remain planned until a
future task explicitly activates them.

| Required workstream | Indexed owner |
| --- | --- |
| A — Tool-role and layered orchestration | T001 |
| B — Source identity, run manifest, and evidence ledger | T002-T003 |
| B2 — Live-run API/control plane and persisted-data compatibility | T003F-T003G |
| C — BookNLP extraction expansion | T004 |
| D — Full Subtxt runtime integration | T005-T006 |
| E — Evidence-bounded Ollama and Story Check | T007 |
| F — Cross-adapter semantic guardrails | T008 |
| G — Project-level narrative diagnostics | T009 |
| H — Full NCP gateway | T010 |
| H2 — NCP and diagnostics owner UI | T010H |
| I — Candidate review lifecycle and owner live-run workflow | T011 |
| J — End-to-end layered validation | T012 |

### PHASE8-IMPL-025-T001 — Tool-role and layered-orchestration contract

Status: `complete/PASS`.

- `T001A` — Adapter-role and input/output dependency contract.
- `T001B` — Sequential/parallel execution graph and activation modes
  (automatic only where explicitly safe, explicit owner request, imported
  artifact, normalized-evidence consumer, or approved-context consumer).
- `T001C` — Tool identity, user-facing labels, provenance identity, and
  official-versus-app-owned separation.
- `T001D` — Fail-closed behavior, partial-run reporting, unsupported-output
  lineage, and no-silent-fallback contract validation.

Roles must distinguish evidence producers, interpretation consumers,
semantic guardrails, fusion, review, promotion, and gateway operations.

Closeout/contract:
`docs/roadmap/decisions/PHASE8-IMPL-025-T001-tool-role-and-layered-orchestration-contract.md`.

### PHASE8-IMPL-025-T002 — Source identity and AnalysisRunManifest

Status: `complete/PASS`; depends on T001. Closeout:
`docs/roadmap/decisions/PHASE8-IMPL-025-T002-source-identity-and-analysis-run-manifest.md`.

- `T002A` — Stable project/document/chapter/scene identity and source
  ownership/type contract.
- `T002B` — Exact owner-input snapshot, content hash, source map, and
  token/character/line offset contract.
- `T002C` — Immutable `AnalysisRunManifest` schema: run ID, source IDs/hashes,
  adapter/model/tool versions, configuration, feature flags, operations, and
  dependency graph.
- `T002D` — Rejected, quarantined, unverified, and partial-output lineage.
- `T002E` — Deterministic contract tests and documentation closeout.

### PHASE8-IMPL-025-T003 — Immutable raw artifact and evidence ledger

Status: `complete/PASS`; depends on completed/PASS T002. Accepted implementation
commit: `95a406e3f97899d83c00ff1cdeb229ced1400cef`.

- `T003A` — Immutable raw-artifact reference, file-hash, bundle-hash, and
  manifest linkage contract.
- `T003B` — Exact excerpt/offset evidence records and transformation lineage.
- `T003C` — Adapter output, model response, rejection, quarantine, and
  verification ledger states.
- `T003D` — Retention, cleanup, privacy, and owner-controlled deletion policy;
  cleanup must not break surviving provenance.
- `T003E` — Storage/path safety, replay, tamper, and partial-run tests.
- `T003F` — Application-owned layered live-analysis API and control plane after
  T003A-T003E define the shared contracts. Extend the canonical OMI route
  family with preflight, supported adapter/tool selection, run submission,
  stable run identity, status/result retrieval, supported timeout and
  cancellation semantics, idempotency, partial/unavailable states, controlled
  errors, provenance, and manifest/evidence-ledger references. Outputs remain
  candidate-only and cannot automatically promote, apply-promotion, mutate
  Memory/Canon, or generate prose.
- `T003G` — Existing persisted-data compatibility before production write
  cutover. Detect schema/version state for candidates, raw artifacts,
  grouped-review records, promotion audit records, manifests, and ledgers;
  prove deterministic reads or an explicit migration across old, new, mixed,
  and malformed fixtures; preserve provenance, idempotency, rollback or a
  non-destructive policy, and owner-visible continuity. Compatible reads need
  no new owner decision; physical migration that changes owner-visible stored
  structures does.

Raw artifacts remain support data, not candidates, canon, approval, promotion,
or training data.

### PHASE8-IMPL-025-T004 — BookNLP extraction expansion

Status: implementation milestone accepted; overall real-tool completion open
pending T004G current-layer real execution. Depends on completed/PASS T003.
Accepted implementation commit:
`ca2f99f35a7dc029a217954872ca7a5ab479ed2f`.

- `T004A` — Immutable BookNLP raw artifacts, source hash, run manifest, and
  precise token-to-character offset translation.
- `T004B` — Alias and coreference candidates with ambiguity/risk metadata.
- `T004C` — Quote and speaker-attribution candidates with uncertainty.
- `T004D` — Event/action and timeline candidates.
- `T004E` — Organization, facility, vehicle, object, and possession signals.
- `T004F` — Supersense, token, and dependency evidence mappings.
- `T004G` — Expanded real-runtime fusion and candidate-only persistence
  validation.

BookNLP remains an evidence producer. Coreference and speaker attribution may
support candidates but may not select truth.

Historical PHASE8-IMPL-023 BookNLP execution remains valid foundation evidence,
but no accepted evidence proves that real expanded T004 outputs traversed T002
source identity/hash, T003 manifest/raw artifacts/evidence ledger, fusion, and
candidate output. T004G must supply that proof in a separately authorized
validation task; this audit does not execute it.

### PHASE8-IMPL-025-T005 — Full Subtxt runtime inventory and contracts

Status: `complete/PASS`; depends on completed/PASS T003. Accepted implementation
commit: `7e58e4859f828b3ca0edb886c999f5f376f151ac`. Contract/closeout:
`docs/roadmap/decisions/PHASE8-IMPL-025-T005-full-subtxt-runtime-inventory-and-contracts.md`.

- `T005A` — Current runtime/source/API/CLI/library surface inventory.
- `T005B` — Official analysis-only capability allowlist.
- `T005C` — Forbidden generation/rewrite/mutation surface blocklist.
- `T005D` — Runtime configuration and read-only preflight.
- `T005E` — Request/input contract with exact source identity/hash and
  analysis operation.
- `T005F` — Result/output contract with evidence, unsupported-output, and
  fail-closed states.
- `T005G` — Official-runtime identity, version, model/provider, operation, and
  transformation provenance contract.
- `T005H` — Supported callable interfaces and versions, installation or access
  contract, discovery/configuration rules, compatibility checks, and precise
  missing/incompatible/unavailable/preflight states for every MVP-required
  runtime. Q136-Q139 are technical questions resolved through T005, not new
  authorization gates.

Licensing and owner authorization are resolved. No callable surface was
established on the inspected machine. Configuration, model/provider identity,
and source granularity remain unknown where not evidenced; these are
runtime-availability facts, not unfinished T005 contract work or authorization
blockers.

### PHASE8-IMPL-025-T006 — Full Subtxt adapter, integration, and validation

Status: `active/open`; implementation milestone accepted, real official-runtime
execution pending. Depends on completed/PASS T005. Accepted implementation
commit: `23d4825da9a257180cdc0d1d1239ce13b4e01f78`.
Milestone/pending-runtime record:
`docs/roadmap/decisions/PHASE8-IMPL-025-T006-full-subtxt-adapter-integration-and-validation.md`.

- `T006A` — Official/full Subtxt adapter implementation behind the committed
  allowlist/blocklist and fail-closed gates.
- `T006B` — Conversion to normalized evidence-backed candidate findings.
- `T006C` — Source-hash, run-manifest, raw-artifact, and evidence-ledger
  integration.
- `T006D` — Bounded official-runtime semantic-guardrail seam over normalized
  findings; the shared cross-adapter policy remains owned by T008.
- `T006E` — Deterministic contract validation.
- `T006F` — Mocked runtime validation.
- `T006G` — Real authorized runtime validation with version/model/provider
  provenance.
- `T006H` — Candidate-only persistence validation.
- `T006I` — Grouped-review validation.
- `T006J` — Documentation/status implementation-milestone reconciliation;
  overall closeout remains unavailable until the real-runtime gate passes.
- `T006K` — Current-machine evidence matrix proving supported version,
  discovery, configuration, preflight accuracy, timeout behavior, output
  validation, and one bounded real-input operation for every MVP-required
  available runtime. Protected runtime assets remain outside authoritative
  tracked records; external dramatica-flow stays owner-blocked and the
  app-owned rubric remains a separate identity.

Official/full Subtxt and `subtxt_informed_rubric` remain separate identities.
Subtxt findings remain pending, non-canon, owner-review-required, and unable to
mutate Memory/Canon.

T006G is `NOT_EXECUTED_RUNTIME_UNAVAILABLE`: no verified callable official/full
runtime was available, and no real Subtxt/runtime/API/model call occurred.
T006K truthfully records zero currently available official/full runtime
surfaces on this machine. The adapter/integration/mocked-validation milestone
is accepted, but overall T006 remains open. Completion requires a verified
production official runner, T003-to-official-Subtxt wiring, and successful
bounded real execution through the current layered path.

### PHASE8-IMPL-025-T007 — Evidence-bounded Ollama and Story Check

Status: `planned`; depends on completed/PASS T003; not begun and not the
immediate frontier while T006 remains open. It consumes the completed
`PHASE8-IMPL-024-T002` grounding repair rather than duplicating it.

- `T007A` — Ollama exact-source structured extraction role.
- `T007B` — Ollama evidence-bounded interpretation of normalized evidence.
- `T007C` — Story Check source identity/hash and deterministic grounding
  integration with the run manifest/evidence ledger.
- `T007D` — Unsupported factual-output quarantine, source-mismatch failure,
  and mixed factual/non-factual regression fixtures.
- `T007E` — Mocked regression validation plus bounded real Ollama/qwen3:8b and
  Story Check execution through current exact-source/hash, run-manifest,
  native/raw-artifact, evidence-ledger, grounding/quarantine, normalization,
  and candidate semantics; then documentation closeout. Historical
  PHASE8-IMPL-023 live runs are foundation, not T007E completion evidence.

Neither role may assert truth or canon. Original tool/model output is retained
with its verification state and is never silently rewritten.

### PHASE8-IMPL-025-T008 — Cross-adapter semantic guardrails

Status: `planned`; not begun; depends on T004, T006, and T007. T004 and T006
retain accepted implementation milestones but still have real-execution gates;
the shared guardrail and integration layer waits for every required contributor
branch and its required real current-layer output.

- `T008A` — Shared guardrail input/result contract and execution ordering.
- `T008B` — Classification of Ollama, Story Check, NCP, Subtxt, and rubric
  claims as supported, unsupported, ambiguous, subject-matter-only,
  author-intent-dependent, or insufficient evidence.
- `T008C` — Perspective ambiguity and unsupported Storypoint/Throughline
  overclaim checks.
- `T008D` — Preserved original output plus separate guardrail annotation; no
  rewriting or truth selection.
- `T008E` — Deterministic fixture regression validation plus cross-adapter
  validation using actual outputs from current-layer real executions for every
  applicable MVP-required external contributor. Fixture-only contributor runs
  cannot satisfy T008 acceptance.

### PHASE8-IMPL-025-T009 — Read-only project-level narrative diagnostics

Status: `planned`; depends on T008.

- `T009A` — Project-level context contract covering multiple exact sources and
  approved-context snapshots.
- `T009B` — Causal continuity and timeline/thread activity diagnostics.
- `T009C` — Information-boundary and relationship-delta diagnostics.
- `T009D` — Emotional-state delta diagnostics.
- `T009E` — Promise/payoff, hook/foreshadowing, and lifecycle diagnostics.
- `T009F` — Multi-source and approved-context comparison with read-only
  candidate output.
- `T009G` — Validation that no diagnostic settles world state, truth,
  relationships, emotions, hooks, or canon.

No outline, chapter, revision, rewrite, continuation, or truth-file mutation
surface is authorized.

### PHASE8-IMPL-025-T010 — Full NCP gateway

Status: `planned`; depends on T008 and may build its backend gateway contracts
in parallel with T009 diagnostics.

- `T010A` — Immutable original import artifact, pinned schema/mapping version,
  and validation-before-import.
- `T010B` — Explicit mappings for ideation, narrative, perspective, player,
  dynamic, storypoint, storybeat, moment, setting, overview, authorial intent,
  and metadata.
- `T010C` — JSON-pointer provenance, source-value hashes, and external-status
  preservation as source metadata only.
- `T010D` — Candidate-only import, conflict reconciliation, owner review, and
  omitted-field non-deletion behavior.
- `T010E` — Approved-context-only standard export plus optional separately
  labeled candidate-review bundle.
- `T010F` — Validation-before-export and trusted app-generated round-trip
  provenance rules, proven against a real supported NCP schema/interface.
- `T010G` — Schema-drift, semantic-drift, flattening, export-completeness, and
  real supported-schema import/export/validation round-trip tests. Historical
  owner-selected import is foundation evidence, not full T010 completion.
- `T010H` — Owner-facing NCP import/export and scoped diagnostics workflow
  after the T009 diagnostics and T010 backend contracts. Cover safe destination
  selection, validation feedback, loading, empty, invalid, unavailable,
  request-failure, retry, success, confirmation, accessibility, responsive
  behavior, browser validation, and no automatic canon mutation. Preserve
  explicit later owner decisions for export-destination semantics, retention
  or deletion, destructive operations, and unresolved candidate-bundle
  behavior.

An external `complete` status never becomes local approval.

### PHASE8-IMPL-025-T011 — Candidate review lifecycle expansion

Status: `planned`; depends on T008 and may proceed in parallel with T009/T010.
These actions are separate bounded tasks;
they are not authorized as one implementation change.

- `T011A` — Approve, reject, and needs-more-evidence lifecycle contract.
- `T011B` — Merge-duplicate workflow.
- `T011C` — Split-incorrect-cluster workflow.
- `T011D` — Rename and correct-source-linkage workflow.
- `T011E` — Supersede and owner-authored-correction workflow.
- `T011F` — Rerun-selected-source workflow with prior-run lineage.
- `T011G` — Grouped-review integration and audit validation.
- `T011H` — Owner-facing live-run workflow, separate from T003F backend
  implementation and using the PHASE8-IMPL-024 component/navigation
  foundation. Cover readiness/preflight, tool selection, run submission,
  progress, partial results, unavailable/failure/timeout states, retry and
  recovery, result/provenance/manifest/ledger inspection, candidate-review
  handoff, explicit owner-controlled apply boundaries, accessibility,
  responsive behavior, and clean browser console/network validation.

No review status alone mutates canon. Promotion and apply-promotion remain
separate.

### PHASE8-IMPL-025-T012 — Layered end-to-end validation

Status: `planned`; depends on T009, T010, and T011. All required contributor,
control-plane, compatibility, guardrail, integration, diagnostics, gateway,
review, and owner-UI paths must join before this workstream begins.

- `T012A` — Source identity and run-manifest suite.
- `T012B` — Raw extraction and immutable artifact/evidence-ledger suite.
- `T012C` — Interpretation suite.
- `T012D` — Semantic-guardrail suite.
- `T012E` — Fusion suite.
- `T012F` — Candidate-persistence suite.
- `T012G` — Owner-decision suite.
- `T012H` — Promotion-record and handoff suite.
- `T012I` — Isolated apply-promotion suite.
- `T012J` — NCP approved-export and round-trip suite.
- `T012K` — Browser-to-HTTP live-run, partial/unavailable/timeout, manifest,
  evidence-ledger, compatibility, provisioning-matrix, and owner-workflow
  integration deltas over the PHASE8-IMPL-024-T008 baseline.

Apply-promotion is never combined with read-only, candidate-decision, or NCP
candidate-import validation.

T012 must reuse PHASE8-IMPL-024-T008 candidate lifecycle, promotion,
apply-promotion, review-command, and owner-decision assertions. Historical
PHASE8-IMPL-023-T024 automated end-to-end intent is incorporated here;
T023C/T023D lifecycle intent is incorporated in T011; and historical
T025/T026 manual/closeout intent is incorporated in the current terminal
PHASE8-IMPL-027 gate. Those historical identities remain historical evidence,
not competing terminal suites or owner gates.

For every enabled MVP-required external contributor, T012 must prove:

```text
real source
-> current layered control plane
-> real external tool/runtime/interface
-> native/raw output
-> manifest/artifact/evidence ledger
-> normalization
-> guardrails/fusion
-> candidate persistence
-> owner review
```

Deterministic mocks remain required regression coverage but cannot satisfy this
terminal integration gate by themselves.

## Implementation sequence and parallelism

Documentation publication occurred before this reconciliation. The
PHASE8-IMPL-024 parent-closeout boundary has passed and this parent is
published/active. T001 -> T002 -> T003 established the shared contracts. T005
is complete/PASS. T004 and T006 retain accepted implementation milestones but
their real-execution gates remain open. T006 is the immediate active frontier;
T007 stays planned/not begun. T008 joins real current-layer outputs from the
required contributor branches. T009,
T010 backend work, and T011 lifecycle work may then proceed according to their
actual prerequisites; T010H waits for T009 and T010 backend contracts, while
T011H waits for T003F and the completed PHASE8-IMPL-024 component foundation.
T009, T010, and T011 join at T012.
T012 must pass before terminal PHASE8-IMPL-027 acceptance.

No parallel execution may bypass source identity, manifest, evidence-ledger,
allowlist/blocklist, compatibility, guardrail, or owner-review dependencies.
This graph has no all-serial T004-through-T011 chain and no circular edge.

## Pending owner decisions

- External `dramatica_flow` requires
  `OWNER_DECISION_REQUIRED_BEFORE_EXTERNAL_DRAMATICA_FLOW_IMPLEMENTATION`.
  T020B currently blocks/reference-limits the external runtime, while the
  newer completion rule requires real execution for every MVP-required
  external integration. The owner must decide whether external
  `dramatica_flow` remains MVP-required before any implementation or execution.
  The app-owned `dramatica_flow_informed_rubric` is not equivalent evidence.
- T003D/T003G require owner review only if retention/deletion or physical
  migration changes owner-visible stored structures.
- T010H preserves later decisions for export destination, retention/deletion,
  destructive operations, and unresolved candidate-bundle behavior.
- PHASE8-IMPL-027 requires the final owner accept/reject/defer decision.

## Product boundaries

- Analysis-only.
- Owner-authored prose storage/editing is allowed.
- No generated story prose.
- No rewriting, continuation, polishing, improvement, expansion, outlining,
  drafting, revision, or imitation.
- No automatic Storyform or structural truth.
- No automatic candidate approval or promotion.
- No automatic apply-promotion.
- No direct tool/model Memory/Canon mutation.
- Evidence/provenance and exact source identity are required.
- Owner-controlled approval remains authoritative.

## Validation for this publication

Documentation-only validation:

```bash
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-025.enrichment.json
python3 -m json.tool docs/roadmap/roadmap_index.yaml
python3 scripts/validate_roadmap.py
python3 scripts/check_enrichment.py
git diff --check
git status --short --branch
```

No backend, frontend, runtime, model, extraction, Story Check, Playwright, or
application test is part of this publication.
