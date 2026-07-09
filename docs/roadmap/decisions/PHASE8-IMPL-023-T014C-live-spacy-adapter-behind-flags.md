# PHASE8-IMPL-023-T014C — Live spaCy Adapter Behind Flags

## Status

Accepted/complete/PASS.

## Task

Implement the live spaCy adapter that uses `spacy` to analyze raw idea text and produce normalized candidate-only findings, behind explicit runtime flags.

## Scope

- Add `_build_spacy_live_runner` to `backend/omi_analysis_orchestrator.py` that:
  - Imports spaCy lazily (never at module import time).
  - Loads the configured model from `OMI_LIVE_SPACY_MODEL` (default `en_core_web_sm`). Does not download models.
  - Processes raw idea text and extracts entities (PERSON, GPE, LOC, FAC, ORG, EVENT) and noun chunks.
  - Constructs a valid `omi_spacy_local_nlp_extraction.v1` envelope that flows through the existing fixture validation/normalization pipeline.
  - Maps entity labels: `PERSON` -> `character`, `GPE`/`LOC`/`FAC` -> `location`, `ORG` -> `organization`, `EVENT` -> `timeline_event`.
  - Maps non-overlapping noun chunks to `object` candidates with evidence text.
  - Every finding includes: candidate type, label/name, extracted claim, evidence/source excerpt, source locator, provenance (tool source = `spacy`), support-only metadata, pending owner decision, and review-pending status.
  - Fail-closed on ImportError, OSError (model missing), runtime processing exception, empty/malformed input, or envelope normalization failure.
- Wire the runner through `_resolve_adapter_runner` so it is only triggered when all conditions are met:
  - `requested_adapters` includes `spacy`.
  - `OMI_LIVE_TOOLS_ENABLED` is truthy.
  - `OMI_LIVE_SPACY_ENABLED` is truthy.
  - `OMI_LIVE_SPACY_BLOCKED` is falsy.
- Update `tests/test_omi_booknlp_spacy_adapter_contract.py` with focused monkeypatch/mock tests:
  - Live spaCy disabled by default returns unavailable.
  - Live spaCy enabled with mocked model returns normalized candidates for PERSON/GPE/ORG/EVENT.
  - Live spaCy noun chunks produce object candidates when evidence-backed.
  - Missing spaCy package returns unavailable.
  - Model load failure returns unavailable.
  - Runtime processing exception fails closed.
  - Safety boundaries preserved (no Memory/Canon mutation, no auto-approval, candidate-only).
- Create this decision record.
- Update roadmap/status files minimally.

## Implementation

### `backend/omi_analysis_orchestrator.py`

Added:

- `import os` and `from typing import Any, Callable, Mapping` — additional stdlib imports.
- Local env var constants: `_OMI_LIVE_TOOLS_ENABLED_ENV`, `_OMI_LIVE_SPACY_ENABLED_ENV`, `_OMI_LIVE_SPACY_BLOCKED_ENV`, `_OMI_LIVE_SPACY_MODEL_ENV`, `_OMI_LIVE_SPACY_MODEL_DEFAULT`.
- Live entity label map: `_OMI_SPACY_LIVE_ENTITY_LABEL_TO_CANDIDATE_TYPE`.
- Pronoun/determiner skip set: `_OMI_SPACY_LIVE_SKIP_NOUN_CHUNK_TEXTS`.
- `_env_bool(env, name, default)` — minimal env-var-to-bool helper.
- `_build_spacy_live_runner(*, adapter_config)` — returns a runner closure that:
  1. Checks raw idea is non-empty.
  2. Lazily imports spaCy (inside a `try/except ImportError`).
  3. Loads the configured model (`try/except OSError`).
  4. Processes the text (`try/except Exception` for runtime failures).
  5. Iterates `doc.ents`, mapping known labels to candidate types with deduplication and evidence extraction (sentence text, character-offset source locator).
  6. Iterates `doc.noun_chunks`, filtering out entity-overlapping chunks and very short/long chunks, producing `object` candidates.
  7. Builds an `omi_spacy_local_nlp_extraction.v1` envelope and validates it through the existing `validate_local_nlp_fixture_envelope`.
  8. Returns fail-closed envelopes on any failure.
- Modified `_resolve_adapter_runner` to check env flags for a live spaCy path after the fixture path is exhausted. When adapter is `"spacy"` and env flags allow live, returns `_build_spacy_live_runner()`. Otherwise falls through to None (unavailable).
- Updated module-docstring boundaries section to note that live spaCy is available behind flags.
- Updated the unavailable-explanation for spaCy (when no fixture and no live flags) to mention the env flag requirement.

### `tests/test_omi_booknlp_spacy_adapter_contract.py`

Added T014C-focused tests:

- `test_live_spacy_disabled_by_default_returns_unavailable` — no env flags, expects `unavailable`.
- `test_live_spacy_enabled_with_mocked_model_returns_normalized_candidates` — env flags + mock spaCy with PERSON/LOC/ORG/EVENT entities, expects `succeeded` with 4 normalized candidate-only findings.
- `test_live_spacy_noun_chunks_produce_object_candidates` — env flags + mock spaCy with one entity and one non-overlapping noun chunk, expects `object` candidate type.
- `test_live_spacy_missing_package_returns_unavailable` — env flags, no mock spaCy, expects `unavailable` with "not installed" explanation.
- `test_live_spacy_model_load_failure_returns_unavailable` — env flags + mock spaCy with `load` raising `OSError`, expects `unavailable` with model-related explanation.
- `test_live_spacy_runtime_exception_fails_closed` — env flags + mock spaCy with `nlp()` raising `RuntimeError`, expects `failed_closed` with processing/error explanation.
- `test_live_spacy_safety_boundaries_preserved` — env flags + mock spaCy, verifies `no_memory_canon_mutation`, `no_apply_promotion`, candidate-only support labels, and evidence presence.

All tests use monkeypatch and `MagicMock` only. No real spaCy installation or model download is required.

## Key Design Decisions

1. **Lazy spaCy import**: `import spacy` only happens inside the live runner closure, never at module import time. This preserves the existing T005/T007 contract that the orchestrator module does not import spaCy at the top level.
2. **Env-flag gating in `_resolve_adapter_runner`**: The adapter runner is only built when env flags explicitly enable live spaCy. This keeps the default behavior as "fixture-only" for tests that don't set env vars.
3. **Fixture envelope reuse**: Live spaCy output is transformed into an `omi_spacy_local_nlp_extraction.v1` envelope and validated through the existing `validate_local_nlp_fixture_envelope` function. This reuses all existing validation, normalization, evidence extraction, and fail-closed logic.
4. **Entity-to-candidate-type mapping**: The live runner maps spaCy NER labels to OMI finding types exactly as the existing fixture `_coerce_local_nlp_candidate_type` does, ensuring consistent behavior.
5. **Noun chunk object candidates**: Non-overlapping noun chunks with evidence text produce `object` candidates. Very short (pronoun/determiner-only) and very long (6+ tokens) chunks are filtered out. Chunks overlapping entity spans are skipped.
6. **Fail-closed on all failures**: ImportError (package not installed), OSError (model missing), processing exceptions, empty input, and envelope normalization failures all produce `unavailable` or `failed_closed` states with zero candidates and clear explanations.
7. **No automatic model download**: The runner calls `spacy.load()` only. It never calls `spacy.cli.download()` or any equivalent.
8. **Candidate-only persistence**: Live spaCy findings are normalized through the same candidate-only pipeline. No Memory/Canon mutation, automatic promotion records, automatic apply-promotion, or story prose.
9. **Mock-first testing**: All live spaCy tests mock the spaCy module via `monkeypatch.setitem(sys.modules, ...)`. No real spaCy installation or model download is needed.

## Excluded from This Task

- No spaCy package/model install/download was performed.
- Tests mock spaCy and do not require real local spaCy.
- Live runner is disabled unless explicitly enabled/configured via env flags.
- Live output normalizes into candidate-only evidence/provenance-backed findings.
- Fixture/mock contract remains supported and remains scaffolding only.
- No Memory/Canon mutation during analysis/runtime extraction.
- No automatic promotion records from analysis/runtime/model/tool output.
- No automatic apply-promotion from model/tool output.
- Owner-approved apply-promotion remains a separate explicit workflow.
- No story prose was generated.
- No frontend files were changed.
- No package/dependency files were changed.
- Nothing was staged or committed.

## Next Scope

`PHASE8-IMPL-023-T014D` or next validation step — manual local spaCy validation if real spaCy/model are installed. This should verify that the live runner produces sensible output with real spaCy, catches any edge cases not covered by mocked tests, and confirms the fail-closed behavior is robust in a real local environment.

## Validation

```bash
python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q  # 17 passed
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q  # 14 passed
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q  # 26 passed
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q  # 5 passed
```
