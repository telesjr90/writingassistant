# PHASE8-IMPL-023-T020D — App-owned dramatica-flow-informed analysis-rubric evaluator

## Result

PASS — a pure local deterministic/rule-assisted in-memory evaluator now
consumes the committed T020C request contract and returns only normalized
T020C results. No OMI adapter is implemented by this task.

## Public surface and contract flow

The public surface is exactly:

```python
DRAMATICA_FLOW_INFORMED_RUBRIC_EVALUATOR_VERSION = (
    "app_owned_dramatica_flow_informed_rubric_evaluator.v1"
)

def evaluate_dramatica_flow_informed_analysis_rubric(
    request: object,
) -> dict[str, object]:
    ...
```

All other evaluator helpers are private. The flow is:

```text
request
  -> deep copy
  -> validate_dramatica_flow_informed_rubric_request
  -> normalized request
  -> original app-owned deterministic rules
  -> T020C result envelope
  -> validate_dramatica_flow_informed_rubric_result
  -> normalized result
```

The module imports only `copy`, `re`, `typing`, and the committed T020C
contract module. Caller input is never mutated.

## Original cue groups and category thresholds

The bounded module-level cue groups are original app-owned ordinary-English
signals: causal connectors; consequence language; open commitments; commitment
follow-through; emotional states; emotional changes; relationship roles;
relationship changes; temporal ordering; thread activity/return/delay;
knowledge access; information transfer/concealment; uncertainty; and narrowly
phrased conflicting signals.

The six substantive categories emit on the first span containing either of
their paired signal families. One family gives `low_support`; both independent
families in the same span give `medium_support`:

- `causal_chain_diagnostic`: causal connector or consequence signal.
- `narrative_commitment_lifecycle_diagnostic`: open commitment or
  follow-through signal.
- `emotional_state_consistency`: emotional state or emotional-change signal.
- `relationship_delta_diagnostic`: relationship role or relationship-change
  signal.
- `timeline_thread_activity_diagnostic`: temporal-order or thread-activity
  signal.
- `information_boundary_diagnostic`: knowledge-access or information-transfer
  signal.

`multidimensional_diagnostic_question` requires one evidence span supporting
at least two distinct substantive dimensions. `ambiguity` requires a bounded
uncertainty cue or a narrowly phrased conflicting signal. `owner_review_question`
always emits for every valid non-empty source. `insufficient_evidence` is
decided only after substantive evaluation.

## Precedence, evidence, and item IDs

The evaluator splits source text at sentence punctuation (`.`, `!`, `?`, `;`,
`:`) and line boundaries into ordered non-empty spans. Each emitted excerpt is
the unchanged original span and therefore an exact `source_text` substring;
only a separate local copy is normalized for matching.

Categories run in `requested_categories` order and spans run in source order.
At most one item emits per category. The first qualifying span wins, including
when a later span could receive stronger confidence. IDs use the category's
one-based request position plus its exact name:

```text
rubric_item_NN_<category>
```

This ordering and ID policy makes repeated evaluation equal and deterministic.

## Confidence, uncertainty, empty, and insufficient evidence

`high_support` is never emitted. Questions, ambiguity, and insufficient
evidence use `low_support`. A substantive observation uses `medium_support`
only when both independent signal families match in the selected span and
otherwise uses `low_support`. Questions use
`requires_owner_interpretation`; ambiguity and insufficient evidence use their
exact committed values; ordinary substantive observations use `null`; a
narrow conflicting-signal match may use `conflicting_support`.

The exact material-length threshold is fewer than 12 word tokens.
`insufficient_evidence` emits when requested and either the source is below
that threshold or no substantive diagnostic category fired. It does not emit
merely because another requested category did not match. If no requested
category emits, the result is `empty`, not `error`.

## Evidence, provenance, owner review, and failure behavior

Every item uses the exact T020C category mappings and fixed app-owned
diagnostic wording, carries one exact source excerpt and the request locator
and reference lists, uses exact app-owned provenance/support labeling, remains
pending and unapproved with `candidate_review_pending`, and keeps every item
and result operation flag false. Questions end with `?`. Diagnostic wording is
not copied from evidence and does not request story writing or changes.

All failures use the committed T020C fail-closed builder:

- invalid request: `request_validation_failed`;
- invalid generated result: `result_validation_failed`;
- unexpected exception: `unexpected_evaluator_failure`.

The committed result validator is the final safety gate.

## Safety boundaries and validation

The evaluator performs no file or environment access, subprocess/shell/network
operation, model/provider/server call, external-source read, project-state
read or mutation, persistence, queue creation, Memory/Canon mutation,
promotion/apply-promotion, training-artifact operation, or story-prose
generation/change. It does not import or execute dramatica-flow and does not
run `df`. No external code, prompt, template, algorithm, issue text,
suggestion, generated material, or project-state semantics were copied.

Validation results:

- compile validation: PASS;
- focused T020D evaluator tests: `142 passed`;
- requested T020C/T019D/T009/runtime-integration/orchestrator/persistence/
  preflight regression selection: `787 passed`, with one environment-only NVML
  warning;
- successful and failed-closed shapes remain compatible with generic
  `rubric_mapping_support` runtime-output validation.

T009 fixture identity/contract, T019D evaluator, T020A preflight hard-false
runtime state, T020B reference-only decision, T020C contract, generic runtime
integration, orchestrator, and persistence behavior are preserved. No existing
contract or test file was modified.

## Next frontier

Open question 121 is resolved by the rules above. `PHASE8-IMPL-023-T020`
remains `in_progress`. The next child is:

```text
PHASE8-IMPL-023-T020E
App-owned dramatica-flow-informed analysis-rubric OMI adapter integration
planned
```

T020E must add a new explicit-only app-owned OMI adapter identity distinct from
T009 `dramatica_flow`, preserve candidate-only evidence/provenance-backed
pending-review fail-closed behavior, and default to no persistence. T020E is
not implemented here; do not skip to T021.
