# PHASE8-IMPL-023-T019F — Manual real owner-authored Subtxt-informed rubric validation

## Result

`PASS`.

`PHASE8-IMPL-023-T019F` ran one explicit real in-process OMI orchestrator
validation using the committed T019E built-in `subtxt_informed_rubric`
adapter and the committed T019D
`evaluate_subtxt_informed_semantic_rubric` evaluator through
`analyze_omi_raw_idea_with_tools(requested_adapters=["subtxt_informed_rubric"],
persist_candidates=False)` against a controlled non-story owner-authored
validation note. The committed built-in adapter and the committed
evaluator were each reached exactly once, the analysis succeeded with
non-empty candidate-only findings, every required provenance/owner-review/
safety-envelope assertion passed, the before/after protected snapshots
were identical, and no live Subtxt, model, network, subprocess,
environment, or external-documentation call was reached.

T019F is a manual validation + docs/status task. It does NOT modify
implementation code, the working tree, or any project/Memory/Canon
storage. It is the last child task under the T019 parent
(`PHASE8-IMPL-023-T019 - Live Subtxt integration in OMI and analysis`).

## Current HEAD and branch

* Branch: `docs/opencode-go-routing-small-task-execution`.
* HEAD before validation: `5e0d23bd18cefe665ba3bd3e788ee096aa793d4d`.
* HEAD after validation: `5e0d23bd18cefe665ba3bd3e788ee096aa793d4d`.
* HEAD before vs after: identical (no commit was performed during
  T019F; the T019E commit `5e0d23bd...` remains the current HEAD).

## Exact controlled validation input

```
Owner validation note: I want this analysis check to complete, but a blocked dependency prevents completion because the missing context creates risk. After I decide to continue, perhaps my partner and I still need to clarify which perspective applies.
```

The controlled input is test input only. It is not canon, not an
approved story fact, not stored in the project, not persisted as a
candidate, and not a request for generated story prose.

## Exact invocation arguments

```python
oao.analyze_omi_raw_idea_with_tools(
    "example",
    "Owner validation note: I want this analysis check to complete, "
    "but a blocked dependency prevents completion because the missing "
    "context creates risk. After I decide to continue, perhaps my "
    "partner and I still need to clarify which perspective applies.",
    source_idea_id="t019f_owner_validation",
    persist_candidates=False,
    requested_adapters=[oao.OMI_SUBTXT_INFORMED_RUBRIC_ADAPTER_NAME],
)
```

* `project_name="example"` (safe project name; preserved as the OMI
  project name; the request preserves the original because
  `example` matches `[A-Za-z0-9_-]+`).
* `source_idea_id="t019f_owner_validation"`. The committed
  orchestrator signature `analyze_omi_raw_idea_with_tools(...)` accepts
  `source_idea_id: str | None`; the value is passed through the
  committed `_build_subtxt_informed_rubric_request` helper, which uses
  it to derive a deterministic SHA-256-based `request_id` (the value
  itself is never persisted, never written to disk, never written to
  Memory/Canon, and never treated as canon).
* `persist_candidates=False`.
* `requested_adapters=["subtxt_informed_rubric"]`. The T019E explicit-
  only adapter gate is the only activation path; no
  `adapter_fixture_outputs` and no `adapter_runners` injection is
  passed, so the committed `_resolve_adapter_runner` path is forced
  to select the real built-in T019E runner.
* `allow_deterministic_fallback=False`. The controlled input is
  analyzed through the built-in T019E runner only; no
  `deterministic_fallback` adapter is appended.
* `adapter_runners=None`. No fake `adapter_runners` is injected; the
  committed `_resolve_adapter_runner` path must select the real
  built-in T019E adapter, which it does.

Environment flags were explicitly cleared before the run
(`OMI_LIVE_TOOLS_ENABLED`, `OMI_LIVE_NCP_ENABLED`,
`OMI_LIVE_NCP_BLOCKED`, `OMI_LIVE_OLLAMA_ENABLED`,
`OMI_LIVE_SPACY_ENABLED`, `OMI_LIVE_BOOKNLP_ENABLED`,
`OMI_LIVE_STORY_CHECK_ENABLED`, and
`OMI_LIVE_NCP_VALIDATE_WITH_NODE` were all popped from
`os.environ` to ensure no live runtime path is taken). The committed
T019E runner is in-memory only and the live-flag clearing is
defensive.

## Adapter builder / runner / evaluator counts

The validation script monkeypatch-wrapped (in-memory only, restored in
a `finally` block) exactly three callables:

* `backend.omi_analysis_orchestrator._build_subtxt_informed_rubric_runner`
  (the committed T019E built-in adapter builder),
* the returned built-in runner (the committed T019E
  `_runner(...)` closure), and
* `backend.story_knowledge.subtxt_informed_semantic_rubric_evaluator.evaluate_subtxt_informed_semantic_rubric`
  (the committed T019D evaluator).

Recorded counts from the in-process manual validation:

```text
adapter_builder_calls == 1
adapter_runner_calls  == 1
evaluator_calls       == 1
```

This proves the committed `_resolve_adapter_runner` path selected the
real built-in T019E adapter exactly once, the built-in T019E runner
was invoked exactly once, and the committed T019D evaluator was
invoked exactly once.

## Top-level analysis and persistence states

```text
analysis_status        == "succeeded"
persistence_status     == "not_requested"
persisted_candidate_ids == []
new_candidate_ids      == []
reused_candidate_ids   == []
findings               is non-empty
```

`findings` count = 8. No candidate was persisted; no
candidate storage path was touched; no review-queue path was
touched; no promotion record path was touched.

## Adapter result state

```text
adapter_results == [
  {
    "adapter": "subtxt_informed_rubric",
    "state": "succeeded",
    "explanation": "App-owned Subtxt-informed semantic-rubric adapter "
                   "produced 8 evidence-backed candidate-only "
                   "finding(s) through the committed T019D evaluator; "
                   "OMI adapter identity='subtxt_informed_rubric'; "
                   "T019C/T019D internal rubric identity="
                   "'app_owned_subtxt_informed_rubric'; support label="
                   "'App-owned Subtxt-informed diagnostic support'; "
                   "status mapping T019C succeeded -> OMI succeeded; "
                   "no live Subtxt execution; no model call; no "
                   "Memory/Canon mutation; no promotion/apply-promotion; "
                   "no story prose.",
    "candidates": [8 normalized findings]
  }
]
```

No other adapter ran. `other_adapter_names == []`. The T009
`subtxt` adapter identity was not requested in T019F and did not
run. The `deterministic_fallback` adapter was not requested and did
not run. The T018B live NCP adapter was not requested and did not
run. The T015C live Ollama adapter was not requested and did not
run. The T014C live spaCy adapter was not requested and did not run.
The T016C live Story Check adapter was not requested and did not
run. The T017B live BookNLP adapter was not requested and did not
run.

## Finding count and candidate types

Finding count: 8. Candidate types observed:

```text
structural_diagnostic     (1)
conflict_diagnostic       (2 items, including source_of_conflict_hypothesis)
diagnostic_question       (4 items: throughline_context_question,
                                story_point_context_question,
                                subject_vs_conflict_question,
                                owner_review_question)
ambiguity                 (1)
```

The committed bounded `OMI_SUBTXT_INFORMED_RUBRIC_ALLOWED_FINDING_TYPES`
allowlist (`structural_diagnostic`, `conflict_diagnostic`,
`diagnostic_question`, `ambiguity`, `evidence_note`) is a subset of
`OMI_ORCHESTRATOR_FINDING_TYPES`, and every emitted candidate type
belongs to it.

## Expected category coverage

Category IDs preserved by the committed T019E normalizer (extracted
from each finding's deterministic `raw_finding_id` of the form
`subtxt_informed_rubric::rubric_item_NN_<category>`):

```text
structural_diagnostic
conflict_diagnostic
throughline_context_question
story_point_context_question
source_of_conflict_hypothesis
subject_vs_conflict_question        (allowed but not required;
                                     fired on the controlled input)
ambiguity
owner_review_question
```

All 7 required category IDs from the T019F brief are present. The
brief explicitly notes that `subject_vs_conflict_question` and
`insufficient_evidence` are not required and may correctly decide not
to emit; here `subject_vs_conflict_question` fires on the controlled
input (allowed), and `insufficient_evidence` correctly decides not
to emit because the source has more than 12 word tokens and at
least one substantive non-question rule fired.

## Evidence / source-locator verification

Every finding has at least one evidence item. For every evidence
item:

* `source_excerpt` is non-empty.
* `source_excerpt` is an exact substring of the controlled input
  (verified directly against the controlled raw idea text in
  `raw-orchestrator-result.json`).
* `source_locator == "source_locator_ref_raw_idea"` (the committed
  raw-idea source locator produced by the T019E
  `_build_subtxt_informed_rubric_request` helper).

Every finding's top-level `source_locator ==
"source_locator_ref_raw_idea"`. The `source_locator` on every
item equals the committed T019C request `source_locator` and
appears in the per-item `source_locator_refs` list per the T019C
contract.

No evidence excerpt was copied into any `extracted_claim`. No
question was normalized as a story fact. No finding claims truth,
canon, approval, promotion, or official Subtxt output.

## Provenance and support-label verification

For every finding:

```text
source_adapter                  == "subtxt_informed_rubric"
provenance.adapter              == "subtxt_informed_rubric"
provenance.tool_source          == "subtxt_informed_rubric"
provenance.support              == "App-owned Subtxt-informed diagnostic support"
support_label                   == "App-owned Subtxt-informed diagnostic support"
```

The OMI provenance uses the OMI adapter identity
`subtxt_informed_rubric` (not the T019C internal identity
`app_owned_subtxt_informed_rubric`) because the existing
`validate_normalized_finding` requires `provenance.adapter`,
`provenance.tool_source`, and `source_adapter` to match. The T019C
internal provenance is validated before conversion by the T019C
result validator and is not duplicated in the OMI provenance.

`confidence` is one of `medium_support` (for the two dual-cue
observations `structural_diagnostic` and
`source_of_conflict_hypothesis`) or `low_support` (for the four
questions, the `ambiguity`, and the `conflict_diagnostic`
opposing-pressure observation). `high_support` is never emitted
(per the T019D confidence policy).

`uncertainty_label` is one of `null`,
`requires_owner_interpretation` (for the four questions and the
`source_of_conflict_hypothesis` hypothesis), or `ambiguity` (for
the `ambiguity` finding). It is uncertainty metadata only and is
never interpreted as truth or approval.

## Owner-decision and review-status verification

For every finding:

```text
owner_decision == {"approved": false, "decision": "pending"}
review_status  == "candidate_review_pending"
```

The orchestrator never auto-approves. Queue presence is not
approval. Candidate persistence is not canon. Confidence/support is
not truth. Tool/model output is not canon.

## Persistence result

```text
persistence_status      == "not_requested"
persisted_candidate_ids == []
new_candidate_ids       == []
reused_candidate_ids    == []
```

`persist_candidates=False` produces no persistence. The generic
caller-controlled persistence path
(`backend.project_manager.persist_omi_tool_assisted_findings_as_candidates`)
is not exercised by T019F and was never reached. No candidate
storage, no review-queue path, and no promotion record path was
touched.

## Before / after mutation proof

Captured before the manual invocation:

* `git rev-parse HEAD` = `5e0d23bd18cefe665ba3bd3e788ee096aa793d4d`.
* `git status --short --branch` shows only the pre-existing
  unrelated leftovers (T005 decisions file, T006 context zip, T018C1
  recovery zip, OMI PDF, and the three pre-existing dirty
  `artifacts/mvp-readiness/owner-acceptance/` files).
* `projects/` snapshot: SHA-256, byte size, and nanosecond mtime for
  every regular file under `projects/`, captured to
  `projects-before.json` (66 files, sorted by relative path).
* `git status --short -- projects/ .external_sources/` is empty.
* `git status --short -- .external_sources/` is empty.

Captured after the manual invocation and after the seven pytest
regressions:

* `git rev-parse HEAD` = `5e0d23bd18cefe665ba3bd3e788ee096aa793d4d`
  (identical to before; no commit was performed).
* `git status --short --branch` shows exactly the same unrelated
  leftovers; no new modified file; no new untracked path under
  `projects/`, `.external_sources/`, `ai_context/`,
  `graphify-out/`, or `artifacts/mvp-readiness/owner-acceptance/`.
* `projects/` snapshot: SHA-256, byte size, and nanosecond mtime
  for every regular file under `projects/`, captured to
  `projects-after.json` (66 files). The before and after
  `projects-*.json` files are byte-for-byte identical
  (`cmp -s` exits 0; `git diff --check` clean).
* `git status --short -- projects/ .external_sources/` is empty
  (identical to before).
* `git status --short -- .external_sources/` is empty (identical
  to before).

The validation process did not modify the repository. The T019F
evidence directory `.codex-context/PHASE8-IMPL-023/manual-validation/
T019F-subtxt-informed-rubric/` is preserved under the standard
`.codex-context/` ignore pattern (defined in `.git/info/exclude`)
and remains untracked. No staging, commit, or push was performed.

## Safety-envelope verification

The committed top-level safety envelope returned by
`build_orchestrator_safety_envelope()` is preserved intact
(every flag is `True`):

```text
no_prose                                == True
no_memory_canon_mutation                == True
no_apply_promotion                      == True
no_canon_promotion                      == True
no_real_tool_calls                      == True
no_story_prose_generation               == True
candidate_presence_is_not_canon         == True
queue_presence_is_not_approval          == True
support_is_not_truth                    == True
tool_output_is_not_canon                == True
```

The committed envelope also includes `no_package_installs == True`.
T019F did not install any package, did not start any server, and
did not perform any network, subprocess, environment, or external-
documentation read. No live Subtxt, model, network, subprocess,
environment, or external-documentation path was reached. The T019E
adapters gate remains intact: `subtxt_informed_rubric` is registered
in `OMI_TOOL_ADAPTER_IDENTITIES` and `OMI_ADAPTER_CONTRACTS`, is
absent from `OMI_DEFAULT_ADAPTERS` and `OMI_CONTEXT_ADAPTER_NAMES`,
has no fixture path, has no live-runtime path, has no preflight
integration, and has no environment-flag gate.

## Evidence-directory location

```text
.codex-context/PHASE8-IMPL-023/manual-validation/T019F-subtxt-informed-rubric/
```

Preserved evidence files (untracked, not staged, not committed,
not pushed):

```text
before-status.txt
after-status.txt
projects-before.json
projects-after.json
protected-paths-before.txt
protected-paths-after.txt
external-sources-before.txt
external-sources-after.txt
raw-orchestrator-result.json
invocation-counts.json
validation-summary.json
```

This evidence directory is allowed only for T019F manual-validation
evidence. No other `.codex-context/` path was created or modified
during T019F.

## Regression results

Run from the repo root with
`PYTHON=.venv-unsloth-clean/bin/python` and
`PYTHONPYCACHEPREFIX=/tmp/t019f-validation-pycache`:

```text
$ .venv-unsloth-clean/bin/python -m py_compile \
    backend/omi_analysis_orchestrator.py \
    backend/story_knowledge/subtxt_informed_semantic_rubric_contract.py \
    backend/story_knowledge/subtxt_informed_semantic_rubric_evaluator.py
exit 0

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_subtxt_informed_semantic_rubric_omi_adapter_contract.py \
    -q -p no:cacheprovider
78 passed in 0.35s

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_subtxt_informed_semantic_rubric_evaluator.py \
    -q -p no:cacheprovider
81 passed in 0.21s

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_subtxt_informed_semantic_rubric_contract.py \
    -q -p no:cacheprovider
91 passed in 0.20s

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_tool_assisted_orchestrator_contract.py \
    -q -p no:cacheprovider
30 passed in 0.73s

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_tool_assisted_persistence_contract.py \
    -q -p no:cacheprovider
5 passed in 0.11s

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py \
    -q -p no:cacheprovider
59 passed in 0.31s

$ .venv-unsloth-clean/bin/python -m pytest \
    tests/test_omi_live_runtime_preflight_contract.py \
    -q -p no:cacheprovider
89 passed, 5 warnings in 60.74s (0:01:00)
```

Combined: 433 passed across the seven contract test files. The
literal counts match the T019E decision-record baseline
(T019E 78, T019D 81, T019C 91, orchestrator 30, persistence 5, T009
context adapters 59, preflight 89). No regression was introduced
by T019F.

## No live Subtxt claim

The T019F manual validation does not claim live Subtxt execution.
The app-owned evaluator is described as `App-owned Subtxt-informed
diagnostic support` and the OMI adapter identity is
`subtxt_informed_rubric`. The T019C internal rubric identity is
`app_owned_subtxt_informed_rubric`. The forbidden T009-style
wording (`Subtxt runtime result`, `Live Subtxt analysis`, `Official
Subtxt diagnosis`, `Subtxt-confirmed Storyform`) was not used in
the OMI outputs, the adapter envelope, the per-item provenance,
the per-item support label, or the evidence excerpts.

## Live Subtxt runtime remains owner-blocked

The T019A preflight `subtxt_live_runtime_available: False` is
preserved unchanged. The T019B integration-path decision
(`Live Subtxt runtime: OWNER-BLOCKED`, `App-owned Subtxt-informed
semantic-rubric path: ACCEPTED`) is preserved unchanged. No live
Subtxt CLI, library, or API was called. No `.external_sources/
subtxt-docs/` was read or imported. The accepted app-owned
Subtxt-informed path is now both implemented in
`backend/omi_analysis_orchestrator.py` (T019E) and manually
validated against a real owner-authored raw idea (T019F).

## Actual result

`PASS`.

All T019F required-result assertions passed:

* built-in adapter builder called exactly once;
* built-in adapter runner called exactly once;
* committed evaluator called exactly once;
* `analysis_status == "succeeded"`;
* expected category coverage is present (all 7 required category
  IDs are present; `subject_vs_conflict_question` also fires on the
  controlled input, which is allowed);
* findings are non-empty (8 evidence-backed candidate-only
  findings) and contract-valid;
* provenance, evidence, owner-review, support-label, and safety
  assertions all passed (156 assertions in the manual
  verification script, all OK);
* persistence is not requested (`persistence_status ==
  "not_requested"`, empty `persisted_candidate_ids` /
  `new_candidate_ids` / `reused_candidate_ids`);
* before/after protected snapshots are identical (HEAD stable;
  `projects/` snapshot byte-for-byte identical; candidate/review/
  promotion paths clean; `.external_sources/` paths clean);
* no unsafe side effect occurred (no project / Memory / Canon
  mutation, no promotion record, no apply-promotion, no story
  prose, no live Subtxt, no model call, no network call, no
  subprocess, no environment-variable read for live-flag enable,
  no external-documentation read).

The T019 parent (`PHASE8-IMPL-023-T019 - Live Subtxt integration in
OMI and analysis`) is now complete/PASS. T019F is the last child
under the T019 parent. The next task is the existing roadmap task
that follows T019:

`PHASE8-IMPL-023-T020 - Live dramatica-flow integration in OMI and
analysis`

(per the current `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json`
child sequence: T020 is the next child after T019F; do not skip
to T021, T022, T023, T024, T025, or T026). T020 is the next
parent task to be executed by future T019+1 children. T020 is NOT
implemented in T019F; T020 is a future planned task whose
implementation is intentionally deferred to a later child.

## Safety and scope confirmations

* Real committed T019E built-in adapter used.
* Real committed T019D evaluator used.
* Each reached exactly once (counters above).
* No injected fake `adapter_runners` used; the committed
  `_resolve_adapter_runner` path was forced to select the real
  built-in T019E adapter by NOT passing `adapter_runners` and
  NOT passing `adapter_fixture_outputs`.
* No live Subtxt execution or claim.
* No existing T009 `subtxt` identity change.
* No model call.
* No network, subprocess, or environment access (live flags
  explicitly cleared before the run).
* No external documentation read (the T019E adapter and T019D
  evaluator never import or read `.external_sources`).
* No persistence.
* No project mutation (byte-for-byte identical `projects/`
  snapshot before and after).
* No Memory/Canon mutation.
* No promotion/apply-promotion.
* No story prose.
* No backend, test, frontend, or package/dependency file
  modification.
* The T019F evidence directory
  (`.codex-context/PHASE8-IMPL-023/manual-validation/T019F-subtxt-informed-rubric/`)
  is the only new untracked path; it remains untracked, unstaged,
  uncommitted, and unpushed.
* No stage, commit, or push was performed.

## Known unrelated leftovers preserved

The following files remain untouched and unstaged during T019F and
are explicitly preserved as the unrelated known leftovers (the
same set preserved by T019E and earlier T019 children):

* `artifacts/mvp-readiness/owner-acceptance/checklist-results.json`
  (dirty since a previous task).
* `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`
  (dirty since a previous task).
* `artifacts/mvp-readiness/owner-acceptance/workflow-log.json`
  (dirty since a previous task).
* `PHASE8-IMPL-023-T006-context-files.zip` (untracked).
* `PHASE8-IMPL-023-T018C1-recovery-context.zip` (untracked).
* `docs/Writing Assistant_OMI.pdf` (untracked).
* `docs/roadmap/decisions/PHASE8-IMPL-023-T005-tool-assisted-orchestrator-contract-adapter-boundaries.md`
  (untracked).

## Next task

`PHASE8-IMPL-023-T020 - Live dramatica-flow integration in OMI and
analysis`

(planned; per the current roadmap enrichment, T020 is the next
child after T019F; do not skip to T021, T022, T023, T024, T025, or
T026). T020 scope is "live dramatica-flow integration in OMI and
analysis" (the dramatica-flow subpath mirrors the T019 Subtxt
subpath: preflight, integration-path decision, contract,
evaluator, OMI adapter integration, and manual real owner-authored
validation).
