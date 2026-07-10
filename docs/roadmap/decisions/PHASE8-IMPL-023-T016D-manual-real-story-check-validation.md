# PHASE8-IMPL-023-T016D — Manual Real Story Check Validation

## Result

PASS for manual real Story Check validation through the OMI orchestrator
behind the T016C/T016C1 live flags.

T016D confirms that the T016C live `story_check` adapter bridges the
OMI orchestrator to the existing in-repo
`backend.analysis_engine.run_story_check(project_name, scene_id)`
callable surface, the live adapter correctly exercises the T016C1
strict no-sanitization boundary, the T008 `validate_story_check_fixture_envelope`
validator remains authoritative, and the orchestrator returns 14
evidence-backed candidate-only diagnostic findings with no Memory/Canon
mutation, no candidate persistence, no automatic promotion records,
no automatic apply-promotion, and no story prose.

T016D is the manual real Story Check validation for the T016C/T016C1
live adapter path. The T016C1 safety boundary (strict safety checker +
skip-on-unsafe policy) is exercised end-to-end against a real
`qwen3:8b` model response.

## Nature

- Manual/local runtime validation + docs/status task only (T016D).
- No backend/frontend/package/dependency/test code was edited.
- Builds on T016A (runtime surface inspection), T016B (preflight),
  T016C (live adapter behind flags), and T016C1 (tightened converter
  safety boundary).
- Does NOT call the legacy `POST /api/projects/{project_name}/story-check/{scene_id}`
  route. The orchestrator imports `backend.analysis_engine` lazily and
  calls `run_story_check(project_name, scene_id)` directly through the
  in-repo callable surface.
- Does NOT mutate Memory/Canon, does NOT create promotion records,
  does NOT run apply-promotion, does NOT persist candidates, and
  does NOT generate story prose.

## Validation Environment

- **Platform**: WSL (Ubuntu) -> Windows-hosted Ollama
- **Ollama version**: 0.31.2 (confirmed via `GET /api/version`)
- **Ollama base URL**: `http://172.25.144.1:11434` (WSL default gateway)
- **Target model**: `qwen3:8b` (confirmed available via `GET /api/tags`)
- **Project**: `projects/example` (existing in-repo example project)
- **Scene ID**: `scene_001` (only scene in the example project)
- **Scene text**: "The Princess and the Pea" by Hans Christian Andersen
  (public domain; owner-supplied scene fixture)

## Runtime Flags Used

```bash
OMI_LIVE_TOOLS_ENABLED=1
OMI_LIVE_STORY_CHECK_ENABLED=1
OMI_LIVE_STORY_CHECK_SCENE_ID=scene_001
OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434
OMI_LIVE_OLLAMA_MODEL=qwen3:8b
OLLAMA_BASE_URL=http://172.25.144.1:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT_SECONDS=600
ANALYSIS_MODE=ollama_baseline
```

T016D uses `OLLAMA_TIMEOUT_SECONDS=600` (vs. the default 300) to give
the full `analysis_engine.run_story_check` prompt — which includes
`storyform_context`, `scene_text`, and `bible_summary` — enough time
to complete on the owner's hardware. With the default 300s timeout
the call timed out and the adapter correctly failed closed. The
`_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS` env var (T015F) is separate from
`OLLAMA_TIMEOUT_SECONDS` (the in-repo `analysis_engine.run_story_check`
timeout). The latter is the env var the analysis engine reads.

## Validation Steps

### 1. Git State (preflight)

Branch: `docs/opencode-go-routing-small-task-execution`

Pre-existing modifications (unrelated to T016D) in
`artifacts/mvp-readiness/owner-acceptance/`. Untracked decision records
and zips. No staged or committed changes were made during T016D.

### 2. `python3 -m py_compile`

```
python3 -m py_compile backend/omi_analysis_orchestrator.py \
                       backend/omi_runtime_preflight.py \
                       backend/main.py \
                       backend/analysis_engine.py
```

Exit `0`. `py_compile OK`.

### 3. Ollama HTTP API Reachability (from WSL)

- `GET /api/version` -> `{"version":"0.31.2"}` (REACHABLE)
- `GET /api/tags` -> model list returned; `qwen3:8b` confirmed available
  with `completion`, `tools`, and `thinking` capabilities
  (digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`,
  8.2B parameters, Q4_K_M, 40960 context length)

### 4. Project + Scene Inspection

```
projects/example/bible.json
projects/example/omi/candidates/candidate_2853700065e84f069accc318d9af7f10.json
projects/example/omi/candidates/candidate_7b6057b42a31479dbf4d62f59bfa3511.json
projects/example/omi/ideas/idea_fd419d72decc4313af6ab95eb1a6d5ea.json
projects/example/omi/index.json
projects/example/project.json
projects/example/scenes/scene_001.md
projects/example/storyform.json
```

Only scene ID in the project: `scene_001` ("The Princess and the Pea").

### 5. Automated Tests

```
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_story_check_adapter_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
```

Combined result: `114 passed, 1 warning` (the warning is the
pre-existing NVML/CUDA init warning from the spacy import path, which
is unrelated to T016D).

### 6. Live Adapter Manual Run (default `OLLAMA_TIMEOUT_SECONDS=180`)

First manual run attempted with `OLLAMA_TIMEOUT_SECONDS=180`:

```
adapter_results[0].adapter: "story_check"
adapter_results[0].state: "error"
adapter_results[0].candidates: []
adapter_results[0].explanation: "Live Story Check adapter bridged the
  OMI orchestrator to backend.analysis_engine.run_story_check and
  converted the legacy result into the existing
  omi_story_check_diagnostic_handoff.v1 envelope shape. The T008
  fixture validator remains authoritative. Legacy Story Check returned
  an error shape: HTTPConnectionPool(host='172.25.144.1', port=11434):
  Read timed out. (read timeout=180.0). Failing closed with no findings."
analysis_status: "fail_closed"
findings: []
```

The live path was exercised. The bridge reached
`analysis_engine.run_story_check`. The model took longer than 180s
to complete on the owner's hardware. The converter failed closed
with no findings, no persistence, no Memory/Canon mutation, no
promotion records, no apply-promotion, and no story prose. This is
**PASS-SAFE-FAIL-CLOSED** for the 180s timeout.

### 7. Direct `run_story_check` Smoke Test (`OLLAMA_TIMEOUT_SECONDS=600`)

To confirm `analysis_engine.run_story_check` can complete on the
owner's hardware, a direct call was run with `OLLAMA_TIMEOUT_SECONDS=600`:

```python
from backend.analysis_engine import run_story_check
result = run_story_check("example", "scene_001")
# elapsed: 324.63 s
```

The function returned a valid rich-Story-Check dict (no `error` key)
with `task: "story_check"`, `coherence_score: 7`, plus structured
`warnings`, `suggestions`, `insufficient_evidence`, `throughline_alignment`,
`theme_drift`, and `character_consistency` blocks. The model response
was structurally valid and parseable.

### 8. Live Adapter Manual Run (`OLLAMA_TIMEOUT_SECONDS=600`)

The OMI orchestrator was run with the bumped timeout:

```bash
OMI_LIVE_TOOLS_ENABLED=1 \
OMI_LIVE_STORY_CHECK_ENABLED=1 \
OMI_LIVE_STORY_CHECK_SCENE_ID=scene_001 \
OMI_LIVE_OLLAMA_BASE_URL=http://172.25.144.1:11434 \
OMI_LIVE_OLLAMA_MODEL=qwen3:8b \
OLLAMA_BASE_URL=http://172.25.144.1:11434 \
OLLAMA_MODEL=qwen3:8b \
OLLAMA_TIMEOUT_SECONDS=600 \
ANALYSIS_MODE=ollama_baseline \
.venv-unsloth-clean/bin/python - <<'PY'
import json
from backend.omi_analysis_orchestrator import analyze_omi_raw_idea_with_tools

result = analyze_omi_raw_idea_with_tools(
    project_name="example",
    raw_idea=(
        "Manual T016D Story Check validation. "
        "Use the selected owner-authored scene as the evidence source. "
        "Return only candidate diagnostic findings if Story Check output is safe."
    ),
    requested_adapters=["story_check"],
    persist_candidates=False,
    story_check_scene_id="scene_001",
)

print(json.dumps(result, indent=2, sort_keys=True))
PY
```

Result:

```json
{
  "adapter_results": [
    {
      "adapter": "story_check",
      "state": "succeeded",
      "candidates": [<14 T008-shaped candidate findings>],
      "explanation": "Live Story Check adapter bridged the OMI
        orchestrator to backend.analysis_engine.run_story_check and
        converted the legacy result into the existing
        omi_story_check_diagnostic_handoff.v1 envelope shape. The T008
        fixture validator remains authoritative."
    }
  ],
  "analysis_status": "succeeded",
  "findings": [<14 evidence-backed candidate findings>],
  "fusion_summary": {
    "adapters_contributing_findings": ["story_check"],
    "conflict_group_count": 3,
    "total_input_findings": 14,
    "total_output_findings": 14,
    "uncertain_finding_count": 14
  },
  "new_candidate_ids": [],
  "persisted_candidate_ids": [],
  "persistence_explanation": "persist_candidates=False; fused findings
    were returned without candidate persistence.",
  "persistence_status": "not_requested",
  "reused_candidate_ids": [],
  "safety": {
    "candidate_presence_is_not_canon": true,
    "no_apply_promotion": true,
    "no_canon_promotion": true,
    "no_memory_canon_mutation": true,
    "no_package_installs": true,
    "no_prose": true,
    "no_real_tool_calls": true,
    "no_story_prose_generation": true,
    "queue_presence_is_not_approval": true,
    "support_is_not_truth": true,
    "tool_output_is_not_canon": true
  }
}
```

`analysis_status: "succeeded"`,
`adapter_results[0].state: "succeeded"`,
14 T008-validated candidate findings produced,
`persistence_status: "not_requested"`,
`new_candidate_ids: []`, `persisted_candidate_ids: []`, `reused_candidate_ids: []`.

All 11 safety envelope flags returned `true`.

### 9. `analysis_engine.run_story_check` Reachability Confirmation

Confirmed at `backend/omi_analysis_orchestrator.py:5443-5475` (T016C
implementation):

```python
try:
    from backend import analysis_engine  # lazy import
    run_story_check = getattr(analysis_engine, "run_story_check", None)
    if not callable(run_story_check):
        ...
try:
    legacy_result = run_story_check(
        project_name.strip(), scene_id
    )
```

The live path imports `backend.analysis_engine` lazily and calls
`run_story_check(project_name, scene_id)` directly. The live adapter
did reach the function on both the 180s and 600s runs (the 180s run
failed inside the function due to timeout; the 600s run completed
inside the function and returned a valid rich-Story-Check dict).

### 10. Legacy Route Avoidance Confirmation

The T016C live adapter does NOT call the legacy
`POST /api/projects/{project_name}/story-check/{scene_id}` route at
`backend/main.py:327-332`. The T016C live runner reaches
`backend.analysis_engine.run_story_check` directly through Python
import (lazy, behind env flags). The legacy route remains bypassed
during T016D. No HTTP server was started, no requests were sent to
the FastAPI server, and the in-process function call is the only path
exercised.

### 11. T016C1 Safety Boundary Exercise

The T016C1 strict safety checker was exercised against the real
`qwen3:8b` model response. The model's structured `suggestions`
field was entirely filtered out — none of the model's suggestion
items made it into the candidate findings. The model's structured
`warnings` and `insufficient_evidence` fields were partially
filtered (1 warning item and 1 insufficient_evidence item dropped
as unsafe per the T016C1 `_story_check_legacy_text_is_safe`
classifier), and the remaining 4+4+4+1+1 = 14 safe items were
converted into T008-shaped findings.

The unsafe text classification reused the same T008 forbidden
patterns (`_OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE`,
`_OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE`,
`_OMI_STORY_CHECK_FINAL_TRUTH_LABEL_RE`, `is_truth_label`, and
`is_prose_like_text`) — the exact same patterns the authoritative
T008 `validate_story_check_fixture_envelope` validator uses. The
T008 validator accepted the converted envelope with no rewrites or
sanitization of the AI/tool/model output.

Converter-owned labels are all generic (no legacy text in labels):

- `Story Check warning` (4)
- `Story Check insufficient evidence` (4)
- `Story Check throughline diagnostic` (4)
- `Story Check storyform diagnostic` (1)
- `Story Check character consistency diagnostic` (1)

Candidate categories observed (`candidate_type`):

- `structural_diagnostic` (4)
- `evidence_note` (4)
- `throughline_context` (4)
- `storyform_context` (1)
- `continuity_warning` (1)

### 12. `persist_candidates=False` Honored

`persistence_status: "not_requested"`,
`new_candidate_ids: []`, `persisted_candidate_ids: []`,
`reused_candidate_ids: []`. `persistence_explanation: "persist_candidates=False;
fused findings were returned without candidate persistence."`. No
candidate files were written to `projects/example/omi/candidates/`
during T016D; the directory's two pre-existing candidate files
(`candidate_2853700065e84f069accc318d9af7f10.json` and
`candidate_7b6057b42a31479dbf4d62f59bfa3511.json`) were not
modified, and no new candidate files appeared. The `find
projects/example -newer` check returned no results.

### 13. No Memory/Canon Mutation

The orchestrator's safety envelope reports
`no_memory_canon_mutation: true`. `projects/example/bible.json`,
`projects/example/project.json`, and `projects/example/storyform.json`
were not modified during T016D. `find projects/example -newer
/tmp/t016d/result1.json` returned no results.

### 14. No Automatic Promotion Records / No Apply-Promotion

The orchestrator's safety envelope reports `no_apply_promotion: true`
and `no_canon_promotion: true`. No `promotion_record` JSON files
were created under `projects/example/`. No apply-promotion function
was invoked. The strict owner-controlled apply-promotion workflow
remains a separate explicit workflow and was not exercised.

### 15. No Story Prose

The orchestrator's safety envelope reports `no_story_prose_generation: true`
and `no_prose: true`. None of the 14 candidate findings contain
story-prose text; all 14 are short diagnostic-support claims with
project-scoped `source_locator: "project:example::scene:scene_001"`,
support-only `provenance.support: "Story Check diagnostic support only"`,
pending `owner_decision: {approved: false, decision: "pending"}`,
and `review_status: "candidate_review_pending"`. The findings are
candidate-only, evidence-backed, and support-only — not story
content, not canon, not truth.

## Manual Validation Summary

| Aspect | Result |
|---|---|
| Ollama reachable | YES (HTTP 200, `0.31.2`) |
| `qwen3:8b` available | YES (via `/api/tags`) |
| Project/scene used | `example` / `scene_001` |
| Live adapter reached | YES (`analysis_engine.run_story_check` was called) |
| Legacy route called | NO (lazy Python import only; no FastAPI server) |
| `analysis_engine.run_story_check` reached | YES (returned valid rich-Story-Check dict on the 600s run) |
| T008 validator accepted converted envelope | YES (14 findings produced; status `succeeded`) |
| T016C1 safety boundary exercised | YES (unsafe items were skipped, not rewritten) |
| `persist_candidates=False` honored | YES (`not_requested`, empty candidate ID lists) |
| No Memory/Canon mutation | YES |
| No automatic promotion records | YES |
| No automatic apply-promotion | YES |
| No story prose | YES |

## Candidate Findings Detail

14 T008-validated candidate findings were produced, broken down by
label and candidate_type:

- 4 `Story Check warning` (structural_diagnostic) — `[Factual]`/`[Stylistic]`
  model warnings about scene coverage, fairy-tale style, public-domain
  fixture, etc.
- 4 `Story Check insufficient evidence` (evidence_note) — model notes
  about missing Dramatica Main Character, Influence Character, marriage
  outcome / Relationship Story proof, and unresolved dynamics.
- 4 `Story Check throughline diagnostic` (throughline_context) — throughline
  alignment items for `overall_story`, `main_character`,
  `influence_character`, `relationship_story` (each with `present` and
  `concerns` counts).
- 1 `Story Check storyform diagnostic` (storyform_context) — theme drift
  with `status='insufficient_evidence'` and a safe `reason` excerpt.
- 1 `Story Check character consistency diagnostic` (continuity_warning) —
  character consistency with `status='insufficient_evidence'` and a safe
  `reason` excerpt.

All 14 carry:

- `source_adapter: "story_check"`
- `provenance.tool_source: "story_check"`,
  `provenance.adapter: "story_check"`,
  `provenance.support: "Story Check diagnostic support only"`
- `support_label: "Story Check diagnostic support only"`
- `confidence: "Story Check diagnostic support only"` (a confidence
  *label*, not a numeric truth value)
- `owner_decision: {approved: false, decision: "pending"}`
- `review_status: "candidate_review_pending"`
- `source_locator: "project:example::scene:scene_001"`
- `evidence[].source_locator: "project:example::scene:scene_001"`
- `candidate_fingerprint: "omi-cand-..."` (12-hex-char stable fingerprint)
- `raw_finding_id: "story_check_live::Story Check warning::project:example::scene:scene_001"`
  (or the analogous label)

The T008 `validate_story_check_fixture_envelope` validator accepted
the converted envelope. The per-finding no-prose, no-truth-label,
no-forbidden-field-name, support-only, evidence/provenance/source-locator
guards all passed.

## Files Touched by T016D

None. T016D is manual/local runtime validation + docs/status only.
No backend, frontend, test, package, dependency, fixture, prompt,
or runtime-config file was edited during T016D. No git index
operation (add/commit/push) was performed.

## Files Created by T016D (docs/status only)

- `docs/roadmap/decisions/PHASE8-IMPL-023-T016D-manual-real-story-check-validation.md` — this decision record.
- `docs/roadmap/decision_log.md` — appended T016D decision entry.
- `docs/roadmap/implementation_status.md` — updated active frontier
  (latest child) and appended a T016D result line.
- `docs/roadmap/task_backlog.md` — updated latest completed backlog
  item, appended a T016D result line, refined the T016D planned line
  in the corrected next sequence.
- `docs/roadmap/phase_map.md` — updated latest completed phase-map
  item, appended a T016D result line, refined the T016D planned line
  in the corrected next sequence.
- `docs/roadmap/open_questions.md` — refined Q112 with the T016D
  manual validation evidence and the recommended next step.
- `docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json` — added
  T016D child entry; updated `latest_child_task`,
  `latest_decision_record`, `next_child_task`, and `next_child_status`.

`docs/roadmap/risk_register.md` is unchanged (no new risk; T016D
confirms the live path works as designed with strict safety guards).

## Validation Commands Re-Run

```
git status --short --branch   # unchanged pre-existing modifications only
git diff --stat               # pre-existing 3 files in owner-acceptance only
git diff --check              # clean
python3 -m py_compile backend/omi_analysis_orchestrator.py \
                       backend/omi_runtime_preflight.py \
                       backend/main.py \
                       backend/analysis_engine.py
                              # exit 0
.venv-unsloth-clean/bin/python -m pytest \
  tests/test_omi_story_check_adapter_contract.py \
  tests/test_omi_tool_assisted_orchestrator_contract.py \
  tests/test_omi_tool_assisted_persistence_contract.py \
  tests/test_omi_live_runtime_preflight_contract.py -q
                              # 114 passed, 1 warning (NVML init, unrelated)
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json \
  > /tmp/phase8-impl-023-enrichment.json.ok
                              # exit 0; valid JSON
```

## Confirmation Statements

- T016D was a manual real Story Check validation only; no code was
  edited.
- Live adapter reached `backend.analysis_engine.run_story_check`
  through the OMI orchestrator's `_build_story_check_live_runner`
  (T016C implementation).
- The live adapter did NOT call the legacy
  `POST /api/projects/{project_name}/story-check/{scene_id}` route.
- 14 T008-validated candidate-only diagnostic findings were
  produced (status `succeeded`); all are evidence-backed with
  `source_excerpt` and `source_locator: "project:example::scene:scene_001"`.
- T016C1 safety boundary was exercised end-to-end against the real
  `qwen3:8b` model response: unsafe items in the legacy
  `suggestions` field were entirely filtered, and unsafe items in
  the legacy `warnings` and `insufficient_evidence` fields were
  partially filtered. The converter did NOT rewrite or sanitize
  AI/tool/model output; unsafe items were SKIPPED, not converted
  into a safe phrase.
- The T008 `validate_story_check_fixture_envelope` validator
  remains authoritative. T008 accepted the converted envelope.
- `persist_candidates=False` was honored; no candidate files were
  created; `persistence_status: "not_requested"`,
  `new_candidate_ids: []`, `persisted_candidate_ids: []`,
  `reused_candidate_ids: []`.
- No Memory/Canon mutation. No automatic promotion records. No
  automatic apply-promotion. No story prose. All 11 safety envelope
  flags returned `true`.
- No frontend/package/dependency files were touched.
- No git add/commit/push was performed.

## Recommended Next Task

- **T017**: Live BookNLP integration in OMI and analysis. The next
  selected tool in the corrected sequence. T014 (live spaCy) and
  T015 (live Ollama/local model) and T016 (live Story Check; T016A
  inspect/docs, T016B preflight, T016C live adapter, T016C1 safety
  repair, T016D manual validation) are all complete/PASS. T017 is
  the next blocker on the path to MVP closeout; the BookNLP runtime
  is NOT installed on the owner's hardware, so the first T017 child
  will be the runtime availability check (T017A inspect/docs or
  T017B preflight).
