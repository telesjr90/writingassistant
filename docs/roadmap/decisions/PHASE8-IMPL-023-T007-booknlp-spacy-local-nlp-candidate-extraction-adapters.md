# PHASE8-IMPL-023-T007 BookNLP/spaCy Local NLP Candidate Extraction Adapters

## Result

PASS for fixture-only BookNLP/spaCy local NLP adapter contracts.

`PHASE8-IMPL-023-T007` wires the `booknlp` and `spacy` adapters through the existing OMI analysis orchestrator extension point using fixture/mock/local deterministic output only. No live BookNLP or spaCy runtime call is performed or enabled.

The next child is `PHASE8-IMPL-023-T008 - Story Check diagnostic-only OMI handoff`.

## Implementation

- Extended `backend/omi_analysis_orchestrator.py` with fixture-only local NLP schema support:
  - `OMI_BOOKNLP_SCHEMA_VERSION = "omi_booknlp_local_nlp_extraction.v1"`.
  - `OMI_SPACY_SCHEMA_VERSION = "omi_spacy_local_nlp_extraction.v1"`.
  - `validate_local_nlp_fixture_envelope`.
  - `_build_local_nlp_fixture_runner`.
  - `_resolve_adapter_runner` support for `adapter_fixture_outputs["booknlp"]` and `adapter_fixture_outputs["spacy"]`.
- `requested_adapters=["booknlp"]` or `["spacy"]` without fixture/runner returns `unavailable` with explanation, no findings, and no live runtime call.
- Valid BookNLP fixtures may normalize person/entity/location/event/object/relationship/coreference-style support into candidate-only findings.
- Valid spaCy fixtures may normalize `PERSON`, `GPE`/`LOC`/`FAC`, `ORG`, `EVENT`, and object/concrete-noun-style support into candidate-only findings.
- Local NLP findings remain non-persistent, even when `persist_candidates=True`.

## Validation Rules

- Top-level payload must be a JSON object, not an array or scalar.
- Required envelope fields: `schema_version`, `adapter`, `status`, `provenance`, `findings`.
- Only the matching schema version and adapter identity are accepted.
- Allowed statuses: `succeeded`, `empty`, `failed_closed`, `error`.
- Non-`succeeded` statuses must carry zero findings.
- Findings must carry type/label/claim, evidence excerpt, source locator, and provenance.
- Unknown candidate/finding types fail closed.
- Missing evidence, source locator, or provenance fails closed.
- Truth/canon/approved/promoted labels fail closed.
- Auto-approved owner decisions fail closed.
- Prose-like extracted claims fail closed.
- Memory/Canon mutation, promotion-record, and apply-promotion fields fail closed.

## Safety

- BookNLP/spaCy output is support only, not truth.
- Owner decision remains pending.
- Review status remains candidate/review-pending.
- AI/tool findings from `booknlp` and `spacy` are never persisted in T007.
- `deterministic_fallback` remains off by default, opt-in only via `allow_deterministic_fallback=True`, and marked `fallback_only`.
- `story_check` remains deferred to T008.
- `ncp`, `subtxt`, and `dramatica_flow` remain deferred to T009.
- No Memory/Canon mutation, promotion record, apply-promotion, live BookNLP/spaCy runtime call, frontend UI, package change, or story prose generation occurred.

## Tests

- `python3 -m py_compile backend/omi_analysis_orchestrator.py` -> PASS.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q` -> `10 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_ollama_model_adapter_contract.py -q` -> `19 passed`.
- `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q` -> `26 passed`.

## Boundaries Confirmed

- No live BookNLP/spaCy call.
- No dependency installation.
- No Story Check, NCP, Subtxt, or dramatica-flow run.
- No Memory/Canon mutation.
- No promotion/apply-promotion created, run, or enabled.
- No candidates persisted from BookNLP/spaCy findings.
- No frontend UI change.
- No story prose generated.
- No staging, commit, or push.
