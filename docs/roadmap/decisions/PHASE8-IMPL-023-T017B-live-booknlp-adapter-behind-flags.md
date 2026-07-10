# PHASE8-IMPL-023-T017B: Live BookNLP Adapter Behind Flags

## Status

Accepted.

## Task type

Live BookNLP adapter wiring — adds a `booknlp` runner behind explicit env flags, normalizes evidence-backed BookNLP output into the existing T007 envelope shape, and adds mocked-BookNLP contract tests. No real BookNLP processing is required by automated tests. T017C must later perform manual real BookNLP validation on owner-authored text to prove the live BookNLP MVP path.

## Scope

Add a live BookNLP adapter runner behind explicit env flags and integrate it with the existing OMI tool-assisted orchestrator adapter-resolution path.

The live adapter:

1. Is disabled by default.
2. Is reachable only when all of the following hold:
   - `OMI_LIVE_TOOLS_ENABLED=1` (or `true`/`yes`/`on`)
   - `OMI_LIVE_BOOKNLP_ENABLED=1` (or `true`/`yes`/`on`)
   - `OMI_LIVE_BOOKNLP_BLOCKED` is not truthy
3. Fails closed with no findings when:
   - any of the above flags is missing/disabled/blocked
   - the BookNLP package is not installed (`ImportError`)
   - BookNLP model assets or the temporary directory are unavailable (`OSError`)
   - `BookNLP.process(...)` raises any other exception
   - the parsed `.entities` / `.quotes` output is empty or malformed
   - any text is unsafe (truth / canon / approved / promoted / rewrite / continue / outline / draft / prose-shaped)
   - the T007 `validate_local_nlp_fixture_envelope` rejects the converted envelope
4. Never mutates Memory/Canon.
5. Never creates automatic promotion records.
6. Never runs apply-promotion.
7. Never generates story prose (rewriting, polishing, continuing, expanding, drafting, improving, imitating, revising, outlining, or generating).
8. Never persists raw BookNLP output to project storage in T017B. Raw artifact persistence is intentionally deferred to a later task.
9. Reuses the existing T007 `omi_booknlp_local_nlp_extraction.v1` envelope shape and the authoritative T007 `validate_local_nlp_fixture_envelope` validator; existing fixture/mock BookNLP behavior is preserved when the live flags are off.
10. Honors the existing candidate-only persistence boundary: candidate persistence only runs through the existing orchestrator entrypoint path when `persist_candidates=True` and source context is sufficient; T017B does not introduce any new persistence path.

## Implementation

- Extended `backend/omi_analysis_orchestrator.py` with:
  - Live BookNLP env constants:
    - `_OMI_LIVE_BOOKNLP_ENABLED_ENV = "OMI_LIVE_BOOKNLP_ENABLED"`
    - `_OMI_LIVE_BOOKNLP_BLOCKED_ENV = "OMI_LIVE_BOOKNLP_BLOCKED"`
    - `_OMI_LIVE_BOOKNLP_BLOCKED_REASON_ENV = "OMI_LIVE_BOOKNLP_BLOCKED_REASON"`
    - `_OMI_LIVE_BOOKNLP_MODEL_ENV = "OMI_LIVE_BOOKNLP_MODEL"` (default `"small"`)
    - `_OMI_LIVE_BOOKNLP_PIPELINE_ENV = "OMI_LIVE_BOOKNLP_PIPELINE"` (default `"entity,quote,supersense,event"`)
    - `_OMI_LIVE_BOOKNLP_INPUT_BOOK_ID = "omi_booknlp_input"` (deterministic safe book id)
    - `_OMI_LIVE_BOOKNLP_INPUT_FILENAME = "omi_booknlp_input.txt"`
  - Category mapping `_OMI_BOOKNLP_LIVE_ENTITY_CATEGORY_TO_CANDIDATE_TYPE` for `PER`/`GPE`/`LOC`/`FAC`/`ORG`/`VEH` → orchestrator finding types.
  - Skip-list `_OMI_BOOKNLP_LIVE_SKIP_ENTITY_TEXTS` for pronoun / possessive / demonstrative mentions.
  - Helper functions:
    - `_booknlp_safe_text_excerpt` (plain trim+truncate, no sanitization)
    - `_booknlp_entity_category_is_safe` (safe-token validator for BookNLP `cat` codes)
    - `_booknlp_parse_entities_file` (TSV → list of row dicts; skips unsafe/empty rows)
    - `_booknlp_parse_quotes_file` (TSV → list of row dicts; skips unsafe/empty rows)
    - `_booknlp_parse_tokens_file` (TSV → list of token row dicts; used to resolve byte-offset locators)
    - `_booknlp_resolve_token_locator` (turns `start_token`/`end_token` ids into a `raw_idea:L1:C<onset>-<offset>` locator)
    - `_booknlp_safe_locator` (fallback numeric locator)
    - `_booknlp_entity_candidate_type_from_category` (category → orchestrator finding type)
    - `_booknlp_make_entity_finding` (T007-shaped evidence-backed entity finding; rejects unsafe text)
    - `_booknlp_make_quote_finding` (T007-shaped dialogue-attribution candidate finding; rejects unsafe text)
    - `_booknlp_live_result_to_envelope` (parsed rows → T007 envelope; empty rows fail closed)
    - `_booknlp_entity_result_to_envelope` (entity-only envelope; used as defensive fallback)
  - Live runner factory `_build_booknlp_live_runner`:
    - Imports `from booknlp.booknlp import BookNLP` lazily inside the runner path.
    - Validates `OMI_LIVE_BOOKNLP_MODEL` against `{"small", "big", "custom"}` and falls back to `"small"` for anything else.
    - Validates `OMI_LIVE_BOOKNLP_PIPELINE` against the safe pipe set `{"entity", "event", "supersense", "quote", "coref"}` and always keeps `entity` first.
    - Writes the owner raw idea to a temporary `omi_booknlp_input.txt` under `tempfile.TemporaryDirectory(prefix="omi_booknlp_live_")`.
    - Calls `BookNLP("en", model_params).process(input_path, output_dir, "omi_booknlp_input")` against the temporary output directory.
    - Parses the temporary `.entities` / `.quotes` / `.tokens` files.
    - Converts the parsed rows into the T007 `omi_booknlp_local_nlp_extraction.v1` envelope shape.
    - Validates the converted envelope through `validate_local_nlp_fixture_envelope` (the T007 validator is authoritative).
    - Fail-closed on `ImportError`, `OSError`, generic `Exception`, empty/malformed output, or T007 validation failure.
    - The temporary directory is always cleaned up (the runner does not persist raw BookNLP output).
- Wired the live runner into `_resolve_adapter_runner` so `analyze_omi_raw_idea_with_tools` reaches it whenever `OMI_LIVE_TOOLS_ENABLED=1` + `OMI_LIVE_BOOKNLP_ENABLED=1` and `OMI_LIVE_BOOKNLP_BLOCKED` is unset. The existing T005/T006/T007 fixture-only paths remain unchanged.
- Updated the BookNLP unavailable explanation to mention the new live env-flag path and to clarify that the orchestrator does not perform live BookNLP calls by default and does not import or install BookNLP automatically.

## Normalized BookNLP outputs supported in T017B

- `.entities` rows (BookNLP entity mentions) → evidence-backed candidate findings
  - `cat` suffix `PER` → `character`
  - `cat` suffix `GPE`/`LOC`/`FAC` → `location`
  - `cat` suffix `ORG` → `organization`
  - `cat` suffix `VEH` → `object`
  - Other categories (e.g. `EVENT`) are rejected at the converter; deferred to a later task
- `.quotes` rows (BookNLP attributed quotations) → `diagnostic_question` candidate findings
  - Each row emits one candidate when the row carries a safe `quote`, `mention_phrase`, and `char_id`.
  - The `char_id` is treated as an opaque BookNLP-internal id; it is never treated as a confirmed canon identity.
- `.tokens` rows (BookNLP token table) → used to resolve byte-offset source locators
  - The runner resolves `raw_idea:L1:C<byte_onset>-<byte_offset>` locators from the `start_token`/`end_token` ids in each entity/quote row.
  - When `.tokens` is missing, the runner falls back to a numeric-token-id locator and still validates the resulting envelope through the T007 validator.

## Outputs deliberately deferred

- `cat` suffix `EVENT` (and any other non-`PER/GPE/LOC/FAC/ORG/VEH` entity categories) → parsing safely is deferred to a later task.
- Coreference/alias truth → BookNLP coreference output is evidence only; the runner never claims two mentions are the same person. Alias candidate normalization is deferred to a later task.
- Referential gender / pronoun outputs → never treated as gender identity. Pronoun-evidence candidate normalization is deferred to a later task.
- Supersense tags → not yet parsed in T017B; deferred to a later task.
- Raw BookNLP artifact persistence → the runner does not write the temporary `.entities` / `.quotes` / `.tokens` files outside the temporary directory, and the temporary directory is cleaned up after the run. Persisting raw BookNLP artifacts into project storage is intentionally a later task if ever authorized.

## Safety

- Live BookNLP output is support only, not truth.
- Owner decision remains `pending`; `review_status` remains `candidate_review_pending`.
- Truth / canon / approved / promoted / rewrite / continue / outline / draft / prose-shaped text is rejected at the converter level. The runner does NOT rewrite or sanitize unsafe legacy text into a safe claim; unsafe items are SKIPPED.
- The T007 `validate_local_nlp_fixture_envelope` is the authoritative downstream validator and remains unchanged. T017B does not modify the T007 contract.
- `no_memory_canon_mutation`, `no_apply_promotion`, `no_canon_promotion`, `no_story_prose_generation`, `candidate_presence_is_not_canon`, `queue_presence_is_not_approval`, `support_is_not_truth`, `tool_output_is_not_canon` all remain `True`.
- No live BookNLP call is made by default; no live BookNLP call is made by automated tests; no live BookNLP call is required by automated tests. The mocked-BookNLP tests cover disabled-by-default, blocked, missing package, runtime exception, empty output, malformed output, unsafe category, unsafe excerpt, no-mutate/persist/prose, and env-override behavior.
- Existing T007 fixture tests still pass when the live flags are off (the BookNLP path returns `unavailable` with the new explanation when no fixture and no live flags are provided).

## Runtime caveats from T017A (still in effect)

- CPU fallback: BookNLP runs on the owner CPU; the pre-existing `Can't initialize NVML` warning is non-blocking.
- `setuptools==80.9.0` is required because `setuptools>=81` removes/breaks the `pkg_resources` import path that BookNLP uses. The pre-existing `pkg_resources is deprecated` warning is non-blocking.
- `torch==2.10.0+cu129` is below the `>=2.11` required by BookNLP cpp extensions. The `Skipping import of cpp extensions due to incompatible torch version` warning is non-blocking for import; T017C must prove actual BookNLP processing on owner-authored text.

## Next task

PHASE8-IMPL-023-T017C — Manual real BookNLP validation. Manual real BookNLP processing on owner-authored text, behind the T017B live env flags, using the installed `.venv-unsloth-clean` BookNLP runtime, with explicit pass/fail classification and a documented closeout decision.

## Validation

- `python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py backend/analysis_engine.py` → exit 0
- `tests/test_omi_booknlp_spacy_adapter_contract.py -q` → 30 passed (16 existing T007/T014C + 13 new T017B) [pre-existing `test_live_spacy_missing_package_returns_unavailable` failure is unrelated to T017B; verified pre-existing on a stashed working tree before T017B edits]
- `tests/test_omi_tool_assisted_orchestrator_contract.py -q` → 30 passed
- `tests/test_omi_tool_assisted_persistence_contract.py -q` → 5 passed
- `tests/test_omi_live_runtime_preflight_contract.py -q` → 50 passed
- `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` → VALID
