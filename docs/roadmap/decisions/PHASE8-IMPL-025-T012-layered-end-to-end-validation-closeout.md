# PHASE8-IMPL-025-T012 Layered End-to-End Validation Closeout

Date: 2026-10-07
Status: complete/PASS

## Accepted binding

- Task: `PHASE8-IMPL-025-T012 — Layered end-to-end validation`
- Accepted implementation commit: `e216d08eb5255d7dd58a3934e7c328249a4f52c9`
- Subject: `fix(omi): enforce exact live-analysis evidence attribution (T012)`
- Reviewed implementation patch SHA-256:
  `956600a23735009f28c7388ac19062711b692a290af9b565f0bedd93cf2f078e`

## Accepted implementation and test scope

- `backend/omi_analysis_orchestrator.py`
- `tests/test_omi_booknlp_spacy_adapter_contract.py`
- `tests/test_omi_ollama_model_adapter_contract.py`
- `tests/test_owner_action_review_workflow_safety_regression.py`
- `tests/test_t003_analysis_control_and_compatibility.py`

The accepted correction preserves exact spaCy evidence excerpts and locators,
uses Ollama JSON Schema output plus deterministic app-owned source-span IDs,
reconstructs exact Unicode-character and UTF-8-byte offsets from selected spans,
and fails closed on malformed, unknown, duplicate, ambiguous, paraphrased, or
otherwise non-exact model evidence. T003 exact-attribution requirements were
not relaxed. The focused T003 regressions prove both degraded fail-closed
submission and successful manifest/evidence-ledger construction from valid
exact Ollama evidence. The owner-action regression correction verifies the
current safety fields without relying on an obsolete whole-dictionary shape.

## Validation summary

- Focused validation: `135 passed, 7 warnings`.
- Real contributor chain: PASS.
- Browser validation: PASS.
- `git diff --check`: PASS.

The seven warnings are existing Pydantic v2 deprecation warnings and do not
represent T012 failures.

## Real contributor-chain evidence

- BookNLP succeeded with 49 findings.
- spaCy succeeded with 62 findings.
- Combined local NLP produced 111 exact-evidence findings.
- Real Ollama/qwen3:8b succeeded with six exact-grounded findings and retained
  native output.
- Story Check reached the real interface and failed closed safely with retained
  diagnostics.
- App-owned rubrics succeeded with 13 findings.
- Candidate persistence produced 130 pending, non-canon,
  promotion-ineligible candidates.
- Owner-review handoff was present.
- NCP covered 20 scenarios with no file or project-state writes.

## Browser validation evidence

- Live-analysis submission, status, and result through HTTP: PASS.
- Grouped-review empty-candidate handoff: PASS.
- NCP unsafe-destination rejection: PASS.
- The safe NCP handoff remained UI-local.
- NCP import and candidate-bundle controls remained disabled.
- Keyboard focus reached `Open live analysis` using eight real Tab presses.
- Chromium `:focus-visible` was true with a solid 2px outline.
- At a 390px viewport, document scroll width was 390px.
- Protected before/after files were byte-identical.
- Console errors, page errors, failed requests, and HTTP errors: none.
- Forbidden mutation requests: none.
- The only browser mutation was the authorized
  `POST /omi/analysis/runs` request.

## Evidence paths

- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/browser-http-validation-summary.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/browser-omi-mobile.png`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/browser-protected-before.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/browser-protected-after.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/live-runtime-summary.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/isolated-ollama-span-selection-live-attempt-1.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/isolated-local-nlp-summary.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/ollama-correction-cycle-summary.json`
- `.codex-context/PHASE8-IMPL-025/manual-validation/T012-layered-end-to-end/20261007T174534Z/ollama-json-output-correction-summary.json`

The correction-cycle summaries preserve intermediate insufficient-evidence
states. The later successful span-selection, real contributor-chain, and
browser summaries are the controlling final T012 evidence.

## Preserved safety boundaries

T012 performed no application-generated story prose, automatic approval,
promotion, apply-promotion, Memory/Canon mutation, project-truth mutation,
source mutation, or NCP export/import write. It did not execute the optional
official Subtxt paid runtime or external `dramatica_flow`. It introduced no
dependency, package, model, or permanent infrastructure change.

Candidate output remained pending, non-canon, promotion-ineligible,
evidence/provenance-backed, and owner-controlled. Promotion and
apply-promotion remain separate explicit audited boundaries.

## Next lifecycle and open gates

T012 is complete/PASS at the accepted implementation commit. This closeout
does not close the PHASE8-IMPL-025 parent and does not begin or complete
`PHASE8-IMPL-027`. Existing roadmap authority continues to identify
PHASE8-IMPL-027 as the terminal MVP owner accept/reject/defer gate after T012;
it remains published/planned/inactive until separately authorized.

Project Memory, Plan Integrity, supervision, and execution routing remain
paused and nonblocking for ordinary application work under the accepted
implementation-only policy.
