# PHASE8-IMPL-023-T020C — App-owned dramatica-flow-informed analysis-rubric contract

## Result

PASS — the pure app-owned input/output contract is complete. It defines data
shapes and fail-closed validation only; no evaluator, adapter, runtime, route,
UI, persistence, project access, or prose behavior is implemented.

## Identity and schemas

- Internal identity: `app_owned_dramatica_flow_informed_rubric`
- Request schema: `omi_app_owned_dramatica_flow_informed_rubric_request.v1`
- Result schema: `omi_app_owned_dramatica_flow_informed_rubric_result.v1`
- Output class: `rubric_mapping_support`
- Support label: `App-owned dramatica-flow-informed diagnostic support`

These are separate from T009's unchanged `dramatica_flow` identity,
`omi_dramatica_flow_analysis_handoff.v1` schema,
`dramatica-flow analysis support only` label, and fixture-only behavior.

## Categories and mappings

| Category | Candidate type | Statement kind | Bucket |
| --- | --- | --- | --- |
| `causal_chain_diagnostic` | `plot_thread` | `candidate_observation` | substantive support |
| `narrative_commitment_lifecycle_diagnostic` | `plot_thread` | `candidate_observation` | substantive support |
| `emotional_state_consistency` | `continuity_warning` | `candidate_observation` | substantive support |
| `relationship_delta_diagnostic` | `relationship` | `candidate_observation` | substantive support |
| `timeline_thread_activity_diagnostic` | `timeline_event` | `candidate_observation` | substantive support |
| `information_boundary_diagnostic` | `continuity_warning` | `candidate_observation` | substantive support |
| `multidimensional_diagnostic_question` | `diagnostic_question` | `question` | questions |
| `owner_review_question` | `diagnostic_question` | `question` | questions |
| `ambiguity` | `ambiguity` | `ambiguity` | ambiguity |
| `insufficient_evidence` | `evidence_note` | `insufficient_evidence` | insufficient evidence |

No OS, MC, IC, RS, domain, concern, issue, problem, solution, approach,
dynamic, or signpost classification is present.

## Contract rules

Requests require exact identity/schema, safe identifiers, non-empty
owner-authored or owner-provided text, a matching source locator, ordered
unique reference/category lists, diagnostic-only intent, owner-source
affirmation, and the exact sixteen all-true safety confirmations. Caller input
is deep-copied and missing or unexpected fields fail closed.

Results require exact identity/schema/output class/label/provenance, copied
safe reference lists, four separate finding buckets, and exact hard-false
operation flags. Only `succeeded` may contain findings. Every item has a safe
unique ID, exact category mappings, safe diagnostic text, exact evidence,
matching locator, reference lists, app-owned provenance/label, confidence and
uncertainty, pending/unapproved owner decision,
`candidate_review_pending`, and hard-false runtime/official/model/external
source/project-state flags. Evidence items contain only `source_excerpt` and
`source_locator`.

Confidence is limited to `low_support` and `medium_support`; `high_support` is
rejected. Ambiguity and insufficient-evidence categories require their exact
uncertainty labels. Questions allow only `null` or
`requires_owner_interpretation`; substantive observations allow bounded
non-truth uncertainty metadata.

Recursive validation rejects unsafe claims or requests at any result depth,
while request `source_text` and evidence `source_excerpt` remain exact
owner-source quotation exemptions. Unsafe output is rejected, never rewritten
or sanitized. The legitimate app-owned identity and support label are allowed.

The fail-closed builder never raises for ordinary malformed input, returns the
exact app-owned failed-closed envelope with empty buckets and hard-false flags,
copies only independently validated safe reference lists, never copies source
text, and bounds or replaces unsafe reasons.

## Validation

- T020C focused tests: `237 passed`.
- Requested T019C/T009/runtime-integration/orchestrator/persistence/preflight
  regression selection: `560 passed` (one environment-only NVML warning).
- The normalized successful result is accepted by
  `validate_analysis_runtime_output` with a synthetic allowlist permitting
  `rubric_mapping_support`; this is schema compatibility, not external runtime
  execution.
- The required T009, T019C, generic runtime-integration, orchestrator,
  persistence, and preflight regressions pass (see task validation output).
- JSON, enrichment, roadmap, diff, and worktree checks pass.

## Preserved boundaries

T009, T019C, T020A, T020B, and `analysis_runtime_integration.py` are unchanged.
No dramatica-flow import, execution, or source read occurred. No external
material was copied. No evaluator or adapter was added. No model, provider,
server, network, subprocess, shell, persistence, review-queue, project/truth
state, Memory/Canon, promotion/apply-promotion, training-artifact, or prose
operation was performed or enabled.

## Next frontier

`PHASE8-IMPL-023-T020` remains `in_progress`. The next task is:

`PHASE8-IMPL-023-T020D — App-owned dramatica-flow-informed analysis-rubric evaluator`

T020D must implement a pure local deterministic/rule-assisted evaluator using
this committed contract and original app-owned rules. It must not read or
execute dramatica-flow, call a model, persist candidates, mutate state, or
generate prose.
