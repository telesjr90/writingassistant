# PHASE8-IMPL-023-T020E — App-owned dramatica-flow-informed analysis-rubric OMI adapter integration

## Result

PASS — the committed T020D evaluator is integrated into the OMI analysis
orchestrator under the new app-owned adapter identity
`dramatica_flow_informed_rubric`. The integration is local, deterministic,
in-memory, candidate-only, and explicit-only. It is not live or official
dramatica-flow output.

## Identity separation and activation

The identities remain distinct:

| Role | Identity |
| --- | --- |
| T020E OMI adapter | `dramatica_flow_informed_rubric` |
| T020C/T020D internal rubric | `app_owned_dramatica_flow_informed_rubric` |
| Support label | `App-owned dramatica-flow-informed diagnostic support` |
| T009 fixture adapter | `dramatica_flow` |
| T009 fixture schema | `omi_dramatica_flow_analysis_handoff.v1` |
| T009 support label | `dramatica-flow analysis support only` |

The new identity is registered in `OMI_TOOL_ADAPTER_IDENTITIES` and
`OMI_ADAPTER_CONTRACTS`, produces candidates, and supports exactly
`plot_thread`, `continuity_warning`, `relationship`, `timeline_event`,
`diagnostic_question`, `ambiguity`, and `evidence_note`. It is absent from
`OMI_DEFAULT_ADAPTERS`, `OMI_CONTEXT_ADAPTER_NAMES`, T009 fixture routing,
environment flags, and runtime preflight. It runs only through an explicit
`requested_adapters=["dramatica_flow_informed_rubric"]` request. An injected
runner with that identity retains precedence over the built-in runner.

## Request and evaluator flow

`_build_dramatica_flow_informed_rubric_request` constructs the exact T020C
request using committed constants. It preserves the raw owner source
unchanged, preserves a safe project name or derives a deterministic safe
`project_<16 hex>` alias, and derives a safe deterministic request ID from the
safe project name, `source_idea_id`, and raw source. It supplies the exact ten
ordered categories, diagnostic-only intent, owner-source affirmation, all
required safety confirmations as true, and non-empty deterministic source,
evidence, provenance, and locator references.

The built-in runner accepts only `dict | None` adapter configuration, lazily
imports the committed T020C contract and T020D evaluator, validates the
request, calls `evaluate_dramatica_flow_informed_analysis_rubric` exactly once,
and validates the returned result before normalization. It performs no file,
environment, project-storage, external-source, model, provider, server,
network, subprocess, shell, or persistence operation.

## Four-bucket normalization and provenance conversion

The adapter combines all four committed result buckets:

- `candidate_support`
- `diagnostic_questions`
- `uncertainty_notes`
- `insufficient_evidence_notes`

Items are sorted deterministically by `item_id`. Each converted finding
preserves the T020C candidate type and statement kind, evidence excerpts,
source locator, all reference lists, confidence, uncertainty, pending and
unapproved owner decision, and `candidate_review_pending`. `extracted_claim`
is the T020D `diagnostic_text`, never owner evidence. `raw_finding_id` is the
OMI identity plus the committed item ID.

The T020C internal provenance is validated before conversion. The OMI finding
then uses `dramatica_flow_informed_rubric` for `source_adapter`,
`provenance.adapter`, and `provenance.tool_source`, while preserving the exact
app-owned support label. No normalized finding uses the T009
`dramatica_flow` identity.

## Status, failure, and persistence boundaries

Status mapping is exact: `succeeded` to OMI `succeeded` (or `empty` if no
findings survive), `empty` to `empty`, `failed_closed` to `failed_closed`, and
`error` to `error`. Every non-succeeded result has a non-empty explanation and
no candidates. Malformed, non-dictionary, unsafe, contract-invalid, or
exception results fail closed. One invalid item closes the whole adapter call;
partial findings are never returned.

The adapter adds no persistence code. With `persist_candidates=False`, the
existing orchestrator returns `persistence_status=not_requested` and empty
persisted, new, and reused candidate-ID lists. The runner never creates
candidate or review-queue records and never mutates project, truth-state,
Memory, or Canon data.

## T020D lifecycle-test repair

T020D correctly contained a frontier assertion that no T020E adapter existed.
T020E intentionally introduces that adapter, so the one obsolete assertion
was minimally renamed and updated. It now verifies explicit-only registration,
identity separation, T009 preservation, the unchanged T020C internal identity,
the independently callable T020D evaluator, and the absence of a live-runtime
claim. No T020D evaluator logic or T020C contract behavior changed.

## Validation and preserved boundaries

- Authorized lifecycle test repair: `1 passed`.
- Focused T020E tests: `104 passed`.
- Requested T020D/T020C/T019E/T009/orchestrator/persistence/runtime-integration/
  preflight regressions: `926 passed`, with one environment-only NVML warning.
- Python compilation: PASS.
- T009 fixture behavior, T019E, T020A, T020B, T020C, and T020D implementation
  remain unchanged.

No dramatica-flow import, execution, `df`, or source read occurred. No external
material was copied. No environment or preflight integration, model/server/
network/subprocess call, persistence, project or Memory/Canon mutation,
promotion/apply-promotion, training artifact, or prose was added or performed.

## Next frontier

Open question 122 is resolved by this integration. `PHASE8-IMPL-023-T020E` is
complete/PASS and parent `PHASE8-IMPL-023-T020` remains `in_progress`.

```text
PHASE8-IMPL-023-T020F
Manual real owner-authored dramatica-flow-informed rubric validation
planned
```

T020F must run one explicit real in-process OMI validation with
`requested_adapters=["dramatica_flow_informed_rubric"]` and
`persist_candidates=False` against controlled owner-authored non-story source
text. It must prove the built-in adapter and T020D evaluator are each reached
exactly once, return non-empty evidence-backed pending-review candidates, and
perform no persistence, mutation, promotion, runtime/model/external-source
call, or prose. T020F was not implemented or executed here; do not skip to
T021.
