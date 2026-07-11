# PHASE8-IMPL-023-T019C — App-owned Subtxt-informed semantic-rubric contract

## Task

Implement a pure, app-owned input/output contract for future
Subtxt-informed semantic-rubric evaluation. This task defines and
validates data shapes only. It does not execute Subtxt, does not
implement an evaluator, does not inspect or classify real project
text, does not call a model, does not add an OMI adapter, does not
change the existing T009 `subtxt` adapter contract, does not persist
candidates, and does not mutate projects, Memory, or Canon.

The new contract has an identity distinct from the existing T009
live/fixture adapter identity. The new contract identity is
`app_owned_subtxt_informed_rubric` and its user-facing support label
is `App-owned Subtxt-informed diagnostic support`. The forbidden
T009-style wording (`subtxt`, `Subtxt runtime result`, `Live Subtxt
analysis`, `Official Subtxt diagnosis`, `Subtxt-confirmed Storyform`)
is never used as the new contract's adapter or provenance identity.

## Module location

`backend/story_knowledge/subtxt_informed_semantic_rubric_contract.py`

## Test location

`tests/test_omi_subtxt_informed_semantic_rubric_contract.py`

## Public constants

```python
SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION = (
    "omi_app_owned_subtxt_informed_rubric_request.v1"
)

SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION = (
    "omi_app_owned_subtxt_informed_rubric_result.v1"
)

SUBTXT_INFORMED_RUBRIC_ID = "app_owned_subtxt_informed_rubric"

SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS = "rubric_mapping_support"

SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL = (
    "App-owned Subtxt-informed diagnostic support"
)
```

## Public APIs

Exactly three public validator / safe-builder functions:

* `validate_subtxt_informed_rubric_request(request: object) -> dict`
* `validate_subtxt_informed_rubric_result(result: object) -> dict`
* `build_subtxt_informed_rubric_fail_closed_result(reason: str, *, request: dict | None = None) -> dict`

No evaluator (no `run_*`, `analyze_*`, `evaluate_*`, `classify_*`,
`infer_*`, `generate_*`) is added. The module is contract-only.

## Request schema

A valid request is a dictionary containing exactly the required
logical fields:

* `schema_version` = `omi_app_owned_subtxt_informed_rubric_request.v1`
* `rubric_id` = `app_owned_subtxt_informed_rubric`
* `request_id` = non-empty safe identifier
* `project_name` = non-empty safe identifier
* `source_text` = non-empty string (owner-authored or owner-provided)
* `source_locator` = non-empty safe source locator
* `source_refs` = non-empty list of non-empty safe strings
* `evidence_refs` = non-empty list of non-empty safe strings
* `provenance_refs` = non-empty list of non-empty safe strings
* `source_locator_refs` = non-empty list of non-empty safe
  `source_locator_ref_*` strings, and `source_locator` must appear
  in this list
* `requested_categories` = non-empty deduplicated list of allowed
  categories
* `analysis_intent` = exactly `diagnostic_support`
* `owner_authored_or_owner_provided_source` = exactly `True`
* `safety_confirmations` = dictionary whose 13 required keys are all
  exactly `True`:
  `no_subtxt_execution`, `no_official_subtxt_output_claim`,
  `no_storyform_truth`, `no_generated_prose`, `no_rewrite`,
  `no_continuation`, `no_outline`, `no_candidate_persistence`,
  `no_review_queue_creation`, `no_memory_canon_mutation`,
  `no_promotion_record`, `no_apply_promotion`, `no_training_artifacts`.

## Diagnostic categories

The exact app-owned category set is:

```
structural_diagnostic
conflict_diagnostic
throughline_context_question
story_point_context_question
source_of_conflict_hypothesis
subject_vs_conflict_question
ambiguity
insufficient_evidence
owner_review_question
```

Normalized candidate-type mapping (the rubric never implies
Storyform truth):

```
structural_diagnostic              -> structural_diagnostic
conflict_diagnostic                -> conflict_diagnostic
throughline_context_question       -> diagnostic_question
story_point_context_question       -> diagnostic_question
source_of_conflict_hypothesis      -> conflict_diagnostic
subject_vs_conflict_question       -> diagnostic_question
ambiguity                          -> ambiguity
insufficient_evidence              -> evidence_note
owner_review_question              -> diagnostic_question
```

Non-question categories map to a required `statement_kind`:

```
structural_diagnostic              -> candidate_observation
conflict_diagnostic                -> candidate_observation
source_of_conflict_hypothesis      -> hypothesis
ambiguity                          -> ambiguity
insufficient_evidence              -> insufficient_evidence
```

Question categories require `candidate_type == "diagnostic_question"`
and `statement_kind == "question"`. Question `diagnostic_text` must
end with `?`. Questions may ask the owner to clarify evidence or
interpretation; they must not request prose, rewriting, continuation,
outlining, drafting, polishing, expansion, improvement, revision, or
imitation.

## Result-envelope schema

A valid result is a dictionary containing exactly the required
logical fields:

* `schema_version` = `omi_app_owned_subtxt_informed_rubric_result.v1`
* `rubric_id` = `app_owned_subtxt_informed_rubric`
* `output_class` = `rubric_mapping_support`
* `display_label` = `App-owned Subtxt-informed diagnostic support`
* `status` = one of `succeeded`, `empty`, `failed_closed`, `error`
* `provenance` = the app-owned provenance object below
* `source_refs`, `evidence_refs`, `provenance_refs` = non-empty lists
  of non-empty safe strings
* `source_locator_refs` = non-empty list of non-empty
  `source_locator_ref_*` strings
* `candidate_support` = list (items follow the candidate-support
  schema)
* `diagnostic_questions` = list (items follow the question schema)
* `uncertainty_notes` = list
* `insufficient_evidence_notes` = list
* `safety` = the safety object below

Status rules:

* `succeeded` requires at least one valid item in `candidate_support`
  or `diagnostic_questions`
* `empty`, `failed_closed`, and `error` must contain no items in
  `candidate_support` or `diagnostic_questions`.

## Required app-owned provenance

Top-level and per-item provenance must be exactly:

```python
{
    "tool_source": "app_owned_subtxt_informed_rubric",
    "adapter": "app_owned_subtxt_informed_rubric",
    "support": "App-owned Subtxt-informed diagnostic support",
    "executes_subtxt": False,
    "official_subtxt_output": False,
}
```

The contract rejects:

* `tool_source == "subtxt"`
* `adapter == "subtxt"`
* `executes_subtxt == True`
* `official_subtxt_output == True`
* wording that claims official Subtxt execution, compatibility,
  confirmation, or endorsement.

## Support and uncertainty fields

* `support_label` must equal `App-owned Subtxt-informed diagnostic support`.
* `confidence` must be one of `low_support`, `medium_support`,
  `high_support`. Confidence is support metadata only and is never
  truth.
* `uncertainty_label` must be one of `null`, `ambiguity`,
  `insufficient_evidence`, `conflicting_support`,
  `requires_owner_interpretation`.
* Category `ambiguity` requires
  `uncertainty_label == "ambiguity"`.
* Category `insufficient_evidence` requires
  `uncertainty_label == "insufficient_evidence"`.
* Question categories may use `requires_owner_interpretation`.
* No uncertainty value is interpreted as truth or approval.

## Owner-decision and review fields

Every candidate and every diagnostic question must contain exactly:

```python
"owner_decision": {"approved": False, "decision": "pending"}
```

and `review_status == "candidate_review_pending"`. Approved findings,
accepted/final/canon/promoted review states, owner decisions other
than `pending`, automatic rejection or promotion, and any field that
implies apply-promotion are rejected.

## Evidence item schema

Each candidate or question must contain a non-empty `evidence` list.
Every evidence item must contain `source_excerpt` and `source_locator`
as non-empty strings. Evidence excerpts are quoted owner source
material and may contain otherwise sensitive words; the contract
never rewrites, sanitizes, or rejects evidence excerpts. The contract
never copies source excerpts into newly invented diagnostic prose.

## Result safety object

The result-level `safety` object must contain all of the following
exact `False` values:

```
executes_subtxt
official_subtxt_output
persists_candidates
creates_review_queue_entries
mutates_memory_canon
creates_promotion_records
applies_promotion
generates_prose
rewrites_prose
continues_prose
creates_outline
creates_training_artifacts
```

A supplied `True` value is not silently defaulted to `False`; the
contract fails closed on any supplied unsafe value.

## Recursive unsafe-output rejection

Outside `source_text` and evidence `source_excerpt` (which are
quoted owner source material), the contract fails closed on
normalized labels, claims, questions, metadata, and operation
fields when the text contains truth/final/canon/approved/promoted
assertions, definitive Storyform claims, definitive OS/MC/IC/RS
claims, definitive problem/solution/concern/issue/domain/approach/
dynamic/signpost claims, official Subtxt execution or endorsement
claims, generated prose, rewrite/continuation/outline/draft/
polish/improve/expand/revise/imitate/chapter-generation requests,
candidate persistence requests, review-queue creation requests,
Memory/Canon mutation, promotion records, apply-promotion,
training/model artifacts, or project/scene/note/material mutation
fields. The contract never sanitizes an unsafe normalized output
into a safe-looking claim; it rejects it.

## Validation response convention

Both validators return a result dictionary rather than raising for
ordinary invalid input. A valid response includes
`status="valid"`, `valid=True`, `fail_closed=False`, `errors=[]`,
`normalized_request` (or `normalized_result`), and all operation
flags set to `False`. An invalid response includes
`status="fail_closed"`, `valid=False`, `fail_closed=True`, and a
non-empty deterministic `errors` list. All operation flags are
always `False`, including for invalid results.

## Fail-closed builder

`build_subtxt_informed_rubric_fail_closed_result(reason, *, request=None)`
returns a complete result-envelope-shaped dict with
`status="failed_closed"`, zero findings, safe app-owned provenance,
and every operation flag set to `False`. It includes a non-empty
reason (falling back to `"fail_closed"` if the supplied reason is
blank or non-string), copies top-level refs from a valid request
when available, tolerates a missing or invalid request, and never
throws. The result is fail-closed, has no persistence/queue/canon/
promotion/prose side effect, and never claims Subtxt execution.

## Generic analysis-runtime compatibility

The normalized valid result is compatible with the existing
`backend.story_knowledge.analysis_runtime_integration.validate_analysis_runtime_output`
when validated against an allowlist record whose
`output_classes_allowed` includes `rubric_mapping_support`. The
generic validator remains authoritative and unchanged. The T019C
module is not an OMI adapter; it does not call, replace, or
reconfigure the generic validator.

## No T009 contract changes

The T009 contract is preserved unchanged:

* `OMI_SUBTXT_SCHEMA_VERSION = "omi_subtxt_diagnostic_handoff.v1"`
* existing T009 adapter identity `subtxt`
* existing T009 support label `Subtxt diagnostic support only`
* T019A `subtxt_live_runtime_available: False`
* `analysis_runtime_integration` boundary:
  `SUPPORTED_ACTIONS["Subtxt"] == {"build_rubric_mapping_support"}`,
  `TOOL_BOUNDARIES["Subtxt"] == "rubric/diagnostic guidance only"`,
  `executes_subtxt == False`.

## No live Subtxt execution

The T019C contract is pure, deterministic, in-memory only. It does
not execute Subtxt, does not read or import
`.external_sources/subtxt-docs`, does not copy Subtxt
documentation, does not inspect or classify real project text, does
not call a model, does not implement an OMI adapter, does not add a
route or UI, does not persist candidates, does not create review
queue entries, does not mutate Memory/Canon, does not create
promotion records, does not run apply-promotion, and does not
generate story prose.

## Tests

91 focused in-memory tests added to
`tests/test_omi_subtxt_informed_semantic_rubric_contract.py`. The
tests cover:

1. Exact public schema/version/identity constants and T009 contract
   preservation.
2. Generic analysis-runtime-integration Subtxt boundary preservation.
3. Valid request normalization (deep-copy preserved).
4. Valid succeeded result normalization.
5. Empty result with no items.
6. Failed-closed result with no items.
7. Error result with no items.
8. Succeeded status rejected when no items exist.
9. Non-succeeded status rejected when findings exist.
10. Every allowed category validates at minimum.
11. Exact category-to-candidate-type mapping.
12. Unknown category fails closed.
13. Question categories require
    `candidate_type == "diagnostic_question"`.
14. Question `diagnostic_text` must end with `?`.
15. Prose-intent questions fail closed.
16. `adapter == "subtxt"` or `tool_source == "subtxt"` fails closed
    on result and per-item.
17. `executes_subtxt=True` fails closed.
18. `official_subtxt_output=True` fails closed.
19. Missing evidence excerpt or locator fails closed.
20. Missing evidence list fails closed.
21. Item `source_locator` must appear in `source_locator_refs`.
22. Empty item refs fail closed.
23. Owner source text and evidence excerpts may contain quoted words
    like `canon`, `final`, `approved`, `rewrite`, `outline` without
    being rewritten or falsely rejected.
24. Truth/final/canon/approved language in normalized labels or
    diagnostic text fails closed.
25. Auto-approved owner decision fails closed.
26. Non-pending review status (including `accepted`, `promoted`,
    `accepted_final`) fails closed.
27. Unsafe persistence, Memory/Canon, promotion, apply-promotion,
    training, or mutation fields in normalized diagnostic text fail
    closed.
28. Missing/false request safety confirmation fails closed.
29. Ambiguity and insufficient-evidence uncertainty rules.
30. Question may use `requires_owner_interpretation` uncertainty.
31. Fail-closed builder always returns zero findings and all
    operation flags false, tolerates missing/invalid request, copies
    top-level refs from a valid request when available, and
    validates through the T019C result validator when given a valid
    request.
32. Module does not import `subprocess`, `urllib`, `requests`,
    `openai`, `anthropic`, `ollama`, `socket`, `http`, `pathlib`, or
    `os`; only `copy`, `re`, `__future__`, and `typing` are imported.
33. Validator does not call `subprocess.run`, `subprocess.Popen`, or
    `socket.socket` at runtime.
34. Validator does not import or read
    `.external_sources/subtxt-docs`.
35. Generic `rubric_mapping_support` allowlist record compatibility
    with `analysis_runtime_integration.validate_analysis_runtime_output`.
36. Succeeded result validates against the generic rubric mapping
    support validator.

Tests use in-memory dictionaries only. No real project files are
read in tests. The real `.external_sources/subtxt-docs` checkout is
not used.

### Actual test counts

* `tests/test_omi_subtxt_informed_semantic_rubric_contract.py`:
  `91 passed` (in-memory only, all mocked).

## Regression results

* `tests/test_omi_subtxt_informed_semantic_rubric_contract.py`
  (T019C new) → `91 passed`.
* `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`
  → `63 passed` (T019C did not modify
  `analysis_runtime_integration.py`).
* `tests/test_writer_assistant_core_analysis_runtime_integration_handoff_contract.py`
  → `8 passed` (T019C did not modify the handoff module).
* `tests/test_writer_assistant_core_analysis_runtime_integration_safety_regression.py`
  → `5 passed` (T019C did not modify the safety regression module).
* `tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`
  (T009 NCP/Subtxt/dramatica-flow adapter regression) →
  `30 passed` (T019C did not modify the T009 contract).
* `tests/test_omi_tool_assisted_orchestrator_contract.py`
  → `30 passed`.
* `tests/test_omi_tool_assisted_persistence_contract.py`
  → `5 passed`.
* `tests/test_omi_live_runtime_preflight_contract.py`
  → `23 passed`.

Combined T019C and existing-regression validation: `255 passed`
across the seven contract test files listed above. No
`python3 -m py_compile` failure on the new contract module.

## Result

`PASS` — pure, app-owned input/output contract for future
Subtxt-informed semantic-rubric evaluation is implemented and
validated in-memory with 91 focused tests. No evaluator, adapter,
model, prompt, route, UI, persistence, queue, Memory/Canon
mutation, promotion, apply-promotion, or story prose generation
behavior was added. No live Subtxt execution, no
`.external_sources` read or copy, and no T009 contract change. No
backend file other than the new contract module changed. No existing
test file changed. No package/dependency change. No subprocess,
shell, network, or server operation. No staging, commit, or push.

## Next task

`PHASE8-IMPL-023-T019D — App-owned Subtxt-informed semantic-rubric
evaluator`

T019D implements a pure local, deterministic/rule-assisted,
in-memory evaluator that consumes the committed T019C request
contract and produces the committed T019C result contract. It uses
original app-owned rubric logic, never reads or copies external
Subtxt documentation at runtime, never executes or impersonates
Subtxt, never calls a model, and never persists candidates or
mutates project, Memory, Canon, promotion, or prose state. OMI
adapter integration remains deferred. Do not skip directly to T020.
