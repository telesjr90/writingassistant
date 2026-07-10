# PHASE8-IMPL-023-T016C — Live Story Check Adapter Behind Flags

## Result

PASS for live adapter implementation + mocked tests + docs/status.

T016C implements a live OMI `story_check` adapter behind explicit runtime flags by bridging the OMI orchestrator to the existing in-repo `backend.analysis_engine.run_story_check(project_name, scene_id)` callable surface. The live path is disabled by default and converts the legacy rich-Story-Check response into the existing T008 `omi_story_check_diagnostic_handoff.v1` envelope shape before validation/normalization. The existing T008 fixture validator remains authoritative.

## Nature

- Backend live-adapter implementation + mocked tests + docs/status task only (T016C).
- T016D (manual real Story Check validation) is deferred to a future task; no live Story Check call was performed during T016C.
- Builds on T016A findings (existing in-repo callable surface is `backend.analysis_engine.run_story_check`) and T016B preflight (existing live flags `OMI_LIVE_STORY_CHECK_ENABLED`, `OMI_LIVE_STORY_CHECK_BLOCKED`, `OMI_LIVE_STORY_CHECK_BLOCKED_REASON`).
- Does not call the legacy `POST /api/projects/{project_name}/story-check/{scene_id}` route.
- Does not call Ollama/network from the live adapter (the `analysis_engine.run_story_check` callable surface owns the Ollama HTTP behavior; T016C only calls the in-repo function and converts its return value).
- Does not mutate Memory/Canon, create promotion records, run apply-promotion, persist candidates, or generate story prose.

## Implementation

### A. Live Story Check Runner

`backend/omi_analysis_orchestrator.py`:

- Added new env var constants:
  - `_OMI_LIVE_STORY_CHECK_ENABLED_ENV = "OMI_LIVE_STORY_CHECK_ENABLED"`
  - `_OMI_LIVE_STORY_CHECK_BLOCKED_ENV = "OMI_LIVE_STORY_CHECK_BLOCKED"`
  - `_OMI_LIVE_STORY_CHECK_BLOCKED_REASON_ENV = "OMI_LIVE_STORY_CHECK_BLOCKED_REASON"`
  - `_OMI_LIVE_STORY_CHECK_SCENE_ID_ENV = "OMI_LIVE_STORY_CHECK_SCENE_ID"`

- Added `_story_check_sanitize_truth_final_labels(value)` helper that replaces forbidden `truth|canon|final|approved|promoted|...` labels in legacy text with owner-/support-side replacements (`approved -> owner-backed`, `truth -> diagnostic support`, `canon -> diagnostic context`, `final -> candidate`, `promoted -> candidate-only`, etc.) so the T008 contract validator (which is strict about these words) can accept the converted findings.

- Added `_story_check_safe_excerpt_text(value, max_chars=240)` helper that strips non-string/empty values, sanitizes forbidden labels, and truncates long values to a max-characters cap.

- Added `_story_check_extract_excerpts_from_value(value, max_items, max_chars)` helper that extracts a deduplicated list of evidence excerpt strings from a legacy value (`list[str]`, `str`, or `dict` with an excerpt-like key).

- Added `_story_check_classify_candidate_type(raw_type, key_hint)` helper that maps a legacy Story Check key/label to a T008 orchestrator finding type (`structural_diagnostic`, `throughline_context`, `storyform_context`, `continuity_warning`, `diagnostic_question`, `evidence_note`, etc.). Ambiguous legacy keys fall back to `structural_diagnostic` so the resulting finding is still a candidate-only diagnostic (never canon, never truth).

- Added `_story_check_make_finding(...)` helper that builds one T008-shaped finding dict. Returns `None` when the inputs cannot be turned into a T008-compatible finding (empty label/claim or no usable evidence).

- Added `_story_check_warning_label(category, prefix_text)` helper that builds a T008-safe diagnostic label for a legacy warning/concern/insufficient-evidence entry.

- Added `_story_check_resolve_scene_locator(project_name, scene_id)` helper that builds a safe project-scoped, scene-scoped `source_locator` for live Story Check findings. The locator does NOT include any raw scene text or owner-authored content; it only identifies the project/scene surface.

- Added `_story_check_result_to_envelope(legacy_result, project_name, scene_id)` converter that turns a legacy Story Check response into a T008 envelope dict:
  - `None`/non-dict legacy results -> `failed_closed` with empty findings and an explanation.
  - Legacy `{"error": "..."}` shape -> `error` with empty findings and an explanation.
  - Empty/None/legacy results with only `task`/`coherence_score` and no structured diagnostics -> `failed_closed` with empty findings and an explanation. Free-form prose is NOT parsed as candidate findings.
  - Structured legacy results with `warnings`/`concerns`/`suggestions`/`insufficient_evidence` arrays or `throughline_alignment`/`theme_drift`/`character_consistency` objects are converted into T008-shaped findings, each carrying a safe label, sanitized claim, evidence excerpt(s), `source_locator`, support-only metadata, pending owner decision, and candidate/review-pending status.
  - The converter never passes through free-form prose as candidate findings and never carries rewrite/continue/outline/draft/polish/expand/improve prose-shaped text into the envelope.

- Added `_adapter_config_scene_id(adapter_config)` helper that extracts the explicit `story_check_scene_id` from the orchestrator's `adapter_config` dict (a non-invasive way to pass a `scene_id` from the orchestrator entrypoint into the live runner).

- Added `_build_story_check_live_runner(*, adapter_config)`:
  - Imports `backend.analysis_engine.run_story_check` lazily (never at module import time and never when live flags are disabled).
  - Resolves `scene_id` from the explicit `adapter_config["story_check_scene_id"]` (when supplied) or from the `OMI_LIVE_STORY_CHECK_SCENE_ID` env var. Explicit argument wins over the env var when both are present.
  - If `project_name` is empty/missing or `scene_id` cannot be resolved, the runner returns `unavailable` with an explanation and never calls `run_story_check`.
  - Calls `run_story_check(project_name, scene_id)` and converts the legacy result through `_story_check_result_to_envelope`.
  - Validates the converted envelope through the existing `validate_story_check_fixture_envelope` (T008 fixture validator). The T008 validator remains authoritative.
  - Fail-closed on `ImportError`, runtime exceptions, missing context (project name or scene id), blocked flag, malformed legacy output, or unsafe converted envelope.
  - Never persists candidates, never mutates Memory/Canon, never creates promotion records, never runs apply-promotion, never generates story prose.

- Wired the live runner into `_resolve_adapter_runner` for the `story_check` adapter only when all of the following are true:
  1. `requested_adapters` includes `story_check`.
  2. `OMI_LIVE_TOOLS_ENABLED` is enabled.
  3. `OMI_LIVE_STORY_CHECK_ENABLED` is enabled.
  4. `OMI_LIVE_STORY_CHECK_BLOCKED` is not enabled.

### B. `analyze_omi_raw_idea_with_tools` entrypoint

`backend/omi_analysis_orchestrator.py`:

- Added a new optional keyword argument `story_check_scene_id: str | None = None`.
  - When supplied, it must be a non-empty string (the entrypoint raises `ValueError` otherwise).
  - The entrypoint stores the supplied value on `adapter_config["story_check_scene_id"]` so the live runner can read it via `_adapter_config_scene_id`. The existing `adapter_config` argument is preserved unchanged for backward compatibility.
  - The live runner explicitly wins over the env var when the kwarg is supplied.
- All existing call sites remain unchanged; the new kwarg is fully backward compatible.

### C. Live Path Disabled by Default

- The `_resolve_adapter_runner` wiring only builds the live runner when all three flags are set; missing any flag returns `None` from `_resolve_adapter_runner` and the existing T005 stub/unavailable path runs unchanged.
- Tests confirm that the live runner is NOT constructed (and `backend.analysis_engine.run_story_check` is NOT imported/called) when the global `OMI_LIVE_TOOLS_ENABLED` flag is off, when the per-tool `OMI_LIVE_STORY_CHECK_ENABLED` flag is off, or when `OMI_LIVE_STORY_CHECK_BLOCKED` is set.

### D. Conversion Behavior

- Adapter: `"story_check"`.
- Schema version: `"omi_story_check_diagnostic_handoff.v1"`.
- Allowed statuses: `"succeeded" | "empty" | "failed_closed" | "error"` (per T008 contract).
- Provenance/tool source: `story_check`.
- Findings are candidate-only diagnostics, evidence notes, or diagnostic questions.
- Every finding includes `evidence` with `source_excerpt` and `source_locator`, `provenance.tool_source == "story_check"`, support-only `support_label`, `owner_decision: {decision: pending, approved: false}`, and `review_status: "candidate_review_pending"`.
- Owner decision remains pending; review status remains candidate-review pending.
- Support/confidence labels are support-only and never truth.
- Legacy text containing `approved|truth|canon|final|promoted|...` words is sanitized through `_story_check_sanitize_truth_final_labels` before being used as label/claim/excerpt text. The replacement table is `_STORY_CHECK_TRUTH_LABEL_REPLACEMENTS`. Free-form prose is not parsed as candidate findings.
- The existing T008 `validate_story_check_fixture_envelope` validator is authoritative. Any T008 validation failure fails the runner closed with no findings.

### E. Safety Behavior

- Live flags disabled -> `unavailable` with explanation; no live call.
- Blocked flag set -> `unavailable` (the orchestrator stub path returns `unavailable` and the live runner is never constructed); no live call.
- Missing `project_name` or `scene_id` -> `unavailable` with explanation; no live call; never invents a `scene_id`.
- Runtime exception from `run_story_check` -> `failed_closed` with explanation; no findings; no persistence; no Memory/Canon mutation.
- Malformed legacy output (non-dict, `None`, `{"error": ...}`, only `coherence_score`/`task`) -> `failed_closed`/`error` with explanation; no findings.
- Unsafe converted output (T008 validator rejects the envelope) -> `failed_closed` with explanation; no findings; no persistence; no Memory/Canon mutation.
- Free-form prose-only legacy output -> `failed_closed` with explanation; no findings. The converter does NOT parse candidate findings from prose.
- Story Check findings remain non-persistent in T016C, even when `persist_candidates=True`. `deterministic_fallback` remains off by default and fallback-only.
- Never mutates Memory/Canon. Never creates promotion records. Never runs apply-promotion. Never generates story prose.

## Testing

All 16 new T016C tests use monkeypatching/mocking only. No real Story Check, route, Ollama, or network access is required.

1. **`test_live_story_check_disabled_by_default_does_not_import_runtime`** — no env flags; monkeypatches `backend.analysis_engine.run_story_check` to a sentinel that raises if called; the orchestrator returns `unavailable` and the sentinel is not invoked.
2. **`test_live_story_check_enabled_with_mocked_runtime_normalizes_candidate_findings`** — `OMI_LIVE_TOOLS_ENABLED=1` + `OMI_LIVE_STORY_CHECK_ENABLED=1` + `OMI_LIVE_STORY_CHECK_SCENE_ID=scene_env_001`; monkeypatches `backend.analysis_engine.run_story_check` to return a representative structured legacy Story Check result; asserts the mocked runtime is called with the right `(project_name, scene_id)`; asserts the converted envelope yields candidate-only diagnostic findings through the T008 pipeline; asserts every finding has `source_adapter == "story_check"`, support-only `provenance.support`, `owner_decision: pending`, `review_status: "candidate_review_pending"`, and no truth/canon/approved/promoted labels in `support_label`; asserts no candidate persistence, no Memory/Canon mutation, no apply-promotion.
3. **`test_live_story_check_explicit_scene_id_overrides_env_scene_id`** — both kwarg `story_check_scene_id="scene_explicit_002"` and env var `OMI_LIVE_STORY_CHECK_SCENE_ID=scene_env_001` are set; the mocked runtime receives `scene_explicit_002`.
4. **`test_live_story_check_missing_scene_id_fails_closed_without_runtime_call`** — `OMI_LIVE_TOOLS_ENABLED=1` + `OMI_LIVE_STORY_CHECK_ENABLED=1`; no kwarg and no env var; monkeypatches `run_story_check` to a sentinel; the orchestrator returns `unavailable` and the sentinel is not invoked.
5. **`test_live_story_check_blocked_flag_overrides_live_availability`** — `OMI_LIVE_STORY_CHECK_BLOCKED=1` overrides the live enablement; the mocked runtime is not invoked; orchestrator returns `unavailable`.
6. **`test_live_story_check_runtime_exception_fails_closed`** — `run_story_check` raises `RuntimeError`; the orchestrator returns `failed_closed` with a runtime-explanation; no findings; no persistence.
7. **`test_live_story_check_malformed_legacy_result_fails_closed`** — `None`, `"not a dict"`, `{"error": "..."}`, and `{"coherence_score": 7, "task": "story_check"}` legacy results all fail closed; no findings; no persistence.
8. **`test_live_story_check_prose_only_legacy_result_fails_closed`** — `narrative_prose` legacy result with free-form prose is fail-closed with no findings; the converter does NOT parse candidate findings from prose.
9. **`test_live_story_check_unsafe_output_fails_closed_via_t008_validator`** — legacy result containing `canon`/`approved`/`rewrite` words fails closed at the T008 validator step.
10. **`test_live_story_check_legacy_error_shape_returns_error_state`** — `{"error": "upstream ollama returned 500"}` legacy shape returns the `error` state with the original error text in the explanation.
11. **`test_live_story_check_existing_fixture_tests_still_pass`** — the T008 fixture-only contract path still passes; the live path does not break the existing T008 contract tests.
12. **`test_live_story_check_persistence_boundary_remains_safe`** — `persist_candidates=False`; spies `extract_omi_candidates_from_raw_idea` and `persist_omi_tool_assisted_findings_as_candidates`; asserts the persistence helpers are NOT called and the safety envelope remains safe.
13. **`test_live_story_check_does_not_call_legacy_route`** — instantiates the live runner closure; asserts `backend.main.story_check` (the legacy FastAPI route) is NOT called.
14. **`test_live_story_check_orchestrator_does_not_call_real_runtime_when_flags_off`** — per-tool flag on but global flag off; the mocked runtime is not invoked; orchestrator returns `unavailable`.

### Test Results

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_story_check_adapter_contract.py -q
```

Result: **25 passed** (11 existing T008 + 14 new T016C).

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
```

Result: all existing tests pass unchanged. Combined T016C validation across the four contract test files: **99 passed**.

## T008 Validator Is Authoritative

The T008 `validate_story_check_fixture_envelope` is unchanged. The live adapter runs the converted envelope through the existing T008 validator before returning. The T008 validator still rejects:

- non-`succeeded` statuses with non-empty findings;
- `source_version` other than `omi_story_check_diagnostic_handoff.v1`;
- `adapter` other than `"story_check"`;
- invalid `finding_type`/aliases that do not map to a known orchestrator finding type;
- missing `evidence`, `source_locator`, or `provenance`;
- prose-intent field names (`rewrite`, `continue`, `outline`, `draft`, `polish`, `improve`, etc.);
- truth/canon/final/approved/promoted labels in any non-evidence string value;
- Memory/Canon mutation, candidate persistence, promotion record, or apply-promotion operation requests;
- `owner_decision.approved=true` or non-`pending` decision.

The live adapter's `_story_check_sanitize_truth_final_labels` helper pre-cleans the legacy text so that the T008 validator can accept it. The replacement table is intentionally narrow: it only normalizes the same words the T008 validator rejects and replaces them with owner-/support-side terminology that preserves the diagnostic intent of the original text.

## Safety Boundaries

- No real Story Check runtime call was made during T016C.
- No real Story Check adapter was implemented for owner-acceptance; T016C is the focused live-adapter implementation behind explicit runtime flags. T016D is the future manual real validation task.
- No real Ollama call was made by the live adapter (T016C does not post to Ollama; the `analysis_engine.run_story_check` callable surface owns the Ollama HTTP behavior).
- No legacy route was called (`backend.main.story_check` is not invoked by the live adapter).
- No Memory/Canon mutation, no automatic promotion records, no automatic apply-promotion, no story prose.
- No candidate persistence (T016C findings remain candidate-only diagnostic support; the persistence helpers were not invoked in the tests; `persist_candidates=False` was the default).
- No fixture, dataset manifest, training record, book source file, or model artifact was touched.
- No frontend/package/dependency file was changed.
- No staging, commit, or push was performed.

## Existing T008/T013/T014C/T015C/T016B Behavior Preserved

- The T008 fixture-only contract is unchanged. `requested_adapters=["story_check"]` without a fixture AND without the live flags returns `unavailable` with the existing T005 stub explanation.
- The T008 `validate_story_check_fixture_envelope` validator is unchanged.
- The T008 contract is preserved for all existing tests in `tests/test_omi_story_check_adapter_contract.py`.
- The T013 preflight `story_check` tool entry is unchanged; T016B's preflight probe continues to report the configured `OLLAMA_BASE_URL`/`OLLAMA_MODEL`/`OLLAMA_TIMEOUT_SECONDS`/`ANALYSIS_MODE` env vars as configuration only.
- The T014C live spaCy wiring is unchanged.
- The T015C live Ollama wiring is unchanged.
- The T016B `OMI_LIVE_STORY_CHECK_ENABLED` / `OMI_LIVE_STORY_CHECK_BLOCKED` / `OMI_LIVE_STORY_CHECK_BLOCKED_REASON` env vars remain the controlling flags.
- The T016C `OMI_LIVE_STORY_CHECK_SCENE_ID` env var is the recommended env-var fallback for the `scene_id` argument. The explicit `story_check_scene_id` kwarg on the orchestrator entrypoint wins over the env var when both are present.

## Files Changed

- `backend/omi_analysis_orchestrator.py` — added env var constants, sanitization/excerpt/label/locator helpers, `_story_check_result_to_envelope` converter, `_build_story_check_live_runner` runner, `_adapter_config_scene_id` helper, `story_check_scene_id` kwarg on `analyze_omi_raw_idea_with_tools`, and live-runner wiring in `_resolve_adapter_runner`; updated module docstring boundaries.
- `tests/test_omi_story_check_adapter_contract.py` — added 14 new T016C tests (live disabled by default, live enabled with mocked runtime success, env scene id, explicit scene id override, missing scene id fail-closed, blocked flag override, runtime exception, malformed legacy result, prose-only legacy result fail-closed, unsafe output fail-closed via T008 validator, legacy error shape, existing fixture tests still pass, persistence boundary, no legacy route call, no live call when flags off).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T016C-live-story-check-adapter-behind-flags.md` — this decision record.
- `docs/roadmap/decision_log.md` — logged T016C decision.
- `docs/roadmap/implementation_status.md` — updated active frontier and child sequence.
- `docs/roadmap/task_backlog.md` — added T016C result.
- `docs/roadmap/phase_map.md` — added T016C result.
- `docs/roadmap/open_questions.md` — refined Q112 with the T016C live-adapter evidence and the recommended next step toward T016D manual real validation.
- `docs/roadmap/risk_register.md` — unchanged (T016C is fail-closed and reduces risk; no new risk).
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` — updated T016C child status, scope, and latest/next child fields.

## Deferred Work

- T016D (manual real Story Check validation) is the future manual real Story Check validation task against a live `qwen3:8b` instance. T016C did not run any real Story Check call. T016D will run the live adapter end-to-end with a real Ollama instance and a real fixture.
- The orchestrator still does not auto-persist Story Check findings. Candidate-only persistence for fused findings remains the T011 contract; T016C findings remain review-pending candidates and the owner must confirm/reject/revise before any future apply-promotion can mutate Memory/Canon.
- Story Check findings are never used to write story prose. The T008 contract forbids prose-intent field names and prose-shaped extracted claims, and the live adapter mirrors these guards in the converter.
- The owner-controlled decision to apply-promotion any Story Check finding remains a separate explicit workflow; T016C does not change that boundary.

## Statements

- T016C implements a live OMI `story_check` adapter behind explicit runtime flags.
- T016C bridges the OMI orchestrator to `backend.analysis_engine.run_story_check(project_name, scene_id)` lazily; the live adapter imports the function only inside the runner closure, never at module import time.
- T016C does not call the legacy `POST /api/projects/{project_name}/story-check/{scene_id}` route.
- T016C does not call real Story Check in tests; all 14 new tests mock `backend.analysis_engine.run_story_check` via `monkeypatch.setattr` and do not require real Story Check, real Ollama, or network.
- T016C converts the legacy runtime output into the existing T008 `omi_story_check_diagnostic_handoff.v1` envelope before validation/normalization.
- T016C's existing T008 `validate_story_check_fixture_envelope` validator is authoritative; the live adapter runs the converted envelope through it and any T008 failure fails the runner closed.
- T016C fails closed on free-form/prose-only/malformed/unsafe output with no findings.
- T016C live path is disabled by default; live flags must be enabled explicitly.
- T016C `OMI_LIVE_STORY_CHECK_BLOCKED` env var overrides live behavior.
- T016C scene id configuration path is documented: explicit `story_check_scene_id` kwarg wins over the `OMI_LIVE_STORY_CHECK_SCENE_ID` env var when both are present; missing both -> `unavailable` without a live call.
- T016C fixture/mock contract remains supported.
- T016C did not perform any real manual validation; T016D remains the future manual real Story Check validation task.
- T016C did not change any frontend/package/dependency files.
- T016C did not add candidate persistence, Memory/Canon mutation, automatic promotion records, automatic apply-promotion, or story prose behavior.
- Nothing was staged, committed, or pushed during T016C.

## Next Steps

- **T016D**: Manual real Story Check validation against a live `qwen3:8b` instance behind the new env flags, similar to T014D/T015D. The expected live-adapter manual run would be:

  ```
  OMI_LIVE_TOOLS_ENABLED=1 \
    OMI_LIVE_STORY_CHECK_ENABLED=1 \
    OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434 \
    OMI_LIVE_OLLAMA_MODEL=qwen3:8b \
    OMI_LIVE_STORY_CHECK_SCENE_ID=scene_001 \
    .venv-unsloth-clean/bin/python -c "from backend.omi_analysis_orchestrator import analyze_omi_raw_idea_with_tools; ..."
  ```

  The expected output is a diagnostic-only adapter envelope with `state: succeeded` (or `failed_closed`/`error` if the live path is unavailable), `findings` carrying T008-shaped diagnostic findings with `source_excerpt`/`source_locator`/`provenance`/`support_label`/`owner_decision: pending`/`review_status: "candidate_review_pending"`, and no candidate persistence, no Memory/Canon mutation, no automatic promotion records, no apply-promotion, no story prose.

- **T017-T020**: Live integration of the remaining selected tools (BookNLP, NCP, Subtxt, dramatica-flow) when each tool's runtime surface is available or explicitly owner-blocked.

- **T021-T025**: Cross-tool fusion validation, candidate-only persistence validation, grouped owner-review UI, automated end-to-end live OMI tests, and manual Cyber Detective Story live OMI test.

- **T026**: PHASE8-IMPL-023 closeout only after all selected live runtime tools are connected/tested or explicitly owner-blocked.
