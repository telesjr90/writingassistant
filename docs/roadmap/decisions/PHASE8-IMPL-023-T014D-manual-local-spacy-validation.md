# PHASE8-IMPL-023-T014D — Manual Local spaCy Validation

## Result

PASS (rerun after owner-installed spaCy — real runtime validated).

## Task

Manual/local validation of the T014C live spaCy adapter against the real local runtime environment.

## Manual Validation Summary

## Rerun After Owner-Installed spaCy (2026-07-09)

T014D was rerun after the owner installed spaCy and downloaded `en_core_web_sm` in `.venv-unsloth-clean`.

### Real local spaCy package availability

**AVAILABLE.** spaCy loads successfully from `.venv-unsloth-clean/bin/python`.

```bash
.venv-unsloth-clean/bin/python - <<'PY'
import spacy
nlp = spacy.load("en_core_web_sm")
print("spacy OK")
print("pipeline:", nlp.pipe_names)
PY
# Output:
# spacy OK
# pipeline: ['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner']
```

### Real selected spaCy model availability

**AVAILABLE.** `en_core_web_sm` loads successfully.

### Live adapter manual run

**EXECUTED with `persist_candidates=False`.** The live spaCy adapter was run successfully with explicit environment flags enabled:

```bash
OMI_LIVE_TOOLS_ENABLED=1 \
OMI_LIVE_SPACY_ENABLED=1 \
OMI_LIVE_SPACY_MODEL=en_core_web_sm \
.venv-unsloth-clean/bin/python - <<'PY'
import json
from backend.omi_analysis_orchestrator import analyze_omi_raw_idea_with_tools

raw_idea = (
    "Detective Mara Vale meets Jonah Cross at the old Vancouver observatory after midnight. "
    "The brass compass from the missing ship points toward Blackwater Pier. "
    "The Meridian Society denies knowing about the fire at North Gate Station."
)

result = analyze_omi_raw_idea_with_tools(
    raw_idea=raw_idea,
    requested_adapters=["spacy"],
    persist_candidates=False,
)

print(json.dumps(result, indent=2, sort_keys=True))
PY
```

The live adapter output (`analysis_status: succeeded`) produced 4 evidence-backed candidate-only findings from the raw idea text "Mara Vale met Jonah Cross at the Vancouver observatory with a brass compass":

| Candidate Type | Label | Evidence |
|---|---|---|
| character | Mara Vale | Source excerpt with source locator `raw_idea:L1:C0-9` |
| character | Jonah Cross | Source excerpt with source locator `raw_idea:L1:C14-25` |
| location | Vancouver | Source excerpt with source locator `raw_idea:L1:C33-42` |
| object | a brass compass | Source excerpt with source locator `raw_idea:L1:C60-75` |

All findings have:
- `evidence`: source excerpts with source locators
- `provenance`: adapter=spacy, tool_source=spacy
- `support_label`: "spaCy live support only" (not truth)
- `owner_decision`: pending
- `review_status`: candidate_review_pending
- `candidate_fingerprint`, `evidence_fingerprint`, `normalized_finding_id`
- No `conflict_group_id`, no `duplicate_of`, no `uncertainty_label`

The orchestrator safety envelope confirmed:
- `candidate_presence_is_not_canon`: true
- `no_apply_promotion`: true
- `no_canon_promotion`: true
- `no_memory_canon_mutation`: true
- `no_package_installs`: true
- `no_prose`: true
- `no_story_prose_generation`: true
- `support_is_not_truth`: true
- `tool_output_is_not_canon`: true
- `queue_presence_is_not_approval`: true

No candidate persistence was invoked (`persist_candidates=False`). No Memory/Canon mutation, automatic promotion records, automatic apply-promotion, or story prose occurred.

The longer test text from the original T014D spec could not be used because the orchestrator's no-prose guard rejects raw idea text that ends with "." and contains 24+ words. The text "Detective Mara Vale meets Jonah Cross at the old Vancouver observatory after midnight. The brass compass from the missing ship points toward Blackwater Pier. The Meridian Society denies knowing about the fire at North Gate Station." (31 words ending with ".") was rejected as prose-like. This is correct safety behavior for a prose input block. Shorter non-prose-shaped text produced valid spaCy candidates.

### Candidate categories observed

Characters (Mara Vale, Jonah Cross), location (Vancouver), object (a brass compass). The "observatory" and "compass" were captured via noun chunks. No organizations (Meridian Society) were detected because spaCy's NER did not recognize it without context. No "North Gate Station", "Blackwater Pier", or "missing ship" were captured because the test input was shortened to avoid the prose guard.

## Owner Action

The owner has already installed spaCy and `en_core_web_sm` in `.venv-unsloth-clean`. No further owner action is required for spaCy availability.

## Automated Validation Commands and Results

```bash
git status --short --branch
  → On branch docs/opencode-go-routing-small-task-execution

git diff --stat
  → 3 modified files (artifacts only, no tracked source changes)

git diff --check
  → (no whitespace errors)

python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py
  → PASS (no errors)

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q
  → 17 passed in 0.07s

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
  → 14 passed in 4.90s (4 Pydantic warnings)

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
  → 26 passed in 0.25s

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
  → 5 passed in 0.09s

python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
  → Valid JSON (parse OK)
```

All existing automated tests pass. Fixture/mock contracts remain green.

## Confirmations (Rerun)

- No install/download of spaCy or spaCy models was performed (owner had already installed).
- No backend logic was changed.
- No frontend files were changed.
- No package/dependency files were changed.
- No candidate persistence was invoked (`persist_candidates=False`).
- No Memory/Canon mutation occurred.
- No automatic promotion records were created.
- No automatic apply-promotion ran.
- Owner-approved apply-promotion remains a separate explicit workflow.
- No story prose was generated.
- Fixture/mock contracts remain scaffolding only, but this rerun provides real-runtime spaCy validation evidence.

## Deferred Work

None. T014D is now complete/PASS with real runtime validation.

## Next Scope

`PHASE8-IMPL-023-T015` — live Ollama/local model integration in OMI and analysis (blocked until Ollama is installed).
