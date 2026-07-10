# PHASE8-IMPL-023-T016C1 — Tighten Story Check Live Converter Sanitizer Boundary

## Result

PASS for backend safety repair + mocked tests + docs/status.

T016C1 repairs the T016C converter boundary before T016D manual real Story Check validation. The live Story Check converter no longer rewrites unsafe legacy Story Check output claims/questions/evidence to force T008 acceptance. Unsafe legacy text is now SKIPPED at the item level. If every structured item is unsafe, the converter returns `failed_closed` with no findings. The T008 `validate_story_check_fixture_envelope` validator remains authoritative. Converter-owned labels are generic and safe.

## Nature

- Backend safety repair + mocked tests + docs/status task only (T016C1).
- T016D (manual real Story Check validation) is the future manual real validation task after T016C/T016C1 are committed.
- Builds on T016C live adapter implementation: T016C added `_story_check_sanitize_truth_final_labels` to rewrite legacy text so the converted finding could pass T008 validation. T016C1 found this boundary too broad and unsafe (rewriting AI/tool/model output text to make it pass validation is not an acceptable safety boundary) and replaced the broad rewriter with a strict safety checker + skip-on-unsafe policy.
- Does not call real Story Check, real Ollama, the legacy route, or any network.
- Does not mutate Memory/Canon, create promotion records, run apply-promotion, persist candidates, or generate story prose.

## What Was Repaired

T016C implemented `_story_check_sanitize_truth_final_labels(value)` with a `_STORY_CHECK_TRUTH_LABEL_REPLACEMENTS` table that rewrote:

* `approved` -> `owner-backed`
* `truth` -> `diagnostic support`
* `canon` -> `diagnostic context`
* `final` -> `candidate`
* `promoted` -> `candidate-only`
* `apply-promotion` -> `owner-confirmed apply`
* `promote to canon` -> `advance to review`
* etc.

The sanitizer was called from `_story_check_safe_excerpt_text`, which is invoked for every legacy evidence excerpt, every diagnostic_claim, every `throughline_alignment` evidence/concern item, every `theme_drift.reason`/`character_consistency.reason`. The sanitizer was therefore rewriting the actual model/tool output that flows into the T008 envelope as a `diagnostic_claim`, `extracted_claim`, `question`, or `evidence.source_excerpt` value. The T008 validator then accepted the rewritten text as if it had always been the model's output.

This is not an acceptable safety boundary:

1. The T008 contract is intentionally strict. If the model output is unsafe, the orchestrator must not accept it, even with a safe label.
2. Rewriting `approved -> owner-backed` is rewriting an AI/tool/model claim. It is not a no-op text transformation; it changes the semantic content that downstream owner review reads.
3. Rewriting unsafe evidence text creates fake evidence-backed findings, which is a candidate-persistence risk.
4. The replacement table covered `promote to canon` and `apply-promotion` strings, which is the exact opposite of the AI/tool/model output contract the T008 validator enforces.

T016C1 removes the broad text-rewriting sanitizer entirely and replaces it with a strict safety checker + skip-on-unsafe policy. Unsafe legacy text is rejected at the item level; the converter does not rewrite it into a safe phrase. The T008 validator still runs downstream and is the authoritative validator; the safety checker is just a fast classifier so the converter can drop unsafe items before the T008 validator would fail them.

## Implementation

### Files Changed

`backend/omi_analysis_orchestrator.py`:

- **Removed** `_STORY_CHECK_TRUTH_LABEL_REPLACEMENTS` and `_story_check_sanitize_truth_final_labels`. These helpers rewrote unsafe AI/tool/model output text into a safe phrase; that is the unsafe behavior T016C1 removes.
- **Added** `_story_check_legacy_text_is_safe(value)` helper. Returns `True` only when the value is a non-empty plain string that does NOT carry:
  - truth/canon/canonical/approved/promoted/confirmed_fact labels (`is_truth_label`)
  - truth/canon/final/approved/promoted/confirmed_fact/accepted/locked/definitive/finalized/finalised labels (`_OMI_STORY_CHECK_FINAL_TRUTH_LABEL_RE`)
  - apply-promotion/promotion record/promote to canon/Memory/Canon mutation/persist candidates/save candidates operation text (`_OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE`)
  - rewrite/continue/continuation/expand/expanded/polish/polished/outline/draft/revise/revised/generate story/scene/chapter/outline/draft/prose generation language (`_OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE`)
  - prose-shaped free text (`is_prose_like_text`)
  - empty/non-string values
- **Updated** `_story_check_safe_excerpt_text(value, max_chars)` to a plain trim+truncate helper. It does NOT call any sanitizer. T016C1 documents the safety contract: the caller is responsible for verifying the result is safe before using it as a `diagnostic_claim`, `extracted_claim`, `question`, or `evidence.source_excerpt` value.
- **Updated** `_story_check_extract_excerpts_from_value` to filter out unsafe excerpts via `_story_check_legacy_text_is_safe`. Unsafe items are SKIPPED, not rewritten.
- **Updated** `_story_check_make_finding` to add a safety re-check on the `diagnostic_claim` and the evidence excerpts. The helper returns `None` when the claim or any evidence excerpt is unsafe. This is a defense-in-depth check; the converter also checks safety before invoking the helper.
- **Updated** `_story_check_warning_label(category)` to return ONLY a generic converter-owned label. The label never includes legacy text. Generic labels include:
  - `Story Check warning`
  - `Story Check concern`
  - `Story Check question`
  - `Story Check insufficient evidence`
  - `Story Check throughline diagnostic`
  - `Story Check storyform diagnostic`
  - `Story Check character consistency diagnostic`
  - `Story Check diagnostic` (default fallback)
- **Updated** `_story_check_result_to_envelope`:
  - For each warning/concern/suggestion/insufficient_evidence item, the converter checks `_story_check_legacy_text_is_safe` first. Unsafe items are SKIPPED, not rewritten.
  - For each `throughline_alignment` entry, the converter uses the existing `_story_check_extract_excerpts_from_value` (which already filters unsafe excerpts) and SKIPS the throughline item entirely when no safe evidence/concerns are available. The converter NO LONGER synthesizes placeholder text from the `present` flag alone.
  - For `theme_drift` and `character_consistency`, the converter uses a safe `reason` excerpt as evidence when available. The converter NO LONGER synthesizes a `Theme drift status: 'X'` or `Character consistency status: 'X'` placeholder when `reason` is missing or unsafe; the item is SKIPPED.
  - The `failed_closed` explanation is updated to mention that structured items with unsafe truth/canon/final/approved/promoted/apply-promotion/rewrite/continue/outline/draft/generation language were skipped by the T016C1 safety boundary.
  - The `succeeded` explanation is unchanged.
  - The docstring now states the T016C1 safety boundary explicitly: the converter does NOT rewrite or sanitize legacy text; unsafe items are SKIPPED individually; if every structured item is unsafe, the converter returns `failed_closed` with no findings; the converter never synthesizes placeholder text from `present`/`status`/`reason` flags alone.
- **No change** to `_build_story_check_live_runner`, `_resolve_adapter_runner`, `analyze_omi_raw_idea_with_tools`, the `story_check_scene_id` kwarg, or the T008 `validate_story_check_fixture_envelope` validator. The T008 validator remains authoritative.

`tests/test_omi_story_check_adapter_contract.py`:

- **Updated** `_structured_legacy_story_check_result` to use T016C1-safe legacy text. The previous version used `owner-approved`/`approved`/`canon`/`final` wording that the T016C1 safety boundary now rejects. The updated fixture uses plain diagnostic text (`owner-supplied`, `on hand`, `available evidence`, `incomplete for this fixture`, `What owner-supplied evidence would help identify a Main Character throughline?`).
- **Added** T016C1 fixture helpers for unsafe legacy text:
  - `_unsafe_legacy_warning_fixture` (canon/approved truth wording)
  - `_unsafe_legacy_suggestion_fixture` (rewrite wording)
  - `_unsafe_legacy_concern_fixture` (final/canon wording)
  - `_unsafe_legacy_insufficient_evidence_fixture` (promoted truth wording)
  - `_unsafe_legacy_apply_promotion_fixture` (apply-promotion/promotion record wording)
  - `_unique_unsafe_phrase_legacy_fixture` (MAGIC_PHRASE_ZZZ with approved wording)
- **Added** 15 new T016C1 mocked tests.

### Tests Added (15 new mocked tests)

1. `test_t016c1_unsafe_canon_approved_in_warning_fails_closed` — unsafe wording in `warnings`; envelope fails closed; no findings.
2. `test_t016c1_unsafe_rewrite_in_suggestion_fails_closed` — `rewrite` wording in `suggestions`; envelope fails closed; no findings.
3. `test_t016c1_unsafe_final_in_concern_fails_closed` — `final`/`canon` wording in `concerns`; envelope fails closed; no findings.
4. `test_t016c1_unsafe_promoted_in_insufficient_evidence_fails_closed` — `promoted`/`truth` wording in `insufficient_evidence`; envelope fails closed; no findings.
5. `test_t016c1_unsafe_apply_promotion_text_fails_closed` — `apply-promotion`/`promotion record` wording; envelope fails closed; no findings.
6. `test_t016c1_unsafe_legacy_text_is_not_sanitized_into_finding` — verifies the unique phrase `MAGIC_PHRASE_ZZZ` is never accepted in any adapter-envelope field; the envelope fails closed; the phrase is never rewritten into a safe phrase.
7. `test_t016c1_safe_legacy_text_still_converts_to_candidate_finding` — verifies the safe-text fixture produces `succeeded` with normalized T008 findings; every finding has `source_adapter == "story_check"`, support-only `provenance.support`, `owner_decision: pending`, `review_status: "candidate_review_pending"`, and no truth/canon/final/approved/promoted labels in `support_label`.
8. `test_t016c1_converter_owned_labels_are_generic_and_safe` — every finding label is one of the allowed generic converter-owned labels and contains no truth/canon/final/approved/promoted labels; the `extracted_claim` blob contains no truth/canon/final/approved/promoted labels.
9. `test_t016c1_partial_unsafe_legacy_items_are_skipped_safe_items_kept` — mixed `suggestions` (one safe, one unsafe); the safe one is converted into a T008 finding; the unsafe one is skipped; the envelope remains `succeeded`.
10. `test_t016c1_unsafe_throughline_evidence_is_skipped` — throughline evidence/concerns are all unsafe; the throughline item is skipped; no synthetic placeholder is generated; the envelope fails closed.
11. `test_t016c1_unsafe_theme_drift_reason_is_skipped` — `theme_drift.reason` is unsafe; the theme_drift item is skipped; no synthetic `Theme drift status: '...'` placeholder is generated; the envelope fails closed.
12. `test_t016c1_persistence_boundary_remains_safe_after_unsafe_skip` — `persist_candidates=True`; unsafe legacy text is skipped at the converter; the `extract_omi_candidates_from_raw_idea` and `persist_omi_tool_assisted_findings_as_candidates` helpers are NOT invoked; the safety envelope remains safe.
13. `test_t016c1_t008_validator_remains_authoritative` — verifies the converter returns `failed_closed` for `{"task": "story_check", "coherence_score": 7}` (no structured diagnostics), `failed_closed` for prose-only legacy text (free-form prose is not parsed as candidate findings), and `error` for `{"error": "..."}` legacy shape.
14. `test_t016c1_existing_fixture_tests_still_pass` — the T008 fixture-only path remains supported and unchanged by T016C1.
15. `test_t016c1_existing_t016c_runtime_success_test_still_uses_safe_text` — guard test that the safe-text legacy fixture used by the T016C runtime-success test does not contain truth/canon/final/approved/promoted labels, so the live adapter can convert it into T008-shaped findings.

### Test Results

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_story_check_adapter_contract.py -q
```

Result: **40 passed** (25 existing T008/T016C + 15 new T016C1).

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
```

Result: all existing tests pass unchanged. Combined T016C1 validation across the four contract test files: **114 passed**.

## Safety Boundaries Preserved

- The T008 `validate_story_check_fixture_envelope` validator is unchanged. T016C1 does not loosen T008 validation. T016C1 does not add any bypass around the T008 validator.
- The T008 forbidden patterns (`_OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE`, `_OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE`, `_OMI_STORY_CHECK_FINAL_TRUTH_LABEL_RE`) and the T005 `is_truth_label` helper remain the authoritative safety contract. The new `_story_check_legacy_text_is_safe` helper just reuses the same patterns the T008 validator uses, so safe/unsafe classification is consistent with T008.
- The converter does NOT rewrite AI/tool/model output text. Unsafe text is rejected at the item level, not sanitized into a safe phrase.
- The converter does NOT synthesize placeholder text from `present`/`status`/`reason` flags alone. The throughline, theme_drift, and character_consistency items are SKIPPED when the underlying legacy text is unsafe or missing.
- The `failed_closed` explanation now mentions the T016C1 safety boundary so the orchestrator and any downstream consumer can see why no findings were emitted.
- The T008 validator still rejects prose-intent field names, prose-shaped extracted claims, missing evidence/source_locator/provenance, auto-approved owner decisions, Memory/Canon mutation, candidate persistence, promotion record, and apply-promotion operation requests. T016C1 does not touch the T008 validator.

## Confirmation Statements

- T016C1 repairs the T016C converter boundary before commit/manual validation.
- The live Story Check converter no longer rewrites unsafe legacy Story Check output claims/questions/evidence to force T008 acceptance.
- T008 validation remains authoritative. The T008 validator is unchanged; the live adapter's `_story_check_legacy_text_is_safe` helper just classifies legacy text against the same T008 forbidden patterns the T008 validator uses.
- Converter-owned labels are safe and generic: `Story Check warning`, `Story Check concern`, `Story Check question`, `Story Check insufficient evidence`, `Story Check throughline diagnostic`, `Story Check storyform diagnostic`, `Story Check character consistency diagnostic`, `Story Check diagnostic`. The labels do NOT include legacy text.
- Unsafe truth/canon/final/approval/promotion/apply-promotion legacy text fails closed or is skipped. If every structured item is unsafe, the converter returns `failed_closed` with no findings.
- Safe structured diagnostics still convert: the T016C1 safe-text fixture (and the T008 fixture-only path) still produces normalized T008 findings.
- No real Story Check runtime was called.
- No legacy route was called.
- No Ollama/model/network call was made.
- No frontend/package/dependency files changed.
- No candidate persistence, Memory/Canon mutation, automatic promotion records, automatic apply-promotion, or story prose behavior was added.
- T016D remains the next manual real Story Check validation task after T016C/T016C1 are committed.

## Files Changed

- `backend/omi_analysis_orchestrator.py` — removed `_STORY_CHECK_TRUTH_LABEL_REPLACEMENTS` and `_story_check_sanitize_truth_final_labels`; added `_story_check_legacy_text_is_safe`; updated `_story_check_safe_excerpt_text` (plain trim+truncate), `_story_check_extract_excerpts_from_value` (filters unsafe), `_story_check_make_finding` (defense-in-depth safety re-check), `_story_check_warning_label` (generic converter-owned labels only), `_story_check_result_to_envelope` (skip-on-unsafe policy, no synthesis of placeholder text).
- `tests/test_omi_story_check_adapter_contract.py` — updated `_structured_legacy_story_check_result` to use safe text; added 6 unsafe-text fixture helpers; added 15 new T016C1 mocked tests.
- `docs/roadmap/decisions/PHASE8-IMPL-023-T016C1-tighten-story-check-live-converter-sanitizer-boundary.md` — this decision record.
- `docs/roadmap/decision_log.md` — logged T016C1 decision.
- `docs/roadmap/implementation_status.md` — updated active frontier and child sequence.
- `docs/roadmap/task_backlog.md` — added T016C1 result.
- `docs/roadmap/phase_map.md` — added T016C1 result.
- `docs/roadmap/open_questions.md` — refined Q112 with the T016C1 safety repair evidence.
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` — added T016C1 child entry, updated latest/next child fields.

## Next Steps

- **T016D**: Manual real Story Check validation against a live `qwen3:8b` instance behind the new env flags, similar to T014D/T015D. T016C1 narrows the live adapter safety boundary so T016D will exercise the strict no-sanitization behavior. Expected: the live adapter will produce T008-shaped findings only when the legacy text is safe; unsafe legacy text will be skipped at the item level. The persistence boundary remains safe; the safety envelope remains safe.
- **T017-T020**: Live integration of the remaining selected tools (BookNLP, NCP, Subtxt, dramatica-flow) when each tool's runtime surface is available or explicitly owner-blocked.
- **T021-T025**: Cross-tool fusion validation, candidate-only persistence validation, grouped owner-review UI, automated end-to-end live OMI tests, and manual Cyber Detective Story live OMI test.
- **T026**: PHASE8-IMPL-023 closeout only after all selected live runtime tools are connected/tested or explicitly owner-blocked.
