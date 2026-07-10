# PHASE8-IMPL-023-T017C1 BookNLP / transformers state-dict compatibility repair

## Result

PASS.

`PHASE8-IMPL-023-T017C1` is complete/PASS. The T017C1
BookNLP/transformers state-dict compatibility repair is in place, the
constructor smoke passes, and the real OMI live BookNLP MVP path now
runs end-to-end on owner-authored text and returns evidence-backed,
candidate-only findings.

No Memory/Canon mutation, no promotion record, no apply-promotion, no
canon promotion, no story prose generation, no package upgrade, no
dependency pin, no install, no `strict=False` broad workaround, no
patch to installed site-packages, no edit of `.external_sources/`, no
alteration to candidate schema, no project/candidate persistence
(`persist_candidates=False` honored), no staging, no commit, and no
push occurred.

## Background

The T017C manual real BookNLP validation failed closed at the entity
tagger constructor with:

```
RuntimeError: Error(s) in loading state_dict for Tagger:
    Unexpected key(s) in state_dict: "bert.embeddings.position_ids".
```

at
`booknlp/english/entity_tagger.py:22`
(`self.model.load_state_dict(torch.load(model_file, map_location=device))`).

Root cause: BookNLP 1.0.8 was written against a `transformers` version
in which `BertEmbeddings.position_ids` was a persistent buffer and
therefore part of the saved state_dict. The currently installed
`transformers==5.5.0` registers `position_ids` as a non-persistent
buffer in `BertEmbeddings`, so it is not part of the model's
`state_dict()`. The BookNLP checkpoint saves the key, the model does
not expect it, and `load_state_dict(strict=True)` (the default) raises
`RuntimeError: Unexpected key(s) in state_dict`. The other two model
loaders (`bert_qa.py:20`, `litbank_coref.py:19`) use the same pattern
and would exhibit the same failure.

## Installed runtime versions (before and after)

| package            | before T017C1 | after T017C1 |
| ------------------ | ------------- | ------------ |
| booknlp            | 1.0.8         | 1.0.8        |
| transformers       | 5.5.0         | 5.5.0        |
| torch              | 2.10.0+cu129  | 2.10.0+cu129 |
| tensorflow         | 2.21.0        | 2.21.0       |
| spacy              | 3.8.14        | 3.8.14       |
| setuptools         | 80.9.0        | 80.9.0       |
| huggingface-hub    | 1.16.1        | 1.16.1       |

No dependency change was applied. The T017C1 repair is a code-only,
narrow compatibility shim inside the live BookNLP runner.

## Selected repair path: narrow adapter-side state-dict shim

Three repair options were evaluated:

- **Option A — dependency pin:** `transformers==4.41.2` (or earlier)
  would downgrade `transformers` 5.5.0 → 4.41.2, `huggingface-hub`
  1.16.1 → 0.36.2, and `tokenizers` to 0.19.1. The installed `transformers`
  is Required-by `booknlp`, `peft`, `trl`, `unsloth`, and
  `unsloth_zoo`. Pinning to a 4.x line would force unsafe churn
  across the training stack (`unsloth` and `peft` are tightly
  coupled to the current 5.x line) and risks breaking the rest of
  the platform. A narrow venv-only pin is therefore unsafe.
- **Option B — narrow adapter-side state-dict shim:** wrap
  `torch.load` for the duration of the BookNLP constructor only,
  drop the single known-incompatible non-trainable key
  `bert.embeddings.position_ids`, and preserve `load_state_dict`
  `strict=True` so any other unexpected key still fails closed.
  This option is narrowly scoped to the live BookNLP runner,
  side-effect-free outside the constructor window, and fully covered
  by automated tests.
- **Option C — reduce pipeline:** dropping `entity` from the pipeline
  is documented as a fallback only, not a PASS path; the T017B
  parser still depends on `.entities`/`.quotes`/`.tokens` and the
  MVP adapter contract is entity-aware.

**Selected: Option B.**

## Code change (narrow shim, scoped to live BookNLP runner only)

Added to `backend/omi_analysis_orchestrator.py`:

- New module-level constant
  `_BOOKNLP_STATE_DICT_SHIM_TOLERATED_KEYS = frozenset({"bert.embeddings.position_ids"})`.
  This is the single key the shim is allowed to remove.
- New helper `_filter_state_dict_for_booknlp_compat(state_dict) ->
  (cleaned_state_dict, removed_keys_tuple)`. Pure function, no side
  effects, no `strict=False` flag manipulation. Returns the input
  unchanged (no copy) when nothing to filter, returns a shallow copy
  with the tolerated key removed otherwise. The
  `removed_keys_tuple` is the sorted tuple of keys actually removed
  from the input, used by the test suite to prove the shim did not
  touch other keys.
- New helpers
  `_booknlp_state_dict_shim_install()` /
  `_booknlp_state_dict_shim_uninstall(original_load, torch_module)`
  that install and restore a `torch.load` wrapper. The wrapper
  preserves the original `torch.load` callable's behavior and only
  filters the single tolerated key from returned state-dict-like
  dicts. Non-dict returns (e.g. raw tensors, primitives) pass through
  unchanged so wrapping `torch.load` remains safe even when BookNLP
  loads non-state-dict artifacts.
- New helper
  `_booknlp_construct_with_state_dict_shim(language, model_params)`
  that imports `booknlp.booknlp.BookNLP` lazily, installs the shim
  via `_booknlp_state_dict_shim_install()`, calls
  `BookNLP(language, model_params)`, and unconditionally restores
  the original `torch.load` in a `try/finally` block — even on
  construction failure.
- The live runner's `BookNLP("en", model_params)` call site is
  replaced with a call to
  `_booknlp_construct_with_state_dict_shim("en", model_params)`.
  The `booknlp_instance.process(input_path, output_dir, book_id)`
  call is unchanged (process() does not load models; it only runs
  inference, and the shim is no longer installed by that point).

The shim does NOT use `strict=False`. It does NOT ignore all
state-dict errors. It does NOT touch installed site-packages
(`.venv-unsloth-clean/.../site-packages/booknlp/...`). It does NOT
edit `.external_sources/booknlp`. It does NOT mutate Memory/Canon,
create promotion records, run apply-promotion, or generate story
prose.

The shim is restored even on construction failure, so a failure in
the BookNLP constructor cannot leave the global `torch.load`
wrapped.

## Constructor smoke

`oao._booknlp_construct_with_state_dict_shim("en",
{"pipeline": "entity,quote,supersense,event", "model": "small"})` now
succeeds end-to-end on the installed runtime:

```
BookNLP constructor OK (with shim): <booknlp.booknlp.BookNLP object at 0x...>
```

The bare `BookNLP("en", params)` constructor (without the shim) still
fails with the original `Unexpected key(s) in state_dict: ...`
RuntimeError, confirming the shim is the actual repair and not a
false positive.

## Real OMI live BookNLP validation

Manual re-validation was performed with the same owner-authored input
as T017C:

- input: `projects/example/scenes/scene_001.md`
- requested_adapters=["booknlp"]
- persist_candidates=False
- env:
  - `OMI_LIVE_TOOLS_ENABLED=1`
  - `OMI_LIVE_BOOKNLP_ENABLED=1`
  - `OMI_LIVE_BOOKNLP_MODEL=small`
  - `OMI_LIVE_BOOKNLP_PIPELINE=entity,quote,supersense,event`

Captured to
`.codex-context/PHASE8-IMPL-023/manual-validation/T017C1-booknlp-repair/manual-booknlp-repair-validation-output.txt`.

Results:

- `analysis_status == "succeeded"`
- `adapter_results[booknlp].state == "succeeded"`
- `finding_count == 26`
- `finding_types == ["character", "location"]`
- `persisted_candidate_ids == []`
- `candidate_paths_changed == false`
- `project_files_changed == false`
- safety envelope: `no_prose`, `no_memory_canon_mutation`,
  `no_apply_promotion`, `no_canon_promotion`,
  `no_story_prose_generation`, `no_real_tool_calls`,
  `no_package_installs` — all `true`
- every finding carries `source_adapter="booknlp"`,
  `provenance.tool_source="booknlp"`, `provenance.adapter="booknlp"`,
  `support`/`support_label="BookNLP live support only"`,
  `owner_decision.decision="pending"`, `owner_decision.approved=False`,
  `review_status="candidate_review_pending"`, and a
  `source_excerpt` + `source_locator` evidence pair
- `persist_candidates=False` honored: zero candidates persisted, zero
  project files changed, zero candidate paths added.

## Tests added/updated

`tests/test_omi_booknlp_spacy_adapter_contract.py` gains eight
T017C1-specific tests:

1. `test_state_dict_shim_drops_only_position_ids_key` — proves the
   shim drops only `bert.embeddings.position_ids` and preserves
   unrelated keys.
2. `test_state_dict_shim_does_not_tolerate_arbitrary_unexpected_keys`
   — proves the shim does NOT silently drop
   `bert.pooler.weight` or other unexpected keys; those remain in
   the state dict so `load_state_dict(strict=True)` still fails
   closed on them.
3. `test_state_dict_shim_passes_through_non_dict_inputs` — proves
   the shim does not crash on non-dict `torch.load` returns
   (e.g. raw tensors).
4. `test_state_dict_shim_passes_through_dict_without_tolerated_key`
   — proves the shim returns the same dict object (no unnecessary
   copy) when nothing to filter.
5. `test_state_dict_shim_install_uninstall_roundtrip` — proves
   `torch.load` is restored after the shim is uninstalled.
6. `test_state_dict_shim_filters_only_during_live_booknlp_constructor`
   — proves the shim is scoped to the BookNLP constructor: a
   `torch.load` call before or after the constructor sees the
   original behavior, only the constructor itself sees the wrapped
   load.
7. `test_live_booknlp_state_dict_shim_handles_position_ids_succeeds`
   — proves the constructor succeeds when `torch.load` returns
   `bert.embeddings.position_ids` in the state dict and the shim
   drops it.
8. `test_live_booknlp_state_dict_shim_preserves_strict_true_behavior`
   — proves the shim is NOT a broad `strict=False` workaround:
   arbitrary unexpected keys remain in the state dict and would
   (and do) trigger a `strict=True` failure in the inner Tagger.
9. `test_live_booknlp_state_dict_shim_safety_boundaries_preserved` —
   proves the shim does not affect the OMI safety envelope
   (no Memory/Canon mutation, no candidate persistence, no story
   prose).

Existing T017B mocked tests still pass. Existing orchestrator /
persistence / preflight regressions still pass. The only failing test
in the suite is the pre-existing
`test_live_spacy_missing_package_returns_unavailable`, which fails
because `spacy` is installed in the local venv and was documented as
a known pre-existing failure in T017C1's task brief. The shim does
not touch that test or that adapter.

## Caveats and remaining risks

- **CPU fallback is expected.** No GPU is available in this venv; the
  orchestrator reports `using device cpu`. The shim does not change
  this.
- **`setuptools==80.9.0` / `pkg_resources` is required.** BookNLP
  imports `pkg_resources`; `setuptools>=81` removes it. The current
  pin is intentionally preserved. The `pkg_resources is deprecated`
  UserWarning is non-blocking.
- **Torch C++ extension warning is non-blocking for import.** The
  installed `torch==2.10.0+cu129` triggers
  `Skipping import of cpp extensions due to incompatible torch
  version. Please upgrade to torch >= 2.11.0 (found 2.10.0+cu129).`
  This warning is non-blocking for BookNLP inference.
- **NVML warning is non-blocking.** `Can't initialize NVML` is
  reported because no NVIDIA driver is reachable from this venv; it
  does not affect BookNLP CPU inference.
- **Cached Hugging Face model files.** The shim does not download or
  cache any new models; BookNLP continues to use the existing
  `~/booknlp_models/entities_google_bert_uncased_L-4_H-256_A-4-v1.0.model`
  (and the matching coref / quote model files) plus the cached
  `bert-base-uncased` weights it already pulls from
  `~/.cache/huggingface/`.
- **Transformer pin risks are avoided.** Because Option B was
  selected over Option A, there is no risk of breaking the
  unsloth / peft / trl training stack by downgrading transformers.
- **Scope of the shim.** The shim removes only the single
  `bert.embeddings.position_ids` key. Any other unexpected key
  (e.g. `bert.pooler.weight`, `bert.encoder.layer.99.bias`) is
  preserved untouched and will fail closed at
  `load_state_dict(strict=True)`. If a future transformers upgrade
  introduces a new persistent buffer or key in `BertEmbeddings` and
  another BookNLP release still saves it in the state dict, the
  shim must be updated to tolerate that key as well — but it must
  still be added explicitly, never as a broad wildcard.

## No-prose / candidate-only / evidence-backed / provenance

- All 26 findings carry `source_excerpt` + `source_locator` evidence.
- All 26 findings carry `provenance.tool_source="booknlp"`,
  `provenance.adapter="booknlp"`, and
  `provenance.support="BookNLP live support only"`.
- All 26 findings carry
  `support_label="BookNLP live support only"` and never contain
  the forbidden words `truth`, `canon`, `approved`, or `promoted`.
- All 26 findings carry
  `owner_decision={"decision": "pending", "approved": False}` and
  `review_status="candidate_review_pending"`.
- `persisted_candidate_ids == []`. `persist_candidates=False` was
  honored.
- `project_files_changed == false`. No Memory/Canon mutation, no
  candidate persistence, no promotion record, no apply-promotion,
  no story prose.

## Next task

`PHASE8-IMPL-023-T018A — NCP schema validator preflight` (the next
narrow, MVP-blocking task in the backlog). The T017C1 live BookNLP
MVP path is now proven on owner-authored text; the orchestrator
remains ready for the next adapter to be added without further
repair work.
