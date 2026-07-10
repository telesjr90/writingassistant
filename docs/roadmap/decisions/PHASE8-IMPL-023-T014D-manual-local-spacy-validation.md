# PHASE8-IMPL-023-T014D — Manual Local spaCy Validation

## Result

PASS-WITH-BLOCKED-RUNTIME.

## Task

Manual/local validation of the T014C live spaCy adapter against the real local runtime environment.

## Manual Validation Summary

### Real local spaCy package availability

**UNAVAILABLE.** The spaCy Python package is not installed in the repo virtualenv (`.venv-unsloth-clean/bin/python`), the secondary virtualenv (`.venv-unsloth/bin/python`), or the system Python 3 interpreter.

The exact probe command used:

```bash
.venv-unsloth-clean/bin/python - <<'PY'
import importlib.util
print("spacy_package_available:", importlib.util.find_spec("spacy") is not None)
PY
# Output: spacy_package_available: False
```

### Real selected spaCy model availability

**UNAVAILABLE** (because the spaCy package itself is not available). The default model `en_core_web_sm` could not be loaded.

The exact probe command used:

```bash
.venv-unsloth-clean/bin/python - <<'PY'
import os
model = os.environ.get("OMI_LIVE_SPACY_MODEL", "en_core_web_sm")
try:
    import spacy
    nlp = spacy.load(model)
    print("spacy_model_available=True")
except Exception as exc:
    print("spacy_model_available=False")
    print("spacy_model_name:", model)
    print("error:", type(exc).__name__, str(exc))
PY
# Output: spacy_model_available: False (spacy not available)
```

### Live adapter manual run

**NOT EXECUTED.** The live adapter manual run could not be attempted because spaCy is not available.

The command would have been:

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

### Candidate categories observed

None (live adapter was not run). Expected categories if available: characters (Mara Vale, Jonah Cross), locations (Vancouver observatory, Blackwater Pier, North Gate Station), organizations (Meridian Society), objects (brass compass, missing ship), timeline/events (fire at North Gate Station).

## Owner Action Required

To enable real local spaCy validation, the owner should run:

```bash
# Activate the repo virtualenv
source .venv-unsloth-clean/bin/activate

# Install spaCy
pip install spacy

# Download the default small model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy available:', nlp.pipe_names)"
```

After installation, rerun the manual validation steps in this task.

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

## Confirmations

- No install/download of spaCy or spaCy models was performed.
- No backend logic was changed.
- No frontend files were changed.
- No package/dependency files were changed.
- No candidate persistence was invoked (live adapter was not run with `persist_candidates=False`).
- No Memory/Canon mutation occurred.
- No automatic promotion records were created.
- No automatic apply-promotion ran.
- Owner-approved apply-promotion remains a separate explicit workflow.
- No story prose was generated.
- Fixture/mock contracts remain scaffolding only, but this manual validation would be real-runtime evidence if spaCy/model were available.

## Deferred Work

- Live spaCy manual validation with real spaCy: deferred until spaCy and `en_core_web_sm` are installed.
- Re-run T014D after owner installs spaCy.

## Next Scope

`PHASE8-IMPL-023-T014E` — closeout for live spaCy integration, or T015 (live Ollama/local model integration) if spaCy remains unavailable.
