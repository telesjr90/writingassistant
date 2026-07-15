# PHASE8-IMPL-023-T005 Tool-Assisted Extraction Orchestrator Contract and Adapter Boundaries

## Result

PASS for orchestrator contract and adapter-boundary scaffold only.

`PHASE8-IMPL-023-T005` is complete/PASS. The next child is `PHASE8-IMPL-023-T006 - Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests`.

No frontend product UI, OMI analysis-results UI, browser harness, model/Ollama call, Story Check call, BookNLP/spaCy/NCP/Subtxt/dramatica-flow runtime call, Memory/Canon mutation, apply-promotion run or enablement, promotion record, story prose generation, training artifact, dataset, JSONL record, package install, runtime project file write beyond the existing T004 deterministic extractor, staging, commit, or push occurred.

## Orchestrator Contract Added

- Added `backend/omi_analysis_orchestrator.py` as a new pure, standard-library-only, deterministic, no-I/O orchestrator module.
- Exported entrypoint `analyze_omi_raw_idea_with_tools(project_name, raw_idea, *, source_idea_id=None, persist_candidates=False, requested_adapters=None, allow_deterministic_fallback=False)`.
- Exported helpers: `adapter_contract`, `build_orchestrator_safety_envelope`, `candidate_fingerprint`, `evidence_fingerprint`, `is_prose_like_text`, `is_truth_label`, `normalized_finding_id`, `stub_adapter_result`, `validate_adapter_result`, `validate_normalized_finding`.
- Existing `POST /api/projects/{project_name}/omi/extractions` route and `extract_omi_candidates_from_raw_idea` contract are unchanged. The orchestrator module sits beside, not inside, the route layer.

## Adapter Identities

Allowed OMI tool adapter identities (validate via `OMI_TOOL_ADAPTER_IDENTITIES` and `adapter_contract`):

- `ollama_model`
- `story_check`
- `booknlp`
- `spacy`
- `ncp`
- `subtxt`
- `dramatica_flow`
- `deterministic_fallback`

Each adapter has a per-tool behavior contract documented in `OMI_ADAPTER_CONTRACTS`:

- `ollama_model`: structured JSON extraction only, schema-bound, no prose, no rewrite, no continuation, no outline, no drafting, no improvement; fail closed on invalid schema or unsafe prose.
- `story_check`: diagnostic-only structural observations/questions; no prose suggestions; fails closed on missing storyform/context.
- `booknlp`/`spacy`: local NLP entities, mentions, sentence segmentation, events; every finding must point to source excerpt or source_locator; no canon claims.
- `ncp`: structural context mapping and import/export candidate representation only; not truth export; fails closed on missing NCP context.
- `subtxt`: rubric/reference guidance for diagnostic structural interpretation only; not automatic Dramatica truth; fails closed on missing Subtxt context.
- `dramatica_flow`: analysis-pattern reference only for narrative-state patterns; generation/revision/continuation disabled; no outlines or story text.
- `deterministic_fallback`: wraps the existing T004 `project_manager.extract_omi_candidates_from_raw_idea` marker extractor as fallback/safety baseline ONLY. Not the corrected MVP OMI analysis path.

## Adapter Result States

Allowed states (validate via `OMI_ADAPTER_RESULT_STATES`):

- `succeeded`
- `empty`
- `skipped`
- `unavailable`
- `failed_closed`
- `error`

Only `succeeded` may carry a non-empty candidate list. Any other state must carry an empty candidate list, or `validate_adapter_result` raises `ValueError` and the orchestrator fails closed.

## Normalized Finding / Candidate Schema

Every normalized finding (`validate_normalized_finding`) must carry:

- `candidate_type` (one of `OMI_ORCHESTRATOR_FINDING_TYPES`): `character`, `location`, `organization`, `object`, `timeline_event`, `relationship`, `plot_thread`, `story_fact`, `open_question`, `storyform_context`, `diagnostic_question`, `continuity_warning`, `world_rule`, `evidence_note`.
- `label`, `extracted_claim`, `evidence` (non-empty list of items each with `source_excerpt` or `source_locator`).
- `source_locator`, `provenance` (carrying `tool_source`, `adapter`, `support`).
- `source_adapter` (must match `provenance.adapter` and `provenance.tool_source`).
- `support_label` (must include the word "support" and must NOT include truth/canon/approved/promoted).
- `owner_decision` (decision state limited to pending/approve/reject/revise/needs_review; orchestrator never auto-approves).
- `review_status` (one of `candidate` / `review_pending` / `candidate_review_pending`).
- `raw_finding_id`.
- Fusion/dedupe fields, precomputed by `validate_normalized_finding` for T010 readiness: `candidate_fingerprint`, `evidence_fingerprint`, `normalized_finding_id`, `duplicate_of`, `related_finding_ids`, `conflict_group_id`, `uncertainty_label`.

## Fail-Closed Behavior

- Empty raw idea -> `analysis_status: empty`, every requested adapter returns `skipped`, zero writes.
- Prose-shaped raw idea (continuation/draft/polish/rewrite markers, or dialogue quotes, or long narrative sentences) -> `analysis_status: fail_closed`, every adapter returns `failed_closed`, zero writes, no candidates, no persistence.
- Unimplemented adapters (all AI/tool adapters at T005) -> `state: unavailable` with a non-empty explanation that names the deferred child task; never pretend to succeed.
- Stub helper enforces that `succeeded` is never returned without real findings.
- Non-`succeeded` envelopes with non-empty `candidates` are rejected by `validate_adapter_result`.

## No-Prose Validation

- `is_prose_like_text` flags:
  - Dialogue-quoted text (curly/straight quotes).
  - Prose-shaped prefixes ("meanwhile", "later that", "chapter N", "scene N", "the room", "the chapter", "once upon", "it was a", "there was a").
  - Long sentences (>=24 words) ending in a period.
- `validate_normalized_finding` rejects any `extracted_claim` matching the prose heuristic with a `failed_closed`-style error.
- Orchestrator `analyze_omi_raw_idea_with_tools` short-circuits prose-shaped raw idea before running any adapter.

## Evidence / Provenance / Source Locator Requirements

- Evidence is required (non-empty list) and every item must carry a `source_excerpt` or `source_locator`.
- `source_locator` is a required, non-empty string on every finding (set deterministically by `deterministic_fallback` if the upstream tool did not supply one).
- `provenance` must carry `tool_source`, `adapter`, and `support`; `support` must include the word "support" and must NOT include truth/canon/approved/promoted.
- `source_adapter` must equal `provenance.adapter` and `provenance.tool_source` and must be one of `OMI_TOOL_ADAPTER_IDENTITIES`.

## Deterministic Fallback (Fallback-Only)

- `deterministic_fallback` is OFF by default and is opt-in via `allow_deterministic_fallback=True`.
- When allowed, it wraps the existing T004 marker extractor and produces normalized findings with `source_adapter == "deterministic_fallback"`, `fallback_only` envelope flag set, and explanatory note that it is the safety baseline only.
- Persistence (`persist_candidates=True`) is honored only for `deterministic_fallback` findings; AI/tool adapter findings are NEVER persisted at T005 (T010+T011 own fusion + persistence for the corrected MVP path).

## Required Tests (`tests/test_omi_tool_assisted_orchestrator_contract.py`)

26 tests pass with the new orchestrator module:

- `test_orchestrator_declares_required_adapter_identities`
- `test_orchestrator_declares_adapter_result_states`
- `test_unimplemented_adapters_fail_closed_without_fake_candidates`
- `test_stub_adapter_result_rejects_succeeded_state`
- `test_adapter_envelope_validates_state_and_candidates_shape`
- `test_normalized_findings_require_evidence_source_locator_and_provenance`
- `test_normalized_finding_rejects_unknown_candidate_type`
- `test_normalized_finding_requires_source_adapter_match_provenance`
- `test_unsafe_prose_output_is_rejected`
- `test_prose_guard_helper_detects_narrative_shapes`
- `test_stub_adapter_candidate_is_normalized_as_candidate_only_not_canon`
- `test_tool_output_support_confidence_is_not_truth`
- `test_normalized_finding_rejects_auto_approved_owner_decision`
- `test_is_truth_label_helper_distinguishes_support_from_truth`
- `test_orchestrator_does_not_call_real_tools_by_default`
- `test_deterministic_fallback_is_wired_only_when_opted_in`
- `test_deterministic_fallback_is_marked_fallback_only`
- `test_deterministic_fallback_returns_empty_for_unsupported_input`
- `test_orchestrator_rejects_empty_project_name`
- `test_orchestrator_rejects_non_string_raw_idea`
- `test_orchestrator_rejects_non_bool_persist_candidates`
- `test_orchestrator_rejects_unknown_requested_adapter`
- `test_safety_envelope_is_static_and_safe`
- `test_orchestrator_returns_static_fusion_contract_envelope`
- `test_fingerprint_helpers_are_deterministic`
- `test_existing_omi_extraction_routes_still_work`

## Validation

- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> `26 passed in 0.23s`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_contract.py -q` -> `5 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q` -> `4 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> `20 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> `21 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> `7 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> `18 passed, 51 deselected`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_ui_source_expected_red.py -q` -> `5 failed, 1 passed`; the 5 failures remain expected-red and are deferred to T006 frontend API/UI/detail/empty-state surfaces, per the deferred-frontend policy.
- Aggregate (excluding frontend expected-red): `152 passed in 0.80s` across the OMI regression surface.
- `python3 scripts/check_enrichment.py` -> PASS.
- `python3 scripts/validate_roadmap.py` -> PASS.
- `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null` -> PASS.

## Safety Boundaries

- No Ollama, Story Check, BookNLP, spaCy, NCP, Subtxt, dramatica-flow, or external service runtime call.
- No Memory/Canon mutation.
- No promotion records, no apply-promotion, no canon promotion.
- No story prose generation, rewriting, continuation, drafting, polishing, improvement, expansion, imitation, or revision.
- No frontend UI, frontend API helper, or browser harness.
- No package installs, no new external dependencies, no `requirements.txt` change.
- Candidate persistence via `deterministic_fallback` is the only persistence path T005 enables; AI/tool adapters NEVER persist.
- Queue presence is non-approval. Candidate presence is non-canon. Tool/model output is non-truth.

## Deferred To Follow-Up Children

- T006 wires a real `ollama_model` adapter runner with structured JSON extraction, JSON/schema validation, and no-prose tests.
- T007 wires real `booknlp` / `spacy` adapter runners.
- T008 wires a real `story_check` adapter runner (diagnostic-only).
- T009 wires real `ncp` / `subtxt` / `dramatica_flow` adapter runners.
- T010 implements cross-adapter fusion/dedupe/conflict using `OMI_FUSION_FINDING_FIELDS`.
- T011 implements fused-finding persistence (separate from T005's fallback-only persistence path).
- T012 implements the frontend OMI analysis results UI/UX, including evidence/source locator, conflict/uncertainty display, empty/fail-closed states.

## Next Child Task

`PHASE8-IMPL-023-T006 - Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests`.
