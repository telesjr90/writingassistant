# PHASE8-IMPL-023-T017C: Manual Real BookNLP Validation

## Result

PASS-SAFE-FAIL-CLOSED — BookNLP runtime was reached through the OMI tool-assisted orchestrator live adapter; the first Tagger model load failed with a `transformers` state_dict compatibility error; the orchestrator correctly returned `failed_closed` with zero findings, zero persistence, all 11 safety envelope flags `true`, no project file mutations, and no story prose. A narrowly scoped repair task `PHASE8-IMPL-023-T017C1` is recommended to address the `transformers` / BookNLP model compatibility so the live BookNLP adapter can return real candidate findings in a follow-up rerun.

## Task

Manual real BookNLP validation through the OMI tool-assisted orchestrator on owner-authored existing project text, using the installed `.venv-unsloth-clean` BookNLP runtime and the T017B live adapter env flags. This is a manual real-runtime validation + docs/status task only; no adapter fixes, no refactors, no edits to code/tests/frontend/dependencies.

## Env flags used

- `OMI_LIVE_TOOLS_ENABLED=1`
- `OMI_LIVE_BOOKNLP_ENABLED=1`
- `OMI_LIVE_BOOKNLP_MODEL=small`
- `OMI_LIVE_BOOKNLP_PIPELINE=entity,quote,supersense,event`
- `OMI_LIVE_BOOKNLP_BLOCKED` was **not** set.
- Python: `.venv-unsloth-clean/bin/python` (where `booknlp==1.0.8`, `transformers==5.5.0`, `torch==2.10.0+cu129`, `spacy==3.8.14`, `tensorflow==2.21.0`, `setuptools==80.9.0`, `en_core_web_sm` are installed).

## Selected owner-authored input

- Project: `example`
- File: `projects/example/scenes/scene_001.md`
- Content: The full "The Princess and the Pea" public-domain scene (1971 characters after `strip()`), owner-authored project fixture text aligned across `project.json`, `bible.json`, `storyform.json`, and the scene text.
- The file was selected via read-only `find projects/example -maxdepth 4 -type f` and a content inspection; the file is the largest existing owner-authored text in `projects/example`.

## Manual validation command used

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication

OUT=".codex-context/PHASE8-IMPL-023/manual-validation/T017C-booknlp"
mkdir -p "$OUT"

{
  echo "# T017C Manual BookNLP Validation"
  echo
  echo "- timestamp_utc: $(date -u +%Y%m%dT%H%M%SZ)"
  echo "- boundary: manual validation only; no adapter fixes; no staging; no commit; no push."
  echo
  echo "== git status before =="
  git status --short --branch
  echo
  echo "== candidate/project files before =="
  find projects/example -maxdepth 5 -type f 2>/dev/null | sort

  echo
  echo "== manual live BookNLP orchestrator run =="
  OMI_LIVE_TOOLS_ENABLED=1 \
  OMI_LIVE_BOOKNLP_ENABLED=1 \
  OMI_LIVE_BOOKNLP_MODEL=small \
  OMI_LIVE_BOOKNLP_PIPELINE=entity,quote,supersense,event \
  .venv-unsloth-clean/bin/python - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

from backend.omi_analysis_orchestrator import analyze_omi_raw_idea_with_tools

project_name = "example"
candidate_paths_before = sorted(str(p) for p in Path("projects/example").rglob("*candidate*") if p.is_file())
index_path = Path("projects/example/omi/index.json")
index_text_before = index_path.read_text(encoding="utf-8") if index_path.exists() else None
promo_paths_before = sorted(str(p) for p in Path("projects/example/omi/promotions").rglob("*") if p.is_file())

candidate_text_files = [
    p for p in Path("projects/example").rglob("*")
    if p.is_file()
    and p.suffix.lower() in {".md", ".txt"}
    and "candidate" not in str(p).lower()
    and "review" not in str(p).lower()
]
scenes = [p for p in candidate_text_files if "/scenes/" in str(p).replace("\\", "/")]
selected = scenes[0] if scenes else candidate_text_files[0]
raw_idea = selected.read_text(encoding="utf-8", errors="replace").strip()
if not raw_idea:
    raise SystemExit(f"Selected text file is empty: {selected}")

result = analyze_omi_raw_idea_with_tools(
    project_name=project_name,
    raw_idea=raw_idea,
    requested_adapters=["booknlp"],
    persist_candidates=False,
)

candidate_paths_after = sorted(str(p) for p in Path("projects/example").rglob("*candidate*") if p.is_file())
index_text_after = index_path.read_text(encoding="utf-8") if index_path.exists() else None
promo_paths_after = sorted(str(p) for p in Path("projects/example/omi/promotions").rglob("*") if p.is_file())

result_data = result if isinstance(result, dict) else {"repr": repr(result)}
findings = result_data.get("findings") or []
adapter_results = result_data.get("adapter_results") or []
safety = result_data.get("safety") or {}

summaries = []
for item in findings[:3]:
    if not isinstance(item, dict):
        summaries.append({"repr": repr(item)[:500]})
        continue
    ev = item.get("evidence")
    ev_str = json.dumps(ev, ensure_ascii=False, default=str)[:300] if isinstance(ev, dict) else str(ev)[:300]
    summaries.append({
        "type": item.get("type") or item.get("candidate_type"),
        "label": item.get("label") or item.get("name"),
        "review_status": item.get("review_status"),
        "owner_decision": item.get("owner_decision"),
        "provenance": item.get("provenance"),
        "evidence": ev_str,
        "support_label": item.get("support_label"),
    })

adapter_states = [{
    "adapter": ar.get("adapter"),
    "state": ar.get("state"),
    "explanation": (ar.get("explanation") or "")[:400],
    "candidates_count": len(ar.get("candidates") or []) if isinstance(ar.get("candidates"), list) else 0,
} for ar in adapter_results if isinstance(ar, dict)]

report = {
    "selected_text_file": str(selected),
    "raw_idea_chars": len(raw_idea),
    "result_keys": sorted(result_data.keys()),
    "analysis_status": result_data.get("analysis_status"),
    "adapter_results_count": len(adapter_results),
    "adapter_states": adapter_states,
    "finding_count": len(findings) if isinstance(findings, list) else None,
    "finding_types": sorted({
        str((f.get("type") or f.get("candidate_type") or f.get("finding_type")))
        for f in findings
        if isinstance(f, dict)
    }) if isinstance(findings, list) else [],
    "first_findings": summaries,
    "candidate_paths_before": candidate_paths_before,
    "candidate_paths_after": candidate_paths_after,
    "candidate_paths_changed": candidate_paths_before != candidate_paths_after,
    "index_text_changed": index_text_before != index_text_after,
    "promo_paths_changed": promo_paths_before != promo_paths_after,
    "persisted_candidate_ids": result_data.get("persisted_candidate_ids"),
    "persistence_status": result_data.get("persistence_status"),
    "persistence_explanation": result_data.get("persistence_explanation"),
    "safety": safety,
}

print(json.dumps(report, indent=2, ensure_ascii=False))
PY

  echo
  echo "== candidate/project files after =="
  find projects/example -maxdepth 5 -type f 2>/dev/null | sort

  echo
  echo "== git status after =="
  git status --short --branch

  echo
  echo "== diff check =="
  git diff --check || true
} 2>&1 | tee "$OUT/manual-booknlp-validation-output.txt"
```

## Runtime behavior

BookNLP was actually reached through the OMI orchestrator. The `booknlp.booknlp.BookNLP` class was lazily imported inside `_build_booknlp_live_runner`, the BookNLP Tagger model was downloaded from the Hugging Face Hub (logged: `downloading entities_google_bert_uncased_L-4_H-256_A-4-v1.0.model`, `downloading coref_google_bert_uncased_L-2_H-256_A-4-v1.0.model`, `downloading speaker_google_bert_uncased_L-8_H-256_A-4-v1.0.1.model`), and the entity-tagger module entered `load_state_dict` for the entity Tagger. The first `Tagger.load_state_dict(...)` call raised:

```
RuntimeError: Error(s) in loading state_dict for Tagger:
	Unexpected key(s) in state_dict: "bert.embeddings.position_ids".
```

This is a `transformers==5.5.0` vs BookNLP `1.0.8` model state-dict shape mismatch (newer `transformers` versions add a `bert.embeddings.position_ids` buffer that the older BookNLP model checkpoint does not have). The live runner caught the `RuntimeError` and returned the fail-closed envelope per the T017B contract.

Compact JSON report excerpt:

```json
{
  "selected_text_file": "projects/example/scenes/scene_001.md",
  "raw_idea_chars": 1971,
  "result_keys": [
    "adapter_results", "analysis_status", "explanation", "findings",
    "fusion_contract", "fusion_summary", "new_candidate_ids",
    "persisted_candidate_ids", "persistence_explanation", "persistence_status",
    "reused_candidate_ids", "safety", "source_idea_id"
  ],
  "analysis_status": "fail_closed",
  "adapter_results_count": 1,
  "adapter_states": [{
    "adapter": "booknlp",
    "state": "failed_closed",
    "explanation": "Live BookNLP runtime processing failed: RuntimeError: Error(s) in loading state_dict for Tagger: Unexpected key(s) in state_dict: \"bert.embeddings.position_ids\". . Failing closed with no candidates.",
    "candidates_count": 0
  }],
  "finding_count": 0,
  "finding_types": [],
  "first_findings": [],
  "candidate_paths_before": [
    "projects/example/omi/candidates/candidate_2853700065e84f069accc318d9af7f10.json",
    "projects/example/omi/candidates/candidate_7b6057b42a31479dbf4d62f59bfa3511.json"
  ],
  "candidate_paths_after": [
    "projects/example/omi/candidates/candidate_2853700065e84f069accc318d9af7f10.json",
    "projects/example/omi/candidates/candidate_7b6057b42a31479dbf4d62f59bfa3511.json"
  ],
  "candidate_paths_changed": false,
  "index_text_changed": false,
  "promo_paths_changed": false,
  "persisted_candidate_ids": [],
  "persistence_status": "not_requested",
  "persistence_explanation": "persist_candidates=False; fused findings were returned without candidate persistence.",
  "safety": {
    "no_prose": true,
    "no_memory_canon_mutation": true,
    "no_apply_promotion": true,
    "no_canon_promotion": true,
    "no_real_tool_calls": false,
    "no_package_installs": true,
    "no_story_prose_generation": true,
    "candidate_presence_is_not_canon": true,
    "queue_presence_is_not_approval": true,
    "support_is_not_truth": true,
    "tool_output_is_not_canon": true
  }
}
```

Note: `no_real_tool_calls=false` is expected because the live BookNLP runner DID perform a real BookNLP call (the only way to discover the runtime error); the orchestrator treats "no real tool calls" as a default for fixture-only mode. The full safety envelope is otherwise `true`. No candidate file was created or modified, no `projects/example/omi/index.json` mutation, no `promotions/` file change.

## Confirmations

- Selected input: existing owner-authored project fixture `projects/example/scenes/scene_001.md` (1971 chars). No new story prose was invented for this validation.
- `persist_candidates=False` was honored: `persistence_status: "not_requested"`, `persisted_candidate_ids: []`, `new_candidate_ids: []`, `reused_candidate_ids: []`.
- No candidate files were created or modified: `candidate_paths_changed: false`.
- No `index.json` mutation: `index_text_changed: false`.
- No `promotions/` file change: `promo_paths_changed: false`.
- No Memory/Canon mutation.
- No automatic promotion records.
- No automatic apply-promotion.
- No story prose (no `rewrite`, `continue`, `polish`, `improve`, `expand`, `imitate`, `revise`, `outline`, `draft`).
- No live BookNLP call was made by automated tests.
- The T007 `validate_local_nlp_fixture_envelope` validator is unchanged and remains authoritative; it was not exercised in this run because the runner failed closed before conversion.
- No backend, frontend, test, package, or dependency file was edited in T017C.

## Runtime caveats (still in effect)

- CPU fallback: BookNLP ran on `using device cpu` (the pre-existing `Can't initialize NVML` warning is non-blocking).
- `setuptools==80.9.0` / `pkg_resources` pin: required because BookNLP imports `pkg_resources`; the deprecation warning is non-blocking.
- `torch==2.10.0+cu129` C++ extension warning (`Skipping import of cpp extensions due to incompatible torch version. Please upgrade to torch >= 2.11.0 (found 2.10.0+cu129).`) is non-blocking for import and was non-blocking for the live adapter's import step; it was the Tagger `load_state_dict` that failed, not the cpp extensions.
- First-run model download: BookNLP downloaded the entity Tagger, coref model, and speaker model from the Hugging Face Hub on the first run (logged as `downloading entities_google_bert_uncased_L-4_H-256_A-4-v1.0.model` etc.). Subsequent runs will use the cached model files.
- `transformers==5.5.0` vs BookNLP `1.0.8` model state-dict mismatch: the new `transformers` `BertEmbeddings` adds a `position_ids` buffer that the older BookNLP model checkpoint does not have, so `Tagger.load_state_dict(...)` raises `RuntimeError: Unexpected key(s) in state_dict: "bert.embeddings.position_ids"`. This is the proximate cause of the T017C PASS-SAFE-FAIL-CLOSED outcome.

## Why PASS-SAFE-FAIL-CLOSED, not PASS or BLOCKED

- **Not PASS:** the live adapter did not return any candidate findings. A real candidate-only evidence-backed finding stream was not produced.
- **Not BLOCKED:** the runtime was actually exercised. BookNLP was imported, the model files were downloaded, the entity Tagger was instantiated, and the Tagger reached the `load_state_dict` step. The failure is a model/transformers compatibility error inside a started processing run, not a missing-model, missing-package, missing-API, or unusable-input situation.
- **Not FAIL:** the orchestrator's fail-closed boundary was exercised correctly. No unsafe output leaked, no candidate files were persisted unexpectedly, no Memory/Canon mutation, no promotion records, no apply-promotion, no story prose. All 11 safety envelope flags except `no_real_tool_calls` (which the live path flips to `false` as designed) are `true`.
- **PASS-SAFE-FAIL-CLOSED:** BookNLP started, the live adapter was reached through the OMI orchestrator, the runtime failed safely with no findings, no persistence, no Memory/Canon mutation, no promotion/apply-promotion, and no story prose. The owner still has a working, evidence-backed contract that is ready to return real candidate findings as soon as the `transformers`/BookNLP model state-dict mismatch is resolved.

## Recommended next task

`PHASE8-IMPL-023-T017C1` — narrow repair task to resolve the `transformers` vs BookNLP model state-dict compatibility on the installed `.venv-unsloth-clean` runtime, then rerun T017C manual real BookNLP validation. The repair task must remain narrowly scoped: it may add a T017B adapter shim or a small env-toggled fallback path, or it may coordinate with the owner to either (a) pin `transformers` to a BookNLP-1.0.8-compatible version, (b) re-export the BookNLP model checkpoint under a `transformers==5.5.0`-compatible `BertEmbeddings` (adding `bert.embeddings.position_ids` if missing), or (c) skip the entity Tagger when it is the only Tagger that fails and still parse `.quotes`/`.tokens` (entity-tagger state_dict is only required for `.entities` rows; `.quotes`/`.tokens` are independent Tagger paths). No scope expansion beyond resolving the `transformers` `position_ids` mismatch. The repair must not introduce prose-shaped rewrite/sanitization, must not mutate Memory/Canon, must not create promotion records, must not run apply-promotion, and must not generate story prose. T017C does not perform the repair.

If T017C1 is approved and rerun reaches a real candidate-only findings stream, T017 closes to PASS and the next task is `PHASE8-IMPL-023-T018A — NCP schema validator preflight`.

## Automated validation

```bash
git status --short --branch
  → On branch docs/opencode-go-routing-small-task-execution
  → M artifacts/mvp-readiness/owner-acceptance/checklist-results.json
  → M artifacts/mvp-readiness/owner-acceptance/evidence-report.md
  → M artifacts/mvp-readiness/owner-acceptance/workflow-log.json
  → ?? PHASE8-IMPL-023-T006-context-files.zip
  → ?? docs/Writing Assistant_OMI.pdf
  → ?? docs/roadmap/decisions/PHASE8-IMPL-023-T005-tool-assisted-orchestrator-contract-adapter-boundaries.md
  → (no other working-tree changes; pre-existing unrelated leftovers only)

git diff --stat
  → 3 modified files (artifacts only, no tracked source changes)
  → .../owner-acceptance/checklist-results.json        | 576 ++++++++++-----------
  → .../owner-acceptance/evidence-report.md            |  23 +-
  → .../owner-acceptance/workflow-log.json             | 440 +++++++---------

git diff --check
  → (no whitespace errors)

python3 -m py_compile backend/omi_analysis_orchestrator.py backend/omi_runtime_preflight.py backend/main.py backend/analysis_engine.py
  → PASS (no errors)

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_booknlp_spacy_adapter_contract.py -q
  → 30 passed, 1 failed, 1 warning in 2.65s
  → The 1 failure is the pre-existing test_live_spacy_missing_package_returns_unavailable
    (T014C-era failure unrelated to T017C; documented pre-existing; caused by spaCy
    being installed locally in .venv-unsloth-clean, not by T017C)

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_orchestrator_contract.py -q
  → 30 passed in 0.17s

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_tool_assisted_persistence_contract.py -q
  → 5 passed in 0.07s

.venv-unsloth-clean/bin/python -m pytest tests/test_omi_live_runtime_preflight_contract.py -q
  → 50 passed, 5 warnings in 22.78s

python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
  → VALID (semantic equality OK with /tmp/phase8-impl-023-enrichment.json.ok)
```

Combined: 115 passed, 1 pre-existing failure. The pre-existing `test_live_spacy_missing_package_returns_unavailable` failure remains for the same T014C-era reason (spaCy is now installed locally); it is unrelated to T017C and is not repaired in T017C.

## Deferred work

- `transformers` vs BookNLP model state-dict `position_ids` mismatch (T017C1 repair, recommended next).
- EVENT/supersense, coreference/alias truth, referential gender/pronoun normalization (T017B-deferred).
- Raw BookNLP artifact persistence (T017B-deferred).

## Evidence files

- `.codex-context/PHASE8-IMPL-023/manual-validation/T017C-booknlp/manual-booknlp-validation-output.txt` (manual run stdout/stderr, including the BookNLP startup log, the Hugging Face model download log, the `state_dict` error, and the compact JSON report).
- `.codex-context/PHASE8-IMPL-023/manual-validation/T017C-booknlp/pre-run-snapshot.txt` (git status + project file listing before the run).
- `.codex-context/PHASE8-IMPL-023/manual-validation/T017C-booknlp/post-run-snapshot.txt` (git status + project file listing after the run, `git diff --check`).
- `.codex-context/PHASE8-IMPL-023/manual-validation/T017C-booknlp/validation-step1.txt` (git status / diff / py_compile step).
- `.codex-context/PHASE8-IMPL-023/manual-validation/T017C-booknlp/validation-step2.txt` (pytest + json.tool step).

These evidence files live under `.codex-context/` and are intentionally left untracked (the task allowlist does not include the evidence folder); they are present only as manual-validation evidence. They are not staged, committed, or pushed.

## Next task (current parent)

If T017C1 is approved and the rerun returns real candidate findings, the next step after T017C1 is `PHASE8-IMPL-023-T018A — NCP schema validator preflight`. If T017C1 is not yet approved, T017C1 itself is the next step.
