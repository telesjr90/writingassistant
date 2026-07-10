# PHASE8-IMPL-023-T017A: BookNLP Runtime Preflight After Install

## Status

Accepted.

## Task type

Runtime preflight only — no live BookNLP adapter, no BookNLP processing, no candidate creation, no Memory/Canon mutation, no promotion records, no apply-promotion, no story prose.

## Scope

Extend the existing T013 runtime preflight at `backend/omi_runtime_preflight.py` so the preflight report for the `booknlp` tool includes detailed BookNLP runtime surface fields: package availability, module availability, spaCy availability/version/model, TensorFlow availability/version, PyTorch availability/version, Transformers availability/version, setuptools availability/version, pkg_resources availability, setuptools compatibility detail (pin `<81` required), non-blocking torch caveat when `<2.11`, and a human-readable `booknlp_detail` summary. The preflight does not run BookNLP processing, does not call `.process(...)`, does not read project scene text, and does not create extraction outputs.

## Evidence

- `booknlp==1.0.8` is installed in `.venv-unsloth-clean` after owner-approved install/probe.
- `setuptools==80.9.0` is pinned because `setuptools==82.0.1` removed `pkg_resources`, which BookNLP imports.
- BookNLP import smoke passes: `from booknlp.booknlp import BookNLP` reports `using device cpu`.
- `Can't initialize NVML` warning is observed — non-blocking for CPU fallback.
- `Skipping import of cpp extensions due to incompatible torch version` warning observed: `torch==2.10.0+cu129` is below the `>=2.11` required by BookNLP cpp extensions. This is non-blocking for import but requires runtime validation in T017B/T017C.
- `pkg_resources is deprecated` warning observed, confirming the `setuptools<81` pin.

## Compatibility

- `pkg_resources` is required at BookNLP import time.
- `setuptools==80.9.0` provides `pkg_resources`; `setuptools>=81` does not.
- The preflight reports a clear compatibility detail when `setuptools>=81` and `pkg_resources` is missing.
- `torch==2.10.0+cu129` is reported as a non-blocking caveat; it does not by itself cause the preflight to mark BookNLP unavailable.

## CPU fallback

BookNLP runs on CPU on the owner machine. The `device cpu` message and the `Can't initialize NVML` warning confirm this. The preflight does not require GPU availability.

## Preflight fields added

The T017A preflight adds these fields to the `booknlp` tool entry in the preflight report:

- `booknlp_runtime_surface`
- `booknlp_package_available`
- `booknlp_package_version`
- `booknlp_module_available`
- `booknlp_entrypoint_available`
- `booknlp_spacy_available`
- `booknlp_spacy_version`
- `booknlp_spacy_model_available`
- `booknlp_tensorflow_available`
- `booknlp_tensorflow_version`
- `booknlp_torch_available`
- `booknlp_torch_version`
- `booknlp_transformers_available`
- `booknlp_transformers_version`
- `booknlp_setuptools_available`
- `booknlp_setuptools_version`
- `booknlp_pkg_resources_available`
- `booknlp_setuptools_compatibility_detail`
- `booknlp_detail`

## Flag behavior

Reuses existing auto-generated blocked env vars (`OMI_LIVE_BOOKNLP_BLOCKED`, `OMI_LIVE_BOOKNLP_BLOCKED_REASON`). The `OMI_LIVE_BOOKNLP_ENABLED` flag and `OMI_LIVE_BOOKNLP_BLOCKED`/`OMI_LIVE_BOOKNLP_BLOCKED_REASON` were already declared in `OMI_LIVE_TOOL_ENABLED_ENVS` and the auto-generated blocked/reason dicts. No new env vars are added by T017A.

## Safety

- Read-only: no files, database, or project state is modified.
- No BookNLP processing is invoked: `_booknlp_runtime_probe` uses only `importlib.util.find_spec`, `importlib.metadata.version`, and (for spaCy model check) `import spacy; spacy.load(...)` — the same pattern as the existing `_spacy_model_probe`.
- No candidates are created, persisted, promoted, or apply-promoted.
- No Memory/Canon mutation occurs.
- No story prose is generated, rewritten, continued, polished, improved, expanded, imitated, drafted, or revised.
- Tests mock the probe function; they do not require real BookNLP, TensorFlow, Torch, spaCy model, or other installed runtimes.

## Next task

PHASE8-IMPL-023-T017B — Live BookNLP adapter behind flags. Implements the actual BookNLP processing adapter in `backend/omi_analysis_orchestrator.py`, gated behind the same `OMI_LIVE_BOOKNLP_ENABLED`/`OMI_LIVE_BOOKNLP_BLOCKED` flags.
