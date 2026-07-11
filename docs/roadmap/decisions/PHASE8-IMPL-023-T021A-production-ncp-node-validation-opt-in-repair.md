# PHASE8-IMPL-023-T021A — Production NCP Node Validation Opt-In Repair

Status: complete/PASS  
Parent: `PHASE8-IMPL-023-T021` — blocked/in_progress  
Active parent: `PHASE8-IMPL-023` — published/active

## Decision

The first T021 cross-tool fusion real-runtime attempt was safely BLOCKED. Four mandatory contributors succeeded and produced 44 partial findings, while Ollama timed out at 180 seconds and requires no code repair. NCP exposed a separate production defect: `_ncp_validate_with_node_opt_in` was an unconditional no-op, so the required opt-in validator could not succeed.

T021A replaces that no-op with a bounded, fail-closed subprocess path. When the existing opt-in gate is enabled, the helper runs exactly `npm run validate:file -- <absolute-resolved-input-path>` as an argument list in `.external_sources/narrative-context-protocol`, with `shell=False`, captured stdout/stderr, text mode, no stdin, and a finite `60.0` second timeout. Success requires exit code zero and an exact `PASS <selected-path>` output line. Missing or unsafe input, unsafe containment, symlinks, forbidden project/artifact/context paths, unavailable source or npm, timeout, OS/process failure, nonzero exit, and malformed output all return false. Default Node-free behavior remains unchanged, and helper failure still yields `failed_closed` with no candidates.

The first T021A execution stopped after two focused-command failures, as repository stop policy required. The remaining failure was fixture idempotency rather than production logic: the `package_root=False` test case attempted to create its already-existing `tmp_path` parent. This continuation changed only that fixture call from `input_path.parent.mkdir(parents=True)` to `input_path.parent.mkdir(parents=True, exist_ok=True)`. No assertion was weakened, skipped, or xfailed, and production behavior was not changed during the continuation.

## Validation

- Formerly failing node: `test_missing_ncp_package_surface_returns_false[False-False-False]` — 1 passed.
- Python byte-compilation of the production helper and focused test file — passed.
- Focused contract: `tests/test_omi_ncp_node_validation_opt_in_contract.py` — 25 passed.
- Prescribed regression suite — 230 passed, 1 warning. The warning was the environment-only Torch `Can't initialize NVML` warning from `test_default_live_tools_are_disabled_or_readiness_only`.

All subprocess interactions were mocked. No real npm or Node validator ran; no NCP live orchestration, Ollama, Story Check, spaCy, BookNLP, Subtxt runtime, dramatica-flow, `df`, model, server, or network call occurred. No package/dependency, persistence, project, Memory/Canon, promotion/apply-promotion, prose, or `.external_sources` mutation occurred. The blocked T021 evidence remains unchanged under `.codex-context/PHASE8-IMPL-023/manual-validation/T021-cross-tool-fusion-real-runtime/`.

## Frontier

T021 remains blocked/in_progress and full MVP completion remains blocked. The next task is `PHASE8-IMPL-023-T021B — Cross-tool fusion real-runtime validation rerun after NCP validator repair` (planned). T021B must use `OMI_LIVE_NCP_VALIDATE_WITH_NODE=1`, `OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=600`, and the same six mandatory contributors. T021B was not implemented or executed here. T022 remains planned after T021 completion.

No staging, commit, or push was performed.
