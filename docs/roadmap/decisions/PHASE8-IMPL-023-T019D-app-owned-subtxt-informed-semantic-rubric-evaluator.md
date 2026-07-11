# PHASE8-IMPL-023-T019D — App-owned Subtxt-informed semantic-rubric evaluator

## Task

Implement a pure, local, deterministic/rule-assisted, in-memory evaluator
that consumes the committed T019C request contract and produces the
committed T019C result contract. The evaluator is a contract-only consumer:
it never executes Subtxt, never reads or copies external Subtxt
documentation, never calls a model, never persists candidates or creates
review-queue entries, never mutates Memory/Canon, never creates promotion
records, never runs apply-promotion, and never generates story prose.
OMI adapter integration is intentionally deferred to T019E.

## Module location

`backend/story_knowledge/subtxt_informed_semantic_rubric_evaluator.py`

## Test location

`tests/test_omi_subtxt_informed_semantic_rubric_evaluator.py`

## Public surface

Exactly two public symbols:

```python
SUBTXT_INFORMED_RUBRIC_EVALUATOR_VERSION = (
    "app_owned_subtxt_informed_rubric_evaluator.v1"
)

def evaluate_subtxt_informed_semantic_rubric(
    request: object,
) -> dict[str, object]:
    ...
```

All other helpers in the module are private (underscore-prefixed). The
single public evaluator function is the only callable. The module is
imported by the test file but is not wired into OMI, routes, UI, or
persistence paths.

## Contract-usage flow

The evaluator reuses the committed T019C public surface from
`backend/story_knowledge/subtxt_informed_semantic_rubric_contract.py`:

```text
request
  -> validate_subtxt_informed_rubric_request
  -> normalized_request
  -> deterministic evaluator rules
  -> T019C result envelope
  -> validate_subtxt_informed_rubric_result
  -> normalized_result
```

Failure paths:

- On request validation failure, the evaluator returns a fail-closed
  result through
  `build_subtxt_informed_rubric_fail_closed_result("request_validation_failed", ...)`.
- On result validation failure (an internal mismatch between the produced
  result and the T019C contract), the evaluator returns a fail-closed
  result with the deterministic reason `result_validation_failed`.
- On any unexpected exception, the evaluator returns a fail-closed
  result with the deterministic reason `unexpected_evaluator_failure`.

The supplied request is never mutated: every call deep-copies the
request before passing it to the T019C request validator.

## Deterministic source segmentation

The evaluator uses only standard-library string and regular-expression
operations on the validated `source_text`:

1. `source_text` is split into ordered non-empty evidence spans using a
   single regex that matches sentence-ending punctuation (`.`, `!`, `?`)
   and any newline sequence. Line endings are normalized only on a
   cue-matching copy of each span; the original `source_text` and each
   evidence excerpt are preserved as exact substrings of the owner-
   provided source.
2. Empty spans (including whitespace-only spans) are removed.
3. Each selected evidence excerpt is an exact substring of the
   owner-provided source (the T019C contract validator confirms the
   excerpt is a non-empty string; the test suite confirms it appears in
   the original `source_text`).
4. Spans are processed in source order.
5. At most one item is emitted per requested category. The first
   matching span wins.
6. Categories are processed in the order of `requested_categories` from
   the normalized request.

## Cue groups (original app-owned, module-level constants)

The cue vocabulary is defined in module-level tuples and compiled into
case-insensitive regex patterns. Cue lists are NOT read from external
files and NOT imported from `.external_sources`. The cue groups are:

- Intention cues: `want`, `need`, `must`, `seek`, `try`, `plan`, `decide`,
  `attempt` (with simple morphological variants such as `wants`,
  `wanting`, `decides`, `deciding`, `attempted`, etc.).
- Resistance cues: `but`, `however`, `unless`, `until`, `prevent`, `block`,
  `risk`, `fail`, `because` (with simple morphological variants such as
  `prevents`, `blocked`, `risks`, `failing`, etc.).
- Opposing-pressure cues (extending the resistance set with): `against`,
  `versus`, `refuse`, `oppose`, `threaten`, `compete`, `despite`.
- Pronoun cues (first/third-person pronoun groups).
- Relationship cues: `mentor`, `rival`, `partner`, `parent`, `child`,
  `friend`, `team`.
- Temporal/change cues: `before`, `after`, `then`, `when`, `until`,
  `later`, `changes`, `decides`, `discovers`, `reveals`, `returns`.
- Causal cues: `because`, `therefore`, `causes`, `forces`, plus multi-
  word `leads to`, `results in`.
- Uncertainty cues: `maybe`, `perhaps`, `might`, `could`, `seems`,
  `appears`, `unclear`, `unknown`, `possibly`, `not sure`.

## Per-category rules

The evaluator implements the nine T019C categories with original
app-owned rules. Categories are processed in `requested_categories`
order; the first non-empty evidence span that satisfies a category's
cue rule emits exactly one item for that category.

1. `structural_diagnostic` — fires when a single evidence span contains
   at least one intention cue AND at least one resistance cue. Label
   `Intention and resistance signal`. Confidence `medium_support`.
   Statement kind `candidate_observation`. Uncertainty label `null`.

2. `conflict_diagnostic` — fires when a span contains at least one
   opposing-pressure cue. Label `Opposing pressure signal`. Confidence
   `low_support`. Statement kind `candidate_observation`. Uncertainty
   label `null`.

3. `throughline_context_question` — fires when a span contains at least
   two distinct actor-signal categories (any two of: a pronoun cue,
   two or more distinct capitalized name-like tokens, a relationship
   cue). Question text: `Which perspective should the owner use when
   reviewing the goal and resistance signals in this evidence?`
   Confidence `low_support`. Statement kind `question`. Uncertainty
   label `requires_owner_interpretation`.

4. `story_point_context_question` — fires when a span contains a
   temporal/change cue. Question text: `Which structural context best
   describes the change indicated by this evidence?` Confidence
   `low_support`. Statement kind `question`. Uncertainty label
   `requires_owner_interpretation`.

5. `source_of_conflict_hypothesis` — fires only when a single span
   contains a causal cue AND a resistance cue. Label `Possible
   resistance mechanism`. Confidence `medium_support`. Statement kind
   `hypothesis`. Uncertainty label `requires_owner_interpretation`.

6. `subject_vs_conflict_question` — fires when a span contains an
   actor/topic signal (pronoun or capitalized name-like token) and
   does NOT contain any opposing-pressure cue. Question text: `Does
   the highlighted subject actively create resistance, or is it only
   the topic being described?` Confidence `low_support`. Statement
   kind `question`. Uncertainty label
   `requires_owner_interpretation`.

7. `ambiguity` — fires when a span contains at least one uncertainty
   cue. Label `Uncertain structural reading`. Confidence `low_support`.
   Statement kind `ambiguity`. Uncertainty label `ambiguity`.

8. `insufficient_evidence` — decided at the orchestrator level. When
   requested, the evaluator emits one `insufficient_evidence` item if
   the complete source has fewer than 12 word tokens OR if no
   substantive non-question category fired. Label `Limited diagnostic
   support`. Candidate type `evidence_note`. Confidence `low_support`.
   Statement kind `insufficient_evidence`. Uncertainty label
   `insufficient_evidence`.

9. `owner_review_question` — when requested, the evaluator emits one
   question from the first non-empty evidence span. Question text:
   `What additional owner-provided context would clarify the
   structural reading of this evidence?` Candidate type
   `diagnostic_question`. Confidence `low_support`. Statement kind
   `question`. Uncertainty label `requires_owner_interpretation`.

## Output construction

Each emitted item includes:

- `item_id` derived from the category with a deterministic
  zero-padded numeric prefix (e.g. `rubric_item_01_structural_diagnostic`).
- `category` from the request's category name.
- `candidate_type` from the T019C `CATEGORY_TO_CANDIDATE_TYPE` mapping.
- `label` from the per-category fixed app-owned label.
- `diagnostic_text` from the per-category fixed app-owned wording
  (original app-owned text; never derived from the owner source).
- `statement_kind` from the T019C `CATEGORY_TO_STATEMENT_KIND` mapping
  for non-question categories; `question` for the four question
  categories; `insufficient_evidence` for the `insufficient_evidence`
  category.
- `evidence` — a single evidence item containing the exact
  `source_excerpt` (a verbatim substring of the owner source) and the
  request `source_locator`. Evidence excerpts are NEVER copied into
  `diagnostic_text`.
- `source_locator` = the validated request `source_locator` (and
  appears in `source_locator_refs`).
- `source_refs`, `evidence_refs`, `provenance_refs` copied from the
  validated request top-level reference lists.
- `source_locator_refs` copied from the validated request and
  containing the `source_locator`.
- `provenance` = the T019C app-owned provenance object:
  `{"tool_source": "app_owned_subtxt_informed_rubric", "adapter":
  "app_owned_subtxt_informed_rubric", "support": "App-owned
  Subtxt-informed diagnostic support", "executes_subtxt": False,
  "official_subtxt_output": False}`.
- `support_label` = `App-owned Subtxt-informed diagnostic support`.
- `confidence` per the confidence policy below.
- `uncertainty_label` per the uncertainty policy below.
- `owner_decision = {"approved": False, "decision": "pending"}`.
- `review_status = "candidate_review_pending"`.
- `executes_subtxt = False` and `official_subtxt_output = False`.

## Confidence policy

- `medium_support` when a category rule requires and finds two
  distinct cue groups in a single span (currently
  `structural_diagnostic` and `source_of_conflict_hypothesis`).
- `low_support` for all question categories, `ambiguity`, and
  `insufficient_evidence`.
- `high_support` is NEVER emitted in T019D; the only `confidence`
  values in the output are `medium_support` and `low_support`.

## Uncertainty policy

- `ambiguity` category -> `uncertainty_label = "ambiguity"`.
- `insufficient_evidence` category -> `uncertainty_label =
  "insufficient_evidence"`.
- Question categories and the `source_of_conflict_hypothesis`
  hypothesis -> `uncertainty_label = "requires_owner_interpretation"`.
- All other observation categories -> `uncertainty_label = "null"`.

## Result status and placement

- Status `succeeded` when at least one candidate or question is emitted
  in `candidate_support` or `diagnostic_questions`.
- Status `empty` when no requested category produces an item; the
  result has empty `candidate_support` and empty `diagnostic_questions`
  but the all-`False` safety object and app-owned provenance.
- Status `failed_closed` only through the fail-closed builder, used
  for `request_validation_failed`, `result_validation_failed`, and
  `unexpected_evaluator_failure`.
- Status `error` is never produced by T019D for normal no-match
  behavior.

Non-question items go to `candidate_support`. Question-category items
go to `diagnostic_questions`. The result-level `uncertainty_notes` and
`insufficient_evidence_notes` lists are populated as empty lists
because the T019C contract does not require separate uncertainty/insuff-
icient-evidence top-level notes; the per-item `uncertainty_label` and
`insufficient_evidence` item carry the equivalent information.

## T019C validator usage

- The evaluator deep-copies the supplied request, calls
  `validate_subtxt_informed_rubric_request`, and uses the returned
  `normalized_request` to drive all evaluation.
- The evaluator constructs a result envelope (with the exact schema
  version, rubric id, output class, display label, provenance,
  safety, and required field set), then calls
  `validate_subtxt_informed_rubric_result` on the constructed result.
- The evaluator returns the `normalized_result` from the validator, so
  the returned dict is always a T019C-normalized result.
- If the produced result fails T019C validation, the evaluator returns
  `build_subtxt_informed_rubric_fail_closed_result("result_validation_failed", ...)`.
- On any unexpected exception, the evaluator returns
  `build_subtxt_informed_rubric_fail_closed_result("unexpected_evaluator_failure", ...)`.
- The fail-closed result still validates through the T019C result
  validator when the supplied request contains valid reference lists.

## Fail-closed behavior

| Trigger | Result | Reason |
| --- | --- | --- |
| `request` is not a dict | fail-closed | `request_validation_failed` |
| `validate_subtxt_informed_rubric_request` returns non-`valid` | fail-closed | `request_validation_failed` |
| `validate_subtxt_informed_rubric_result` returns non-`valid` on produced result | fail-closed | `result_validation_failed` |
| Any unexpected exception | fail-closed | `unexpected_evaluator_failure` |

`error` is never produced by the T019D evaluator.

## Generic runtime compatibility

The normalized valid result is compatible with the existing generic
`analysis_runtime_integration.validate_analysis_runtime_output` when
validated against an allowlist record whose `output_classes_allowed`
includes `rubric_mapping_support`. The test suite confirms both the
`succeeded` and `failed_closed` shapes pass the generic
`validate_analysis_runtime_output` validator. The T019D module does not
import or call `analysis_runtime_integration`. The generic validator is
authoritative and unchanged.

## No external documentation copying

The evaluator does not import, read, or copy any text from
`.external_sources/subtxt-docs` or any other Subtxt-related
documentation. The cue vocabulary, labels, diagnostic text, and
question text are original app-owned strings. No source code, README
content, comment, or page structure is copied from external sources.

## No live Subtxt execution

The evaluator does not execute Subtxt, does not call any CLI, does
not invoke a Nuxt documentation site command, does not import
`.external_sources/subtxt-docs`, and does not start or communicate
with any Subtxt-related process. It is a pure in-memory deterministic
function.

## No OMI integration

The evaluator is not wired into the OMI orchestrator (`backend/
omi_analysis_orchestrator.py`), the OMI preflight (`backend/
omi_runtime_preflight.py`), the FastAPI routes (`backend/main.py`),
the OMI adapter registry, or any other OMI integration surface. It is
a self-contained module that consumes the T019C request contract and
produces the T019C result contract. OMI integration is intentionally
deferred to `PHASE8-IMPL-023-T019E`.

## Tests

81 focused in-memory tests in
`tests/test_omi_subtxt_informed_semantic_rubric_evaluator.py` cover
every required test area. Tests use in-memory dictionaries only. No
real project files are read in tests. The real `.external_sources`
checkout is not used.

The required coverage areas (1-40 in the task brief) are all
exercised; the actual test file currently reports `81 passed`. Key
coverage areas:

1. Exact evaluator version constant and single public evaluator API.
2. Valid request produces a valid T019C result (succeeded).
3. Invalid request returns fail-closed result with reason
   `request_validation_failed`.
4. Caller request is not mutated on valid and invalid inputs.
5. Repeated evaluation is deterministic.
6. Category order follows the request's `requested_categories` order
   for both candidate_support and diagnostic_questions.
7. At most one item per category in both candidate_support and
   diagnostic_questions.
8. Each of the nine categories triggers independently with an
   appropriate fixture source.
9. Each category does not trigger without its required cues
   (the `insufficient_evidence` case is exercised both with and
   without a substantive match found).
10. Category-to-candidate-type mapping is exact against the T019C
    `CATEGORY_TO_CANDIDATE_TYPE` dictionary.
11. Non-question items go to `candidate_support`; question items go
    to `diagnostic_questions`.
12. Statement-kind mapping is exact against the T019C
    `CATEGORY_TO_STATEMENT_KIND` dictionary; question items always
    have `statement_kind == "question"`.
13. Evidence excerpt is an exact substring of the source text.
14. Evidence is not copied into generated diagnostic text.
15. Top-level reference lists and `source_locator` are preserved on
    the result and on each item; the `source_locator` appears in
    each item's `source_locator_refs`.
16. `owner_decision` and `review_status` remain
    `{"approved": False, "decision": "pending"}` and
    `"candidate_review_pending"` on every item.
17. Top-level and per-item provenance use the exact app-owned
    identity and support label.
18. The evaluator never uses the `subtxt` adapter or `tool_source`
    identity.
19. All result-level safety flags are exactly `False`.
20. No live or official Subtxt claim; the serialized result does not
    contain forbidden live/official Subtxt wording.
21. Confidence policy: no `high_support`; dual-cue observations emit
    `medium_support`; questions, ambiguity, and insufficient evidence
    emit `low_support`.
22. Uncertainty policy: ambiguity items use `ambiguity`,
    insufficient-evidence items use `insufficient_evidence`,
    questions and the hypothesis use `requires_owner_interpretation`,
    other observations use `null`.
23. Short input (>= 12 word tokens threshold rule) produces an
    `insufficient_evidence` item when requested.
24. No-match request returns `status: "empty"` with empty lists.
25. Owner-review question always emits for a valid non-empty source
    (two distinct source variants exercised).
26. `source_of_conflict_hypothesis` requires both a causal cue AND a
    resistance cue in the same span; a span with only a causal cue
    or only a resistance cue does NOT emit the hypothesis.
27. Every question `diagnostic_text` ends with `?`.
28. Source text containing quoted sensitive words like `canon`,
    `final`, `approved`, `rewrite`, or `outline` is preserved as
    evidence excerpts and does not cause false rejection.
29. Generated labels, diagnostic text, questions, metadata, and
    provenance pass the T019C recursive safety checks (the
    `validate_subtxt_informed_rubric_result` validator is the
    authoritative gate).
30. The evaluator result passes `validate_subtxt_informed_rubric_result`.
31. The evaluator result passes the generic
    `analysis_runtime_integration.validate_analysis_runtime_output`
    with output class `rubric_mapping_support` for both the
    `succeeded` and `failed_closed` shapes.
32. Unexpected internal evaluator failure returns fail closed with
    reason `unexpected_evaluator_failure` (test uses
    `monkeypatch` to make `_split_into_evidence_spans` raise).
33. No file I/O — the module source does not contain
    `open(`, `Path(`, or `with open(`.
34. No subprocess/shell/network — the module source does not contain
    `subprocess`, `urllib`, `requests`, `socket`, `http.client`, or
    `httpx`; a runtime guard monkeypatches `subprocess.run`,
    `subprocess.Popen`, and `socket.socket` and confirms none are
    called during evaluation.
35. No environment-variable read — the module source does not contain
    `import os`, `from os`, `os.environ`, or `getenv`.
36. No model import or call — the module source does not contain
    `openai`, `anthropic`, or `ollama`.
37. No project-storage helper import — the module source does not
    contain `project_manager`, `candidate_storage`,
    `candidate_index`, `candidate_record`, `candidate_schema`,
    `review_queue_storage`, `raw_artifacts`,
    `raw_extraction_storage`, `candidate_persistence`,
    `candidate_review_gate`, or `apply_promotion`.
38. No candidate-persistence call — the module source does not
    contain `persist_candidate`, `create_candidate`,
    `save_candidate`, `write_candidate`, `add_candidate`,
    `store_candidate`, or `persist_finding`.
39. No promotion/apply-promotion call — the module source does not
    contain `apply_promotion`, `promote_to_canon`,
    `promotion_record`, `mutate_canon`, `mutate_memory`, or
    `approved_memory`.
40. No `.external_sources` import or read — the module does not
    have `.external_sources`, `subtxt_docs`, or
    `narrative_context_protocol` attributes; the module source does
    not contain those tokens.

Two additional safety tests are included:

- The module only imports the standard library plus the T019C
  contract module; an unexpected import is a hard test failure.
- The serialized evaluator result does not contain forbidden
  `storyform`, `dramatica`, or truth-final language.

### Actual test counts

* `tests/test_omi_subtxt_informed_semantic_rubric_evaluator.py`:
  `81 passed` (in-memory only, all mocked).

## Regression results

* `tests/test_omi_subtxt_informed_semantic_rubric_evaluator.py`
  (T019D new) → `81 passed`.
* `tests/test_omi_subtxt_informed_semantic_rubric_contract.py`
  (T019C contract) → `91 passed` (T019D did not modify the T019C
  contract).
* `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`
  → `103 passed` (T019D did not modify `analysis_runtime_integration.py`).
* `tests/test_writer_assistant_core_analysis_runtime_integration_handoff_contract.py`
  → `26 passed` (T019D did not modify the handoff module).
* `tests/test_writer_assistant_core_analysis_runtime_integration_safety_regression.py`
  → `115 passed` (T019D did not modify the safety regression module).
* `tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`
  (T009 NCP/Subtxt/dramatica-flow adapter regression) →
  `59 passed` (T019D did not modify the T009 contract).
* `tests/test_omi_tool_assisted_orchestrator_contract.py`
  (orchestrator) → `30 passed` (T019D did not modify the orchestrator).
* `tests/test_omi_tool_assisted_persistence_contract.py`
  (persistence) → `5 passed` (T019D did not modify persistence).
* `tests/test_omi_live_runtime_preflight_contract.py`
  (preflight) → `89 passed` (T019D did not modify the preflight).

Combined T019D + T019C + existing-regression validation: `599 passed`
across the nine contract test files listed above. No
`python3 -m py_compile` failure on the T019D evaluator module or the
T019C contract module. No contract or backend file outside the
allowlist was modified.

## Roadmap frontier

- `PHASE8-IMPL-023-T019D` → `complete/PASS`.
- `PHASE8-IMPL-023-T019` parent → still `in_progress`.
- Live Subtxt runtime → still `owner-blocked`.
- Evaluator implemented, but not connected to OMI.
- Next child: `PHASE8-IMPL-023-T019E — App-owned Subtxt-informed
  semantic-rubric OMI adapter integration` (status `planned`).

T019E scope (as recorded by this decision):

```text
Integrate the committed T019D evaluator into the OMI analysis
orchestrator under a new app-owned adapter identity such as
subtxt_informed_rubric, never under the existing subtxt identity. Reuse
the committed T019C request/result contracts, preserve T009 unchanged,
add explicit fail-closed adapter gating and candidate-only
normalization, and prove no persistence, Memory/Canon mutation,
promotion, apply-promotion, model call, external documentation read,
live Subtxt claim, or story prose. Manual real owner-authored
validation remains a later child.
```

Do not skip to T020.

## Safety and scope confirmations

- No live Subtxt execution.
- No `subtxt` provenance or adapter identity.
- No external documentation read or copied.
- No model call.
- No OMI integration.
- No T019C contract modification.
- No existing test file modification.
- No file, network, subprocess, or environment-variable access.
- No persistence or queue creation.
- No Memory/Canon mutation.
- No promotion/apply-promotion.
- No story prose.
- No stage, commit, or push.

## Known unrelated leftovers preserved

The following files remain untouched and uncommitted during T019D and
are explicitly preserved as the unrelated known leftovers:

- `artifacts/mvp-readiness/owner-acceptance/checklist-results.json`
  (dirty since a previous task).
- `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`
  (dirty since a previous task).
- `artifacts/mvp-readiness/owner-acceptance/workflow-log.json`
  (dirty since a previous task).
- `PHASE8-IMPL-023-T006-context-files.zip` (untracked).
- `PHASE8-IMPL-023-T018C1-recovery-context.zip` (untracked).
- `docs/Writing Assistant_OMI.pdf` (untracked).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T005-tool-assisted-orchestrator-contract-adapter-boundaries.md`
  (untracked).

## Result

`PASS` — pure, local, deterministic/rule-assisted, in-memory
evaluator is implemented and validated in-memory with 81 focused
tests. The evaluator consumes the T019C request contract and produces
the T019C result contract. It uses original app-owned cue rules, never
reads or copies external Subtxt documentation, never executes or
impersonates Subtxt, never calls a model, and never persists
candidates or mutates project, Memory, Canon, promotion, or prose
state. OMI adapter integration remains deferred to T019E. No
backend/test/frontend/package/dependency file outside the allowlist
was modified. No staging, commit, or push.
