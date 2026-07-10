# PHASE8-IMPL-023-T018B NCP candidate-import validation adapter

## Result

PASS.

`PHASE8-IMPL-023-T018B` is complete/PASS. The OMI orchestrator now
exposes a focused, mocked, owner-controlled live NCP candidate-import
validation adapter behind explicit env flags. NCP remains a
schema/interchange validation surface (not an automatic analysis
runtime, not canon/truth). The T018B live adapter is intentionally
deferred from any project-data auto-scan and from any non-owner-driven
invocation.

No real `npm install`, no real `npm audit fix`, no real Node server,
no real `npm run validate:file` over project data, no Memory/Canon
mutation, no automatic promotion record, no automatic apply-promotion,
no NCP candidate persistence, and no story prose generation occurred
during T018B. T018B completes through mocked automated adapter tests
and preflight/docs/status updates; manual real NCP validation against
an owner-selected NCP JSON file is intentionally deferred to
`PHASE8-IMPL-023-T018C`.

## Scope

T018B adds a T018B live NCP candidate-import validation adapter to
the existing T009 NCP/Subtxt/dramatica-flow context handoff contract
(`omi_ncp_context_handoff.v1`). The adapter is reachable only when:

- `OMI_LIVE_TOOLS_ENABLED=1` (existing T013 global gate), AND
- `OMI_LIVE_NCP_ENABLED=1` (existing T013 per-tool gate), AND
- `OMI_LIVE_NCP_BLOCKED` is unset, AND
- An explicit `OMI_LIVE_NCP_INPUT_PATH` is set, AND
- The resolved path passes the T018B path-allowlist (see below).

When the opt-in Node validation flag is also set, the runner requires
a mocked `_ncp_validate_with_node_opt_in` to return `True`; the
default T018B implementation of the opt-in helper returns `False`
so the runner is intentionally Node-free by default. The opt-in is
never used against project data, never runs `npm install`, never
runs `npm audit fix`, and never starts a Node server.

T018B does NOT:

- run `npm install`
- run `npm audit fix`
- run `npm run validate:file` over project data
- start a Node server
- auto-scan project data
- walk `projects/`
- import NCP as a Python module
- mutate `.external_sources/`
- persist NCP-derived candidate findings on its own
- mutate Memory/Canon
- create promotion records
- run apply-promotion
- generate story prose
- silently rewrite unsafe source text

## Env vars added/used

T018B adds these env vars. All are read-only and fail-closed:

- `OMI_LIVE_NCP_INPUT_PATH` — required, explicit, owner-selected
  absolute path to an NCP JSON file. The adapter is unavailable
  when this is unset, empty, outside the allowlist, a symlink, a
  directory, hidden unsafe, or in a forbidden tree.
- `OMI_LIVE_NCP_VALIDATE_WITH_NODE` — optional, opt-in. Off by
  default. When set AND a safe input file is set AND the mocked
  subprocess returns success, the runner proceeds; otherwise the
  runner fails closed with no candidates.

T018B preserves the existing T013/T018A env-var contract:

- `OMI_LIVE_NCP_ENABLED` — per-tool enabled flag.
- `OMI_LIVE_NCP_BLOCKED` — overrides availability to blocked.
- `OMI_LIVE_NCP_BLOCKED_REASON` — owner reason.
- `OMI_LIVE_TOOLS_ENABLED` — T013 global live-tools gate.
- `OMI_LIVE_NCP_INPUT_PATH` and `OMI_LIVE_NCP_VALIDATE_WITH_NODE`
  are reported in the T018A/T018B-extended preflight as
  configuration-only fields; the preflight does NOT read the NCP
  JSON file or invoke Node/npm based on these env vars.

## Live adapter helper(s) added

`backend/omi_analysis_orchestrator.py`:

- `_OMI_LIVE_NCP_INPUT_PATH_ENV = "OMI_LIVE_NCP_INPUT_PATH"`
- `_OMI_LIVE_NCP_VALIDATE_WITH_NODE_ENV = "OMI_LIVE_NCP_VALIDATE_WITH_NODE"`
- `_OMI_LIVE_NCP_MAX_FINDINGS = 64`
- `_OMI_LIVE_NCP_MAX_EVIDENCE_CHARS = 240`
- `_OMI_LIVE_NCP_FIELD_TO_CANDIDATE_TYPE` — the T018B field-to-
  candidate-type mapping (see "Supported NCP candidate mappings"
  below).
- `_ncp_safe_excerpt(value, *, max_chars)` — read-only excerpt
  helper; never rewrites/sanitizes unsafe source text.
- `_ncp_label_is_safe(value)` — rejects empty, truth/canon/final/
  approved/promoted labels, and prose-intent-shaped prefixes.
- `_ncp_claim_is_safe(value)` — rejects empty/blank/truth/canon/
  final/approved/promoted/prose-like claim text.
- `_ncp_resolve_allowed_input_path(raw_path, *, repo_root=None)` —
  fail-closed, strict, allowlist-based path resolver. Accepts only:
  - the in-repo `tests/` tree,
  - the system `tempfile.gettempdir()` tree,
  - the in-repo `.external_sources/` tree.
  Rejects: traversal segments (`..`), symlinks (checked before
  AND after `Path.resolve`), directories, hidden unsafe locations,
  any path with a `projects` / `artifacts` / `graphify-out` /
  `ai_context` / `.codex-context` segment along the resolved path.
- `_ncp_json_pointer_for_path(parts)` — RFC 6901 JSON pointer helper.
- `_ncp_extract_field(node, field_names)` — first non-empty
  extractor.
- `_ncp_collect_narrative_subtext_lists(ncp_doc)` — walks only the
  explicit allowlisted NCP subtext/storytelling containers. Never
  walks `projects/`, never imports NCP, never reads external
  schema files.
- `_ncp_safe_field_for_candidate_type(field_label)` — mapping lookup
  helper.
- `_ncp_validate_with_node_opt_in(*, absolute_input_path)` — opt-in
  Node validation entry point. The T018B implementation returns
  `False` by default; the helper is mockable. Tests that need a
  successful opt-in monkeypatch this helper.
- `_ncp_build_finding_from_item(*, candidate_type, item,
  container_pointer, item_index, adapter_name)` — builds a single
  T009-shaped finding dict from one NCP list item. Returns `None`
  for empty/unsafe items; never raises; never rewrites source.
- `_build_ncp_live_runner(*, adapter_config=None)` — the live NCP
  adapter runner factory. The runner:
  - re-validates the explicit owner-selected input path inside the
    runner so the runner is never reachable with an unsafe path,
  - reads the explicit JSON file,
  - parses with `json.loads` (never `npm`, never a Node validator),
  - runs a minimal Python-side schema/readiness check on the JSON
    document (top-level `schema_version` and either `narratives` or
    `story` container),
  - maps only the allowlisted subtext/storytelling lists into
    candidate-only T009 envelope findings,
  - validates the converted envelope through the existing
    `validate_context_adapter_fixture_envelope` T009 validator,
  - fails closed on every error path,
  - never persists candidates on its own,
  - never mutates Memory/Canon, never creates promotion records,
    never runs apply-promotion, never generates story prose.

`_resolve_adapter_runner` gains a T018B branch: when `adapter ==
"ncp"`, the global and per-tool live flags are all enabled, and
`OMI_LIVE_NCP_BLOCKED` is not set, the orchestrator returns the
T018B live runner. The branch is symmetric with the existing
T014C/T015C/T016C/T017B live branches.

`backend/omi_runtime_preflight.py` (T018A follow-up): the existing
`_ncp_runtime_probe` now also takes an optional `env` argument and
surfaces the new `OMI_LIVE_NCP_INPUT_PATH` / `OMI_LIVE_NCP_VALIDATE_WITH_NODE`
env vars as configuration-only fields:

- `ncp_input_path_env` — the env var name (`OMI_LIVE_NCP_INPUT_PATH`).
- `ncp_input_path_configured` — boolean, set when the env var is
  non-empty.
- `ncp_input_path_value` — string, the configured value (trimmed;
  no path resolution, no file read).
- `ncp_validate_with_node_env` — the env var name
  (`OMI_LIVE_NCP_VALIDATE_WITH_NODE`).
- `ncp_validate_with_node_enabled` — boolean, set when the env
  var is truthy.

The preflight does NOT read the NCP JSON file even when the input
path env var is set, and does NOT invoke Node or `npm` based on
these env vars. The preflight remains read-only and fail-closed.

## Supported NCP candidate mappings

The T018B runner maps a small, evidence-backed subset of NCP fields
into the existing T009 `omi_ncp_context_handoff.v1` envelope shape
through the existing T009 fixture validator. The T009 envelope only
accepts the narrow NCP-specific candidate types listed in
`OMI_CONTEXT_ALLOWED_NORMALIZED_TYPES_BY_ADAPTER["ncp"]`:
`story_fact`, `storyform_context`, `throughline_context`,
`relationship`, `open_question`, `ambiguity`, `diagnostic_question`,
`evidence_note`. Per-item NCP character / location / organization /
object / timeline_event / plot_thread content is therefore mapped to
`evidence_note` (or `story_fact` for beat/point items) so the T009
envelope validator remains authoritative. The supported NCP
subtext/storytelling containers and their T018B candidate-type
mappings are:

| NCP container | T018B candidate type |
| --- | --- |
| `narratives[].subtext.players` | `evidence_note` |
| `narratives[].subtext.storypoints` | `story_fact` |
| `narratives[].subtext.storybeats` | `story_fact` |
| `narratives[].subtext.appreciations` | `story_fact` |
| `narratives[].subtext.dynamics` | `open_question` |
| `narratives[].subtext.vectors` | `open_question` |
| `narratives[].storytelling.overviews` | `throughline_context` |
| `narratives[].storytelling.relationships` | `relationship` |
| `narratives[].storytelling.open_questions` | `open_question` |
| `narratives[].storytelling.diagnostic_questions` | `diagnostic_question` |
| `story.moments` | `story_fact` |

The runner accepts both top-level `narratives[]` and
`story.narratives[]` (NCP allows both shapes). It never walks
`projects/`, never reads `.external_sources/` content beyond the
configured NCP JSON file, and never mutates NCP files.

Every finding carries:

- a candidate/finding type from the T009-allowed set,
- a label or extracted claim drawn from the NCP item,
- a `source_excerpt` from the NCP item (capped at 240 chars; never
  rewritten/sanitized),
- a `source_locator` as an RFC 6901 JSON pointer (e.g.,
  `/story/narratives/0/subtext/players/0/player_t018b_001`),
- provenance `tool_source: "ncp"`, `adapter: "ncp"`, and
  `support: "NCP context support only"`,
- `owner_decision: {"decision": "pending", "approved": false}`,
- `review_status: "candidate_review_pending"`.

The runner never labels anything `truth`, `canon`, `final`,
`approved`, or `promoted`. Unsafe labels are skipped (or the
runner fails closed); unsafe source text is never silently rewritten
into a safe claim. The NCP envelope explanation does not contain
any of the forbidden substrings (`truth`, `canon`, `final`,
`approved`, `promoted`).

## Tests added

`tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`
gains 18 new T018B tests (all mocked; no test requires the real
`.external_sources/narrative-context-protocol` tree, real Node,
real npm, real `node_modules`, or any network access). All tests
operate on small NCP JSON files written to `tmp_path`. The full
test file is `49 passed` (31 existing T009 + 18 new T018B).

1. `test_live_ncp_disabled_by_default_returns_unavailable` — no env
   flags -> live NCP path not triggered -> `unavailable`.
2. `test_live_ncp_enabled_but_no_input_path_returns_unavailable` —
   `OMI_LIVE_NCP_ENABLED=1` with no `OMI_LIVE_NCP_INPUT_PATH`
   -> fail-closed with no findings and no live call.
3. `test_live_ncp_blocked_overrides_enabled_returns_no_live_call` —
   `OMI_LIVE_NCP_BLOCKED=1` overrides enabled and makes no live
   call.
4. `test_live_ncp_missing_input_file_fails_closed` — configured
   path does not exist -> fail-closed with no findings; never
   falls back to any default project file.
5. `test_live_ncp_invalid_json_fails_closed` — invalid JSON in
   owner-selected file -> fail-closed with no findings.
6. `test_live_ncp_minimal_invalid_payload_fails_closed` — missing
   `schema_version` and any `narratives`/`story` containers -> fail
   closed.
7. `test_live_ncp_valid_payload_maps_to_candidate_only_findings` —
   a valid owner-selected NCP JSON maps to candidate-only NCP
   findings with evidence excerpts, JSON pointer source locators,
   provenance, support-only labels, pending owner decisions, and
   the candidate review pending status.
8. `test_live_ncp_finding_includes_evidence_excerpt_pointer_provenance` —
   every finding carries `source_excerpt` AND JSON pointer
   `source_locator` AND provenance block with
   `tool_source: "ncp"` AND support-only label AND pending owner
   decision AND candidate review status.
9. `test_live_ncp_unsafe_canon_final_approved_truth_label_is_skipped_or_failed` —
   unsafe labels (truth/canon/final/approved/promoted) and
   prose-like labels are skipped or fail closed; no sanitizer
   rewrites unsafe source text.
10. `test_live_ncp_does_not_run_automatically_over_project_data` —
    the runner never auto-opens any project file when the input
    path env var is unset.
11. `test_live_ncp_does_not_call_npm_install_or_audit_fix` —
    intercepts `subprocess.run` / `subprocess.Popen` / `node` /
    `npm` entry points and asserts none are called.
12. `test_live_ncp_does_not_run_validate_file_unless_opted_in` —
    the runner never invokes `npm run validate:file` over project
    data; the opt-in is honored but the subprocess step is mocked
    so the test does not require real Node.
13. `test_live_ncp_opt_in_node_validation_subprocess_success` —
    with the opt-in set AND a mocked
    `_ncp_validate_with_node_opt_in` that returns `True`, the
    runner proceeds and produces findings.
14. `test_live_ncp_opt_in_node_validation_subprocess_failure_fails_closed` —
    with the opt-in set but a mocked opt-in that returns `False`,
    the runner fails closed.
15. `test_live_ncp_no_persistence_memory_canon_or_promotion_or_prose` —
    the runner never persists candidates, never mutates
    Memory/Canon, never creates promotion records, never runs
    apply-promotion, never generates story prose. The full safety
    envelope is asserted.
16. `test_live_ncp_existing_t009_fixture_tests_still_pass` — the
    original T009 fixture-based NCP adapter tests remain unaffected
    when the live flags are not set.
17. `test_live_ncp_path_allowlist_rejects_projects_tree` — a path
    under a `projects/...` tree is rejected even when the file
    exists; the runner never treats the project data tree as a
    valid NCP input source.
18. `test_live_ncp_path_allowlist_rejects_symlinks` — a symlink to
    a valid NCP file is rejected; the runner does not follow
    symlinks.

`tests/test_omi_live_runtime_preflight_contract.py` gains 4 new
T018B preflight tests:

1. `test_ncp_t018b_input_path_env_field_is_reported` — the new
   `ncp_input_path_env`, `ncp_input_path_configured`,
   `ncp_input_path_value`, `ncp_validate_with_node_env`, and
   `ncp_validate_with_node_enabled` fields are present in the
   preflight tool report.
2. `test_ncp_t018b_input_path_configured_when_env_set` — when
   `OMI_LIVE_NCP_INPUT_PATH` is set, `ncp_input_path_configured`
   is `True` and `ncp_input_path_value` matches.
3. `test_ncp_t018b_validate_with_node_opt_in_is_reported` — when
   `OMI_LIVE_NCP_VALIDATE_WITH_NODE=1` is set,
   `ncp_validate_with_node_enabled` is `True`.
4. `test_ncp_t018b_preflight_does_not_read_input_file` — a sentinel
   NCP file at the configured `OMI_LIVE_NCP_INPUT_PATH` is not read
   or mutated by the preflight; the safety envelope is asserted.

The preflight probe is mocked in all T018B tests via
`monkeypatch.setattr(preflight, "_ncp_runtime_probe", ...)`. The
real probe is verified separately on the owner machine via the
`build_omi_runtime_preflight_report` call.

## Code change

`backend/omi_analysis_orchestrator.py`:

- New T018B env-var constants and field-to-candidate-type mapping
  (see "Live adapter helper(s) added" above).
- New helpers: `_ncp_safe_excerpt`, `_ncp_label_is_safe`,
  `_ncp_claim_is_safe`, `_ncp_resolve_allowed_input_path`,
  `_ncp_json_pointer_for_path`, `_ncp_extract_field`,
  `_ncp_collect_narrative_subtext_lists`,
  `_ncp_safe_field_for_candidate_type`,
  `_ncp_validate_with_node_opt_in`,
  `_ncp_build_finding_from_item`.
- New runner: `_build_ncp_live_runner`.
- `_resolve_adapter_runner` gains a T018B branch gated by the same
  live-tool flag pattern as T014C/T015C/T016C/T017B.
- Module-level docstring updated to mention the T018B live NCP
  runner alongside the existing T014C/T015C/T016C/T017B live
  runners.
- The `ncp` "unavailable" explanation in
  `analyze_omi_raw_idea_with_tools` is updated to mention the
  T018B live option, the explicit `OMI_LIVE_NCP_INPUT_PATH`
  requirement, and the no-auto-scan / no-`npm install` / no-Node
  server guarantee.

`backend/omi_runtime_preflight.py`:

- New env-var constants: `NCP_INPUT_PATH_ENV`,
  `NCP_VALIDATE_WITH_NODE_ENV`.
- `_ncp_runtime_probe` now takes an optional `env` argument and
  surfaces the T018B configuration-only fields
  (`ncp_input_path_env`, `ncp_input_path_configured`,
  `ncp_input_path_value`, `ncp_validate_with_node_env`,
  `ncp_validate_with_node_enabled`).
- `_dependency_probe(adapter="ncp", env)` and
  `_tool_report(adapter="ncp", env)` propagate the new fields.
- The preflight header docstring is updated to mention T018B.

`tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py`:
18 new T018B tests, all mocked. The T009 fixture-based tests are
unchanged.

`tests/test_omi_live_runtime_preflight_contract.py`: 4 new T018B
preflight tests + helper update to the existing
`_patch_ncp_probe` so it can be made env-aware (so the new
`ncp_input_path_value` field can be exercised without depending on
the real `.external_sources/narrative-context-protocol` tree).

## Safety envelope

The T018B live NCP runner is fail-closed on every error path:

- missing or empty `OMI_LIVE_NCP_INPUT_PATH` -> `unavailable`, no
  live call, no candidates;
- unsafe or unresolvable `OMI_LIVE_NCP_INPUT_PATH` (traversal,
  symlink, directory, hidden unsafe, `projects` segment, etc.) ->
  `unavailable`, no live call, no candidates;
- opt-in `OMI_LIVE_NCP_VALIDATE_WITH_NODE=1` with a mocked opt-in
  helper that returns `False` -> `failed_closed`, no candidates;
- missing/unreadable input file -> `failed_closed`, no candidates;
- invalid JSON -> `failed_closed`, no candidates;
- top-level non-object JSON -> `failed_closed`, no candidates;
- missing `schema_version` -> `failed_closed`, no candidates;
- missing both `narratives` and `story` containers -> `failed_closed`,
  no candidates;
- T009 envelope validation failure on the converted envelope ->
  `failed_closed`, no candidates;
- unsafe label/claim values (truth/canon/final/approved/promoted
  and prose-like text) are skipped per item, never silently
  rewritten;
- the orchestrator-level safety envelope
  (`no_prose`, `no_memory_canon_mutation`, `no_apply_promotion`,
  `no_canon_promotion`, `no_real_tool_calls`, `no_package_installs`,
  `no_story_prose_generation`, `candidate_presence_is_not_canon`,
  `queue_presence_is_not_approval`, `support_is_not_truth`,
  `tool_output_is_not_canon`) is preserved for every T018B result.

## Validation evidence

- `python3 -m py_compile backend/omi_runtime_preflight.py
  backend/omi_analysis_orchestrator.py backend/main.py
  backend/analysis_engine.py` -> exit `0`.
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_ncp_subtxt_dramatica_flow_adapter_contract.py -q`
  -> **49 passed** (31 existing T009 + 18 new T018B).
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> 30
  passed.
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_tool_assisted_persistence_contract.py -q` -> 5
  passed.
- `.venv-unsloth-clean/bin/python -m pytest
  tests/test_omi_live_runtime_preflight_contract.py -q` -> 72
  passed (68 existing T018A + 4 new T018B).
- `python3 -m json.tool
  docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json
  >/tmp/phase8-impl-023-enrichment.json.ok` -> valid (T018B scope
  block added; file is well-formed JSON).
- `git diff --check` -> clean.

## Caveats

- NCP is a schema/interchange validation surface, not an automatic
  analysis runtime. The T018B live adapter maps only a small,
  evidence-backed subset of NCP fields into the existing T009
  fixture envelope shape; it does not infer canon, storyform
  truth, continuity, or prose intent from the NCP JSON.
- The known `ajv` moderate / `fast-uri` high npm audit caveat
  remains a recorded, owner-known evidence note. T018B does not
  run `npm audit fix`, does not run `npm install`, and does not
  start a Node server.
- T018C (manual real NCP validation) is still required. T018B
  completes through mocked automated tests and docs/status; the
  T018B live adapter was not invoked against an owner-selected
  real NCP JSON file in this task.

## Next task

`PHASE8-IMPL-023-T018C — Manual real NCP validation` (recommended
next). T018C must invoke the T018B live adapter against an
owner-selected real NCP JSON file using the documented env flags
(`OMI_LIVE_TOOLS_ENABLED=1`, `OMI_LIVE_NCP_ENABLED=1`,
`OMI_LIVE_NCP_INPUT_PATH=<owner-selected-safe-path>`, optionally
`OMI_LIVE_NCP_VALIDATE_WITH_NODE=1`) and confirm:

- the runner successfully reads and parses the owner-selected real
  NCP JSON file,
- the converted envelope is accepted by the T009 fixture validator,
- every finding carries the safety envelope (evidence excerpt,
  JSON pointer source locator, provenance, support-only label,
  pending owner decision, candidate review pending status),
- the safety envelope is preserved (no Memory/Canon mutation, no
  promotion records, no apply-promotion, no story prose, no
  candidate persistence side effect from the runner),
- no `npm install`, no `npm audit fix`, no Node server, no
  `npm run validate:file` over project data occurred.

## No-prose / candidate-only / evidence-backed / provenance

T018B is adapter + tests + docs/status only. The live runner does
not produce story prose, does not rewrite unsafe source text, does
not write to candidate storage, does not mutate Memory/Canon, does
not create promotion records, does not run apply-promotion, and
does not require `npm install` / `npm audit fix` / a Node server.
The T009 fixture envelope validator is authoritative for the
converted envelope; the T018B runner never bypasses it.
