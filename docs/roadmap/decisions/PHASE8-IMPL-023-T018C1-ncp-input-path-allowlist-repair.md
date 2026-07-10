# PHASE8-IMPL-023-T018C1 Repair NCP input-path allowlist overreach

## Result

PASS.

`PHASE8-IMPL-023-T018C1` is complete/PASS. The T018B
`_ncp_resolve_allowed_input_path` allowlist overreach identified in
T018C has been repaired: a safe allowlisted path under
`.external_sources/narrative-context-protocol/examples/` is now
accepted even when the absolute `Path.parts` include an ancestor
directory named `projects` (or `artifacts` / `graphify-out` /
`ai_context` / `.codex-context`) outside the repo. A path that is
actually inside the resolved `repo_root / "projects"` (or
`repo_root / "artifacts"` / `repo_root / "graphify-out"` /
`repo_root / "ai_context"` / `repo_root / ".codex-context"`) is
still rejected. The T018B traversal / symlink / directory /
not-a-file / `tests_root` / `temp_root` / `external_root` allowlist
contract is preserved.

The bug was strictly in the T018B allowlist granularity, not in the
safety contract. T018C's PASS-SAFE-FAIL-CLOSED result is preserved
unchanged; the live NCP adapter was reachable through the OMI
orchestrator, fail-closed, and side-effect-free. T018C1 only narrows
the allowlist so a T018C-rerun can read the selected real NCP JSON
and emit a real candidate-only findings stream.

NCP remains a schema/interchange validation surface only, not an
automatic analysis runtime, not canon/truth. No `npm install`, no
`npm audit fix`, no Node server, no `npm run validate:file` over
project data, no Memory/Canon mutation, no automatic promotion
record, no automatic apply-promotion, no NCP candidate persistence,
and no story prose generation occurred during T018C1. T018C1
completes through a narrowly-scoped code repair plus regression
tests plus docs/status updates.

A T018C rerun is required after T018C1 to confirm that the live NCP
runner now reads the selected owner-selected real NCP JSON file
(`/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json`),
parses the JSON, walks the subtext/storytelling containers, and
emits a candidate-only envelope of T009-allowed types
(`story_fact`, `throughline_context`, `open_question`, etc.) with
the full result-level safety envelope preserved.

## Scope

T018C1 is a narrow backend repair + regression tests + docs/status
task that does NOT:

- run any of: CCE, Graphify, Repomix, LeanCTX, AI Context generation,
  MCP tools, scaffold, collect-plan, context health scripts, or broad
  context collection,
- edit any frontend files,
- edit any package/dependency files,
- run `npm install`, `npm audit fix`, dependency mutation commands,
  or network/server commands,
- run the full manual real NCP validation as T018C1 completion
  proof (that belongs to the T018C rerun after T018C1),
- stage, commit, or push,
- mutate `.external_sources/`, `ai_context/`, `graphify-out/`,
  `.codex-context/`, or any project data under `projects/`,
- mutate any candidate queue/storage files except test temp dirs,
- mutate any artifacts / mvp-readiness / owner-acceptance files,
- mutate Memory/Canon,
- create automatic promotion records,
- run apply-promotion,
- generate story prose,
- import NCP as a Python module.

## Bug repaired

The T018B `_ncp_resolve_allowed_input_path` resolver at
`backend/omi_analysis_orchestrator.py:4583-4719` (pre-T018C1
`4650-4663`) walked `resolved.parts` and rejected any path with a
literal `projects` / `artifacts` / `graphify-out` / `ai_context` /
`.codex-context` segment anywhere along the resolved path:

```python
# Pre-T018C1 overreach (REMOVED):
for part in resolved.parts:
    if part == "projects":
        return None
for forbidden_segment in (
    "artifacts",
    "graphify-out",
    "ai_context",
    ".codex-context",
):
    for part in resolved.parts:
        if part == forbidden_segment:
            return None
```

This is a path-allowlist granularity bug, not a safety-contract
bug:

- The fail-closed behavior for traversal segments, symlinks,
  directories, missing files, unreadable files, and files outside
  the allowed roots was correct.
- The bug rejected valid allowlisted NCP inputs whose absolute
  `Path.parts` happened to include a literal `projects` segment
  outside the repo. In this workspace the parent directory is
  literally `/home/tjrpirateking/projects/`, so the selected NCP
  file at
  `/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json`
  was mis-rejected even though the file is genuinely inside the
  allowed `repo_root / ".external_sources"` tree.
- The same overreach applied to `artifacts` (e.g., when a
  workspace parent directory is named `artifacts`),
  `graphify-out`, `ai_context`, and `.codex-context`.

## Helper added

`backend/omi_analysis_orchestrator.py`:

- `_ncp_path_is_relative_to(child, parent) -> bool` — safe resolved
  containment check. Uses `Path.is_relative_to` when available
  (Python 3.9+) and otherwise falls back to
  `Path.relative_to` + `ValueError` catch.

## Function changed

`backend/omi_analysis_orchestrator.py`:

- `_ncp_resolve_allowed_input_path(raw_path, *, repo_root=None)`
  rewritten to use a strict resolved-root containment check
  against the resolved forbidden repo-local trees:

  ```python
  forbidden_roots: tuple[Path, ...] = tuple(
      (repo_root / name).resolve(strict=False)
      for name in (
          "projects",
          "artifacts",
          "graphify-out",
          "ai_context",
          ".codex-context",
      )
  )
  for forbidden_root in forbidden_roots:
      if _ncp_path_is_relative_to(resolved, forbidden_root):
          return None
  ```

  The same `_ncp_path_is_relative_to` helper is used to check
  membership in the allowed roots
  (`repo_root / "tests"`, `tempfile.gettempdir()`,
  `repo_root / ".external_sources"`), so the T018B allowlist
  contract is preserved by the same primitive.

The pre-existing rejection behavior is preserved for:

- empty / non-string / blank `raw_path` values,
- traversal segments (`..`) in the unresolved candidate parts,
- symlinks before `Path.resolve` (the unresolved candidate),
- symlinks after `Path.resolve` (the resolved path),
- directories (the resolved path is not a regular file),
- missing files (the resolved path is not a regular file),
- unreadable files (the `OSError` paths),
- files outside the allowed roots (`tests_root`, `temp_root`,
  `external_root`).

The pre-existing acceptance behavior is preserved for:

- files under `repo_root / "tests"`,
- files under `tempfile.gettempdir()`,
- files under `repo_root / ".external_sources"`.

The T018C1 repair does NOT broaden the allowlist beyond what T018B
intended, does NOT default to any project file, does NOT scan
`projects/`, does NOT run `npm run validate:file` over project
data, does NOT start a Node server, does NOT import NCP as a Python
module, does NOT mutate `.external_sources/`, does NOT mutate
project data, and does NOT persist candidates as a side effect.

## Tests added/updated

`tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`:

The T018B test
`test_live_ncp_path_allowlist_rejects_projects_tree` was rewritten
to align with the T018C1 contract. The pre-T018C1 test created a
file under `tmp_path / "projects" / "demo" / "scene.json"` and
expected rejection; that expectation depended on the overreach.
T018C1 only rejects files actually inside the resolved
`repo_root / "projects"`, so the rewritten test creates a
`tmp_path / "projects" / "fake_repo" / "projects" / "demo" / "scene.json"`
file inside a fake repo root and verifies the resolver rejects it
when given the fake `repo_root` as the explicit `repo_root`
parameter.

New T018C1 regression tests added (all use `tmp_path` and an
explicit `repo_root`, so they do NOT require the real
`.external_sources` tree, real Node/npm, network, or real NCP
install):

- `test_t018c1_allowlist_accepts_external_sources_path_when_ancestor_is_named_projects` —
  the central T018C bug regression: a safe
  `.external_sources/narrative-context-protocol/examples/...` NCP
  file under a fake repo root whose parent directory is itself
  named `projects` is accepted; the resolved path's `Path.parts`
  include the literal `projects` segment outside the repo, and
  the resolver still returns the resolved `Path`.
- `test_t018c1_allowlist_rejects_repo_local_projects_tree` —
  a file actually inside the resolved
  `repo_root / "projects"` tree is rejected.
- `test_t018c1_allowlist_rejects_repo_local_artifacts_tree` —
  a file actually inside the resolved
  `repo_root / "artifacts"` tree is rejected.
- `test_t018c1_allowlist_rejects_repo_local_graphify_out_tree` —
  a file actually inside the resolved
  `repo_root / "graphify-out"` tree is rejected.
- `test_t018c1_allowlist_rejects_repo_local_ai_context_tree` —
  a file actually inside the resolved
  `repo_root / "ai_context"` tree is rejected.
- `test_t018c1_allowlist_rejects_repo_local_codex_context_tree` —
  a file actually inside the resolved
  `repo_root / ".codex-context"` tree is rejected.
- `test_t018c1_allowlist_accepts_tempfile_gettempdir_path` —
  a file under `tempfile.gettempdir()` is accepted, matching the
  T018B allowed-root design.
- `test_t018c1_allowlist_rejects_symlink_input_path` — a
  symlink pointing at a valid NCP file is rejected (pre- and
  post-`Path.resolve` symlink checks remain fail-closed).
- `test_t018c1_allowlist_rejects_symlinked_parent_into_forbidden_tree`
  — a path whose parent directory is a symlink resolving into a
  forbidden repo-local tree is rejected (the post-`Path.resolve`
  containment check is not weakened by the T018C1 fix).
- `test_t018c1_allowlist_rejects_empty_traversal_and_directory_inputs`
  — the existing T018B rejection behavior for empty input paths,
  traversal segments, directories, and missing files is preserved.

Helper added in the test file:

- `_make_fake_repo_root(tmp_path)` — builds a fake repo root under
  `tmp_path / "projects" / "fake_repo" /` that mirrors the T018B
  forbidden / allowed roots. The `tmp_path / "projects"` parent
  reproduces the workspace-parent-is-named-projects case.
- `_write_ncp_payload_in_dir(directory, name="minimal.json")` —
  writes a minimal NCP JSON payload inside a given directory
  using the existing `_valid_minimal_ncp_payload()` helper.

All T018B live NCP mocked tests still pass. All T009 fixture
tests still pass. All orchestrator / persistence / preflight
tests still pass.

## Confirmation

- The T018B allowlist design (allowed roots, forbidden trees,
  fail-closed behavior) is preserved.
- NCP remains a schema/interchange validation surface only, not
  an automatic analysis runtime, not canon/truth.
- No `npm install`, no `npm audit fix`, no Node server, no
  `npm run validate:file` over project data, no Memory/Canon
  mutation, no automatic promotion records, no automatic
  apply-promotion, no candidate persistence side effect, and no
  story prose generation occurred during T018C1.
- No manual real NCP validation was required as T018C1 completion
  proof. T018C1 only repairs the code and adds regression tests;
  a T018C rerun is the next task.
- No automatic project scan occurred.
- No frontend files, no package/dependency files, no
  `.external_sources/`, no `ai_context/`, no `graphify-out/`, no
  `.codex-context/`, no `artifacts/mvp-readiness/owner-acceptance/`,
  no project data under `projects/`, no candidate queue/storage
  files, no generated context packs, no source-cache /
  runtime-output / training / model / dataset files were edited
  by T018C1.
- T018C1 does not stage, commit, or push any file.

## Caveats

- NCP is schema/interchange only, not automatic analysis runtime.
- The pre-existing T017B1 `npm audit` caveat remains: a `npm audit`
  run was not performed during T018C1; the T018B opt-in Node
  validation path is mocked in tests and off by default in
  production.
- The known pre-existing local test failure
  `tests/test_omi_booknlp_spacy_adapter_contract.py::test_live_spacy_missing_package_returns_unavailable`
  may still fail because spaCy is installed locally. T018C1
  validation does not require running that file.
- The T018C-rerun task is required after T018C1 to confirm
  candidate-only findings from the selected real NCP JSON.

## Recommended next task

`PHASE8-IMPL-023-T018C-rerun - Manual real NCP validation rerun
after allowlist repair` (recommended next).

The T018C-rerun must run the committed T018B live NCP
candidate-import validation adapter through
`analyze_omi_raw_idea_with_tools` against the same
`/home/tjrpirateking/projects/WritingAssistantApplication/.external_sources/narrative-context-protocol/examples/complete-space-adventure-storyform.json`
owner-selected real NCP JSON file, behind the same live env flags
(`OMI_LIVE_TOOLS_ENABLED=1 OMI_LIVE_NCP_ENABLED=1
OMI_LIVE_NCP_INPUT_PATH=<selected>`; `OMI_LIVE_NCP_BLOCKED` unset;
`OMI_LIVE_NCP_VALIDATE_WITH_NODE` unset, default Node-free path),
and confirm that the live runner now reads the file, parses the
JSON, walks the subtext/storytelling containers, and emits a
candidate-only envelope of T009-allowed types
(`story_fact`, `throughline_context`, `open_question`,
`evidence_note`, `relationship`, `diagnostic_question`, etc.) with
the full result-level safety envelope preserved.

Only after the T018C-rerun reaches a real candidate-only findings
stream can the T018 sequence
(`T018A` schema-validator preflight,
`T018B` candidate-import validation adapter,
`T018C` manual real NCP validation) close to PASS. The next
parent-level task after `T018` is
`PHASE8-IMPL-023-T019A - Subtxt docs/source preflight`.

## Allowed / disallowed files in T018C1

### Allowed files (edited in T018C1)

- `backend/omi_analysis_orchestrator.py` (narrow repair only,
  inside `_ncp_path_is_relative_to` and
  `_ncp_resolve_allowed_input_path`).
- `tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`
  (T018C1 regression tests + minor rewrite of
  `test_live_ncp_path_allowlist_rejects_projects_tree`).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T018C1-ncp-input-path-allowlist-repair.md`
  (this file).
- `docs/roadmap/decision_log.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json`

### Disallowed files (not touched in T018C1)

- `backend/omi_runtime_preflight.py`
- `backend/main.py`
- `backend/analysis_engine.py`
- Any frontend files.
- Any package/dependency files.
- Any project data under `projects/`.
- Any candidate queue/storage files except test temp dirs.
- `.external_sources/`.
- `.codex-context/`.
- `ai_context/`.
- `graphify-out/`.
- `artifacts/mvp-readiness/owner-acceptance/`.
- Any generated context pack.
- Any source-cache, runtime-output, training, model, or dataset
  files.
- Any `.codex-context/PHASE8-IMPL-023/manual-validation/T018C-ncp/`
  untracked evidence file (T018C1 does not modify or add
  T018C evidence files).
