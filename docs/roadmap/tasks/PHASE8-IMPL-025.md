# PHASE8-IMPL-025 — Layered Analysis Architecture and Tool Integration Expansion

## Status

Published/active. T001-T003 implementation milestones and the T005 contract are
complete/PASS. T004 is complete/PASS through T004G: implementation commit
`ca2f99f35a7dc029a217954872ca7a5ab479ed2f` is preserved separately from the
accepted T004G real-runtime validation/fix commit
`bc2a65e6350fdd65720606253b120d7fbcfa2b78`. T006 is accepted/closed as the
optional paid Subtxt/Dramatica integration foundation; T006G remains
`NOT_EXECUTED_RUNTIME_UNAVAILABLE`, and paid real-runtime execution is deferred
without blocking MVP. T007 is complete/PASS through T007E at implementation
commit `f843b615762192ca8f6865e76b2c4e4c9bcc2170`. T008 is complete/PASS
through T008E at accepted implementation commit
`2465722cedfe9f8dcb4135d8de124f36a999593f`. Accepted T004/T004G and
T007/T007E supplied the satisfied contributor prerequisites for T008. T009 is
complete/PASS, T010 is implemented, T010H is complete/PASS at accepted
implementation commit `9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`, and T011 is
complete/PASS through accepted T011H at
`66d3c587655161415e9508c2dfb1aa2e09f3d231`. T012A dependency/eligibility
preflight is next; implementation has not begun and T012 eligibility remains
unasserted until that separate preflight verifies every recorded prerequisite.

Activation had one explicit boundary: `PHASE8-IMPL-024` fully complete/closed
with application closeout validation PASS. That boundary is satisfied by the
accepted PHASE8-IMPL-024-T008 closeout, so this parent is published/active.
Project Memory is not an activation gate while the accepted 2026-07-17 pause
decision remains current. T007 is complete/PASS through T007E. The current
accepted/closed child is `PHASE8-IMPL-025-T010H` at
`9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`. The accepted T004G closeout HEAD
`bc2a65e6350fdd65720606253b120d7fbcfa2b78` satisfied the BookNLP prerequisite
before T008 implementation began. Optional paid Subtxt execution was not an
MVP or T008 blocker. T010H is accepted/closed and T012 remains open; no T012A
implementation is activated by this closeout.

The owner-authorized T001 context prerequisite is satisfied by the generated,
read-only supporting pack at
`.codex-context/PHASE8-IMPL-025/T001-tool-role-layered-orchestration/20260830T175126Z/`.
The pack is navigation evidence only, is not roadmap authority, and is not a
tracked deliverable.

Controlling decision:
`docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`.

Controlling Subtxt/MVP scope reconciliation:
`docs/roadmap/decisions/2026-09-07-subtxt-optional-paid-integration-free-local-mvp-path.md`.

Controlling dramatica-flow/MVP scope reconciliation:
`docs/roadmap/decisions/2026-09-08-dramatica-flow-analysis-only-reference-and-app-owned-rubric-mvp-boundary.md`.

Controlling T001 contract:
`docs/roadmap/decisions/PHASE8-IMPL-025-T001-tool-role-and-layered-orchestration-contract.md`.

## Goal

Expand the implemented independent-adapter/fusion/candidate-review foundation
into a layered-plus-parallel architecture with stable source identity,
immutable run evidence, evidence-bounded interpretation, semantic guardrails,
an optional paid Subtxt runtime integration foundation, richer BookNLP
extraction, a full NCP gateway, bounded owner-correction workflows, and
isolated end-to-end validation.

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
  validation; `dramatica_flow_informed_rubric` is the approved MVP boundary
  for wanted dramatica-flow-derived analysis concepts and is not evidence that
  the external runtime ran;
- deterministic normalized IDs, fingerprints, duplicate/conflict/uncertainty
  metadata, candidate-only persistence, and grouped review;
- `PHASE8-IMPL-023-T023A` and T023B.

Persisted findings remain pending, unapproved, promotion-ineligible,
candidate-only, and non-canon. The app-owned Subtxt-informed rubric remains a
valid separate deterministic contributor and supplemental semantic guardrail.
It is not official/full Subtxt runtime execution and cannot silently substitute
for or impersonate official `subtxt`.

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
| D — Optional paid Subtxt runtime integration | T005-T006 |
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

Status: `complete/PASS` through T004G. Depends on completed/PASS T003.
Accepted implementation commit:
`ca2f99f35a7dc029a217954872ca7a5ab479ed2f`. Accepted T004G real-runtime
validation/fix commit:
`bc2a65e6350fdd65720606253b120d7fbcfa2b78` (`fix(analysis): validate BookNLP
real-runtime retry`).

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

Historical PHASE8-IMPL-023 BookNLP execution remains valid foundation evidence.
Accepted T004G real-runtime retry validation subsequently proved the required
current-layer BookNLP path and satisfied the final T004 completion condition
before T008 began.

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

Status: accepted/closed as an optional paid-integration foundation; real paid
runtime deferred. Depends on completed/PASS T005. Accepted implementation
commit: `23d4825da9a257180cdc0d1d1239ce13b4e01f78`.
Accepted-foundation/deferred-runtime record:
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
- `T006G` — Optional paid real-runtime validation with
  version/model/provider provenance when separately authorized and available.
- `T006H` — Candidate-only persistence validation.
- `T006I` — Grouped-review validation.
- `T006J` — Documentation/status reconciliation for the accepted optional paid
  integration foundation and deferred real-runtime debt.
- `T006K` — Current-machine evidence matrix proving supported version,
  discovery, configuration, preflight accuracy, timeout behavior, output
  validation, and one bounded real-input operation when the optional paid
  runtime is separately authorized and available. Protected runtime assets
  remain outside authoritative tracked records; external `dramatica_flow`
  remains reference/provenance-only for MVP and the app-owned rubric remains a
  separate identity.

Official/full Subtxt and `subtxt_informed_rubric` remain separate identities.
Subtxt findings remain pending, non-canon, owner-review-required, and unable to
mutate Memory/Canon.

T006G is `NOT_EXECUTED_RUNTIME_UNAVAILABLE`: no verified callable official/full
runtime was available, and no real Subtxt/runtime/API/model call occurred.
T006K truthfully records zero currently available official/full runtime
surfaces on this machine. The adapter/integration/mocked-validation milestone
is accepted, and T006 is closed as an optional paid-integration foundation.
Future production-runner work, T003-to-official-Subtxt wiring, provisioning,
and bounded real execution remain separately authorized optional debt. A
future claim that the official integration is fully operational still requires
that real execution; no such claim is made here.

### PHASE8-IMPL-025-T007 — Evidence-bounded Ollama and Story Check

Status: `complete/PASS`; dependency on completed/PASS T003 satisfied.
Implementation commit:
`f843b615762192ca8f6865e76b2c4e4c9bcc2170`.
It consumes the completed `PHASE8-IMPL-024-T002` grounding repair rather than
duplicating it.

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

T007E closeout accepted the current-layer deterministic and real-runtime gates.
The final deterministic gate passed 379 tests. Real `analyze-ollama-model`
execution reached Ollama/qwen3:8b through the application path, preserved the
exact 180-byte source and immutable original output, truthfully recorded model
execution, rejected unsupported `candidate_type="person"` output without
coercion, and persisted zero candidates. A separate real
`analyze-story-check` application-path execution reached Story Check ->
Ollama/qwen3:8b exactly once, preserved exact source identity, produced
16 grounded diagnostics (0 verified, 15 unverified, 1 quarantined), retained
all 16 through output lineage with 16 `output_recorded` events and zero
nonvalidated evidence references, and persisted zero candidates.

No automatic approval, promotion/apply-promotion, Memory/Canon mutation,
training/dataset/model mutation, or generated story prose occurred.

Closeout:
`docs/roadmap/decisions/PHASE8-IMPL-025-T007-evidence-bounded-ollama-and-story-check-closeout.md`.

### PHASE8-IMPL-025-T008 — Cross-adapter semantic guardrails

Status: `complete/PASS` through T008A-T008E. Accepted implementation commit:
`2465722cedfe9f8dcb4135d8de124f36a999593f` (parent
`bc2a65e6350fdd65720606253b120d7fbcfa2b78`).

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
  applicable MVP-required contributor. Fixture-only contributor runs
  cannot satisfy T008 acceptance. When official Subtxt is configured and
  available, its output may participate and must pass the same guardrails and
  evidence/candidate boundaries; its absence is an accepted fail-closed
  optional-feature state.

The accepted implementation provides the shared six-classification contract:
`supported`, `unsupported`, `ambiguous`, `subject_matter_only`,
`author_intent_dependent`, and `insufficient_evidence`. It requires normalized
evidence, prevents interpretive output from self-supporting its own claims,
distinguishes ordinary owner interpretation from author intent, and checks
perspective ambiguity plus unsupported Storypoint/Throughline overclaims.
Guardrails run exactly once before a single deterministic fusion pass.
Immutable guardrail annotations remain separate from unchanged findings and do
not rewrite findings or select truth/canon.

Accepted deterministic validation: `458 passed, 7 warnings`; the warnings were
existing Pydantic deprecations and not product failures. `py_compile` and
`git diff --check` passed. Accepted T008E current-layer evidence covered 49
BookNLP findings with 49 annotations (45 `supported`, 4 `ambiguous`), one live
Ollama/qwen3:8b finding classified `insufficient_evidence` for
`eligible_normalized_evidence_missing`, and 16 retained Story Check diagnostics
with 16 separate annotations (15 `insufficient_evidence`, 1 `unsupported`) and
zero candidate transformations or fusion-eligible retained annotations. A
separate malformed-locator qwen3:8b output failed closed with zero findings and
annotations. Original outputs remained unchanged and runtime validation
persisted zero candidates.

Official Subtxt remained unavailable/unconfigured optional paid integration;
no installation, subscription, provisioning, or execution occurred, and its
absence was nonblocking. External `dramatica_flow` was not executed and remains
reference/provenance-only for MVP. No owner approval, automatic truth/canon
selection, promotion/apply-promotion, Memory/Canon mutation,
training/dataset/model mutation, or generated story prose occurred.

Closeout:
`docs/roadmap/decisions/PHASE8-IMPL-025-T008-cross-adapter-semantic-guardrails-closeout.md`.

### PHASE8-IMPL-025-T009 — Read-only project-level narrative diagnostics

Status: `planned`; not begun. Its T008 dependency is satisfied. This
reconciliation does not activate or prioritize T009.

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

Status: `planned`; not begun. Its T008 dependency is satisfied, and it may
build its backend gateway contracts in parallel with T009 diagnostics. This
reconciliation does not activate or prioritize T010.

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

T010H status: `complete/PASS`; accepted implementation commit
`9376ddd379e8cb9addac00b3aa691c7c82fe1bf2` (`feat(ui): add NCP diagnostics
owner workflow (T010H)`). The accepted UI exposes the owner-facing NCP
gateway/diagnostics workflow, standard approved-context export readiness,
separately blocked/pending candidate-bundle behavior, candidate-only external
import review, safe opaque destination validation, deterministic loading,
empty, invalid, unavailable, request-failure/retry, success, and confirmation
states, accessibility, and responsive containment. Validation recorded 27
backend T010H contract passes; frontend Node suites of 4, 3, 9, and 3 passes;
frontend build PASS; 100 frontend source/accessibility passes; and browser
smoke PASS with no mutation requests, console/page errors, failed requests, or
HTTP errors. No story prose, live model/tool/runtime execution, export/import
write, candidate/review/promotion/apply action, Memory/Canon mutation, or
project-truth mutation occurred. Closeout:
`docs/roadmap/decisions/PHASE8-IMPL-025-T010H-ncp-diagnostics-owner-workflow-closeout.md`.

An external `complete` status never becomes local approval.

### PHASE8-IMPL-025-T011 — Candidate review lifecycle expansion

Status: `complete/PASS` through T011H. T011A-T011H were implemented as separate
bounded tasks. Latest accepted implementation commit:
`66d3c587655161415e9508c2dfb1aa2e09f3d231` (`feat(ui): add owner-facing
live-run workflow (T011H)`).

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

T011H uses the existing control-plane endpoints and PHASE8-IMPL-024/T011
foundations. Accepted validation covered the frontend build and Node tests,
source/accessibility/responsive contracts, backend analysis-control/manifest/
ledger/preflight contracts, and browser smoke with exact source preservation,
idempotent retry, 390px mobile containment, visible focus, and no unexpected
console/page/network/HTTP failures other than the intentionally injected
`503 POST /omi/analysis/runs`. It added no backend endpoint and did not redefine
OMI grouped-review or candidate-decision route semantics. It performed no live
model/runtime completion proof, candidate persistence, automatic approval,
promotion/apply-promotion, Memory/Canon, project-truth, source, or story-prose
mutation. Closeout:
`docs/roadmap/decisions/PHASE8-IMPL-025-T011H-owner-facing-live-run-workflow-closeout.md`.

No review status alone mutates canon. Promotion and apply-promotion remain
separate.

### PHASE8-IMPL-025-T012 — Layered end-to-end validation

Status: `planned`; not begun. The next lifecycle is T012A dependency/eligibility
preflight, not T012A implementation. Live repository evidence must verify T003F,
T003G, T009, T010, accepted T010H at
`9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`, T011, and T011H before this
workstream begins. This closeout does not assert T012 eligibility.

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
is complete/PASS. T004 is complete/PASS through accepted T004G real-runtime
retry validation. T006 is accepted/closed as the optional paid integration
foundation, with real paid runtime deferred. T007 and T008 are complete/PASS.
T008 accepted real current-layer outputs from the applicable
MVP-required free/local contributor branches; optional official Subtxt was
unavailable and nonblocking. T009, T010 backend work, and T011 through T011H
have local acceptance evidence. T010H is accepted/closed at
`9376ddd379e8cb9addac00b3aa691c7c82fe1bf2`. T012A is the next
dependency/eligibility preflight, not active implementation, and must verify
T003F, T003G, T009, T010, T010H at that accepted commit, T011, and T011H before
T012 may begin.
T012 must pass before terminal PHASE8-IMPL-027 acceptance.

The external `dramatica_flow` runtime is not part of this execution graph or
the T007, T008, T012, or PHASE8-IMPL-027 acceptance path. Its upstream identity
is reference/provenance only for MVP. No implementation or execution is
authorized; any future integration requires a separate explicit owner
authorization and analysis-only safety review.

No parallel execution may bypass source identity, manifest, evidence-ledger,
allowlist/blocklist, compatibility, guardrail, or owner-review dependencies.
This graph has no all-serial T004-through-T011 chain and no circular edge.

## Resolved dramatica-flow MVP boundary

The app-owned `dramatica_flow_informed_rubric` is the approved application/MVP
boundary for permitted analysis-only concepts, rules, and structural reasoning
derived from `ydsgangge-ux/dramatica-flow` at the observed upstream commit
`3a6fa55e84a8248e596527f0a5013748945a6cb8`. It must never be represented as
evidence that the external runtime ran. The external runtime is not
MVP-required, and no external runtime proof is required.

Historical T020B remains unchanged. The controlling 2026-09-08 owner decision
resolves only the later MVP-classification question.

## Pending owner decisions

- T003D/T003G require owner review only if retention/deletion or physical
  migration changes owner-visible stored structures.
- Accepted T010H preserves later decisions for export destination, retention/deletion,
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
