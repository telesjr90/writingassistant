# PHASE8-IMPL-024-T002 Story Check Grounding Integrity Closeout

## Decision

`PHASE8-IMPL-024-T002 - Story Check grounding integrity` is complete/PASS under parent `PHASE8-IMPL-024`. The completed child sequence is T002A source identity/hash and diagnostic contract, T002B deterministic grounding validator, T002C engine/route/normalizer/API/UI integration, T002D fixture regression and live validation, and T002E documentation and status closeout.

Implementation commits are `1ee250b9c1432651436149c3f377ce69790d7add` (T002A), `cde5f8855925c1a8245d3c9b5c939de8b93316eb` (T002B), `02e9e5e40ff63aaa2e092a98ca6f9a1a7dc38ad2` (T002C), and `467b7b747c7544054685053f5a44154e4e5eefe1` (T002D). T002E is documentation/status closeout only.

## Accepted contract

- Story Check carries exact selected-source identity: project ID, source type, source kind, source ID, source SHA-256 hash calculated on exact UTF-8 bytes, hash algorithm `sha256`, hash basis `utf-8-exact`, and UTF-8 byte length. The identity is validated at the route boundary; mismatched identity fails closed.
- Every diagnostic carries a deterministic verification state: `verified` for source-evidence-backed claims, `quarantined` for unsupported factual claims, or `unverified` for structural/contextual diagnostics without direct factual-claim evidence. No diagnostic may be falsely presented as verified when source evidence is absent.
- The grounding validator is deterministic, in-memory, and consumes the exact selected source identity and content. It compares diagnostic claims against direct source evidence spans and classifies each diagnostic accordingly.
- Source mismatch (identity fields, hash, or selected source not found) produces a fail-closed response without diagnostic findings. The fail-closed response preserves the identity mismatch reason.
- Story Check remains non-mutating: no project files, candidates, Memory/Canon, promotions, or apply-promotion records are created or modified. Model output remains non-canon.
- The supported evidence/status UI renders the selected-source identity, verification state per diagnostic, and explicit unverified/quarantined labeling.

## Validation evidence

T002D final result is PASS at `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z`.

The live route returned HTTP 200, elapsed time 266.762 seconds, runtime model `qwen3:8b` at `http://172.25.144.1:11434`, with Ollama timeout 600 seconds. The disposable project was `t002d-grounding-20260713t022337z`, which copied the `example` project (including its `storyform.json`, `bible.json`, and `scenes/scene_001.md` with verified SHA-256 hashes). The selected source was type `scene`, ID `scene_001`, with exact SHA-256 `4bd30a8138d2ab8579739b962021af2de892bf634118d991be2df9445ef072c3` and UTF-8 byte length 1972. Source identity matched.

The response contained 22 diagnostics total: 17 `unverified` and 5 `quarantined`. Zero diagnostics appeared in unknown verification states. No diagnostic was falsely presented as `verified`. The disposable project was unchanged by Story Check; existing projects were unchanged; only the exact disposable project was removed after evidence packaging. Story Check remained non-mutating; no Memory/Canon mutation, promotion, apply-promotion, or generated prose was introduced.

The result is a valid PASS because unsupported model claims were handled fail-closed: 17 structural/contextual diagnostics were correctly classified as `unverified` (no direct factual-claim evidence needed), and 5 unsupported factual claims were correctly `quarantined` (not presented as verified findings). The source identity was exact, the hash matched, the grounding validator ran deterministically, and the fail-closed mismatch path was validated through fixtures. The 22 diagnostics are model-claimed observations, not source-verified findings.

## Historical evidence

Four evidence directories from the T002D validation campaign are preserved with accurate classifications:

1. **Successful live run** at `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z`: PASS. This is the controlling T002D final evidence. The disposable project was copied from `example` and included the required `storyform.json`.

2. **Blocked — missing Storyform** at `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260712T235515Z`: BLOCKED (`unavailable_safe_fail_closed`). The disposable blank project lacked `storyform.json`, which the live Story Check engine requires before model invocation. The task boundary forbids creating or mutating Bible/storyform data. The route returned HTTP 200 but the engine stopped before producing a grounding envelope. All automated regressions passed; the browser UI rendered error states correctly.

3. **Validation-script failure** at `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T021350Z`: incomplete evidence. The validation script failed with an outdated helper invocation before the Story Check route executed. This was a validation-script API-drift error, not a product or T002D implementation failure. The run was at repository HEAD `b872670f` (before the T002D commit) with the same disposable-project strategy that succeeded in the final run.

4. **Test-harness defect** at `.codex-context/PHASE8-IMPL-024/T002D-unrelated-test-harness-defect/20260713T020959Z`: PRE-EXISTING / OUT-OF-SCOPE. `tests/test_context_routes.py` fails during collection with `ImportError: cannot import name 'Request' from 'fastapi'` because the test installs a synthetic FastAPI module whose stub defines `FastAPI` and `HTTPException` but not `Request`, while the real installed FastAPI environment imports `Request` successfully. T002D did not modify that test. This is a separate pre-existing non-blocking test-harness compatibility defect.

## P0-B repaired/closed

The release blocker P0-B (Story Check accepts contradictory ungrounded findings) is repaired and closed by T002 PASS. The selected source now carries exact identity and content hash; diagnostics carry deterministic verification states; unsupported factual claims are quarantined, not presented as verified; and source-mismatch causes fail-closed behavior. The architecture risk of future ungrounded model output remains an active concern owned by `PHASE8-IMPL-025-T007`.

## Remaining frontier

`PHASE8-IMPL-024` remains published/active. Its latest completed workstream is T002. The immediate next bounded child is `PHASE8-IMPL-024-T003A - Context-availability/readiness contract for Bible, storyform, and storyform-context`. T003 optional-resource handling remains planned/pending. Broad owner acceptance and MVP readiness remain blocked.

P0-A guided-creation input loss remains repaired/closed by T001 PASS.

## PHASE8-IMPL-025 coordination boundary

`PHASE8-IMPL-025` remains published/planned and inactive. Its external prerequisites T001 and T002 are now satisfied, but no PHASE8-IMPL-025 implementation child is activated. PHASE8-IMPL-024-T003A is the immediate active implementation frontier.

`PHASE8-IMPL-025-T007` must consume and extend the completed grounding contract (exact source identity/hash, deterministic verification-state classification, unsupported-factual quarantine, source-mismatch fail-closed, and non-mutating evidence status). It must not duplicate or replace it with a conflicting contract.

## Open questions resolved

- Question 132 (quarantine versus unverified versus omission): resolved. Unsupported factual claims are quarantined; structural/contextual diagnostics without factual-claim evidence are unverified; no diagnostic is omitted solely for being unsupported. The classification is deterministic and evidence-backed.

- Question 133 (exact evidence object per grounded warning): resolved. Every grounded diagnostic carries source ID, content hash, verification state (`verified`/`unverified`/`quarantined`), and the validator outcome. Source-evidence-backed `verified` diagnostics additionally carry normalized comparison evidence and exact excerpt/range. The contract is implemented at the route boundary and enforced by the deterministic grounding validator.

## Unrelated FastAPI test-stub defect

The pre-existing `tests/test_context_routes.py` failure (synthetic FastAPI stub missing `Request`) is recorded in the roadmap as a separate non-blocking follow-up. The file was not modified by T002A–T002D. Do not repair it as part of this closeout.
