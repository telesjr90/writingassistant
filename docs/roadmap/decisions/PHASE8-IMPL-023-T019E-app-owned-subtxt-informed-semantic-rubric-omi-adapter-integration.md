# PHASE8-IMPL-023-T019E — App-owned Subtxt-informed semantic-rubric OMI adapter integration

## Task

Integrate the committed T019D app-owned Subtxt-informed semantic-rubric
evaluator into the OMI analysis orchestrator under a new app-owned
adapter identity `subtxt_informed_rubric`, distinct from the existing
T009 `subtxt` adapter identity. Reuse the committed T019C request/result
contracts, preserve T009 unchanged, add explicit fail-closed adapter
gating and candidate-only normalization, and prove no persistence,
Memory/Canon mutation, promotion, apply-promotion, model call, external
documentation read, live Subtxt claim, or story prose.

The OMI adapter integration is owned by the orchestrator
(`backend/omi_analysis_orchestrator.py`) and exercised through
`analyze_omi_raw_idea_with_tools(requested_adapters=["subtxt_informed_rubric"])`.

## Identity roles

Three distinct identities are now in play, all preserved by the T019E
contract:

| Layer | Identity | Source |
| --- | --- | --- |
| OMI adapter identity | `subtxt_informed_rubric` | T019E (this task) |
| T019C/T019D internal rubric identity | `app_owned_subtxt_informed_rubric` | T019C (unchanged) |
| User-facing support label | `App-owned Subtxt-informed diagnostic support` | T019C (unchanged) |
| T009 fixture adapter identity | `subtxt` | T009 (unchanged) |
| T009 user-facing support label | `Subtxt diagnostic support only` | T009 (unchanged) |

The OMI adapter identity `subtxt_informed_rubric` is registered in
`OMI_TOOL_ADAPTER_IDENTITIES` and used by `OMI_ADAPTER_CONTRACTS`,
`adapter_contract(...)`, and the orchestrator's adapter-resolution path.

The T019C/T019D internal rubric identity `app_owned_subtxt_informed_rubric`
is preserved unchanged at
`backend/story_knowledge/subtxt_informed_semantic_rubric_contract.py`
and is used by the T019C request/result envelopes, the T019D evaluator,
and the T019E adapter boundary. The T019C contract validator
(`validate_subtxt_informed_rubric_result`) is the authoritative gate
for the evaluator's output; the OMI adapter is the boundary that
translates T019C results into OMI normalized findings.

The user-facing support label `App-owned Subtxt-informed diagnostic
support` is preserved by the T019C result envelope (`display_label`,
top-level and per-item `provenance.support`, and per-item
`support_label`) and is the only support label exposed through the
T019E adapter.

## Explicit-only adapter gate

The new adapter is registered in `OMI_TOOL_ADAPTER_IDENTITIES` and
`OMI_ADAPTER_CONTRACTS` and is intentionally absent from every default
or context route:

- Added to `OMI_TOOL_ADAPTER_IDENTITIES` (the orchestrator's
  authoritative identity allowlist).
- Added as a contract entry in `OMI_ADAPTER_CONTRACTS` (the orchestrator
  uses `adapter_contract(adapter_name)` to introspect every
  `OMI_TOOL_ADAPTER_IDENTITIES` member).
- Not added to `OMI_DEFAULT_ADAPTERS` (the default adapter set used when
  `requested_adapters is None`).
- Not added to `OMI_CONTEXT_ADAPTER_NAMES` (the T009 fixture
  diagnostic/context adapter set).
- Not routed through the T009 fixture contract path
  (`OMI_CONTEXT_ADAPTER_NAMES` / `_build_context_adapter_fixture_runner`).
- Not supported through `adapter_fixture_outputs`.
- No environment flags added (`OMI_LIVE_*`, `_BLOCKED`, etc.).
- No runtime preflight integration.
- Never treated as live Subtxt or as `executes_subtxt=True`.
- The explicit `requested_adapters=["subtxt_informed_rubric"]` request
  is the only T019E activation path; the explicit injected
  `adapter_runners["subtxt_informed_rubric"]` override (test-only
  extension point) retains precedence over the built-in runner.

## Adapter contract entry

The T019E `OMI_ADAPTER_CONTRACTS["subtxt_informed_rubric"]` entry
documents the adapter boundary:

- Behavior: app-owned, local, deterministic/rule-assisted diagnostic
  support only; pure in-memory evaluation of the T019C request contract
  through the T019D evaluator; not live Subtxt; not a model; not a
  truth/Storyform oracle; no generated prose; no
  rewrite/continuation/outline; evidence/source-locator required;
  owner-review pending; candidate-only; no automatic persistence,
  canon mutation, promotion record, or apply-promotion.
- `produces_candidates: True`.
- `supports_finding_types` (bounded set): `structural_diagnostic`,
  `conflict_diagnostic`, `diagnostic_question`, `ambiguity`,
  `evidence_note`.

The bounded set is a subset of `OMI_ORCHESTRATOR_FINDING_TYPES` and
covers exactly the T019C category-to-candidate-type mapping. The
context-only types `throughline_context`, `storyform_context`,
`open_question`, `continuity_warning`, and `world_rule` are not in the
T019E contract, because T019D does not produce them. No additional
finding types are introduced.

## T019C request construction

T019E adds `_build_subtxt_informed_rubric_request(...)` in
`backend/omi_analysis_orchestrator.py`. The helper builds the request
from the committed T019C constants and OMI `project_name` /
`raw_idea` / `source_idea_id` inputs.

Exact fields and values used by the helper:

- `schema_version = sisc.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION`
- `rubric_id = sisc.SUBTXT_INFORMED_RUBRIC_ID`
- `request_id = "subtxt_informed_rubric_<16 hex characters>"`
  (deterministic SHA-256 of
  `safe_project_name + NUL + source_idea_id-or-empty + NUL + raw_idea`,
  hex prefix).
- `project_name = original_name` when it matches `[A-Za-z0-9_-]+`;
  otherwise `project_<16 hex characters>` (deterministic safe
  contract-only alias). The actual OMI `project_name` is never mutated
  and the OMI orchestrator never sees the alias.
- `source_text = raw_idea` (owner source passed through unchanged).
- `source_locator = "source_locator_ref_raw_idea"`.
- `source_refs = ["source_ref_raw_idea"]`.
- `evidence_refs = ["evidence_ref_raw_idea"]`.
- `provenance_refs = ["provenance_ref_subtxt_informed_rubric"]`.
- `source_locator_refs = ["source_locator_ref_raw_idea"]` (and the
  per-item `source_locator` must appear in this list, per the T019C
  contract).
- `requested_categories = list(OMI_SUBTXT_INFORMED_RUBRIC_REQUESTED_CATEGORIES)`
  (deterministic 9-tuple, in exact committed order).
- `analysis_intent = "diagnostic_support"`.
- `owner_authored_or_owner_provided_source = True`.
- `safety_confirmations` = dictionary whose 13 required keys
  (`no_subtxt_execution`, `no_official_subtxt_output_claim`,
  `no_storyform_truth`, `no_generated_prose`, `no_rewrite`,
  `no_continuation`, `no_outline`, `no_candidate_persistence`,
  `no_review_queue_creation`, `no_memory_canon_mutation`,
  `no_promotion_record`, `no_apply_promotion`, `no_training_artifacts`)
  are all exactly `True`.

The helper calls `validate_subtxt_informed_rubric_request` (the
authoritative T019C contract gate) before invoking the T019D evaluator.
The T019D evaluator also re-validates the request internally. The
adapter boundary fails closed on a request-validation failure
(adapter-envelope state `failed_closed`, no candidates, non-empty
explanation).

## T019D invocation flow

T019E adds `_build_subtxt_informed_rubric_runner(...)` in
`backend/omi_analysis_orchestrator.py`. The builder:

1. Validates `adapter_config` strictly as `dict | None`.
2. Lazily imports the committed T019C validator/constants
   (`backend.story_knowledge.subtxt_informed_semantic_rubric_contract`)
   and the T019D evaluator
   (`backend.story_knowledge.subtxt_informed_semantic_rubric_evaluator`)
   inside the runner closure (never at module import time).
3. Invokes the T019D evaluator exactly once per runner call
   (`sise.evaluate_subtxt_informed_semantic_rubric(request)`).
4. Never reads files, never reads environment variables, never reads
   project storage, never reads external documentation, never calls a
   model, never calls a live Subtxt runtime, and never persists
   anything.

The runner returns a normal OMI adapter-envelope dict
(`{adapter, state, explanation, candidates}`) so the existing
`validate_adapter_result` validator remains authoritative.

## Evaluator status mapping

The T019E runner maps the T019C evaluator result status to the OMI
adapter-envelope state:

| T019C evaluator status | OMI adapter-envelope state | Notes |
| --- | --- | --- |
| `succeeded` AND normalized candidates are non-empty | `succeeded` | Carries the normalized findings. |
| `succeeded` AND normalized candidates are empty | `empty` | Clears findings list. |
| `empty` | `empty` | Clears findings list. |
| `failed_closed` | `failed_closed` | No findings. |
| `error` | `error` | No findings. |
| Unknown / malformed / unsafe / exception | `failed_closed` | No findings. |

Every non-`succeeded` OMI state carries `candidates: []` and a non-empty
`explanation`. The runner never silently converts an invalid
evaluator output into a `succeeded` or `empty` result. Every adapter
envelope passes through the existing
`validate_adapter_result` validator at the orchestrator's
adapter-loop boundary.

## Result-to-OMI normalization

T019E adds `_normalize_subtxt_informed_rubric_item(item)` in
`backend/omi_analysis_orchestrator.py`. The normalizer:

1. Combines the T019D `candidate_support` and `diagnostic_questions`
   lists into a single list of T019C items.
2. Restores deterministic evaluator order by sorting the combined
   list on the committed deterministic `item_id` prefix
   (`rubric_item_NN_<category>`) before normalization, so the OMI
   adapter envelope is stable across runs and across process
   restarts.
3. Maps each T019C item to the existing OMI normalized-finding
   schema with these exact fields:
   - `candidate_type = item["candidate_type"]` (T019C contract
     mapping).
   - `label = item["label"]` (preserved; never rewritten).
   - `extracted_claim = item["diagnostic_text"]` (the per-category
     app-owned diagnostic text, never derived from owner source).
   - `evidence = item["evidence"]` (the single T019C evidence item
     with verbatim owner source excerpt and `source_locator_ref_raw_idea`).
   - `source_locator = item["source_locator"]`.
   - `provenance` = `{"tool_source": "subtxt_informed_rubric",
     "adapter": "subtxt_informed_rubric", "support": "App-owned
     Subtxt-informed diagnostic support"}`. The OMI provenance uses
     the OMI adapter identity because the existing
     `validate_normalized_finding` requires `provenance.adapter`,
     `provenance.tool_source`, and `source_adapter` to match.
   - `source_adapter = "subtxt_informed_rubric"`.
   - `support_label = "App-owned Subtxt-informed diagnostic support"`.
   - `owner_decision = {"approved": False, "decision": "pending"}`.
   - `review_status = "candidate_review_pending"`.
   - `raw_finding_id = "subtxt_informed_rubric::" + item["item_id"]`.
   - `confidence = item["confidence"]` (one of
     `low_support` / `medium_support`; never `high_support` per the
     T019D confidence policy).
   - `uncertainty_label = item["uncertainty_label"]` (one of
     `null` / `ambiguity` / `insufficient_evidence` /
     `conflicting_support` / `requires_owner_interpretation`).

The normalizer does not copy evidence excerpts into
`extracted_claim`, does not convert questions into story facts, does
not mark anything approved, and never claims Storyform truth.

Each converted item runs through the existing
`validate_normalized_finding`. One invalid item fails the whole
adapter call closed (`failed_closed`, `candidates: []`, non-empty
explanation). No partial candidate set is ever returned on failure.

## Evidence, provenance, and owner-review preservation

- Evidence excerpts are preserved as exact substrings of the owner
  source. T019C contract `validate_subtxt_informed_rubric_result`
  guarantees the excerpt is a non-empty string; the T019E adapter
  passes the evidence through unchanged.
- The `source_locator` field on every item equals
  `source_locator_ref_raw_idea` (the adapter-constructed locator
  string) and appears in the per-item `source_locator_refs` list per
  the T019C contract.
- The T019D evaluator's per-item provenance uses the T019C
  `app_owned_subtxt_informed_rubric` identity and the T019C support
  label `App-owned Subtxt-informed diagnostic support` with
  `executes_subtxt=False` and `official_subtxt_output=False`. The
  T019C result validator (`validate_subtxt_informed_rubric_result`)
  is the authoritative gate for this T019C provenance.
- The T019E OMI adapter converts the per-item T019C provenance to the
  OMI adapter identity `subtxt_informed_rubric` (with the same T019C
  support label) so the OMI `validate_normalized_finding` validator
  (which requires `provenance.adapter`, `provenance.tool_source`,
  and `source_adapter` to match) accepts the finding. The
  per-item `owner_decision` stays
  `{"approved": False, "decision": "pending"}` and `review_status`
  stays `candidate_review_pending` on every item.
- `support_label` and `provenance.support` both equal
  `App-owned Subtxt-informed diagnostic support`, never `truth`,
  `canon`, `approved`, `promoted`, or any Storyform claim.

## Fail-closed behavior

The T019E adapter is fail-closed at every layer:

- Unknown OMI adapter identity → existing T005 path returns
  `unavailable` with no candidates.
- `analyze_omi_raw_idea_with_tools` with empty `raw_idea` → existing
  T005 short-circuit returns `empty` with `analysis_status: "empty"`
  and `candidates: []`; every requested adapter envelope is
  `state: "skipped"`.
- `_resolve_adapter_runner` is not the implementation path
  (`adapter_runners` may override; no fixture path; no live path;
  no preflight path).
- `_build_subtxt_informed_rubric_request` exception →
  `failed_closed` (no candidates, non-empty explanation).
- `validate_subtxt_informed_rubric_request` exception or non-`valid`
  response → `failed_closed`.
- `evaluate_subtxt_informed_semantic_rubric` exception →
  `failed_closed`.
- Evaluator returns a non-dict → `failed_closed`.
- `validate_subtxt_informed_rubric_result` exception or non-`valid`
  response → `failed_closed`.
- T019C result has no `normalized_result` dict → `failed_closed`.
- T019C status is unknown → `failed_closed`.
- T019C `candidate_support` / `diagnostic_questions` item fails
  `_normalize_subtxt_informed_rubric_item` or
  `validate_normalized_finding` → `failed_closed` (the whole adapter
  call is closed; no partial candidate set is ever returned).
- Adapter envelope `candidates` is `[]` for every non-`succeeded`
  OMI state.

## Persistence boundary

T019E does not add, call, or change persistence logic. The T019E
adapter never persists candidates, never mutates projects, never
mutates Memory/Canon, never creates promotion records, and never
runs `apply-promotion`. The existing
`persist_candidates=False` orchestrator path is preserved unchanged.

All focused T019E tests use `persist_candidates=False` and confirm:

- `persistence_status == "not_requested"`
- `persisted_candidate_ids == []`
- `new_candidate_ids == []`
- `reused_candidate_ids == []`

The existing generic caller-controlled persistence path
(`backend.project_manager.persist_omi_tool_assisted_findings_as_candidates`)
is not exercised by T019E and is unchanged.

## No preflight/env/live-runtime integration

T019E adds no environment variables, no `OMI_LIVE_*` flags, no
`OMI_LIVE_SUBTXT_INFORMED_*` constants, no `_BLOCKED` overrides, no
runtime preflight probes, no `_ncp_resolve_allowed_input_path`-style
allowlist resolvers, no `OMI_LIVE_NCP_VALIDATE_WITH_NODE`-style
opt-in subprocesses, and no `.external_sources` reads. The
T019E adapter is a pure in-memory orchestration extension.

The existing T019A preflight
(`subtxt_live_runtime_available: False`) and T019A risk vocabulary
are preserved unchanged.

## T009 preservation

- T009 adapter identity `subtxt` is preserved unchanged.
- `OMI_SUBTXT_SCHEMA_VERSION = "omi_subtxt_diagnostic_handoff.v1"` is
  preserved unchanged.
- T009 support label `Subtxt diagnostic support only` is preserved
  unchanged.
- T009 `OMI_CONTEXT_ADAPTER_NAMES` is preserved unchanged.
- T009 fixture validation
  (`validate_context_adapter_fixture_envelope(adapter_name="subtxt")`)
  is preserved unchanged.
- T009 fixture runner (`_build_context_adapter_fixture_runner`) is
  preserved unchanged.
- T009 fixture routing in `_resolve_adapter_runner` is preserved
  unchanged.
- T019A preflight `subtxt_live_runtime_available: False` is preserved
  unchanged.
- `analysis_runtime_integration.py` is preserved unchanged (T019C
  result is compatible with
  `analysis_runtime_integration.validate_analysis_runtime_output`
  for output class `rubric_mapping_support`; the generic validator
  is unchanged).
- All live adapter branches (T014C, T015C, T016C, T017B, T018B) are
  preserved unchanged.
- `deterministic_fallback` and persistence behavior are preserved
  unchanged.

No current `subtxt` test is repurposed to test the new adapter.
The new tests live in
`tests/test_omi_subtxt_informed_semantic_rubric_omi_adapter_contract.py`
and use in-memory inputs and `monkeypatch` /
`unittest.mock.patch.object` only. The existing orchestrator test
file is updated only to add the new identity to the
`REQUIRED_ADAPTERS` allowlist set so the existing equality test
against `OMI_TOOL_ADAPTER_IDENTITIES` keeps passing; this is the
minimum modification required by the explicit-only adapter gate.

## Tests

T019E adds 78 focused in-memory tests in
`tests/test_omi_subtxt_informed_semantic_rubric_omi_adapter_contract.py`.
Tests use only the orchestrator module, the T019C contract module,
the T019D evaluator module, synthetic in-memory dictionaries, and
`unittest.mock.patch.object` / `monkeypatch`. No real project files
are read. The real `.external_sources/subtxt-docs` checkout is not
used.

Coverage areas (61 areas covered, 78 tests):

1. exact adapter identity constant.
2. identity registered in `OMI_TOOL_ADAPTER_IDENTITIES`.
3. adapter contract exists.
4. supported finding types are bounded.
5. supported finding types exclude context-only types.
6. adapter contract describes app-owned diagnostic-only behavior.
7. adapter is absent from `OMI_DEFAULT_ADAPTERS`.
8. default orchestrator call does not run the new adapter.
9. adapter is absent from `OMI_CONTEXT_ADAPTER_NAMES`.
10. adapter does not route through the T009 fixture contract.
11. existing `subtxt` identity remains present.
12. existing `subtxt` contract entry remains.
13. explicit request resolves the built-in runner.
14. explicit orchestrator call runs the built-in runner.
15. omitted request does not run the new adapter.
16. unrelated explicit request does not run the new adapter.
17. injected `adapter_runners` override retains precedence.
18. `adapter_fixture_outputs` is not the implementation path.
19. exact category tuple and ordering.
20. request construction uses the exact category tuple.
21. request uses the committed T019C schema and rubric identity.
22. request validates through the T019C request validator.
23. deterministic safe request id.
24. different inputs produce different request ids.
25. request id uses a safe identifier pattern.
26. valid project name preserved.
27. unsafe project name converted to deterministic safe alias.
28. unsafe project alias is deterministic.
29. non-string project name converted to safe alias.
30. raw owner source passed unchanged.
31. exact source locator and four reference collections.
32. all 13 safety confirmations are `True`.
33. evaluator invoked exactly once per runner call.
34. actual committed evaluator succeeds through the orchestrator.
35. structural diagnostic normalization.
36. conflict diagnostic normalization.
37. diagnostic-question normalization.
38. ambiguity normalization.
39. evidence-note normalization.
40. deterministic item ordering.
41. exact OMI `source_adapter` and provenance identity.
42. exact support label.
43. evidence excerpt and locator preserved.
44. confidence and uncertainty preserved.
45. owner decision remains pending and unapproved.
46. review status remains candidate-review-pending.
47. `succeeded` status maps correctly.
48. `empty` status maps correctly.
49. `failed_closed` status maps correctly.
50. `error` status maps correctly.
51. malformed evaluator result fails closed.
52. non-dict evaluator result fails closed.
53. unsafe evaluator result fails closed.
54. evaluator exception fails closed.
55. one invalid normalized item fails the whole adapter call closed.
56. no partial findings on failure.
57. no live/official Subtxt wording in adapter envelopes and
    evidence excerpts.
58. no `subtxt` provenance identity in converted items.
59. no Storyform / truth / canon / approval claim.
60. owner source containing `canon`, `approved`, `rewrite`, or
    `outline` remains analyzable evidence.
61. `persist_candidates=False` produces no persistence.
62. no Memory/Canon mutation.
63. no promotion/apply-promotion.
64. no story-prose generation.
65. no file, subprocess, network, model, environment, or
    `.external_sources` operation.
66. runner does not open files.
67. existing T009 `subtxt` fixture behavior remains unchanged.
68. mixed invocation with an existing adapter remains valid.
69. empty raw idea follows the existing skipped-adapter short
    circuit.
70. whitespace-only raw idea follows the existing skipped-adapter
    short circuit.
71. orchestrator fusion accepts the normalized findings.
72. runner rejects non-dict `adapter_config`.
73. runner accepts `None` `adapter_config`.
74. runner accepts dict `adapter_config`.
75. request id is safe for unicode source.
76. `source_idea_id` appears in the request id.
77. provenance conversion uses OMI adapter identity (not internal
    rubric).
78. adapter runner counts invocations correctly.

### Actual test counts

- `tests/test_omi_subtxt_informed_semantic_rubric_omi_adapter_contract.py`
  (T019E new) → `78 passed` (in-memory only, all mocked).
- T019D evaluator regression
  (`tests/test_omi_subtxt_informed_semantic_rubric_evaluator.py`) →
  `81 passed`.
- T019C contract regression
  (`tests/test_omi_subtxt_informed_semantic_rubric_contract.py`) →
  `91 passed`.
- T009 NCP/Subtxt/dramatica-flow regression
  (`tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`) →
  `59 passed`.
- Orchestrator regression
  (`tests/test_omi_tool_assisted_orchestrator_contract.py`) →
  `30 passed`.
- Persistence regression
  (`tests/test_omi_tool_assisted_persistence_contract.py`) →
  `5 passed`.
- Generic runtime-integration regressions
  (`tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`,
  `tests/test_writer_assistant_core_analysis_runtime_integration_handoff_contract.py`,
  `tests/test_writer_assistant_core_analysis_runtime_integration_safety_regression.py`)
  → `103 passed`, `26 passed`, `115 passed` (T019E did not modify
  `analysis_runtime_integration.py`).
- Preflight regression
  (`tests/test_omi_live_runtime_preflight_contract.py`) → `89 passed`
  (T019E did not modify the preflight).

Combined T019E + T019D + T019C + existing-regression validation: all
focused T019E + regression suites pass.

## Roadmap frontier

- `PHASE8-IMPL-023-T019E` → `complete/PASS`.
- T019 parent: still `in_progress`.
- Live Subtxt runtime: still `owner-blocked` (T019A / T019B).
- App-owned Subtxt-informed semantic-rubric OMI adapter integration
  is implemented in `backend/omi_analysis_orchestrator.py` and
  validated in-memory, but is **not** yet manually validated
  end-to-end against a real owner-authored raw idea.
- Next child: `PHASE8-IMPL-023-T019F — Manual real owner-authored
  Subtxt-informed rubric validation` (status `planned`).

T019F scope (as recorded by this decision):

```text
Run one explicit real in-process OMI orchestrator validation using
requested_adapters=["subtxt_informed_rubric"] and persist_candidates=False
against a controlled owner-authored raw idea designed to exercise multiple
T019D diagnostic categories. Verify the built-in adapter and evaluator are
reached exactly once, produce non-empty evidence-backed candidate-only
findings with subtxt_informed_rubric OMI provenance, pending owner decisions,
candidate-review-pending status, and no persistence, project mutation,
Memory/Canon mutation, promotion/apply-promotion, model call, external
documentation read, live Subtxt claim, or story prose. Preserve before/after
snapshots and record the actual result. Do not skip directly to T020.
```

## Safety and scope confirmations

- Adapter identity is `subtxt_informed_rubric`.
- Existing `subtxt` identity is unchanged.
- New adapter is not in defaults (`OMI_DEFAULT_ADAPTERS`).
- New adapter is not in T009 context names (`OMI_CONTEXT_ADAPTER_NAMES`).
- No live Subtxt execution or claim.
- No environment / preflight integration.
- No external documentation read or copied.
- No model call.
- No contract / evaluator / preflight / main / project_manager
  modification.
- No existing test modification (only the minimum one-line addition
  of `"subtxt_informed_rubric"` to the existing test file's
  `REQUIRED_ADAPTERS` allowlist set, required by the explicit-only
  adapter gate that mandates adding the identity to
  `OMI_TOOL_ADAPTER_IDENTITIES`).
- No new persistence logic.
- No project, Memory, or Canon mutation.
- No promotion / apply-promotion.
- No story prose.
- No stage, commit, or push.

## Known unrelated leftovers preserved

The following files remain untouched and uncommitted during T019E and
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

`PASS` — app-owned Subtxt-informed semantic-rubric OMI adapter
integration is implemented in `backend/omi_analysis_orchestrator.py`
and validated in-memory with 78 focused tests. The committed T019C
request/result contract and the committed T019D evaluator are
reused unchanged. T009 `subtxt` adapter, T019C contract, T019D
evaluator, `analysis_runtime_integration`, T013 runtime preflight,
T014C / T015C / T016C / T017B / T018B live adapter branches, and
all other backend modules and existing test files are preserved
unchanged (except for the minimum one-line addition to the existing
orchestrator test file's `REQUIRED_ADAPTERS` allowlist). No live
Subtxt execution, no `subtxt` provenance / adapter identity in
OMI outputs, no external documentation read or copied, no model
call, no Memory/Canon mutation, no automatic promotion records, no
automatic apply-promotion, no story prose, no candidate persistence,
no staging, commit, or push. Manual real owner-authored validation
remains a separate T019F child task.

## Next task

`PHASE8-IMPL-023-T019F — Manual real owner-authored Subtxt-informed
rubric validation`

Status: `planned`.

T019F scope (as recorded by this decision):

```text
Run one explicit real in-process OMI orchestrator validation using
requested_adapters=["subtxt_informed_rubric"] and persist_candidates=False
against a controlled owner-authored raw idea designed to exercise multiple
T019D diagnostic categories. Verify the built-in adapter and evaluator are
reached exactly once, produce non-empty evidence-backed candidate-only
findings with subtxt_informed_rubric OMI provenance, pending owner decisions,
candidate-review-pending status, and no persistence, project mutation,
Memory/Canon mutation, promotion/apply-promotion, model call, external
documentation read, live Subtxt claim, or story prose. Preserve before/after
snapshots and record the actual result. Do not skip directly to T020.
```

Do not skip to T020.
