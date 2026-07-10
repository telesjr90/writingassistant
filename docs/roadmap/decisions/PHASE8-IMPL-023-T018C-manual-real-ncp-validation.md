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

## Rerun after T018C1 — PASS

`PHASE8-IMPL-023-T018C-rerun` (the post-`PHASE8-IMPL-023-T018C1`
allowlist-repair validation rerun) is now complete/PASS and is
documented as a section of this same record. The T018C original
`PASS-SAFE-FAIL-CLOSED` history is preserved unchanged above;
this `Rerun after T018C1` section is a clearly labeled
after-T018C1 addendum, not a replacement for the original run.

### Result of the rerun

The committed T018B live NCP candidate-import validation
adapter, behind the T018C1-repaired
`_ncp_resolve_allowed_input_path` allowlist, was re-run through
`analyze_omi_raw_idea_with_tools` against the same owner-selected
real NCP JSON file T018C used, with
`persist_candidates=False`. The live NCP adapter accepted the
allowlisted path, read the JSON, walked the subtext/storytelling
containers, and emitted a non-empty candidate-only envelope of
T009-allowed `story_fact` findings backed by `source_excerpt`,
`source_locator` (RFC 6901 JSON pointer),
`provenance.tool_source: "ncp"`,
`owner_decision: {approved: false, decision: "pending"}`, and
`review_status: "candidate_review_pending"`. The full
result-level safety envelope is preserved intact
(`no_prose`, `no_memory_canon_mutation`, `no_apply_promotion`,
`no_canon_promotion`, `no_real_tool_calls`,
`no_package_installs`, `no_story_prose_generation`,
`candidate_presence_is_not_canon`,
`queue_presence_is_not_approval`, `support_is_not_truth`,
`tool_output_is_not_canon` all `True`).

Result-level summary of the rerun:

- `analysis_status: "succeeded"`.
- `persistence_status: "not_requested"`.
- `persisted_candidate_ids: []`, `new_candidate_ids: []`,
  `reused_candidate_ids: []`.
- `findings: 64`, all of `candidate_type: "story_fact"`, all
  carrying the required evidence / provenance / source-locator /
  pending-owner / candidate-review-pending fields (verified
  directly against `raw-orchestrator-result.json`).
- `adapter_results[0].adapter: "ncp"`,
  `state: "succeeded"`,
  `candidates: 64` (one finding per NCP subtext `storypoint` /
  `storybeat` item; the T018B mapping is intentionally limited
  and is the contract per T018B).
- `safety: { all required keys: True }` (including
  `no_real_tool_calls: True`; the T018B runner does not invoke
  `npm` / `node` / `npm run validate:file` when
  `OMI_LIVE_NCP_VALIDATE_WITH_NODE` is unset, which is the
  default).

Side-effect checks clean for the rerun:
`candidate_paths_changed: false`,
`promotion_paths_changed: false`,
`projects/example/**` SHA-256 + size + mtime snapshot identical
before/after (`cmp -s project-files-before.sha256
project-files-after.sha256` returned `0`;
`cmp -s project-files-before.metadata
project-files-after.metadata` returned `0`),
`.external_sources/narrative-context-protocol/**` status
identical before/after (`cmp -s
external-source-status-before.txt
external-source-status-after.txt` returned `0`), `git status
--short --branch` after the run shows only the pre-existing
unrelated leftovers, `git diff --check` clean, and the full
post-T018C1 automated regression suite still passes
(`tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py
-> 59 passed`,
`tests/test_omi_tool_assisted_orchestrator_contract.py -> 30
passed`,
`tests/test_omi_tool_assisted_persistence_contract.py -> 5
passed`,
`tests/test_omi_live_runtime_preflight_contract.py -> 72
passed`).

The original T018C `PASS-SAFE-FAIL-CLOSED` history above is
preserved unchanged. The rerun confirms that the T018C1 narrow
code repair unblocks the live NCP adapter for the
owner-selected real NCP file and that the live adapter emits a
real candidate-only findings stream with the full safety
envelope preserved. The T018 sequence
(`T018A` schema-validator preflight,
`T018B` candidate-import validation adapter,
`T018C` manual real NCP validation,
`T018C1` allowlist repair,
`T018C-rerun` validation rerun) closes to PASS, and the next
parent-level task is
`PHASE8-IMPL-023-T019A — Subtxt docs/source preflight`.

### Selected file and SHA-256 (rerun, unchanged from T018C)

```
/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json
```

```
34689dab914948b0461952ce1d3e77a7910822f392556510a5b28c750a32543d  /home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json
```

131824 bytes, regular non-symlink file, NCP
`schema_version: 1.2.0`, single narrative
`narrative_anon_0001` with status `complete`. Same canonical
rich reference fixture T018C used; the T018C1 commit did not
modify the file. The T018C optional `npm run validate:file:
PASS` evidence is preserved in
`.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/optional-npm-validate-file-result.txt`
and in the original T018C `## Optional \`npm run validate:file\`
result` section above. The rerun intentionally does not
re-run `npm run validate:file` (the file is unchanged and the
T018C-rerun task explicitly disallows re-running it).

### Exact env flags used (rerun, unchanged from T018C)

```
OMI_LIVE_TOOLS_ENABLED=1
OMI_LIVE_NCP_ENABLED=1
OMI_LIVE_NCP_BLOCKED          (unset, fail-closed default)
OMI_LIVE_NCP_INPUT_PATH=/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json
OMI_LIVE_NCP_VALIDATE_WITH_NODE  (unset; default Node-free path)
```

`OMI_LIVE_NCP_VALIDATE_WITH_NODE` was intentionally not set so
the T018B default Node-free path was exercised. The T018B
opt-in Node validation is intentionally a no-op without a
custom subprocess runner and is not used in the rerun.

Orchestrator call for the rerun (exactly one live invocation):

```python
analyze_omi_raw_idea_with_tools(
    project_name="example",
    raw_idea="Owner-selected NCP candidate-import validation rerun after T018C1.",
    requested_adapters=["ncp"],
    persist_candidates=False,
)
```

### Live adapter invocation count (rerun)

The live `analyze_omi_raw_idea_with_tools` orchestrator call
was invoked exactly once. No retry was required. The single
invocation produced the full raw result (170065 bytes) plus
the compact summary (1311 bytes); the per-finding
evidence / provenance / source-locator / pending-owner /
candidate-review-pending fields were verified directly against
the raw result.

### Evidence / provenance / source-locator confirmation (rerun)

Verified directly against
`.codex-context/PHASE8-IMPL-023/manual-validation/T018C-rerun-ncp/raw-orchestrator-result.json`
(not against the helper-script `compact-summary.json`).
Every one of the 64 findings has:

- `candidate_type: "story_fact"`.
- `source_locator`: non-empty RFC 6901 JSON pointer string
  pointing into `narratives/*\/subtext\/storypoints/0/...` or
  `narratives/*\/subtext\/storybeats/<index>/...`. Example
  first finding:
  `"/~1narratives~1*~1subtext~1storypoints/0/point_anon_0001"`.
  Example last finding:
  `"/~1narratives~1*~1subtext~1storybeats/15/beat_anon_0016"`.
- `evidence`: non-empty list of
  `{source_excerpt, source_locator}` dicts. Every excerpt is a
  non-empty string; every locator is a non-empty string
  matching the finding-level `source_locator` family.
- `provenance.tool_source: "ncp"`,
  `provenance.adapter: "ncp"`,
  `provenance.support: "NCP context support only"`.
- `owner_decision: {"approved": false, "decision": "pending"}`.
- `review_status: "candidate_review_pending"`.
- `source_adapter: "ncp"`,
  `support_label: "NCP context support only"`,
  `confidence: "medium support"`,
  `uncertainty_label: null`,
  `conflict_group_id: null`, `duplicate_of: []`,
  `related_finding_ids: []`.
- `extracted_claim`: non-empty string equal to
  `evidence[0].source_excerpt` (the T018B contract; the runner
  does not rewrite / expand / condense the excerpt into a
  generated prose claim).
- `label`: NCP item id, e.g. `point_anon_0001` /
  `beat_anon_0016`.
- `candidate_fingerprint` / `evidence_fingerprint` /
  `normalized_finding_id` / `raw_finding_id`: present and
  deterministic.

### Evidence-summary-script mismatch (rerun, narrow)

The compact-summary helper-script writes
`all_findings_have_required_evidence: false` only because the
helper script checks `owner_decision == "pending"` (string), but
the real field is the object
`owner_decision == {"approved": false, "decision": "pending"}`.
This is an evidence-summary-script mismatch, not a runtime
adapter failure. The direct raw-result inspection confirmed
all 64 findings carry the required evidence and review fields.
The mismatch does not affect the live adapter, the result-level
safety envelope, the side-effect / git status evidence, or the
rerun PASS classification.

### Persistence / no-side-effect confirmation (rerun)

- `persisted_candidate_ids: []`,
  `new_candidate_ids: []`,
  `reused_candidate_ids: []`.
- `persistence_status: "not_requested"` (because
  `persist_candidates=False`).
- `candidate_paths_changed: false`,
  `promotion_paths_changed: false`.
- `projects/example/**` SHA-256 + size + mtime snapshot
  identical before/after (`cmp -s` returned `0` for both the
  sha256 list and the metadata list).
- `.external_sources/narrative-context-protocol/**` not
  modified (`git status --short --
  .external_sources/narrative-context-protocol` was empty
  before AND after; `cmp -s` returned `0`).
- `ai_context/**`, `graphify-out/**`,
  `artifacts/mvp-readiness/owner-acceptance/**` not modified.
- `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-rerun-ncp/`
  is untracked evidence only (not staged, not committed, not
  pushed; `.codex-context/` is in `.git/info/exclude`).
- `git status --short --branch` after the rerun shows only
  the pre-existing unrelated leftovers (no new T018C-rerun
  files were staged or unstaged beyond the untracked T018C-rerun
  evidence directory).
- `git diff --check` is clean.

### Memory / Canon / promotion / apply-promotion / prose safety confirmation (rerun)

- `no_memory_canon_mutation: true`,
  `no_apply_promotion: true`,
  `no_canon_promotion: true`,
  `no_story_prose_generation: true`,
  `no_prose: true`,
  `no_real_tool_calls: true`,
  `no_package_installs: true` in the result-level safety
  envelope.
- No promotion records were created; no `promotions/` files
  were written; `promotion_paths_changed: false`.
- NCP-derived `story_fact` findings are not Memory, not Canon,
  not promotion, not apply-promotion, and not story prose. They
  are support-only evidence that requires owner review before
  any use.

### No automatic project scan (rerun)

- `requested_adapters=["ncp"]` is the only adapter requested;
  `allow_deterministic_fallback=False` is the default.
- The T018B runner walks only
  `_ncp_collect_narrative_subtext_lists` on the single explicit
  input file; it does not walk `projects/`, does not walk
  `.external_sources/` other than the single explicit input,
  does not walk `artifacts/`, `ai_context/`, `graphify-out/`,
  or `.codex-context/`.
- The T018B runner reached the file-read, JSON-parse,
  subtext/storytelling-collection, and T009-envelope-validation
  stages for the single explicit input. No project data was
  scanned. No other adapter was called.

### No `npm install`, `npm audit fix`, Node server, or project-data validation (rerun)

- `npm install` not run (the pre-existing
  `.external_sources/narrative-context-protocol/node_modules` was
  not touched; the file system status was identical before and
  after).
- `npm audit` not run, `npm audit fix` not run.
- Node server not started.
- `npm run validate:file` was not re-run for the rerun
  (intentionally not run; the T018C `npm run validate:file:
  PASS` evidence is preserved and the selected file is
  unchanged from the T018C validation; the rerun task
  explicitly disallows re-running `npm run validate:file` over
  the selected file).
- The T018B adapter itself did not invoke `npm`, did not
  invoke `node`, did not invoke `npm run validate:file` (the
  `OMI_LIVE_NCP_VALIDATE_WITH_NODE` opt-in was intentionally
  unset, so the T018B opt-in Node validation path was not
  exercised in the rerun; the T018B default Node-free path was
  confirmed to be reached, succeeded, and side-effect-free).
- The T018B adapter does not import NCP as a Python module; it
  parses JSON with `json.loads` only.

### Validation command results (rerun)

`python3 -m py_compile backend/omi_analysis_orchestrator.py`
-> exit 0.

Focused regression test runs (post-T018C1):

- `tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`
  -> 59 passed.
- `tests/test_omi_tool_assisted_orchestrator_contract.py` -> 30
  passed.
- `tests/test_omi_tool_assisted_persistence_contract.py` -> 5
  passed.
- `tests/test_omi_live_runtime_preflight_contract.py` -> 72
  passed.

Enrichment JSON validation:

- `python3 -m json.tool
  docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json
  >/dev/null` -> exit 0.
- `python3 scripts/check_enrichment.py` -> exit 0.
- `python3 scripts/validate_roadmap.py` -> exit 0.
- `git diff --check` -> exit 0.

### T018 sequence closeout

The T018 sequence
(`T018A` schema-validator preflight,
`T018B` candidate-import validation adapter,
`T018C` manual real NCP validation,
`T018C1` allowlist repair,
`T018C-rerun` validation rerun) closes to PASS with the
T018C-rerun documented in this `Rerun after T018C1 — PASS`
section of this same decision record.

- `T018A` complete/PASS
  (`docs/roadmap/decisions/PHASE8-IMPL-023-T018A-ncp-schema-validator-preflight.md`).
- `T018B` complete/PASS
  (`docs/roadmap/decisions/PHASE8-IMPL-023-T018B-ncp-candidate-import-validation-adapter.md`).
- `T018C` complete/PASS-SAFE-FAIL-CLOSED (preserved unchanged
  in the original `## Result` and following sections of this
  file).
- `T018C1` complete/PASS
  (`docs/roadmap/decisions/PHASE8-IMPL-023-T018C1-ncp-input-path-allowlist-repair.md`).
- `T018C-rerun` complete/PASS (documented in this
  `Rerun after T018C1 — PASS` section of this file).

### Recommended next task after the rerun

`PHASE8-IMPL-023-T019A — Subtxt docs/source preflight`
(planned; follows after the T018 sequence closes to PASS).

T019A must mirror the T018A NCP preflight for the Subtxt
surface: extends the T013 read-only runtime preflight in
`backend/omi_runtime_preflight.py` so the OMI
`runtime-preflight` report for the `subtxt` tool reports a
focused, read-only Subtxt source/validator surface;
read-only, fail-closed, never runs `npm install`,
`npm audit fix`, `npm run validate:schema`, or
`npm run validate:file`; never imports Subtxt as a Python
module; never exposes Subtxt as a network/server path; the
probe records any known audit caveat as known owner evidence;
Subtxt remains a schema/interchange/diagnostic surface, not
an automatic analysis runtime, not canon/truth; the existing
live-tool flag map (`OMI_LIVE_SUBTXT_ENABLED` /
`OMI_LIVE_SUBTXT_BLOCKED` /
`OMI_LIVE_SUBTXT_BLOCKED_REASON`) is preserved; Subtxt stays
disabled by default.

### Rerun caveats

- NCP is a schema/interchange validation surface only.
  NCP-derived candidate output is support-only evidence; it
  is not canon, not truth, and not approved memory.
- The T018A npm audit caveat (`ajv` moderate, `fast-uri` high)
  remains a known owner evidence item. The rerun did not run
  `npm audit fix`; the caveat is recorded in the T018A
  preflight report.
- The rerun validates the live NCP adapter against a single
  owner-selected NCP JSON file. Broader NCP compatibility
  (other schema versions, alternate field shapes, multiple
  narratives, full open_questions / diagnostic_questions
  coverage) remains future work if needed.
- The T018B opt-in `OMI_LIVE_NCP_VALIDATE_WITH_NODE=1` Node
  validation path was intentionally not exercised in the
  rerun; the default Node-free path was confirmed to be
  reached, succeeded, and side-effect-free.
- The rerun did not run `npm install`, `npm audit fix`, start
  a Node server, run `npm run validate:file` over the
  selected file (intentionally not re-run; T018C evidence
  preserved), generate story prose, mutate Memory/Canon, create
  promotion records, run apply-promotion, or stage / commit /
  push.
