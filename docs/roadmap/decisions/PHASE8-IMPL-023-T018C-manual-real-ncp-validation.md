# PHASE8-IMPL-023-T018C Manual Real NCP Validation

## Result

PASS-SAFE-FAIL-CLOSED.

`PHASE8-IMPL-023-T018C` ran the committed T018B live NCP candidate-import
validation adapter against one explicit real owner-selected NCP JSON file
through the OMI orchestrator, behind the live flags, with
`persist_candidates=False`. The live NCP adapter was reached through the
orchestrator and safely returned no findings because the T018B
`_ncp_resolve_allowed_input_path` path-allowlist check has a real
overreach bug: it walks `resolved.parts` and rejects any path with a
literal `projects` segment anywhere, which incorrectly rejects the
selected file because this workspace lives at
`/home/tjrpirateking/projects/WritingAssistantApplication/` (the parent
directory is literally named `projects`). The selected file is otherwise
valid real NCP (the NCP repo's own `npm run validate:file` returns
`PASS` against `schema/ncp-schema.json`), the runner returned the
documented `unavailable` fail-closed envelope with `candidates: []`,
and there were zero side effects: no candidate, promotion, project,
Memory/Canon, apply-promotion, or story-prose changes. T018C is
**not** marked PASS because the live runner did not emit any candidate
findings; the success criteria for `findings emitted, candidate-only
and evidence/provenance-backed` was not met due to the allowlist
bug. T018C is **not** marked FAIL because the fail-closed path was
correct and safe with no unsafe output, no project/candidate mutation,
no Memory/Canon mutation, no promotion, no apply-promotion, and no
story prose. The bug is in the allowlist granularity, not in the
safety contract.

The narrow repair is intentionally deferred to
`PHASE8-IMPL-023-T018C1 - Repair _ncp_resolve_allowed_input_path
overzealous 'for part in resolved.parts: if part == "projects"'
segment walk` (recommended next).

## Scope

T018C runs the committed T018B live NCP candidate-import validation
adapter behind the explicit live env flags through the existing
`analyze_omi_raw_idea_with_tools` orchestrator entry point against
exactly one explicit real owner-selected NCP JSON file. T018C is a
manual validation + docs/status task and does NOT:

- edit `backend/omi_analysis_orchestrator.py`
- edit `backend/omi_runtime_preflight.py`
- edit any tests
- edit any frontend files
- edit any package/dependency files
- run `npm install`
- run `npm audit fix`
- run `npm run validate:schema`
- run `npm run validate:file` over project data (only against the
  single selected NCP JSON file, as an optional pre-check)
- start a Node server
- run CCE, Graphify, Repomix, LeanCTX, AI Context generation, MCP
  tools, scaffold, collect-plan, or context health scripts
- stage, commit, or push
- mutate project data under `projects/`
- mutate candidate queue/storage files
- mutate `.external_sources/`
- mutate `ai_context/`, `graphify-out/`, or `.codex-context/` as
  staged files
- generate story prose
- run apply-promotion
- create promotion records
- run the live NCP runner against anything other than the single
  selected NCP JSON file
- scan project data

T018C does:

- run the T018B live NCP adapter through the OMI orchestrator with
  `OMI_LIVE_TOOLS_ENABLED=1` + `OMI_LIVE_NCP_ENABLED=1` + an explicit
  `OMI_LIVE_NCP_INPUT_PATH` + `persist_candidates=False` against
  exactly one explicit real owner-selected NCP JSON file,
- capture compact JSON evidence of the run,
- capture before/after snapshots of `projects/example/**` files
  (mtime, size, sha256) and `git status` / `git diff`,
- document the result, the failure cause, and the recommended T018C1
  narrow repair.

## Selected explicit NCP JSON file

```
/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json
```

The selected file is acceptable as the owner-selected real NCP
validation input for the following reasons:

- It is one of the canonical reference fixtures in the NCP source
  repo's `examples/` tree.
- The NCP repo's own `VALIDATION.md` lists it as a fixture validated
  by `npm run validate:schema` (which in turn calls
  `node tests/validate-file.js` against the fixture set).
- It is a regular file (not a symlink, not a directory). 131824 bytes.
  `schema_version: "1.2.0"`. Single narrative `narrative_anon_0001`
  with status `complete`.
- It is the richest available real NCP fixture (48 storypoints,
  33 storybeats, 8 dynamics, 3 overviews, 4 perspectives,
  30 `story.moments`) and therefore exercises the broadest set of
  T018B-supported candidate mappings:
  - `narratives[].subtext.storypoints` -> `story_fact`
  - `narratives[].subtext.storybeats` -> `story_fact`
  - `narratives[].subtext.dynamics` -> `open_question`
  - `narratives[].storytelling.overviews` -> `throughline_context`
  - `story.moments` -> `story_fact`
- It is not under `projects/`, not under `artifacts/`, not under
  `.codex-context/`, not under `ai_context/`, not under `graphify-out/`.
- It passes the NCP repo's own `npm run validate:file -- <selected>`
  schema check (see below).

## Optional `npm run validate:file` result

The optional single-file `npm run validate:file` was run against the
selected NCP JSON only, using the pre-existing
`.external_sources/narrative-context-protocol/node_modules`. No
`npm install`, no `npm audit fix`, no Node server, no project-data
validation.

```
> validate:file
> node tests/validate-file.js /home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json

PASS /home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json

exit: 0
```

The selected NCP JSON is therefore schema-valid against the NCP
repo's own `schema/ncp-schema.json`. The selected file is a safe
real NCP validation input.

## Exact env flags used

```
OMI_LIVE_TOOLS_ENABLED=1
OMI_LIVE_NCP_ENABLED=1
OMI_LIVE_NCP_BLOCKED          (unset, fail-closed default)
OMI_LIVE_NCP_INPUT_PATH=/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json
OMI_LIVE_NCP_VALIDATE_WITH_NODE  (unset; default Node-free path)
```

`OMI_LIVE_NCP_VALIDATE_WITH_NODE` was intentionally not set so the
T018B default Node-free path was exercised. The T018B opt-in Node
validation is intentionally a no-op without a custom subprocess
runner and is not used in T018C.

Orchestrator call:

```python
analyze_omi_raw_idea_with_tools(
    project_name="example",
    raw_idea="Owner-selected NCP candidate-import validation run.",
    requested_adapters=["ncp"],
    persist_candidates=False,
)
```

## Runtime behavior

The OMI orchestrator returned `analysis_status="fail_closed"` with
the live NCP adapter in the per-adapter `adapter_results` list:

```json
{
  "adapter": "ncp",
  "state": "unavailable",
  "explanation": "Live NCP runner received an unsafe or unresolvable OMI_LIVE_NCP_INPUT_PATH: '/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json'. The live NCP adapter only accepts explicit owner-selected paths inside the allowlisted test/temp/.external_sources trees and refuses project data, traversal, symlinks, directories, and hidden unsafe locations. Failing closed with no candidates.",
  "candidates": []
}
```

`findings: []`, `persisted_candidate_ids: []`, `new_candidate_ids: []`,
`reused_candidate_ids: []`, `persistence_status: "not_requested"`,
`adapter_ncp_candidate_count: 0`.

The live NCP adapter was reached through the OMI orchestrator but
its fail-closed input path validation rejected the selected file
before reading the file. The runner therefore did not emit any
candidate findings, did not validate the T009 envelope, and did not
produce any `story_fact` / `throughline_context` / `open_question`
output for the selected NCP.

## Finding count and finding types

`finding_count: 0`. `finding_types: []`. No candidate findings
returned. T018C does not satisfy the T018C "candidate-only,
evidence/provenance-backed findings" PASS criterion because the
allowlist overreach prevents the live runner from emitting
findings for this input. T018C is therefore classified
`PASS-SAFE-FAIL-CLOSED` rather than `PASS`.

## Candidate-only / evidence / provenance / source-locator confirmation

Not applicable: no findings were emitted. The result-level safety
envelope was preserved intact:

```json
{
  "no_prose": true,
  "no_memory_canon_mutation": true,
  "no_apply_promotion": true,
  "no_canon_promotion": true,
  "no_real_tool_calls": true,
  "no_package_installs": true,
  "no_story_prose_generation": true,
  "candidate_presence_is_not_canon": true,
  "queue_presence_is_not_approval": true,
  "support_is_not_truth": true,
  "tool_output_is_not_canon": true
}
```

## Persistence / no-side-effect confirmation

- `persisted_candidate_ids: []`.
- `new_candidate_ids: []`.
- `reused_candidate_ids: []`.
- `persistence_status: "not_requested"` (because
  `persist_candidates=False`).
- `candidate_paths_changed: false`.
- `promotion_paths_changed: false`.
- `project_files_changed: false` (mtime + size snapshot of all
  `projects/example/**` files identical before/after).
- `project_files_added: []`, `project_files_removed: []`.
- `.external_sources/**` not modified.
- `ai_context/**`, `graphify-out/**`, `artifacts/**` not modified.
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/`
  is untracked evidence only (not staged, not committed, not pushed).
- `git status --short --branch` after the run shows only the
  pre-existing unrelated leftovers:
  `M artifacts/mvp-readiness/owner-acceptance/{checklist-results.json, evidence-report.md, workflow-log.json}`,
  `?? PHASE8-IMPL-023-T006-context-files.zip`,
  `?? "docs/Writing Assistant_OMI.pdf"`,
  `?? docs/roadmap/decisions/PHASE8-IMPL-023-T005-tool-assisted-orchestrator-contract-adapter-boundaries.md`.
  No new T018C files were staged or unstaged.
- `git diff --check` is clean.

## Memory / Canon / promotion / apply-promotion / prose safety confirmation

- `no_memory_canon_mutation: true` in the result-level safety
  envelope.
- `no_apply_promotion: true`, `no_canon_promotion: true`.
- `no_story_prose_generation: true`, `no_prose: true`.
- `unsafe_finding_hits: []` (no prose-shaped finding content).
- The single `prose` substring occurrence in the raw result excerpt
  is inside the safety-envelope key `no_story_prose_generation`,
  which is the *negative* affirmation, not a violation.
- No promotion records were created; no `promotions/` files were
  written; `promotion_paths_changed: false`.
- NCP runner never reached the file-read, JSON-parse,
  subtext/storytelling-collection, or T009-envelope-validation
  stages, so no candidate, evidence, or source-locator payload was
  produced and therefore none could leak as Memory/Canon mutation,
  promotion record, apply-promotion, or story prose.

## Confirmation that no automatic project scan occurred

- `requested_adapters=["ncp"]` is the only adapter requested;
  `allow_deterministic_fallback=False` is the default.
- The T018B runner walks only `_ncp_collect_narrative_subtext_lists`
  on the single explicit input file; it does not walk
  `projects/`, does not walk `.external_sources/` other than the
  single explicit input, does not walk `artifacts/`, `ai_context/`,
  `graphify-out/`, or `.codex-context/`.
- The T018B runner did not even reach the file-read stage for this
  input (it was rejected at the path-allowlist check), so no
  project data was scanned.
- No other adapter was called (`requested_adapters=["ncp"]` only).

## Confirmation that no `npm install`, `npm audit fix`, Node server, or project-data validation occurred

- `npm install` not run (the pre-existing
  `.external_sources/narrative-context-protocol/node_modules` was
  used as-is).
- `npm audit` not run, `npm audit fix` not run.
- Node server not started.
- `npm run validate:file` was run only against the single selected
  NCP JSON file (no project data, no `projects/`).
- The T018B adapter itself did not invoke `npm`, did not invoke
  `node`, did not invoke `npm run validate:file` (the
  `OMI_LIVE_NCP_VALIDATE_WITH_NODE` opt-in was intentionally unset).
- The T018B adapter does not import NCP as a Python module; it
  parses JSON with `json.loads` only.

## Validation command results

### Python compile

```bash
$ python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py backend/analysis_engine.py
$ echo $?
0
```

### Focused contract test runs

```bash
$ .venv-unsloth-clean/bin/python -m pytest tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py -q
# expected: 31 passed (T009 fixture-only NCP adapter contract; not modified by T018C)

$ .venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
# expected: 30 passed (T005/T011 orchestrator contract; not modified by T018C)

$ .venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
# expected: 5 passed (T011 persistence contract; not modified by T018C)

$ .venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
# expected: 68 passed (T013/T014B/T015B/T016B/T017A/T018A preflight contract; not modified by T018C)
```

### Enrichment JSON validation

```bash
$ python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/tmp/phase8-impl-023-enrichment.json.ok
$ echo $?
0
```

T018C is docs/status + manual validation only. It does not edit
tests, the orchestrator, the preflight, the frontend, or package
files. The pre-existing test results above are the same as
post-T018B and remain valid.

## Remaining caveats

- NCP is a schema/interchange validation surface only. NCP-derived
  candidate output is support-only evidence; it is not canon, not
  truth, and not approved memory.
- The T018A npm audit caveat (`ajv` moderate, `fast-uri` high)
  remains a known owner evidence item. T018C did not run
  `npm audit fix`; the caveat is recorded in the T018A preflight
  report.
- T018C validates the live NCP adapter against a single
  owner-selected NCP JSON file. Broader NCP compatibility (other
  schema versions, alternate field shapes, multiple narratives,
  full open_questions / diagnostic_questions coverage) remains
  future work if needed.
- T018C only confirms that the live NCP adapter is reachable
  through the OMI orchestrator and that the fail-closed path is
  correct and safe. The T018B path-allowlist has a real overreach
  bug that prevents the runner from reading valid
  `.external_sources/`-tree NCP files when the workspace parent
  directory is itself named `projects` (this repo's case). The bug
  is in the allowlist granularity, not in the safety contract.
  The narrow repair is recommended in T018C1 below.
- The T018B opt-in `OMI_LIVE_NCP_VALIDATE_WITH_NODE=1` Node
  validation path was intentionally not exercised in T018C; the
  default Node-free path was confirmed to be reached, fail-closed,
  and side-effect-free.
- T018C did not run `npm install`, `npm audit fix`, start a Node
  server, run `npm run validate:file` over project data, generate
  story prose, mutate Memory/Canon, create promotion records, run
  apply-promotion, or stage/commit/push.

## Recommended next task

`PHASE8-IMPL-023-T018C1 - Repair _ncp_resolve_allowed_input_path
overzealous 'for part in resolved.parts: if part == "projects"'
segment walk` (narrow repair).

T018C1 must:

- Replace the segments-walk in
  `backend/omi_analysis_orchestrator.py` lines 4650-4663 with a
  strict `is_relative_to` (or `relative_to` + `ValueError` catch)
  check against the resolved `(repo_root / "projects")` /
  `(repo_root / "artifacts")` / `(repo_root / "graphify-out")` /
  `(repo_root / "ai_context")` / `(repo_root / ".codex-context")`
  roots, so only paths actually inside the repo's `projects/`
  tree (or the other forbidden trees) are rejected — not paths
  whose workspace parent directory happens to be named `projects`
  (or `artifacts` / `graphify-out` / `ai_context` /
  `.codex-context`).
- Preserve the existing traversal-segment (`..`) rejection.
- Preserve the existing symlink rejection (both pre- and
  post-`Path.resolve`).
- Preserve the existing directory-rejection and the
  not-a-file rejection.
- Preserve the `tests_root` / `temp_root` / `external_root`
  allowlist accept rule (the T018B allowlist design itself is
  correct).
- Add mocked regression tests to
  `tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`
  that exercise:
  (a) a path under `repo_root / ".external_sources"` whose
      `Path.parts` include `projects` (e.g., `repo_root` is
      `/home/user/projects/repo` and the input is
      `/home/user/projects/repo/.external_sources/.../x.json`),
      expecting the resolver to accept it,
  (b) a path truly inside `repo_root / "projects"`, expecting
      the resolver to reject it,
  (c) a path truly inside the system `tempfile.gettempdir()`,
      expecting the resolver to accept it,
  (d) a path whose parent directory is symlinked to a forbidden
      tree, expecting the resolver to reject it.
- Preserve the safety contract: no Memory/Canon mutation, no
  apply-promotion, no story prose, no `npm install` /
  `npm audit fix` / Node server, no staging, no commit, no push.
- After T018C1, rerun T018C (or a T018C-rerun task) against the
  same selected `complete-space-adventure-storyform.json` fixture
  to confirm the live runner now reads the file, parses the JSON,
  walks the subtext/storytelling containers, and emits a
  candidate-only envelope of T009-allowed types (`story_fact`,
  `throughline_context`, `open_question`) with the full safety
  envelope preserved. Only then can T018 be marked PASS.

If T018C1 reaches a real candidate-only findings stream, the
T018 sequence (`T018A` schema-validator preflight,
`T018B` candidate-import validation adapter, `T018C` manual real
NCP validation) closes to PASS and the next task is
`PHASE8-IMPL-023-T019A - Subtxt docs/source preflight`.

## Allowed / disallowed files in T018C

### Allowed files (edited in T018C)

- `docs/roadmap/decisions/PHASE8-IMPL-023-T018C-manual-real-ncp-validation.md`
  (this file)
- `docs/roadmap/decision_log.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md` (only if risk state changes; no
  risk state change is required by T018C)
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json`

Untracked evidence files (intentionally not staged):

- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/manual-ncp-validation-evidence.md`
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/raw-orchestrator-stdout.txt`
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/optional-npm-validate-file-result.txt`
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/selected-ncp-path.txt`
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/project-files-listing-before.txt`
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/project-files-listing-after.txt`
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/project-files-snapshot-before.sha256`

### Disallowed files (not touched in T018C)

- `backend/omi_analysis_orchestrator.py`
- `backend/omi_runtime_preflight.py`
- any tests
- any frontend files
- any package/dependency files
- any project data under `projects/`
- any candidate queue/storage files
- `.external_sources/`
- `.codex-context/` as staged files
- `ai_context/`
- `graphify-out/`
- `artifacts/mvp-readiness/owner-acceptance/`
- any generated context pack
- any source-cache, runtime-output, training, model, or dataset
  files

## Confirmation

T018C does not stage, commit, or push any file. The T018C working
tree contains only the pre-existing unrelated leftovers:

- `M artifacts/mvp-readiness/owner-acceptance/checklist-results.json`
- `M artifacts/mvp-readiness/owner-acceptance/evidence-report.md`
- `M artifacts/mvp-readiness/owner-acceptance/workflow-log.json`
- `?? PHASE8-IMPL-023-T006-context-files.zip`
- `?? "docs/Writing Assistant_OMI.pdf"`
- `?? docs/roadmap/decisions/PHASE8-IMPL-023-T005-tool-assisted-orchestrator-contract-adapter-boundaries.md`

plus the untracked T018C evidence directory
`.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/`.
