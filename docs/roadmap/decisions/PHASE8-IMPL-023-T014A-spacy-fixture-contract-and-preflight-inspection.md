# PHASE8-IMPL-023-T014A — spaCy Fixture Contract and T013 Preflight Inspection

## Result

PASS for T014A inspect/docs only.

## Existing spaCy Fixture Contract

**Location:** `backend/omi_analysis_orchestrator.py:1862-2502` (T007 BookNLP/spaCy local NLP extraction contract).

**Schema version:** `omi_spacy_local_nlp_extraction.v1` (`OMI_SPACY_SCHEMA_VERSION`).

**Key constants (spaCy-specific):**
- `OMI_SPACY_SCHEMA_VERSION = "omi_spacy_local_nlp_extraction.v1"` (line 1863)
- `OMI_LOCAL_NLP_ADAPTER_NAMES` includes `"spacy"` (line 1864)
- `OMI_LOCAL_NLP_SCHEMA_VERSION_BY_ADAPTER["spacy"]` maps to `OMI_SPACY_SCHEMA_VERSION` (lines 1865-1868)
- `OMI_LOCAL_NLP_SUPPORT_LABEL_BY_ADAPTER["spacy"] = "spaCy fixture support only"` (lines 1869-1872)
- `OMI_LOCAL_NLP_ALLOWED_STATUSES` include `succeeded`, `empty`, `failed_closed`, `error` (lines 1873-1875)
- `OMI_LOCAL_NLP_ENVELOPE_REQUIRED_FIELDS`: `schema_version`, `adapter`, `status`, `provenance`, `findings` (lines 1876-1882)

**Behavior:**
- The `spacy` adapter identity is registered in `OMI_TOOL_ADAPTER_IDENTITIES` (line 67-78).
- Adapter contract is declared in `OMI_ADAPTER_CONTRACTS["spacy"]` (lines 193-208): produces `character`, `location`, `organization`, `object`, `timeline_event`, `evidence_note` finding types; every finding must point to a source excerpt or source_locator; no canon claims.
- When `requested_adapters=["spacy"]` is passed **without** a fixture via `adapter_fixture_outputs`, the orchestrator returns `unavailable` with explanation and no candidates (lines 4489-4498 in `analyze_omi_raw_idea_with_tools`).
- When a fixture is supplied via `adapter_fixture_outputs["spacy"]`, a runner is built via `_build_local_nlp_fixture_runner("spacy", fixture)` (lines 4204-4208 in `_resolve_adapter_runner`).
- The runner validates the fixture against `validate_local_nlp_fixture_envelope` (lines 2320-2426), which:
  - Validates envelope shape (schema_version, adapter, status, provenance, findings).
  - Calls `_coerce_local_nlp_candidate_type("spacy", finding)` (lines 1955-2028) which maps spaCy labels (`PERSON`->`character`, `GPE`/`LOC`/`FAC`->`location`, `ORG`->`organization`, `EVENT`->`timeline_event`, `CONCRETE_NOUN`/`noun`->`object`).
  - Calls `_validate_local_nlp_finding` for each finding (lines 2228-2315), which enforces evidence, source_locator, provenance, no-prose, no-truth-label, no-auto-approval rules.
- Always returns non-persistent findings (even when `persist_candidates=True` in T007 scope).
- Fixture/mock only; no live spaCy import or runtime call.

**Test contract location:** `tests/test_omi_booknlp_spacy_adapter_contract.py` (399 lines, 10 tests).

**Key test coverage for spaCy:**
- `test_spacy_without_fixture_returns_unavailable_and_no_findings` (line 146): no fixture -> unavailable.
- `test_valid_spacy_fixture_normalizes_candidate_only_findings` (line 233): valid fixture normalizes PERSON->character, LOC->location, ORG->organization, CONCRETE_NOUN->object, EVENT->timeline_event.
- `test_spacy_fixture_missing_evidence_source_locator_or_provenance_fails_closed` (line 312): missing fields -> fail_closed.
- `test_booknlp_and_spacy_reject_truth_canon_approved_or_promoted_output` (line 327): truth labels -> fail_closed.
- `test_booknlp_and_spacy_reject_prose_like_generated_output` (line 344): prose -> fail_closed.
- `test_booknlp_and_spacy_reject_memory_canon_and_promotion_operations` (line 359): promotion/mutation -> fail_closed.
- `test_booknlp_and_spacy_findings_are_not_persisted_or_mutating` (line 374): persistence blocked.

**Adapter identity/result-state handling (orchestrator module):**
- `OMI_TOOL_ADAPTER_IDENTITIES` (line 67): `frozenset` including `"spacy"`.
- `OMI_ADAPTER_RESULT_STATES` (line 80): `succeeded`, `empty`, `skipped`, `unavailable`, `failed_closed`, `error`.
- `OMI_ADAPTER_NO_CANDIDATE_RESULT_STATES` (line 93): states that must not produce findings.
- No-candidate enforcement: `validate_adapter_result` (line 936) rejects non-empty candidates for non-succeeded states.

## Existing T013 spaCy Preflight/Config Summary

**Location:** `backend/omi_runtime_preflight.py` (299 lines).

**spaCy-specific behavior (lines 85-88):**
```python
if adapter == "spacy":
    configured = True
    available = _find_module("spacy")
    detail = "Python package probe: spacy"
```
- `configured = True` unconditionally (spaCy requires no external command/config beyond the Python package).
- `available = _find_module("spacy")` uses `importlib.util.find_spec("spacy")` — True only if the `spacy` package is installed.
- No model download check, no pipeline load attempt.

**Feature flag for spaCy (line 38):**
```python
OMI_LIVE_TOOL_ENABLED_ENVS = {
    "spacy": "OMI_LIVE_SPACY_ENABLED",
    ...
}
```
- `OMI_LIVE_SPACY_ENABLED` env var enables live spaCy runtime.
- Global gate: `OMI_LIVE_TOOLS_ENABLED`.
- Per-tool blocked flag: `OMI_LIVE_SPACY_BLOCKED`.
- Per-tool blocked reason: `OMI_LIVE_SPACY_BLOCKED_REASON`.

**Status computation (`_tool_report`, lines 167-244):**
- If `OMI_LIVE_SPACY_BLOCKED=true` -> `blocked`.
- If global+tool enabled and **not** configured (but spacy is always configured=True) -> `not_configured`.
- If global+tool enabled and dependency **not** available -> `unavailable`.
- If global+tool enabled and dependency available -> `enabled`.
- If dependency available but flags disabled -> `available`.
- Otherwise -> `disabled`.

**Route:**
- `GET /api/projects/{project_name}/omi/runtime-preflight` in `backend/main.py:358-360` calls `omi_runtime_preflight.build_omi_runtime_preflight_report(project_name)`.

**Preflight safety:** read-only; no heavy analysis, external services, live models, candidate persistence, Memory/Canon mutation, promotion/apply-promotion, or story prose generation.

**Tests:** `tests/test_omi_live_runtime_preflight_contract.py` (193 lines, 8 tests). Tests cover disabled-by-default, missing deps, per-tool flags, global gate, fixture-contract existence, blocked override, and route wrapper safety.

## T014B Recommended Exact Scope

**Goal:** Make spaCy availability checks work with a real installed spaCy package.

**Files to touch:**
1. `backend/omi_runtime_preflight.py` — enhance `_dependency_probe` for `"spacy"` to also check for a model (e.g., `spacy.util.is_package("en_core_web_sm")` or equivalent probe), and report model availability separately.
2. `backend/omi_analysis_orchestrator.py` — add a `_build_spacy_live_runner` function (or extend `_resolve_adapter_runner`) that, when `adapter_config` carries live-mode flags and a fixture is not supplied, attempts to import `spacy`, load a model, and process `raw_idea` text through the spaCy pipeline, producing normalized findings. This function must:
   - Import `spacy` only when live mode is explicitly enabled.
   - Fail closed if spaCy is not installed or model is not available.
   - Fail closed if raw_idea is prose-like or empty.
   - Extract entities (PERSON->character, GPE/LOC/FAC->location, ORG->organization, EVENT->timeline_event, PRODUCT/other->object).
   - Extract noun chunks as object mentions.
   - Build evidence from sentence text spans.
   - Return an adapter envelope with `state="succeeded"` and normalized findings.
   - Never persist candidates, mutate Memory/Canon, create promotion records, call apply-promotion, or generate story prose.
3. `backend/main.py` — no changes needed unless a new route is desired (preflight route already exists).

**Tests to add or modify:**
1. `tests/test_omi_booknlp_spacy_adapter_contract.py` — add expected-red tests for live spaCy adapter:
   - `test_spacy_live_unavailable_when_not_installed` (expected: unavailable/fail_closed when `importlib.util.find_spec("spacy")` returns None)
   - `test_spacy_live_model_unavailable` (expected: unavailable/fail_closed when model is missing)
   - `test_spacy_live_processes_raw_idea` (expected: returns normalized findings from real spaCy entities)
   - `test_spacy_live_rejects_prose_raw_idea` (expected: fail_closed)
   - `test_spacy_live_rejects_empty_raw_idea` (expected: fail_closed)
   - `test_spacy_live_no_candidate_persistence` (expected: no writes when persist_candidates=True)
   - `test_spacy_live_safety_envelope` (expected: no Memory/Canon mutation, no promotion, no prose)
2. `tests/test_omi_live_runtime_preflight_contract.py` — add expected-red test:
   - `test_spacy_preflight_model_probe` (expected: reports model availability status)

**Validation pattern:** focused pytest, env gating via `OMI_LIVE_SPACY_ENABLED`, separate CI-safe (preflight) and local-only (live) test markers.

## T014C Deferred Scope

- **Live spaCy integration test against real installed spaCy:** deferred to T014C implementation.
- **Manual validation with real model output:** deferred to T014D.
- **Cross-tool fusion with real spaCy output:** deferred to T021.
- **Grouped owner-review UI for real spaCy findings:** deferred to T023.
- **spaCy model download automation:** not in scope — the user/installer must install the model manually.
- **Multiple model support:** not in first slice — only `en_core_web_sm` in scope.
- **spaCy pipeline customization / custom components:** deferred beyond PHASE8-IMPL-023.
- **Sentence segmentation as primary extraction mode:** not in first slice — entity/noun-chunk extraction first.

## Current Blocked/Open Questions

1. **spaCy package dependency name:** `spacy`
2. **spaCy model dependency name for MVP:** `en_core_web_sm` (small model, ~12MB download)
3. **spaCy model explicit import path:** `spacy.load("en_core_web_sm")` — must be imported only when live mode is explicitly flagged
4. **spaCy version requirement:** latest stable (>=3.7.x) — not pinned in T014A
5. **Open question 107 in open_questions.md:** "What runtime dependencies are required for BookNLP and spaCy?" — still open. T014A documents that spaCy requires the `spacy` Python package and an `en_core_web_sm` model for MVP, but does not resolve the dependency policy.
6. **Open question 109:** "What owner-blocked documentation format should T014-T020 use when a selected live tool remains unavailable after preflight?" — still open. T014B/C should produce docs-only owner-blocked decision if spaCy cannot be installed.

## Validation Commands and Results

```
git status --short --branch
  → On branch docs/opencode-go-routing-small-task-execution
    (modified artifacts only, no staging)

git diff --stat
  → 3 modified files (artifacts only, no tracked source changes)

git diff --check
  → (no whitespace errors)

python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py
  → PASS (no errors)

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q
  → 10 passed in 0.08s

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
  → 8 passed in 2.61s

python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
  → Valid JSON (parse OK)
```

## Deferred Work

T014B (expected-red tests for live spaCy) and T014C (live spaCy adapter implementation) are deferred to separate tasks. T014A does not implement, install, or test live spaCy.

## Statements

- This T014A inspect/docs task connected no live spaCy runtime.
- Fixture/mock spaCy contract (`omi_spacy_local_nlp_extraction.v1`) is scaffolding only — it validates schema, safety, no-prose boundaries, and candidate normalization, but does not prove that the application can run real spaCy analysis. It does not count as MVP completion.
- T013 preflight readiness reports dependency availability and feature-flag enablement only. Preflight readiness does not prove live spaCy analysis and does not count as MVP completion.
- No Memory/Canon mutation, promotion records, automatic apply-promotion, or story prose were added by this task.
- No backend/frontend runtime behavior was edited.
- No tests were created or modified (future test targets were documented only).
- Nothing was staged, committed, or pushed.
