# PHASE8-IMPL-025-T001 — Tool-Role and Layered-Orchestration Contract

## Result

`PHASE8-IMPL-025-T001` is complete/PASS as a documentation-only architecture
contract. This decision reconciles the implemented OMI independent-adapter,
normalization, fusion, candidate-persistence, and grouped-review foundation
with the accepted PHASE8-IMPL-025 layered-plus-parallel target.

This decision does not implement a runtime, schema, API, persistence format,
user interface, adapter, model call, external-source integration, or test. It
does not begin T002 or any later PHASE8-IMPL-025 workstream.

## Authority and preserved foundation

This is the controlling T001 contract under the parent decision
`PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`.
It preserves rather than replaces:

- the adapter identities, adapter result states, normalized finding contract,
  safety envelope, deterministic fingerprints, fusion behavior, and fallback
  identity in `backend/omi_analysis_orchestrator.py`;
- the read-only preflight and its enabled, disabled, available, unavailable,
  blocked, error, and not-configured reporting in
  `backend/omi_runtime_preflight.py`;
- candidate-only persistence in `backend/project_manager.py`;
- review-queue workflow support and the rule that queue presence is not
  approval in `backend/story_knowledge/review_queue_storage.py`;
- exact-source Story Check grounding, deterministic verified/unverified/
  quarantined handling, and source-mismatch failure from
  PHASE8-IMPL-024-T002;
- deterministic fusion IDs/fingerprints, duplicates and conflicts without
  truth selection, uncertainty, and preserved evidence/provenance from
  PHASE8-IMPL-023-T010; and
- the T023A/T023B grouped-review foundation.

The application remains analysis-only, candidate-first,
evidence/provenance-backed, and owner-controlled. Tool or model output cannot
generate, rewrite, continue, outline, draft, polish, improve, expand, revise,
or imitate story prose and cannot automatically select structural truth,
approve a candidate, promote, apply promotion, or mutate Memory/Canon.

## Abstract dependency classes

The orchestration graph uses the following abstract dependency classes. These
are requirements and handoff categories, not T002/T003 schemas or new runtime
types.

| Dependency class | Meaning in this contract |
| --- | --- |
| Owner-selected source/input | Exact owner-chosen material together with a source-identity boundary. T002 defines its stable identity, snapshot, hashes, maps, and offsets. |
| Imported artifact | An explicit owner-selected external artifact retained as an import source. It is not raw text implicitly supplied to an analyzer. |
| Raw extraction/evidence | Tool-native or deterministic observations tied to the selected source and producer identity. T003 defines immutable artifact and ledger representation. |
| Normalized evidence | Evidence translated into the app's shared, validated evidence form with source and transformation lineage. It is not interchangeable with raw text or an opaque tool response. |
| Diagnostic/candidate finding | A bounded interpretation, diagnostic, question, warning, or candidate claim carrying evidence and provenance and remaining pending/non-canon. |
| Guardrail annotation | A separate assessment of a finding's support, ambiguity, subject-matter/author-intent dependency, or insufficient evidence. It does not rewrite the original output. |
| Fused finding | A normalized finding annotated with deterministic duplicate, conflict, relationship, and uncertainty metadata without truth selection. |
| Approved context | Context made eligible by the explicit owner-controlled approval/promotion/apply boundary, not merely by candidate or queue presence. |
| Gateway input/output | A validated import artifact or a separately labeled export derived from the permitted approved-context or candidate-review boundary. |

Every operation must declare the dependency class or classes it consumes.
Possessing some other class does not satisfy the dependency. In particular, a
normalized-evidence consumer may not silently receive owner source/raw text,
an imported artifact, or unnormalized tool output instead.

## T001A — Adapter roles and input/output dependencies

### Role taxonomy

| Role | Existing identity or operation | Required input class | Permitted output class and boundary |
| --- | --- | --- | --- |
| Owner source/source-identity boundary | Owner selection outside the adapter set | Owner action selecting the source/input | Owner-selected source/input. T002 makes the identity and snapshot contract concrete; downstream work may not infer or replace the selection. |
| Evidence producer | `spacy`, `booknlp` | Owner-selected source/input; after T002/T003, the shared source/run and evidence dependencies | Raw extraction/evidence and then normalized evidence. Entity, syntax, coreference, quote/speaker, event, and related signals are support, not truth. Exact T004 expansion is deferred. |
| Exact-source structured extractor | `ollama_model`, exact-source operation | Owner-selected source/input with exact source identity | Evidence-backed diagnostic/candidate findings. This operation is distinct from the normalized-evidence interpretation operation and cannot assert truth/canon. |
| Grounded diagnostic consumer | `story_check` | Owner-selected source/input with exact source identity and the grounded diagnostic context; normalized evidence as well only when a future layered operation declares it | Grounded diagnostic/candidate findings with original output, direct evidence or explicit unverified/quarantined state, and exact-source mismatch failure. The completed Story Check grounding path remains valid and is not silently converted to a different input contract. |
| Evidence-bounded interpretation/diagnostics | `ollama_model` evidence-interpretation operation; official/full `subtxt`; `dramatica_flow` only if separately available and authorized for a future operation | Normalized evidence plus the declared source identity/context required by the operation | Diagnostic/candidate findings with original output, evidence, provenance, verification/support state, and uncertainty. The target layered Subtxt consumer requires normalized evidence; any direct-source Subtxt operation must first be separately inventoried and allowlisted by T005. External dramatica-flow runtime availability/authorization is not established by T001. |
| App-owned diagnostic contributor | `subtxt_informed_rubric`, `dramatica_flow_informed_rubric` | For the preserved explicit current paths, owner-selected source/input; for any future layered guardrail use, normalized evidence and the finding being assessed | App-owned diagnostic/candidate findings or separate guardrail annotations. The current explicit direct-source paths do not satisfy a future normalized-evidence dependency. |
| Semantic guardrail | App-owned rubric operations and the future shared T008 guardrail layer | Normalized evidence plus the exact diagnostic/candidate finding being assessed; author intent or approved context only when the declared check requires it | A separate guardrail annotation. It preserves the original finding and does not choose truth. Exact shared ordering belongs to T008. |
| Fusion | Existing deterministic OMI fusion | Valid normalized diagnostic/candidate findings and their evidence/provenance; guardrail annotations when the later T008 ordering requires them | Fused findings with stable IDs/fingerprints, duplicate/conflict relationships, support, and uncertainty. Fusion does not manufacture missing evidence or decide truth. |
| Candidate persistence and owner review | Existing candidate persistence and T023A/T023B grouped review | Valid fused or otherwise persistence-eligible candidate findings with source/evidence/provenance; explicit owner review actions for decisions | Pending candidate records and review/audit workflow state. Candidate presence is not canon and queue presence is not approval. Exact correction/merge/split lifecycle is deferred to T011. |
| Promotion and approved-context operations | Existing separate promotion/apply-promotion boundary | Explicit owner-approved eligible candidate/context plus the existing blocker, confirmation, and audit dependencies | Promotion audit records and, only through the separately authorized audited apply operation, approved context/Memory/Canon changes. Review state alone is insufficient. |
| Gateway operations | `ncp` | Import: explicit owner-selected imported artifact. Export: approved context by default; any future candidate-review bundle must be separately labeled and explicitly selected. | Validated candidate-only import findings or validated gateway output with original artifact/value lineage. NCP is not a default raw-text analyzer and external status is not local approval. |
| Fallback/safety baseline | `deterministic_fallback` | Owner-selected source/input and explicit eligibility under the existing orchestrator configuration | Findings attributable only to `deterministic_fallback`. It cannot satisfy or impersonate another adapter's evidence or diagnostic role. |

The same adapter identity may expose more than one declared operation without
collapsing those operations. `ollama_model` therefore retains one internal
adapter ID while its exact-source structured extraction and normalized-
evidence interpretation operations remain conceptually and provenance-wise
distinct. Similarly, an app-owned rubric's preserved explicit direct-source
contributor path does not make raw text valid input to its future layered
semantic-guardrail operation.

### Dependency enforcement

- A consumer waits until every declared dependency class is present, valid,
  source-compatible, and permitted by activation/preflight.
- A missing required class produces a non-producing adapter result; it never
  triggers implicit input conversion or substitution.
- Transformations between raw extraction/evidence, normalized evidence,
  findings, guardrail annotations, and fused findings retain source, producer,
  operation, and transformation lineage.
- Candidate persistence may consume only validated candidate material. It may
  not persist raw artifacts, opaque tool output, or quarantined content as
  candidate truth.
- Approved-context and gateway-export consumers wait for their explicit owner
  and promotion/apply dependencies; candidate or review-queue presence cannot
  satisfy them.

## T001B — Execution graph, parallelism, and activation

### Authoritative task graph

The parent dependency graph remains:

```text
T001 -> T002 -> T003
                  |-> T004 ---------|
                  |-> T005 -> T006 -|-> T008
                  |-> T007 ---------|

T008 -> T009 -------------------------------|
     -> T010 -> T010H (also waits for T009) -|
     -> T011 --------------------------------|-> T012
T003 -> T003F -> T011H ----------------------|
T003 -> T003G -------------------------------|
PHASE8-IMPL-024-T007C -> T011H --------------|

T012 -> PHASE8-IMPL-027
```

T004, the T005-to-T006 branch, and T007 may proceed independently only after
T003 has satisfied the shared T001-to-T003 contracts. T008 waits for T004,
T006, and T007. After T008, T009, T010 backend work, and T011 lifecycle work
may branch according to their declared dependencies. T010H waits for T009 and
T010. T011H waits for T003F and the completed PHASE8-IMPL-024-T007C component
foundation. T012 waits for T003F, T003G, T009, T010, T010H, T011, and T011H.
No task is activated merely because another branch is runnable.

### Tool-level execution

At run level, contributors may execute in parallel only when they are
independent over the same validated owner-selected source/input and when each
has its own satisfied manifest/evidence, configuration, compatibility,
allowlist/blocklist, preflight, and activation requirements. Each contributor
retains a separate result envelope and identity.

A consumer must wait when it declares any producer output, normalized
evidence, guardrail result, owner decision, approved context, or gateway
artifact as an input. Scheduler parallelism is never evidence that a
dependency was satisfied and never authorizes a downstream operation to
consume whichever input happens to be available first.

### Activation modes

These are contract categories, not runtime enums introduced by T001. An
operation may require more than one category.

| Activation mode | Contract |
| --- | --- |
| Automatic only where explicitly safe | Eligible only when current authority and configuration explicitly allow automatic execution, all declared dependencies are satisfied, preflight is safe, and the operation is analysis-only/non-mutating. T001 grants no new adapter automatic activation. |
| Explicit owner request | The owner selects the operation/source and the operation passes its dependency, preflight, allowlist/blocklist, and compatibility gates. Full Subtxt, model/tool execution, fallback eligibility, and any future external dramatica-flow operation are not made implicit by this contract. |
| Imported artifact | Runs only against an explicit owner-selected artifact through the gateway/import contract. The artifact is not silently flattened into raw text for another role. |
| Normalized-evidence consumer | Becomes eligible only after required normalized evidence exists for the same source/run lineage. Absence means unavailable or fail-closed, not raw-text substitution. |
| Approved-context consumer | Becomes eligible only after the explicit owner-controlled approval/promotion/apply boundary has produced eligible approved context. Candidates, support labels, and queue entries are insufficient. |

Parallel execution may not bypass source identity, T002 manifest requirements,
T003 raw-artifact/evidence-ledger requirements, operation allowlists or
blocklists, runtime/provider compatibility, semantic guardrails, or owner-
review and approved-context dependencies.

## T001C — Identity, labels, and provenance

### Four identity planes

Every result and owner-facing presentation keeps these planes distinct:

1. **Internal adapter identity** is the stable application routing ID. T001
   does not rename an existing ID.
2. **User-facing label** describes the actual operation in plain language and
   must disclose official/external, app-owned, fixture/mock, unavailable, or
   fallback status where material. A label must never upgrade what ran.
3. **Provenance/tool identity** attributes a finding to the exact adapter and
   operation that produced it. The existing normalized finding rule that
   `source_adapter`, `provenance.adapter`, and `provenance.tool_source` match
   the adapter identity remains intact.
4. **Runtime/provider/version identity** records the actual executable,
   provider/model, and version when available, separately from the adapter ID.
   Absence remains explicit; it is not inferred from a label. T002/T003 and
   T005 make the concrete manifest/ledger representation and Subtxt inventory
   decisions.

An official external runtime and an app-owned implementation are separate
producers even when they address similar concepts. Fixture/mock output also
does not prove an official runtime executed.

### Preserved identities and required distinctions

| Internal adapter ID | Required owner-facing/provenance meaning |
| --- | --- |
| `ollama_model` | Ollama/model output, with the operation identified as exact-source structured extraction or evidence-bounded normalized-evidence interpretation and with actual provider/model/version reported when available. |
| `story_check` | Story Check diagnostic output using the existing grounded diagnostic identity. Its underlying model/provider, when used, is runtime provenance and does not replace `story_check` as the producing adapter. |
| `booknlp` | BookNLP evidence production, with actual runtime/version recorded when available. |
| `spacy` | spaCy evidence production, with actual runtime/model/version recorded when available. |
| `ncp` | NCP gateway/import-export operation. It must not be labeled as a default raw-text analyzer, and external status remains source metadata only. |
| `subtxt` | Subtxt handoff/full official-runtime path. Official/full execution may be labeled as such only when T005/T006 establish and execute the authorized callable surface with official-runtime provenance. Fixture/mock or unavailable results may not be labeled official execution. |
| `subtxt_informed_rubric` | App-owned Subtxt-informed diagnostic support. It is never official/full Subtxt, even when used as fallback, supplement, or guardrail. |
| `dramatica_flow_informed_rubric` | App-owned dramatica-flow-informed diagnostic support. It is never external/official `dramatica_flow` output. |
| `dramatica_flow` | External dramatica-flow identity only. T001 neither establishes runtime availability nor authorizes execution; an unavailable/not-run result stays explicit. |
| `deterministic_fallback` | Deterministic fallback/safety baseline only. It always remains visibly attributable to `deterministic_fallback` and never masquerades as a model, tool, rubric, or missing consumer. |

The exact full Subtxt callable surface, supported versions, operation
allowlist, runtime configuration/provisioning, and available provider/model
provenance remain T005 decisions. T001 makes no claim that external
dramatica-flow is available or authorized for runtime execution.

## T001D — Fail-closed and partial-run contract

### Preserved adapter result vocabulary

No new adapter result state is introduced. Each requested/selected contributor
retains exactly one existing state and a non-misleading explanation:

| State | Contract meaning |
| --- | --- |
| `succeeded` | The identified adapter operation ran, passed its boundary validation, and produced attributable normalized findings. |
| `empty` | The identified operation ran safely and produced no findings. It does not authorize fallback unless the existing configuration separately makes fallback eligible. |
| `skipped` | The operation did not run because its declared selection/activation condition was not met. The reason remains visible. |
| `unavailable` | The requested operation could not run because a required dependency, compatible runtime/provider, configuration, artifact, normalized evidence, or approved context was unavailable. It produces no findings. |
| `failed_closed` | A source mismatch, unsafe operation/output, invalid contract, missing required grounding, or other safety-boundary violation prevented output from entering the candidate path. It produces no accepted findings. |
| `error` | A bounded execution or adapter error occurred and no findings are attributed as successful output from that operation. The error does not authorize substitution. |

`complete`, `partial`, or `degraded` layered coverage is an orchestration-level
coverage assessment, not a new adapter result state. A run may preserve useful
successful findings while still reporting incomplete architecture coverage.
It may be called complete for its selected graph only when every requested
role ran to an acceptable producing/non-producing completion, every declared
dependency and required guardrail was satisfied, and no required contributor
was skipped, unavailable, failed closed, or errored. This does not mean the
finding set is true, approved, promoted, or canon.

### No silent fallback or impersonation

- Every requested/selected contributor keeps its own state, explanation,
  internal adapter identity, operation identity, and available runtime
  provenance.
- Successful findings remain attributable to the exact producer. A failed,
  unavailable, or absent consumer cannot be replaced by another role under
  the missing role's name.
- A normalized-evidence consumer reports unavailable or fails closed when its
  required normalized evidence is absent, invalid, or belongs to a mismatched
  source/run. Raw text is never silently substituted.
- Official Subtxt absence cannot relabel `subtxt_informed_rubric` as official
  or full Subtxt. The app-owned rubric may run only under its own identity and
  declared activation/input contract.
- External dramatica-flow absence cannot relabel
  `dramatica_flow_informed_rubric` as external runtime output.
- When explicitly eligible under the existing configuration,
  `deterministic_fallback` remains visibly `deterministic_fallback`. Its
  success does not convert failed/missing adapter states to success and does
  not make layered coverage complete.
- Preflight `disabled`, `blocked`, `unavailable`, `error`, or `not_configured`
  information remains visible and cannot be rewritten as adapter success.

### Unsupported output and lineage

The PHASE8-IMPL-024-T002 Story Check grounding foundation remains controlling:
exact-source mismatch fails closed; verified, unverified, and quarantined
diagnostics remain deterministically distinguished; unsupported factual output
is rejected or quarantined rather than presented as verified. An
unsupported/quarantined result remains linked conceptually to the selected
source/run, producer adapter and operation, available runtime/provider/version,
original output, evidence or missing-evidence reason, verification/guardrail
outcome, and subsequent transformation or rejection. T002/T003 must make that
lineage concrete without silently discarding the output or converting it into
candidate truth.

Fusion preserves duplicates, conflicts, evidence, provenance, and uncertainty
without selecting truth. Partial contributor success does not erase failed or
unavailable contributors and must not be reported as full layered architecture
coverage.

The following safety statements remain explicit at every handoff:

- candidate presence is not canon;
- queue presence is not approval;
- support is not truth; and
- tool output is not canon.

## Deferred implementation boundaries

T001 deliberately leaves these decisions and implementations unbegun:

- T002: exact stable source IDs, owner-input snapshots, hashes/maps/offsets,
  exact `AnalysisRunManifest` schema, and concrete rejected/partial lineage;
- T003: immutable raw-artifact and evidence-ledger schemas, retention/deletion,
  path/storage/replay/tamper behavior, T003F live-run API/control plane, and
  T003G persisted-data compatibility/migration;
- T004: exact expanded BookNLP mappings;
- T005/T006: full Subtxt callable inventory, supported versions, exact
  operation allowlist/blocklist, provisioning/configuration, runtime
  integration, and exact available provider/model provenance;
- T007: runtime implementation of the two Ollama roles and layered Story Check
  reuse;
- T008: exact shared guardrail ordering and implementation;
- T009: exact project-level diagnostic context contract;
- T010: exact NCP schema/mapping version and round-trip implementation;
- T011: detailed owner correction, merge, split, supersede, and rerun
  lifecycle; and
- T012: end-to-end runtime validation.

PHASE8-IMPL-025 remains active. T002 is the immediate planned,
dependency-satisfied, not-begun frontier. PHASE8-IMPL-027 remains planned and
inactive. Project Memory remains paused and nonblocking.

## Validation classification

This contract is documentation-only. Validation is limited to roadmap JSON,
roadmap/enrichment consistency, documentation diff checks, the six-file
mutation allowlist, and repository-state inspection. No backend, frontend,
runtime, model, extraction, Story Check, BookNLP, spaCy, NCP, Subtxt,
dramatica-flow, browser, or application test is required or authorized by
T001.
