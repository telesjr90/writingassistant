# PHASE8-IMPL-023-T016A — Story Check Runtime Surface and Fixture Contract Inspection

## Result

PASS for inspect/docs only.

T016A inspects the existing `story_check` fixture/mock contract, any in-repo Story Check runtime surface, current T013 preflight/config/health-check support, the existing Story Check test coverage, and the exact next implementation slice for the live Story Check integration in OMI and analysis. T016A does not implement the live Story Check adapter, does not edit backend runtime behavior, does not edit frontend code, does not add package dependencies, does not install or download anything, does not call any live Story Check runtime, and does not change any preflight config or feature flag. No candidates were produced; no candidate persistence occurred; no Memory/Canon mutation, automatic promotion record, automatic apply-promotion, or story prose occurred.

## Nature

- Inspect/probe/docs task only (T016A).
- T016B (live Story Check preflight/config/availability), T016C (live Story Check adapter behind flags), and T016D (manual real Story Check validation) are deferred.
- This task does not change `backend/omi_runtime_preflight.py`, `backend/omi_analysis_orchestrator.py`, or `backend/main.py`. It only reads them.
- This task does not call the in-repo `backend/analysis_engine.run_story_check` path; it only inspects the source.

## A. Existing Story Check Fixture/Mock Contract

### A.1 Adapter identity

- Adapter identity: `"story_check"` (registered in `OMI_TOOL_ADAPTER_IDENTITIES` and `OMI_ADAPTER_CONTRACTS`).
- Schema version (fixture envelope): `OMI_STORY_CHECK_SCHEMA_VERSION = "omi_story_check_diagnostic_handoff.v1"` (`backend/omi_analysis_orchestrator.py:2554`).
- Support label: `OMI_STORY_CHECK_SUPPORT_LABEL = "Story Check diagnostic support only"` (`backend/omi_analysis_orchestrator.py:2556`).
- Allowed statuses: `OMI_STORY_CHECK_ALLOWED_STATUSES = frozenset({"succeeded", "empty", "failed_closed", "error"})` (`backend/omi_analysis_orchestrator.py:2557-2559`).

### A.2 Required envelope fields

`OMI_STORY_CHECK_ENVELOPE_REQUIRED_FIELDS` (`backend/omi_analysis_orchestrator.py:2560-2566`):

- `schema_version` (must equal `omi_story_check_diagnostic_handoff.v1`).
- `adapter` (must equal `"story_check"`).
- `status` (must be one of `succeeded`, `empty`, `failed_closed`, `error`).
- `provenance` (object).
- `findings` (array; must be empty for non-`succeeded` statuses).

### A.3 Envelope validators (T008 contract)

Implemented in `backend/omi_analysis_orchestrator.py`:

- `validate_story_check_fixture_envelope` (lines 3091-3194).
- `_validate_story_check_provenance` (lines 2865-2875): requires `provenance.adapter == "story_check"` and `provenance.tool_source == "story_check"`.
- `_validate_story_check_finding` (lines 2987-3088): per-finding field/label/claim/evidence/provenance/owner-decision/support-label normalization.
- `_coerce_story_check_candidate_type` (lines 2660-2727): maps fixture `candidate_type`/`finding_type`/aliases into the orchestrator finding-type set (`structural_diagnostic`, `storyform_context`, `throughline_context`, `conflict_diagnostic`, `diagnostic_question`, `open_question`, `plot_thread`, `relationship`, `continuity_warning`, `world_rule`, `evidence_note`).
- `_normalize_story_check_evidence` (lines 2878-2929): normalizes evidence list (or single evidence dict, or single excerpt + `source_locator`) into canonical `source_excerpt` + `source_locator` evidence items.
- `_validate_story_check_owner_decision` (lines 2932-2957): forces `decision: pending`, `approved: false`; rejects any non-`pending` decision or `approved: true`.
- `_validate_story_check_review_status_fields` (lines 2848-2862): requires `review_status`/`candidate_status` to be in `OMI_FINDING_REVIEW_STATUSES` (no `approved`/`canon`/`final`/`promoted`/`truth` states).
- `_normalize_story_check_support_label` (lines 2960-2984): derives a support-only label from `support_label`/`confidence`/`support`/provenance.support; rejects any support/confidence text that contains truth/canon/final/approved/promoted/confirmed_fact labels.

### A.4 Finding type support

`OMI_ADAPTER_CONTRACTS["story_check"]["supports_finding_types"]` (`backend/omi_analysis_orchestrator.py:170-183`):

- `structural_diagnostic`
- `storyform_context`
- `throughline_context`
- `plot_thread`
- `relationship`
- `conflict_diagnostic`
- `diagnostic_question`
- `continuity_warning`
- `open_question`
- `ambiguity`
- `world_rule`
- `evidence_note`

### A.5 Adapter contract summary (`OMI_ADAPTER_CONTRACTS["story_check"]`, lines 162-184)

> "diagnostic-only structural observations and questions; no prose suggestions, no story text, no Memory/Canon mutation, and no promotion/apply-promotion operations. Fixture/mock diagnostic handoff only in T008; live Story Check remains unavailable."

### A.6 Runner

- `_build_story_check_fixture_runner(fixture, *, adapter_config=None)` (`backend/omi_analysis_orchestrator.py:3197-3264`).
- Wired into `_resolve_adapter_runner` at `backend/omi_analysis_orchestrator.py:4737-4741` behind `adapter_fixture_outputs["story_check"]`.
- Unavailable branch (no fixture): `backend/omi_analysis_orchestrator.py:5024-5034` returns `unavailable` with explanation that the orchestrator does not perform live Story Check calls, does not import Story Check runtime code, and does not write Story Check output.

### A.7 Safety/no-prose/no-truth/fail-closed rules (T008 contract)

Implemented in `backend/omi_analysis_orchestrator.py`:

- `_validate_story_check_payload_no_forbidden_operations` (lines 2771-2811): rejects envelope/finding field names containing substrings like `operation`, `action`, `command`, `persist candidate(s)`, `memory mutation`, `canon mutation`, `promotion record`, `apply promotion`, `promote to canon`; and rejects envelope/finding string values matching the `_OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE` regex (`persist(ed)? candidates?`, `save candidates?`, `candidate persistence`, `apply[-_ ]?promotion`, `promotion record`, `promote to canon`, `mutat(e|ion) (memory|canon)`, `write (candidate|memory|canon)`, `perform(ing)? (an )?operation`).
- `_validate_story_check_payload_no_generation_language` (lines 2814-2845): rejects string values matching `_OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE` (`rewrite`, `rewritten`, `continue`, `continuation`, `expand`, `expanded`, `polish`, `polished`, `outline`, `draft`, `revise`, `revised`, `write the story/scene/chapter/prose`, `generate a story/scene/chapter/outline/draft/prose`, `what happens next`, `what should happen next`, `next scene should`, `next chapter should`).
- `_validate_story_check_no_truth_final_label_in_value` (lines 2738-2768) plus `_story_check_string_has_truth_final_label` (lines 2730-2735): rejects truth/canon/final/approved/promoted labels in any non-evidence string value (re-uses the shared `is_truth_label` plus a Story Check-specific regex matching `final|finalized|finalised|definitive|accepted|locked|canon|canonical|truth|approved|promoted|confirmed_fact`).
- `_validate_ollama_field_names_no_prose` is also invoked on the envelope and each finding to reject prose-intent field names (`rewrite`, `continue`, `outline`, `draft`, etc.).
- `is_prose_like_text(extracted_claim)` is invoked on the finding `extracted_claim` (with one exception for `diagnostic_question` candidate type, which must end with `?` and pass the question-shape check).
- `missing` evidence/`source_locator`/`provenance`/`schema_version`/`adapter`/`status` all fail closed.
- Unknown `candidate_type` aliases fail closed (no implicit mapping to orchestrator finding types).
- Auto-approved `owner_decision` (`approved: true` or `decision: approve/reject/finalize`) fails closed.
- `review_status` not in `OMI_FINDING_REVIEW_STATUSES` fails closed.

### A.8 Persistence boundary

- Story Check findings remain non-persistent at the orchestrator level (T008 keeps `story_check` as a fixture-only contract; even with `persist_candidates=True`, the orchestrator path treats `story_check` as scaffold-only and the `_build_story_check_fixture_runner` does not call `project_manager.persist_omi_tool_assisted_findings_as_candidates`).
- The orchestrator entrypoint `analyze_omi_raw_idea_with_tools` calls `project_manager.persist_omi_tool_assisted_findings_as_candidates` only when `requested_adapters` includes adapters whose live runner is reached AND `persist_candidates=True`; the Story Check `requested_adapters=["story_check"]` path is still fixture-only and the T008 contract was scaffolded non-persistent.

## B. Existing Story Check Runtime Surface Inventory

### B.1 In-repo module: `backend/analysis_engine.py`

- File: `backend/analysis_engine.py` (88 lines).
- Entry point: `run_story_check(project_name: str, scene_id: str) -> dict[str, Any]` (line 46).
- Imports: `requests` (third-party; not added by T008 — pre-existing dependency), `analysis_modes`, `analysis_normalizer`, `guardrails`, `project_manager`, `storyform.Storyform`.
- Constant `MOCK_STORY_CHECK_PATH` (line 22) = `Path(__file__).resolve().parent / "mock_responses" / "story_check.json"`.
- Constant `PROMPT_PATH` (line 21) = `Path(__file__).resolve().parent / "prompts" / "story_check.txt"`.
- Constant `DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"` (line 23; note: separate from the orchestrator's `OMI_LIVE_OLLAMA_BASE_URL_DEFAULT = "http://127.0.0.1:11434"`).
- Constant `DEFAULT_OLLAMA_MODEL = "qwen3:8b"` (line 24; same as orchestrator default).
- Constant `OLLAMA_STORY_CHECK_NUM_PREDICT = 2048` (line 25).
- Analysis mode constants (`backend/analysis_modes.py`): `MOCK = "mock"`, `OLLAMA_BASELINE = "ollama_baseline"`, `DEFAULT_ANALYSIS_MODE = OLLAMA_BASELINE`. `get_analysis_mode()` reads `ANALYSIS_MODE` env var (default `ollama_baseline`) and raises `ValueError` on unknown values.
- Behavior of `run_story_check` (lines 46-87):
  - If `analysis_modes.get_analysis_mode() == MOCK`, returns `_load_mock_story_check_response()` (reads `backend/mock_responses/story_check.json`, runs it through `analysis_normalizer.normalize_story_check_output` and `guardrails.sanitize_story_check_output`).
  - Otherwise (default `ollama_baseline`):
    - Reads `OLLAMA_TIMEOUT_SECONDS` (default `300`) — note: this is the pre-T015F hard-coded `analysis_engine` timeout, NOT the orchestrator's `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var. They are separate and not coordinated.
    - Loads `Storyform.from_file(project_name).to_prompt_context()` (fails closed on missing/invalid `storyform.json`).
    - Loads scene text via `project_manager.load_scene(project_name, scene_id)`.
    - Loads bible via `project_manager.load_bible(project_name)`.
    - Renders `backend/prompts/story_check.txt` with `storyform_context`, `scene_text`, `bible_summary`.
    - POSTs to `OLLAMA_BASE_URL/api/chat` (or default `http://localhost:11434/api/chat`) with model=`OLLAMA_MODEL` (default `qwen3:8b`), `format: json`, `think: false`, `temperature: 0`, `num_predict: 2048`, `stream: false`. The `think: false` field is hard-coded in the request body; the pre-T015E `analysis_engine` and the post-T015E `analysis_engine` both include it. **Note:** T015E added `think: false` at the orchestrator level for `_build_ollama_model_live_runner`; the pre-existing `analysis_engine.run_story_check` request body already has `think: false`. The two paths are independent and use different code, different env vars, and different URLs.
    - Parses `response.json()["message"]["content"]` and runs it through `analysis_normalizer.normalize_story_check_output` and `guardrails.sanitize_story_check_output`.
    - On any exception, returns `{"error": str(e)}` (does NOT raise). This is a different error shape from the orchestrator's `failed_closed`/`error` envelope.
- Side effects: `requests.post` is a real HTTP call when `ANALYSIS_MODE=ollama_baseline`. `requests` is a pre-existing dependency in `requirements.txt` (not added by T008 or T016A). `_load_mock_story_check_response` only reads a local file; no writes.
- File writes: none.

### B.2 Existing route: `POST /api/projects/{project_name}/story-check/{scene_id}`

- File: `backend/main.py:327-332`.
- Function: `story_check(project_name: str, scene_id: str) -> dict`.
- Behavior: calls `_analysis_module.run_story_check(project_name, scene_id)` inside try/except; on exception returns `{"error": str(exc)}`. **The route is NOT gated by any live/runtime feature flag.** Any caller that hits the route with `ANALYSIS_MODE=ollama_baseline` will trigger a real `requests.post` to `OLLAMA_BASE_URL/api/chat`. The route is a pre-existing legacy route that is not part of the OMI orchestrator path.
- Comparison to OMI orchestrator path: the route is reachable directly from the existing FastAPI app and is NOT behind `OMI_LIVE_TOOLS_ENABLED` / `OMI_LIVE_STORY_CHECK_ENABLED` flags. The orchestrator path is gated by the same env flags and uses the `_resolve_adapter_runner` mechanism. The T008 fixture-only contract is on the orchestrator path; the pre-existing route is on its own.

### B.3 Existing prompt file: `backend/prompts/story_check.txt`

- 108 lines.
- Defines a strict JSON-only Story Check output schema with `task: "story_check"`, `coherence_score: 0-10`, `throughline_alignment.overall_story/main_character/influence_character/relationship_story` (each with `present: bool`, `evidence: []`, `concerns: []`), `theme_drift: {status, reason}`, `character_consistency: {status, reason}`, `warnings: []` (capped at 5 with allowed prefixes `[Plot/Temporal]`, `[Character]`, `[Worldbuilding]`, `[Factual]`, `[Stylistic]`), `suggestions: []` (capped at 5 writer-focused diagnostic questions), `insufficient_evidence: []`.
- Enforces no-prose boundaries (no rewrite, continue, imitate, polish, improve, expand, generate dialogue/scenes/chapters/paragraphs/openings/endings/monologues/passages).
- Enforces evidence rules (no invented evidence, no inferred Main Character/Influence Character/Relationship Story/CIPS/dynamics/Issue/Variation/Concern/Problem/Solution/signposts/act turns without owner-approved storyform + scene evidence).
- Enforces analysis boundaries (no story prose, no rewrite, no continue, no outline, no draft, no polish, no expand, no imitate, no revise, no improvement suggestion, no generation).

### B.4 Existing mock fixture: `backend/mock_responses/story_check.json`

- Rich Story Check shape: `coherence_score: 7`, `throughline_alignment` with `present: false` for `main_character` / `influence_character` / `relationship_story` and `present: true` for `overall_story`, `theme_drift: insufficient_evidence`, `character_consistency: consistent`, `warnings: []`, `suggestions: []` (writer-focused diagnostic questions), `insufficient_evidence: []`, `diagnostics: {analysis_mode: mock, fixture: backend/mock_responses/story_check.json, candidate_only: true, mutates_project_truth: false}`.
- `diagnostics.candidate_only: true` and `diagnostics.mutates_project_truth: false` are explicit, fixture-level metadata that the mock is non-canon and non-mutating.

### B.5 Existing evaluation fixtures: `tests/fixtures/story_check/`

- `valid_rich_story_check.json`
- `minimal_story_check.json`
- `malformed_story_check.txt`
- `insufficient_evidence_story_check.json`
- `unsafe_output_story_check.json`
- (Implicit `refusal_response.json` referenced by `tests/test_story_check_baseline_eval.py::test_all_app_12_fixtures_are_represented` and present in `tests/fixtures/story_check/`; not enumerated in the find listing because the find pattern matched by name not by extension alone — but it is present per the test.)
- These six fixtures are the App-12 evaluation fixture set used by `tests/test_story_check_baseline_eval.py` and `training/scripts/run_story_check_baseline_eval.py`. They are evaluation-only and never reach the live runtime.

### B.6 Existing schema file (training-only, optional): `training/schemas/story_check.schema.json`

- Read by `backend/analysis_normalizer.validate_story_check_schema` (line 18). If absent, schema validation returns `False, ["Story Check schema validation unavailable."]` and the normalizer still returns a `legacy_small_schema: True` shape with `schema_valid: False`. Not required for runtime correctness.

### B.7 No standalone CLI / no separate Story Check package

- There is no `story_check` CLI command, no `story-check` Python entry point, no `StoryCheck` class, and no Story Check package on PyPI. The runtime surface is `backend/analysis_engine.run_story_check` invoked through the legacy `POST /api/projects/{project_name}/story-check/{scene_id}` route.
- There is no other in-repo Story Check callable surface. The orchestrator-side `_build_story_check_fixture_runner` is fixture-only and does not import or call `analysis_engine.run_story_check`.

### B.8 Callable surface summary

| Callable | File | Triggered by | Live call? |
|---|---|---|---|
| `run_story_check(project_name, scene_id)` | `backend/analysis_engine.py:46` | `POST /api/projects/{project_name}/story-check/{scene_id}` (route) | Yes (if `ANALYSIS_MODE=ollama_baseline`); mock (if `ANALYSIS_MODE=mock`) |
| `_build_story_check_fixture_runner(fixture)` | `backend/omi_analysis_orchestrator.py:3197` | OMI orchestrator with `adapter_fixture_outputs["story_check"]` | No (fixture-only) |
| `_load_mock_story_check_response()` | `backend/analysis_engine.py:34` | internal | No (file read only) |
| `_parse_story_check_response(content)` | `backend/analysis_engine.py:28` | internal | No (parse only) |

## C. T013 Preflight/Config Gap Analysis

### C.1 Existing preflight support for `story_check`

In `backend/omi_runtime_preflight.py`:

- `OMI_LIVE_TOOL_ENABLED_ENVS["story_check"] = "OMI_LIVE_STORY_CHECK_ENABLED"` (line 43).
- `OMI_LIVE_TOOL_BLOCKED_ENVS["story_check"] = "OMI_LIVE_STORY_CHECK_BLOCKED"` (derived at lines 51-54).
- `OMI_LIVE_TOOL_BLOCKED_REASON_ENVS["story_check"] = "OMI_LIVE_STORY_CHECK_BLOCKED_REASON"` (derived at lines 56-59).
- `_dependency_probe(adapter="story_check", env=env)` (lines 280-283):
  ```python
  elif adapter == "story_check":
      configured = _path_exists("backend/analysis_engine.py")
      available = configured
      detail = "In-repo module surface probe: backend/analysis_engine.py"
  ```
  This is a **file-existence-only** probe. It does not check that `analysis_engine.run_story_check` is importable, does not check that `requests` is installed, does not check that `OLLAMA_BASE_URL` is reachable, does not check that `qwen3:8b` is available, does not check that `backend/prompts/story_check.txt` is present, and does not check that `analysis_modes.get_analysis_mode()` resolves to a valid mode.
- The preflight reports `story_check` as `available` whenever `backend/analysis_engine.py` exists, regardless of whether the actual `run_story_check` function can succeed. T014E (`docs/roadmap/decisions/PHASE8-IMPL-023-T014E-live-runtime-tool-installation-inventory.md`) already records: "Story Check: in-repo module (no live adapter); YES: OMI_LIVE_STORY_CHECK_ENABLED, file-existence probe in preflight; NO (T008 fixture-only); NOT_ATTEMPTED; T016 — Live Story Check integration; Live adapter needs implementation."

### C.2 Missing preflight probes (gaps for T016B)

1. **No `run_story_check` importable probe.** T016B should add a read-only probe that confirms `analysis_engine.run_story_check` is importable from `backend.analysis_engine` and is callable with two positional string args. The probe should never call the function; it should only `importlib.util.find_spec` the `analysis_engine` module path or attempt a `getattr(run_story_check, "__call__")` on a `lambda: None` to verify the function object is present. The current probe only checks file existence.
2. **No `requests` package probe.** `analysis_engine.run_story_check` uses `requests.post` to call Ollama. If `requests` is not installed, the live path fails with `ImportError`. The preflight should probe for `importlib.util.find_spec("requests")` and report a clear `unavailable` reason if missing.
3. **No `backend/prompts/story_check.txt` probe.** The prompt file is required for live runs. The preflight should confirm `(_REPO_ROOT / "backend/prompts/story_check.txt").exists()` and report a clear `unavailable` reason if missing. The mock path does not require this file, so this probe is for the live path only.
4. **No `backend/mock_responses/story_check.json` probe.** The mock path reads this file. The preflight could confirm the file exists; missing mock response would still be allowed (the live path would still work), but it's a useful signal.
5. **No `analysis_modes` validity probe.** T016B should confirm `analysis_modes.get_analysis_mode()` returns a known value (mock or ollama_baseline) and that `ANALYSIS_MODE` env var is not set to an unknown value.
6. **No `Storyform` importable probe.** The live path requires `backend.storyform.Storyform.from_file` to be importable. The preflight could confirm the symbol exists.
7. **No Ollama HTTP reachability probe for the analysis_engine base URL.** The preflight's `ollama_model` adapter uses `OMI_LIVE_OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`). `analysis_engine.run_story_check` uses `OLLAMA_BASE_URL` (default `http://localhost:11434`). These are two different env vars. T016B should clarify which env var drives the live Story Check path and document that the preflight probe for Ollama covers `OMI_LIVE_OLLAMA_BASE_URL` (the orchestrator path) but not `OLLAMA_BASE_URL` (the legacy `analysis_engine` route path). If T016C reuses `_build_ollama_model_live_runner` infrastructure, the orchestrator env var is the right one. If T016C wires directly to `analysis_engine.run_story_check`, the legacy env var is the right one.
8. **No timeout / num_predict / model env var.** The legacy route reads `OLLAMA_TIMEOUT_SECONDS` (default `300`, NOT clamped), `OLLAMA_MODEL` (default `qwen3:8b`). These are separate from `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` and `OMI_LIVE_OLLAMA_MODEL`. T016B should either (a) align the legacy path to the orchestrator env vars, or (b) document the divergence and add `OMI_LIVE_STORY_CHECK_TIMEOUT_SECONDS` and `OMI_LIVE_STORY_CHECK_MODEL` for the legacy path.

### C.3 Existing feature flags (already in place)

| Env var | Default | Purpose |
|---|---|---|
| `OMI_LIVE_TOOLS_ENABLED` | `false` | Global live-tools gate |
| `OMI_LIVE_STORY_CHECK_ENABLED` | `false` | Per-tool live gate |
| `OMI_LIVE_STORY_CHECK_BLOCKED` | `false` | Explicit block override |
| `OMI_LIVE_STORY_CHECK_BLOCKED_REASON` | (none) | Block reason |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Legacy route Ollama base URL (note: separate from `OMI_LIVE_OLLAMA_BASE_URL` default `http://127.0.0.1:11434`) |
| `OLLAMA_MODEL` | `qwen3:8b` | Legacy route Ollama model |
| `OLLAMA_TIMEOUT_SECONDS` | `300` | Legacy route Ollama HTTP timeout (hard-coded, not clamped) |
| `ANALYSIS_MODE` | `ollama_baseline` | `mock` or `ollama_baseline` for `analysis_engine.run_story_check` |

### C.4 What the live Story Check preflight should report (T016B)

T016B should report a `story_check` tool entry that includes:

- `runtime_configured` (existing): `backend/analysis_engine.py` exists.
- `runtime_dependency_available` (extended): `_path_exists("backend/analysis_engine.py")` AND `_find_module("requests")` AND `_path_exists("backend/prompts/story_check.txt")` AND (legacy route only) `OLLAMA_BASE_URL` reachable OR (orchestrator path) `OMI_LIVE_OLLAMA_BASE_URL` reachable with `OMI_LIVE_OLLAMA_MODEL` available in `/api/tags`.
- `story_check_prompt_path`: `backend/prompts/story_check.txt` (boolean: exists).
- `story_check_mock_path`: `backend/mock_responses/story_check.json` (boolean: exists).
- `analysis_engine_mode` (new): the value of `ANALYSIS_MODE` env var resolved through `analysis_modes.get_analysis_mode()` — but read-only, no behavior change.
- `story_check_request_timeout` (new, optional): the value of `OLLAMA_TIMEOUT_SECONDS` (legacy) or `OMI_LIVE_STORY_CHECK_TIMEOUT_SECONDS` (new) if T016B adds the latter.
- `ollama_base_url` (existing for `ollama_model` tool): `OMI_LIVE_OLLAMA_BASE_URL` for the orchestrator path; this is reported under the `ollama_model` tool, not under `story_check`, so T016B should clarify in the `story_check` probe detail which Ollama env var it depends on.

## D. Existing Tests for Story Check

### D.1 OMI orchestrator contract tests (fixture-only)

- `tests/test_omi_story_check_adapter_contract.py` (379 lines, 11 passed; T008 contract).
  - `test_story_check_without_fixture_returns_unavailable_and_no_findings` — confirms `requested_adapters=["story_check"]` without fixture returns `unavailable` with "fixture" and "live story check" in the explanation; no findings; no persistence; fail-closed.
  - `test_valid_story_check_diagnostic_fixture_normalizes_candidate_only_findings` — exercises all 5 finding types: `structural_diagnostic`, `storyform_context`, `throughline_context`, `plot_thread`, `relationship`.
  - `test_valid_story_check_diagnostic_question_is_review_support_not_prose` — exercises `diagnostic_question` with the question ending in `?`.
  - `test_story_check_invalid_json_schema_adapter_or_unknown_type_fails_closed` — `not json`, wrong `schema_version`, mismatched `adapter`, unknown `finding_type=scene_prose`.
  - `test_story_check_missing_evidence_fails_closed` — missing `evidence`.
  - `test_story_check_missing_source_locator_fails_closed` — missing `source_locator`.
  - `test_story_check_missing_provenance_fails_closed` — missing `provenance`.
  - `test_story_check_truth_canon_approved_or_final_labels_fail_closed` — truth/canon/approved/final labels in support_label, owner_decision, or review_status.
  - `test_story_check_prose_rewrite_outline_draft_continue_suggestions_fail_closed` — rewrite/continue/outline/draft in `diagnostic_claim` or `question`; fail-closed with prose or diagnostic explanation.
  - `test_story_check_memory_canon_promotion_apply_promotion_and_persistence_fail_closed` — `memory_mutation`, `canon_mutation`, `promotion_record`, `apply_promotion`, `persist_candidates=True` fields all fail closed.
  - `test_story_check_findings_are_not_persisted_even_when_persist_candidates_true` — monkeypatches `project_manager.extract_omi_candidates_from_raw_idea`; even with `persist_candidates=True` and `source_idea_id`, Story Check findings are not persisted; `safety.no_memory_canon_mutation` and `safety.no_apply_promotion` are both `True`.

### D.2 Route tests (legacy `POST /api/projects/.../story-check/...` route)

- `tests/test_story_check_route.py` (187 lines).
  - `test_story_check_route_returns_minimal_report` — minimal report passes through.
  - `test_story_check_route_returns_rich_report` — rich report passes through.
  - `test_story_check_route_returns_fallback_report` — fallback report with `insufficient_evidence` passes through.
  - `test_story_check_route_allows_missing_rich_fields_and_unknown_fields` — unknown future fields preserved.
  - `test_story_check_route_returns_error_shaped_report` — `{"error": ...}` shape passes through.
  - `test_story_check_route_does_not_guard_scene_text_as_request_intent` — scene text containing "write a scene" is accepted (owner-authored).
  - `test_story_check_route_returns_mock_mode_output_without_ollama` — `ANALYSIS_MODE=mock` returns the mock fixture without calling `requests.post`.

### D.3 Evaluation/baseline tests

- `tests/test_story_check_baseline_eval.py` (170 lines).
  - 11 tests, all use `tests/fixtures/story_check/` fixtures, mock `run_live_ollama_evaluation`, never call real Ollama.
  - 6 fixtures expected: `valid_rich_story_check.json`, `minimal_story_check.json`, `malformed_story_check.txt`, `refusal_response.json`, `insufficient_evidence_story_check.json`, `unsafe_output_story_check.json`.
  - `test_default_cli_mode_does_not_call_live_ollama` — default mode is `offline_fixtures`; no live Ollama.
  - `test_live_mode_is_opt_in` — `--live-ollama` is explicit opt-in.

### D.4 Prompt tests

- `tests/test_story_check_prompt.py` (96 lines).
  - `test_story_check_prompt_exists` — file exists.
  - `test_prompt_mentions_required_rich_schema_fields` — task, coherence_score, throughline_alignment, overall_story, main_character, influence_character, relationship_story, theme_drift, character_consistency, warnings, suggestions, insufficient_evidence.
  - `test_prompt_includes_no_prose_boundaries` — "do not write story prose", "do not rewrite the scene", "do not continue the scene", "do not imitate style", "improve, polish", "do not generate dialogue", "scenes, chapters, paragraphs".
  - `test_prompt_requires_json_only_no_markdown_or_code_fences`.
  - `test_prompt_requires_insufficient_evidence_instead_of_guessing`.
  - `test_prompt_blocks_common_dramatica_overclaims` — "A character relationship existing is not proof of Relationship Story.", "A generic theme is not proof of Dramatica Issue/Variation.", "Antagonist is not automatically Influence Character.".
  - `test_prompt_bounds_warnings_and_suggestions`.
  - `test_prompt_does_not_contain_sample_story_prose` — no "once upon a time", "she said", "he said", "the princess and the pea", "elena", "ember crown".

### D.5 Other Story Check touch tests

- `tests/test_omi_extraction_contract.py` — monkeypatches `main._analysis_module.run_story_check` to assert OMI extraction does not call Story Check.
- `tests/test_omi_extraction_expected_red.py` — monkeypatches `main._analysis_module.run_story_check` similarly for the expected-red contract.
- `tests/test_omi_tool_assisted_fusion_dedupe_contract.py` — `story_check` is one of the adapters in the fusion/dedupe/contract test fixture.
- `tests/test_evaluation_fixtures.py` — uses `normalize_story_check_output` and `validate_story_check_schema` over `tests/fixtures/story_check/`.

## E. Recommended Next Slices

The recommended next child after T016A is `PHASE8-IMPL-023-T016B`. The slices are small and bounded; the order is dictated by the existing T013/T015C precedent and the Story Check runtime surface inventory in section B.

### E.1 T016B — Story Check runtime preflight/config/availability (recommended next)

**Goal:** extend `backend/omi_runtime_preflight.py` so the `story_check` tool entry reports more accurate availability and surfaces a clear `unavailable` reason when the live path cannot run.

**Files to touch:**

- `backend/omi_runtime_preflight.py` — extend `_dependency_probe(adapter="story_check", env=env)` to additionally probe:
  - `requests` Python package (`importlib.util.find_spec("requests")`).
  - `backend/prompts/story_check.txt` exists.
  - `backend/mock_responses/story_check.json` exists.
  - `analysis_modes.get_analysis_mode()` returns a valid value (mock or ollama_baseline).
  - `Storyform.from_file` is importable from `backend.storyform`.
  - Optional: surface a `story_check_ollama_base_url` derived from `OLLAMA_BASE_URL` (legacy) or `OMI_LIVE_OLLAMA_BASE_URL` (orchestrator path), with a clear documentation note in `probe_detail` that the env var depends on which path T016C picks.
- `backend/omi_runtime_preflight.py` — add `story_check_request_timeout` to the report, defaulting to `OLLAMA_TIMEOUT_SECONDS` env var (default `300`) for the legacy path, or a new `OMI_LIVE_STORY_CHECK_TIMEOUT_SECONDS` env var if T016B adds it.
- `tests/test_omi_live_runtime_preflight_contract.py` — add expected-red tests:
  - `test_story_check_in_repo_module_reports_available_with_default_flags` — `backend/analysis_engine.py` exists; no env flags; status `available` (dependency is present, flags are off).
  - `test_story_check_runtime_with_flags_reports_enabled_when_module_prompt_and_requests_present` — `OMI_LIVE_TOOLS_ENABLED=1` + `OMI_LIVE_STORY_CHECK_ENABLED=1`; `requests` is `importlib.util.find_spec`-able; `backend/prompts/story_check.txt` exists; status `enabled`.
  - `test_story_check_runtime_reports_unavailable_when_prompt_missing` — delete the prompt file or monkeypatch `_path_exists`; status `unavailable` with prompt-missing reason.
  - `test_story_check_runtime_reports_unavailable_when_requests_missing` — monkeypatch `find_spec` to return None; status `unavailable`.
  - `test_story_check_blocked_flag_overrides_enablement` — `OMI_LIVE_STORY_CHECK_BLOCKED=1` overrides enabled state; status `blocked`.
  - `test_story_check_analysis_mode_env_var_is_reported` — `ANALYSIS_MODE=mock` and `ANALYSIS_MODE=ollama_baseline` are reported; `ANALYSIS_MODE=bogus` falls back to default (or raises — decide in T016B; `analysis_modes.get_analysis_mode` currently raises `ValueError`).
- No live Story Check call, no model analysis, no candidates, no Memory/Canon mutation, no apply-promotion, no story prose.

### E.2 T016C — Live Story Check adapter behind flags (conditional on T016B)

**Goal:** add a live Story Check adapter runner that uses the existing in-repo `backend/analysis_engine.run_story_check` callable (or a new path that reuses the orchestrator's `_build_ollama_model_live_runner` infrastructure) behind explicit env flags.

**Open decision to resolve in T016B (or T016C):**

1. **Which path does T016C wire to?**
   - (A) Wire the orchestrator's `_build_story_check_live_runner` to call the existing `backend.analysis_engine.run_story_check(project_name, scene_id)`. Pros: reuses the existing prompt, schema, and Sanitize pipeline. Cons: the orchestrator's adapter interface is `(*, project_name, raw_idea, source_idea_id)` and the `analysis_engine` interface is `(project_name, scene_id)`. T016C must bridge: load scene text + bible + storyform from `project_manager` and `storyform` modules, then call `analysis_engine.run_story_check`. The orchestrator adapter would be responsible for constructing a `scene_id` from `source_idea_id` or for accepting `scene_id` through `adapter_config`.
   - (B) Build a fresh `_build_story_check_live_runner` that does not go through `analysis_engine.run_story_check` and instead posts to `OMI_LIVE_OLLAMA_BASE_URL/api/chat` directly with a fresh Story Check prompt, similar to `_build_ollama_model_live_runner`. Pros: full control over env vars, timeout, prose guard, validation pipeline; reuses the orchestrator's existing T006/T015C live HTTP infrastructure. Cons: duplicates `analysis_engine.run_story_check` logic.
   - (C) Refactor `analysis_engine.run_story_check` into a pure `_call_ollama_for_story_check` helper that takes a prompt and base URL, then have both the legacy route and the new orchestrator runner call it. Pros: no duplication. Cons: refactor scope expands beyond the small micro-task.

   T016B (or T016C) should pick one and document the choice. The recommended option is (A) or (C) because they reuse the existing prompt + sanitization. The orchestrator's T006/T015C infrastructure is more battle-tested for HTTP and parsing, but it expects a `raw_idea` text and not a `(project_name, scene_id)` pair. Bridging to `analysis_engine.run_story_check` is the smallest correct change.

2. **Which `scene_id` does the orchestrator pass?** The orchestrator signature is `(*, project_name, raw_idea, source_idea_id)`. The `analysis_engine` signature is `(project_name, scene_id)`. T016C must derive a `scene_id` — either from a new `OMI_LIVE_STORY_CHECK_SCENE_ID` env var, from the most-recently-touched scene in the project, from a `scene_id` carried in `adapter_config`, or from `source_idea_id` if it is a scene id. This decision should be made in T016B (proposed: env var `OMI_LIVE_STORY_CHECK_SCENE_ID` with a fail-closed default if missing).

3. **What timeout does the live runner use?** The legacy route uses `OLLAMA_TIMEOUT_SECONDS` (default 300, not clamped). The orchestrator's `_build_ollama_model_live_runner` uses `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` (default 180, clamped). T016C should pick one and document.

4. **Does the live Story Check output go through `analysis_normalizer.normalize_story_check_output` (rich Story Check schema) or `validate_story_check_fixture_envelope` (T008 fixture schema)?** They are different. The legacy route uses `analysis_normalizer.normalize_story_check_output`; the T008 fixture contract uses `validate_story_check_fixture_envelope`. T016C must decide which output shape the orchestrator's live runner produces. The recommended path: the live runner returns a T008-compatible `omi_story_check_diagnostic_handoff.v1` envelope that the existing fixture validator already understands, and the per-finding normalization reuses the T008 `diagnostic_claim`/`extracted_claim`/`source_excerpt`/`source_locator`/`provenance`/`support_label`/`owner_decision`/`review_status`/`candidate_fingerprint` fields. Concretely, the live runner must convert the legacy rich-Story-Check shape (throughline_alignment, theme_drift, character_consistency, warnings, suggestions, insufficient_evidence) into T008-shaped findings, because the orchestrator only understands the T008 finding schema. This is a non-trivial conversion; T016C must do it explicitly.

**Files to touch (T016C, conditional on T016B):**

- `backend/omi_analysis_orchestrator.py` — add `_build_story_check_live_runner` function (analogous to `_build_ollama_model_live_runner` and `_build_spacy_live_runner`); wire into `_resolve_adapter_runner` behind `OMI_LIVE_TOOLS_ENABLED` + `OMI_LIVE_STORY_CHECK_ENABLED` + not `OMI_LIVE_STORY_CHECK_BLOCKED`; convert the rich Story Check response to T008-shaped findings; validate through `validate_story_check_fixture_envelope`; fail-closed on HTTP error, non-JSON, prose, truth, canon, missing evidence, missing source_locator, missing provenance.
- `tests/test_omi_story_check_adapter_contract.py` — add expected-red tests for the live runner (mock `analysis_engine.run_story_check` / mock the HTTP layer).
- No live Story Check call, no model analysis, no candidates, no Memory/Canon mutation, no apply-promotion, no story prose.

### E.3 T016D — Manual real Story Check validation (conditional on T016C)

**Goal:** run the live Story Check adapter against a real Ollama `qwen3:8b` instance (Windows-hosted or WSL-hosted) and confirm the diagnostic-only candidate output, fail-closed behavior, and timeout behavior end to end.

**Tests:** manual validation, not a test file. The acceptance test command should be:

```
OMI_LIVE_TOOLS_ENABLED=1 OMI_LIVE_STORY_CHECK_ENABLED=1 \
  OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434 \
  OMI_LIVE_OLLAMA_MODEL=qwen3:8b \
  OMI_LIVE_STORY_CHECK_SCENE_ID=scene_001 \
  .venv-unsloth-clean/bin/python -c "..."
```

The "..." is a one-line Python snippet that calls the orchestrator with `requested_adapters=["story_check"]` and prints the result. The expected output is a diagnostic-only adapter envelope with `state: succeeded` (or `failed_closed`/`error` if the live path is unavailable), `findings` carrying T008-shaped diagnostic findings with `source_excerpt`/`source_locator`/`provenance`/`support_label`/`owner_decision: pending`/`review_status: candidate_review_pending`, and no candidate persistence, no Memory/Canon mutation, no automatic promotion records, no apply-promotion, no story prose.

### E.4 Alternative path: BLOCKED / owner-decision

If the owner decides that the in-repo `analysis_engine.run_story_check` is not the right live Story Check surface for OMI (for example, because the legacy route is being deprecated, or because the owner wants a fresh implementation), T016C should be replaced with `PHASE8-IMPL-023-T016C-OWNER-DECISION-NEEDED` that records the decision and points the OMI MVP path to (a) an alternative live Story Check surface if one exists, or (b) an explicit `BLOCKED` status for the `story_check` adapter per the T014E precedent. T016A does not need to choose this path; it is documented as a contingency.

## F. Files Inspected

- `backend/omi_analysis_orchestrator.py` (5177 lines; lines 1-299 adapter identities/contracts, 2540-3264 Story Check fixture contract, 3540-3700 context adapters, 4284-4519 spaCy live runner, 4523-4700 Ollama live runner, 4690-4826 `_resolve_adapter_runner`, 5000-5177 `analyze_omi_raw_idea_with_tools`).
- `backend/omi_runtime_preflight.py` (489 lines; lines 40-49 enabled-env map, 51-59 blocked/reason-env map, 220-343 `_dependency_probe`, 280-283 `story_check` probe, 346-434 `_tool_report`, 437-489 `build_omi_runtime_preflight_report`).
- `backend/main.py` (lines 327-332 `story_check` legacy route, 358-360 `/api/projects/{name}/omi/runtime-preflight`).
- `backend/analysis_engine.py` (88 lines; full file).
- `backend/analysis_modes.py` (18 lines; `MOCK`, `OLLAMA_BASELINE`, `VALID_ANALYSIS_MODES`, `DEFAULT_ANALYSIS_MODE`, `get_analysis_mode`).
- `backend/analysis_normalizer.py` (305 lines; `STORY_CHECK_SCHEMA_PATH` line 18, `validate_story_check_schema` line 102, `normalize_story_check_output` line 118, `_normalize_story_check_object` line 137, `_looks_like_rich_story_check` line 263).
- `backend/guardrails.py` (288 lines; `sanitize_story_check_output` line 204, `_sanitize_output_value` line 257, `OUTPUT_GUARD_*` constants).
- `backend/prompts/story_check.txt` (108 lines; full file).
- `backend/mock_responses/story_check.json` (65 lines; full file).
- `tests/test_omi_story_check_adapter_contract.py` (379 lines; 11 tests; T008 contract).
- `tests/test_omi_tool_assisted_orchestrator_contract.py` (884 lines; 30 tests; T005/T015F contract).
- `tests/test_omi_tool_assisted_persistence_contract.py` (354 lines; 5 tests; T011 contract).
- `tests/test_omi_live_runtime_preflight_contract.py` (610 lines; 23 tests; T013/T014B/T015B contract).
- `tests/test_story_check_route.py` (187 lines; 7 tests; legacy route).
- `tests/test_story_check_baseline_eval.py` (170 lines; 11 tests; App-13 evaluation harness).
- `tests/test_story_check_prompt.py` (96 lines; 7 tests; App-3 prompt contract).
- `tests/fixtures/story_check/` (6 fixtures: `valid_rich_story_check.json`, `minimal_story_check.json`, `malformed_story_check.txt`, `insufficient_evidence_story_check.json`, `unsafe_output_story_check.json`, `refusal_response.json`).
- `tests/test_evaluation_fixtures.py` (uses `normalize_story_check_output` over `tests/fixtures/story_check/`).
- `tests/test_omi_tool_assisted_fusion_dedupe_contract.py` (uses `_story_check_finding` and `_story_check_envelope` fixtures).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T008-story-check-diagnostic-only-omi-handoff.md` (74 lines; T008 decision record).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T014A-spacy-fixture-contract-and-preflight-inspection.md` (181 lines; template for T016A).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T015A-ollama-runtime-and-fixture-contract-inspection.md` (198 lines; template for T016A).
- `docs/roadmap/decisions/PHASE8-IMPL-023-T014E-live-runtime-tool-installation-inventory.md` (Story Check row, lines 60-114).
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` (568 lines; T016 planned child, T015D-rerun-after-T015F latest completed child).
- `docs/roadmap/implementation_status.md`, `docs/roadmap/task_backlog.md`, `docs/roadmap/phase_map.md`, `docs/roadmap/decision_log.md`, `docs/roadmap/open_questions.md`, `docs/roadmap/risk_register.md` (status/lifecycle references for T008, T014A, T015A, T016).

## G. Findings Summary

1. The existing `story_check` fixture/mock adapter is fully wired in `backend/omi_analysis_orchestrator.py` (T008 contract: 11 tests, 0 live calls). It accepts `omi_story_check_diagnostic_handoff.v1` JSON or dict fixtures; requires `schema_version`, `adapter: "story_check"`, `status` (one of `succeeded`, `empty`, `failed_closed`, `error`), `provenance`, `findings`; per-finding requires `candidate_type`/`finding_type` (mapped to one of 12 orchestrator finding types), `label`/`name`/`title`/`question_label`, `diagnostic_claim`/`extracted_claim`/etc., `evidence` (with `source_excerpt` and `source_locator`), `source_locator`, `provenance` (with `tool_source: "story_check"`, `adapter: "story_check"`), and forces `owner_decision: {decision: pending, approved: false}` and `review_status: candidate_review_pending`.
2. The existing in-repo Story Check runtime surface is `backend/analysis_engine.run_story_check(project_name, scene_id)` invoked through the legacy `POST /api/projects/{project_name}/story-check/{scene_id}` route. The orchestrator side does not import or call it. The legacy route is **not gated** by `OMI_LIVE_TOOLS_ENABLED` / `OMI_LIVE_STORY_CHECK_ENABLED`; it always runs (mock if `ANALYSIS_MODE=mock`, else live HTTP). The live path uses `requests` (third-party, pre-existing), `analysis_modes.get_analysis_mode()`, `storyform.Storyform.from_file`, `project_manager.load_scene`, `project_manager.load_bible`, and `backend/prompts/story_check.txt`. Side effects: HTTP POST to `OLLAMA_BASE_URL/api/chat` (or `http://localhost:11434`); no file writes.
3. The T013 preflight `story_check` probe is a file-existence probe on `backend/analysis_engine.py` only. It does not check `requests`, the prompt file, the mock fixture, the `analysis_modes` env var, or Ollama reachability. T016B is needed to add these probes.
4. Story Check tests cover (a) T008 fixture contract (11 tests), (b) legacy route (7 tests), (c) App-12 evaluation fixtures (11 tests, never live), (d) prompt contract (7 tests), (e) extraction contract monkeypatches (`test_omi_extraction_contract.py`, `test_omi_extraction_expected_red.py`), and (f) fusion/dedupe fixture participation. Total: at least 36+ Story Check touch tests, all fixture/mock; no test calls real Story Check.
5. The live Story Check integration requires three additional small slices after T016A: T016B (preflight/config/availability), T016C (live adapter behind flags), T016D (manual real validation). T016A is the inspect/docs starting point only.

## H. Safety Confirmations

- No live Story Check runtime call was made during T016A.
- No live Story Check adapter was implemented during T016A.
- No model analysis was run during T016A.
- No candidates were produced during T016A.
- No candidate persistence occurred during T016A.
- No Memory/Canon mutation occurred during T016A.
- No automatic promotion record was created during T016A.
- No automatic apply-promotion was run or enabled during T016A.
- No story prose was generated during T016A.
- No backend runtime code was changed during T016A (no edits to `backend/omi_analysis_orchestrator.py`, `backend/omi_runtime_preflight.py`, `backend/main.py`, `backend/analysis_engine.py`, `backend/analysis_modes.py`, `backend/analysis_normalizer.py`, or `backend/guardrails.py`).
- No frontend code was changed during T016A.
- No package or dependency file was changed during T016A.
- No dependency was installed or downloaded during T016A.
- No context-generation, broad-context-collection, or graph mapping tool was called during T016A (no Repomix, Graphify, LeanCTX, MCP, or subagent).
- No staging, commit, or push occurred during T016A.
- T016A's only writes are to docs/status files: this decision record, the enrichment JSON, the decision log, the implementation status, the task backlog, the phase map, and the open questions (one new open question).

## I. Deferred Work

T016B (live Story Check preflight/config/availability), T016C (live Story Check adapter behind flags), and T016D (manual real Story Check validation) are deferred to separate tasks. T016A does not implement, install, run, validate, or test live Story Check. T016A does not change preflight config, feature flags, or runner behavior.

## J. Statements

- T016A is an inspect/docs task only; no live Story Check runtime, no live adapter, no model analysis, no candidates, no candidate persistence, no Memory/Canon mutation, no automatic promotion records, no automatic apply-promotion, and no story prose.
- The existing `story_check` fixture/mock contract (T008) is complete/PASS; it is scaffolding only and does not count as MVP completion.
- The existing `backend/analysis_engine.run_story_check` legacy route is a pre-existing live runtime surface that the orchestrator does not call. The legacy route is not gated by OMI live-tools env flags and will perform a real `requests.post` to `OLLAMA_BASE_URL/api/chat` if `ANALYSIS_MODE=ollama_baseline`. T016A does not modify this route.
- T013 preflight readiness for `story_check` is currently a file-existence probe only; T016B should add `requests` package probe, prompt file probe, mock fixture probe, `analysis_modes` validity probe, and Ollama reachability probe.
- The recommended next task is T016B. T016C and T016D are conditional on T016B and on owner decision regarding which live Story Check path to use (legacy `analysis_engine.run_story_check` bridge vs fresh orchestrator HTTP runner vs refactor).
- No file outside this decision record, the enrichment JSON, the decision log, the implementation status, the task backlog, the phase map, and the open questions was changed by T016A. Nothing was staged, committed, or pushed.
