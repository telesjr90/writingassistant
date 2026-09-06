# PHASE8-IMPL-025-T005 — Full Subtxt Runtime Inventory and Contracts

## Result

T005 implements the application-owned, non-executing contract for the
authorized official/full Subtxt path. It does not implement or invoke the T006
adapter. Official/full Subtxt remains identified as `subtxt`; the existing
app-owned `subtxt_informed_rubric` remains a separate implementation and
identity.

## Current evidence and inventory (T005A/T005D/T005H)

The bounded current-machine inspection on 2026-09-04 established only the
following inspected channels:

- `.external_sources/subtxt-docs` is missing;
- no `subtxt` executable is discoverable on `PATH`;
- Python distribution metadata contains no Subtxt-identifying distribution;
- no `SUBTXT*` or `OMI_LIVE_SUBTXT*` environment variable is exported; and
- no Subtxt process, library, network endpoint, model, or analysis operation
  was invoked.

This evidence does not claim that no Subtxt runtime exists outside these
channels or on other machines. It establishes that the current machine is not
ready for official/full Subtxt execution.

The inventory contract separately reports protected/external source, installed
package metadata, executable, callable library, callable local API, network
API, configuration, installation/access, runtime version, provider, model,
operation evidence, and compatibility states. Its vocabulary is `available`,
`configured`, `missing`, `inaccessible`, `incompatible`, `unsupported`,
`disabled`, `unavailable`, `malformed_configuration`, and
`unknown_unverified`. Discovery never exposes configuration values and never
imports or executes a possible Subtxt package.

Historical T019A evidence classified the formerly inspected
`.external_sources/subtxt-docs` checkout as a Nuxt documentation/reference
repository rather than an analysis runtime. That historical classification
does not make the now-missing source installed, callable, configured,
compatible, or ready. Historical API-reference pages likewise do not prove a
callable local or network API.

## Capability policy (T005B/T005C)

The exact policy-permitted official operation is `analyze-subtxt`. This is the
existing T003 manifest operation for adapter `subtxt`; it consumes
`normalized_evidence` and produces `diagnostic_candidate_finding` support. It
does not authorize direct-source substitution or any runtime call by itself.

Three capability planes are mandatory and distinct:

1. policy permitted: `analyze-subtxt`;
2. verified runtime supported: currently empty; and
3. currently available: currently empty.

An operation must appear in all three planes before a request is eligible.
Unknown operations fail closed. The named forbidden operations cover story
prose generation/writing, continuation, rewrite, imitation, polishing,
improvement, expansion, outline/draft/revision production, structural-truth
selection, project-story mutation, Memory/Canon mutation, automatic candidate
approval, promotion, automatic promotion, and apply-promotion. The positive
allowlist is authoritative: absence from the named blocklist is never
permission.

## Request contract (T005E)

`SubtxtAnalysisRequest` directly requires the accepted T002/T003 values rather
than defining parallel identities:

- a concrete immutable `AnalysisRunManifest`;
- one `SourceIdentity` already present in that manifest;
- the manifest's exact run ID, source snapshot ID, and exact UTF-8 SHA-256;
- an available manifest `ArtifactReference` for that exact source snapshot and
  hash;
- normalized-evidence IDs already declared by manifest output lineage;
- the existing `analyze-subtxt` operation declaration and normalized-evidence
  dependency edge;
- adapter identity `subtxt` and implementation kind `official_external`;
- a verified available official runtime identity and callable interface;
- explicit `analysis_only` intent and mandatory evidence/provenance; and
- a capability set proving policy permission, verified runtime support, and
  current availability.

Run, source, snapshot, hash, artifact, evidence, dependency, identity, intent,
or capability mismatch raises a fail-closed contract error. The request object
does not invoke a runtime.

## Result and provenance contracts (T005F/T005G)

Result states are:

- `evidence_backed_success`;
- `uncertainty`;
- `unsupported_output`;
- `unavailable_runtime`;
- `runtime_failure`;
- `incompatible_runtime`;
- `malformed_output`;
- `unsafe_output`; and
- `quarantined`.

Evidence-backed success requires a known runtime identity, known callable
interface, preserved raw-output reference, and evidence references. Uncertainty
requires its reason and preserved raw-output reference. Unsupported,
malformed, unsafe, and quarantined output must be quarantined. All non-success
states retain an explicit reason and preserve knowable source/run/provenance
linkage.

Official provenance reuses T002 `AdapterProvenance` and
`ProvenanceComponent`. It adds callable-interface and safe-configuration
identity plus run, source-snapshot, and transformation linkage. Actual runtime,
version, provider, model, model version, interface, and configuration values
remain `unknown` with null names/versions when the runtime does not report
them. They are never synthesized from a label, path, command, package record,
or historical checkout. Official provenance rejects either app-owned rubric
identity.

Every serialized request/result safety boundary states that the contract is
analysis-only and performed no prose generation/transformation, truth
selection, project mutation, Memory/Canon mutation, automatic approval,
promotion, or apply-promotion. Results are content-free references at T005;
candidate conversion and persistence are not implemented.

## Q136–Q139 technical resolutions

### Q136 — callable interface and installation/access

No exact callable CLI, importable library, local API, network API, source
runtime package, or other supported official surface is established by current
evidence. Installation/access mechanism and compatible versions are
`unknown_unverified`; current package and executable states are `missing`.
Configured command/path presence is configuration evidence only and cannot
report readiness. T006 provisioning must identify and validate one exact
authorized interface without changing the T005 allowlist/safety boundary.

### Q137 — operation allowlist and blocklist

The application policy permits only the existing `analyze-subtxt`
normalized-evidence analysis operation. Current verified-runtime-supported and
currently-available operation sets are empty, so no operation is runnable now.
All unknown operations are denied. The explicit generation, rewrite,
continuation, imitation, polish/improve/expand, outline/draft/revision, truth,
approval, mutation, promotion, and apply-promotion surfaces are blocked.

### Q138 — provider/model/version/configuration provenance

Runtime identity/version, provider, model/model version, callable interface,
and safe configuration identity are currently `unknown_unverified`. T006 must
preserve each value if actually reported and must preserve explicit unknown
states otherwise. Package metadata or a command/path cannot be promoted into
runtime/model/provider provenance. No provider or model requirement is
invented by T005.

### Q139 — source/document granularity

The only policy-contracted input is normalized evidence with exact T002 source
and T003 run/artifact/evidence lineage. Actual official-runtime support for raw
idea, scene, chapter, selected document, multi-document project context, or
approved-context snapshot is `unknown_unverified`. T005 authorizes none of
those granularities as callable. T006 must establish exact supported
granularity and compatibility evidence before execution; it may not silently
substitute raw source for normalized evidence.

## Identity separation

`subtxt` means only the official/full external runtime path.
`subtxt_informed_rubric` means the app-owned OMI adapter, while
`app_owned_subtxt_informed_rubric` remains its internal rubric identity. The
official contract requires `official_external` provenance and rejects either
app-owned name. Conversely, app-owned provenance cannot validate as official
Subtxt provenance. Existing fixture-only `subtxt` behavior and all app-owned
rubric code remain unchanged.

## T006 boundary

T005 adds no process, library, CLI, local-service, network, model, or live
runtime invocation; no output parser; no candidate conversion or persistence;
no raw-artifact/manifest/ledger writes; no grouped review; no live semantic
guardrail execution; no provisioning; and no real-input runtime validation.
Those remain T006 work after compatible provisioning evidence exists.
