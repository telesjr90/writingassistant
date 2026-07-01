# PHASE8-IMPL-022-T002 MVP Usability Validation Matrix Decision

## Decision

`PHASE8-IMPL-022-T002` is complete/PASS as docs/decision/planning only. This decision defines the MVP end-to-end usability validation matrix and acceptance gates for `PHASE8-IMPL-022`; it does not implement the smoke harness, does not add tests, and does not record MVP completion or an end-to-end usability pass.

The matrix covers the complete MVP path: owner-authored or owner-provided project text, project/workspace load path required for validation, runtime extraction availability and guarded failure behavior, real BookNLP/spaCy install/import/run checks as already scoped by earlier parents, raw artifact persistence, candidate creation/review handoff, candidate review and review queue/read-only review surface, frontend owner-action execution, explicit audited apply-promotion, approved memory/canon mutation only through owner-approved workflow, model-assisted evidence-backed extraction, analysis-only NCP/Subtxt/dramatica-flow runtime integration, safe unavailable/quarantine/fail-closed states, and no generated prose/prose-production behavior.

## Preserved Boundaries

PHASE8-IMPL-022 must preserve candidate-first behavior; owner review required; evidence/provenance/source-locator backed when available; confidence is not truth; tool output is not canon; model output is not canon; no model output as truth; no automatic canon; no apply-promotion outside explicit audited owner-confirmed path; no memory/canon mutation outside owner-approved workflow; no training artifacts; no generated prose; no rewrite; no continuation; no outline; fail closed; no silent fallback; queue presence is not approval; candidate persistence is not canon.

Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## Acceptance Gate Matrix

### 1. Workspace/project baseline gate

- Validation area: project/workspace load path required for validation.
- Prior parent/artifact dependency: Phase 7 workspace foundation, `PHASE8-IMPL-014` through `PHASE8-IMPL-021`, `docs/master_plan.md`, `docs/roadmap/implementation_status.md`.
- Required user workflow or system behavior: owner can load the selected project/workspace baseline and reach the Writer Assistant Core review path without hidden project mutation.
- Automated validation expectation: T003 should add expected-red contract/smoke checks that assert the selected project can be resolved path-safely and that baseline project metadata is readable before any workflow step runs.
- Smoke/manual validation expectation: manual smoke confirms the workspace opens the same project intended for validation and shows no unsupported success state.
- Evidence to capture: project id, resolved safe project path, workspace load result, route/UI surface reached, and any unavailable state.
- Pass condition: workspace loads deterministically and validation proceeds only against the selected project.
- Fail/blocker condition: missing project, unsafe path, ambiguous project, hidden write, or unsupported success state blocks the MVP smoke.
- Explicit boundary assertions: workspace load is not approval, not canon mutation, not candidate persistence, and not apply-promotion.

### 2. Owner-authored or owner-provided source gate

- Validation area: owner-authored or owner-provided project text.
- Prior parent/artifact dependency: Phase 7 owner-authored scene/note/material storage, `PHASE8-IMPL-006` source/evidence map decisions, `PHASE8-IMPL-019` runtime extraction boundary.
- Required user workflow or system behavior: validation source text must come from owner-authored or owner-provided project text/materials and must be labeled as source input, not assistant-generated prose.
- Automated validation expectation: T003 expected-red tests should reject non-owner source claims and require source refs or source locator refs when available.
- Smoke/manual validation expectation: manual smoke identifies the source document and confirms the owner provided or authored it.
- Evidence to capture: source document refs, source locator refs, provenance refs, ownership/source claim, and source text type.
- Pass condition: all extracted or analyzed material is traceable to owner-authored or owner-provided source.
- Fail/blocker condition: unknown source, generated source, missing source ownership, unsafe locator, or substituted sample data blocks the MVP smoke.
- Explicit boundary assertions: no generated prose, no rewrite, no continuation, no outline, no prose-production, and owner-authored storage remains allowed only for owner-authored content.

### 3. Runtime extraction environment gate

- Validation area: runtime extraction availability, real BookNLP/spaCy install/import/run checks.
- Prior parent/artifact dependency: `PHASE8-IMPL-019` guarded runtime extraction helper and decision.
- Required user workflow or system behavior: runtime extraction checks must distinguish disabled, configured, dependency_missing, model_missing, configuration_invalid, probe_failed, runtime_failed, and valid states.
- Automated validation expectation: T003 should add expected-red contract checks for real BookNLP and spaCy import/probe/run availability reporting without claiming extraction success from import alone.
- Smoke/manual validation expectation: manual smoke may verify environment display or logs for BookNLP/spaCy availability only if the environment is prepared.
- Evidence to capture: environment flags, BookNLP availability state, spaCy availability state, probe/run result, and guarded extraction state.
- Pass condition: real availability is reported accurately and runtime extraction proceeds only when explicitly enabled, configured, and valid.
- Fail/blocker condition: dependency missing, model missing, invalid config, probe failure, runtime failure, or import-only false success blocks the extraction success path.
- Explicit boundary assertions: no silent fallback, fail closed, no model/Ollama substitution, no package/dependency edit inside validation, and no extraction success claim from unavailable tools.

### 4. Runtime extraction unavailable/quarantine/fail-closed gate

- Validation area: runtime extraction unavailable, quarantine, and fail-closed behavior.
- Prior parent/artifact dependency: `PHASE8-IMPL-019` runtime extraction safety regression and `PHASE8-IMPL-018` raw artifact quarantine behavior.
- Required user workflow or system behavior: unsafe, malformed, incomplete, unavailable, or failed runtime extraction output must become explicit unavailable, quarantine, or fail_closed state.
- Automated validation expectation: T003 expected-red tests should assert malformed output, unsafe paths, missing refs, and runtime failures never become valid extraction output.
- Smoke/manual validation expectation: manual smoke confirms the UI/API reports blocked/unavailable state clearly and does not advance review as if extraction passed.
- Evidence to capture: failure reason, quarantine reason, fail_closed state, rejected refs, and blocked transition.
- Pass condition: failures are explicit, auditable, and non-successful.
- Fail/blocker condition: any silent fallback, partial success presented as valid, or missing failure evidence blocks MVP smoke.
- Explicit boundary assertions: fail closed, no silent fallback, no automatic canon, no candidate persistence from quarantined output.

### 5. Raw artifact persistence gate

- Validation area: raw artifact persistence.
- Prior parent/artifact dependency: `PHASE8-IMPL-018` raw artifact persistence implementation and lifecycle/safety regressions.
- Required user workflow or system behavior: valid extraction artifacts persist project-locally as support data only, with manifest, bundle hash, source/evidence/provenance/source-locator refs, and valid-only default listing.
- Automated validation expectation: T003 should add expected-red checks that raw artifact writes/read/list/index behavior is required in the end-to-end path and that quarantined artifacts are excluded from valid indexes.
- Smoke/manual validation expectation: manual smoke may inspect manifest/index evidence without treating raw output as truth.
- Evidence to capture: raw artifact bundle id, manifest, bundle hash, artifact refs, valid/quarantined state, and source linkage.
- Pass condition: valid artifacts persist and can be listed/read as support data with refs intact.
- Fail/blocker condition: missing manifest, unsafe path, missing refs, hash mismatch, quarantine indexed as valid, or raw artifact treated as canon blocks MVP smoke.
- Explicit boundary assertions: raw artifacts are not canon, not approved memory, not candidates, not training data, and not owner approval.

### 6. Candidate creation and evidence/provenance/source-locator gate

- Validation area: candidate creation, evidence, provenance, source-locator, and review handoff.
- Prior parent/artifact dependency: `PHASE8-IMPL-002` through `PHASE8-IMPL-004`, `PHASE8-IMPL-010`, `PHASE8-IMPL-011`, `PHASE8-IMPL-019`, and `PHASE8-IMPL-020`.
- Required user workflow or system behavior: candidate creation/review handoff produces candidate-first records or drafts backed by evidence, provenance, and source-locator refs when available.
- Automated validation expectation: T003 should add expected-red checks that candidate creation rejects missing required refs, unsafe source locators, forbidden destinations, and direct canon writes.
- Smoke/manual validation expectation: manual smoke confirms candidate detail displays source/evidence/provenance and does not present confidence as truth.
- Evidence to capture: candidate id/draft id, source refs, evidence refs, provenance refs, source-locator refs, confidence, and handoff state.
- Pass condition: candidate is review-pending, evidence-backed when available, and traceable to source.
- Fail/blocker condition: candidate lacks required evidence/provenance/source-locator support, bypasses review, or writes canon directly.
- Explicit boundary assertions: candidate-first, owner review required, confidence is not truth, candidate persistence is not canon.

### 7. Review queue/read-only review surface gate

- Validation area: candidate review, review queue, and read-only review surface.
- Prior parent/artifact dependency: `PHASE8-IMPL-012`, `PHASE8-IMPL-013`, `PHASE8-IMPL-014`, and `PHASE8-IMPL-015`.
- Required user workflow or system behavior: candidate review queue/list/detail/index/summary can be read without mutating queue, candidate, memory, canon, or project truth.
- Automated validation expectation: T003 should add expected-red checks that read-only review routes/surfaces remain read-only and expose source/evidence/provenance/source-locator data.
- Smoke/manual validation expectation: manual smoke confirms the review queue and read-only review surface display candidate details, warnings, and evidence without approval side effects.
- Evidence to capture: queue entry id, linked candidate id, read-only response, displayed evidence/provenance/source locator, and no mutation record.
- Pass condition: queue entry is visible for review and all reads are side-effect free.
- Fail/blocker condition: queue read mutates state, hides missing refs, treats queue presence as approval, or creates canon/promotion output.
- Explicit boundary assertions: queue presence is not approval, owner review required, candidate persistence is not canon, no automatic canon.

### 8. Frontend owner-action execution gate

- Validation area: frontend owner-action execution.
- Prior parent/artifact dependency: `PHASE8-IMPL-016`.
- Required user workflow or system behavior: frontend owner-action controls execute explicit review workflow commands with owner intent, visible candidate warnings, and response-only mutation limited to review command workflow.
- Automated validation expectation: T003 should add expected-red smoke/contract checks for frontend owner-action command request shape, explicit owner action, and blocked unsafe commands.
- Smoke/manual validation expectation: manual smoke confirms the owner can intentionally submit allowed review commands and see deterministic results without hidden promotion.
- Evidence to capture: owner action command, queue entry id, candidate id, response status, audit/workflow record, and UI state after action.
- Pass condition: allowed owner actions execute only within review workflow boundaries.
- Fail/blocker condition: missing explicit owner action, hidden command, unsafe command accepted, or promotion/canon mutation from review action blocks MVP smoke.
- Explicit boundary assertions: owner-action execution is not apply-promotion, not memory/canon mutation, not approval by queue presence, and not generated prose.

### 9. Apply-promotion audited owner-confirmation gate

- Validation area: explicit audited apply-promotion.
- Prior parent/artifact dependency: `PHASE8-IMPL-017`.
- Required user workflow or system behavior: apply-promotion must require explicit owner confirmation, destination, source/evidence/provenance/source-locator support, validation, and audit record before approved memory/canon mutation.
- Automated validation expectation: T003 should add expected-red end-to-end checks that apply-promotion succeeds only through the audited owner-confirmed path and rejects candidates missing refs or confirmation.
- Smoke/manual validation expectation: manual smoke confirms final confirmation is visible and no promotion applies before explicit owner approval.
- Evidence to capture: promotion request, owner confirmation, destination, audit record, candidate refs, validation result, and mutation result.
- Pass condition: promotion applies only after audited owner confirmation and records evidence/provenance/source locator when available.
- Fail/blocker condition: apply-promotion without owner confirmation, missing audit, invalid destination, missing refs, or direct mutation blocks MVP smoke.
- Explicit boundary assertions: no apply-promotion outside explicit audited owner-confirmed path, no automatic canon, confidence is not truth.

### 10. Approved memory/canon mutation gate

- Validation area: approved memory/canon mutation only through owner-approved workflow.
- Prior parent/artifact dependency: `PHASE8-IMPL-017` apply-promotion and approved memory/canon mutation boundary.
- Required user workflow or system behavior: approved memory/canon changes occur only as the result of a valid apply-promotion operation and remain project-local approved truth records.
- Automated validation expectation: T003 should add expected-red checks that memory/canon files or records cannot be mutated by extraction, candidate persistence, queue actions, model output, raw artifacts, or analysis runtime output.
- Smoke/manual validation expectation: manual smoke verifies the approved record appears only after promotion and can be traced back to the audit and candidate evidence.
- Evidence to capture: approved memory/canon record id, audit id, source candidate id, evidence/provenance/source-locator refs, and mutation timestamp.
- Pass condition: approved memory/canon mutation is owner-approved, audited, traceable, and limited to allowed destinations.
- Fail/blocker condition: mutation outside owner-approved workflow, missing audit, missing source refs, or model/tool output promoted as truth blocks MVP smoke.
- Explicit boundary assertions: no memory/canon mutation outside owner-approved workflow, tool output is not canon, model output is not canon, no model output as truth.

### 11. Model-assisted evidence-backed extraction gate

- Validation area: model-assisted evidence-backed extraction.
- Prior parent/artifact dependency: `PHASE8-IMPL-020`.
- Required user workflow or system behavior: model-assisted output may produce evidence-backed candidate observations, diagnostic questions, uncertainty notes, insufficient-evidence notes, safe refusals, quarantined/fail-closed states, or candidate support only.
- Automated validation expectation: T003 should add expected-red checks that model-assisted output requires source/evidence/provenance/source-locator refs when available and rejects generated prose, rewrites, continuations, outlines, training artifacts, and direct canon/promotion output.
- Smoke/manual validation expectation: manual smoke confirms model-assisted evidence is displayed as candidate support only and never as truth.
- Evidence to capture: model-assisted request shape, allowed output class, refs, refusal/quarantine/fail_closed state, and candidate handoff.
- Pass condition: model-assisted extraction is evidence-backed, candidate-first, owner-review-required, and bounded.
- Fail/blocker condition: model output treated as truth, missing refs, generated prose, direct promotion, or silent success blocks MVP smoke.
- Explicit boundary assertions: model output is not canon, no model output as truth, confidence is not truth, no generated prose, fail closed.

### 12. Analysis-only NCP/Subtxt/dramatica-flow integration gate

- Validation area: analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Prior parent/artifact dependency: `PHASE8-IMPL-021`.
- Required user workflow or system behavior: NCP remains structured context interchange only, Subtxt remains rubric/diagnostic guidance only, and dramatica-flow remains audited allowlist only; outputs are candidate-first diagnostics/support.
- Automated validation expectation: T003 should add expected-red checks that allowed analysis runtime integrations preserve source/evidence/provenance/source-locator refs and reject prose/outline/improvement actions.
- Smoke/manual validation expectation: manual smoke confirms analysis runtime state is displayed as analysis support, unavailable, quarantined, or fail_closed without truth claims.
- Evidence to capture: allowlist record, request refs, output class, candidate/diagnostic handoff, unavailable/quarantine/fail_closed state.
- Pass condition: analysis-only runtime support remains bounded, traceable, and review-gated.
- Fail/blocker condition: unsupported action, missing allowlist, generated prose, outline generation, direct canon mutation, or silent fallback blocks MVP smoke.
- Explicit boundary assertions: analysis-only NCP/Subtxt/dramatica-flow, tool output is not canon, no automatic canon, no generated prose, no rewrite, no continuation, no outline.

### 13. No-prose/no-rewrite/no-continuation/no-outline gate

- Validation area: no generated prose, no prose-production, no rewrite, no continuation, no outline.
- Prior parent/artifact dependency: global product safety boundaries, guardrail history, `PHASE8-IMPL-020`, and `PHASE8-IMPL-021`.
- Required user workflow or system behavior: every workflow rejects or refuses prose-production behavior and never asks runtime/model/tool paths to write, rewrite, continue, imitate, polish, improve, expand, draft, revise, export-as-prose, or outline story prose.
- Automated validation expectation: T003 should add expected-red no-prose contract checks across the end-to-end path and assert forbidden output classes cannot advance.
- Smoke/manual validation expectation: manual smoke verifies no prose-production buttons, prompts, labels, or success states appear in the MVP validation path.
- Evidence to capture: refusal/block state, forbidden action rejected, output class, and no mutation/no candidate advancement for prose-producing output.
- Pass condition: prohibited prose-production is blocked before execution and after output validation.
- Fail/blocker condition: generated prose, rewrite, continuation, outline, polish, improvement, expansion, style imitation, or story prose output blocks MVP smoke.
- Explicit boundary assertions: no generated prose, no prose-production, no rewrite, no continuation, no outline, permanently forbidden.

### 14. No training artifacts gate

- Validation area: no training artifacts.
- Prior parent/artifact dependency: roadmap product safety boundaries and fine-tuning deferred status.
- Required user workflow or system behavior: end-to-end MVP usability validation must not create JSONL, dataset manifests, model artifacts, fine-tuning configs, or training reports as workflow output.
- Automated validation expectation: T003 should add expected-red checks that validation output cannot target training/JSONL/dataset/model artifact destinations.
- Smoke/manual validation expectation: manual smoke checks no training controls or training-output success messages appear in the MVP path.
- Evidence to capture: forbidden destination rejection, artifact path scan result, and validation output destinations.
- Pass condition: no training artifacts are created or modified by MVP smoke.
- Fail/blocker condition: training_jsonl, dataset_manifest, model_artifact, fine-tuning config, or training output is created or accepted.
- Explicit boundary assertions: no training artifacts; fine-tuning deferred after MVP.

### 15. No silent fallback gate

- Validation area: safe unavailable/quarantine/fail-closed states and no silent fallback.
- Prior parent/artifact dependency: `PHASE8-IMPL-018`, `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, and `PHASE8-IMPL-021`.
- Required user workflow or system behavior: every unavailable dependency, disabled tool, malformed output, rejected request, or missing evidence state must be explicit and must not be replaced by fake success, mock success, or inferred truth.
- Automated validation expectation: T003 should add expected-red checks that fallback states are explicit and do not satisfy success gates.
- Smoke/manual validation expectation: manual smoke confirms blocked/unavailable/quarantined/fail_closed states are visible and actionable for triage.
- Evidence to capture: fallback reason, unavailable state, quarantine state, fail_closed state, and blocked downstream transition.
- Pass condition: fallback is explicit, auditable, and non-successful.
- Fail/blocker condition: any silent fallback, hidden mock, inferred success, or absent blocker evidence blocks MVP smoke.
- Explicit boundary assertions: no silent fallback, fail closed, unavailable is not success, quarantine is not valid.

### 16. End-to-end smoke gate

- Validation area: complete MVP end-to-end usability smoke.
- Prior parent/artifact dependency: all prior MVP-required parents `PHASE8-IMPL-014` through `PHASE8-IMPL-021`, this decision file, and future T003 expected-red tests.
- Required user workflow or system behavior: owner loads a project, uses owner-authored or owner-provided project text, runs guarded extraction/analysis where available, persists raw artifacts, creates candidate/review handoff, reviews in read-only/review queue surface, executes explicit owner action, applies promotion only through audited owner confirmation, and sees approved memory/canon mutation only through the owner-approved workflow.
- Automated validation expectation: T003 should convert this matrix into expected-red end-to-end MVP smoke/contract tests without implementing the smoke harness.
- Smoke/manual validation expectation: T004 and later may implement/execute the smoke harness and manual checklist, but T002/T003 remain planning/tests-first handoff.
- Evidence to capture: ordered workflow trace, project id, source refs, runtime states, raw artifact refs, candidate id, queue entry id, owner action id, promotion audit id, approved record id, and boundary assertions.
- Pass condition: every required gate passes in order with traceable evidence and no boundary violation.
- Fail/blocker condition: any missing required gate, missing evidence, unsafe mutation, unsupported success, or boundary violation blocks MVP usability acceptance.
- Explicit boundary assertions: this gate does not by itself mark MVP complete; acceptance requires later test/harness execution and owner review.

### 17. MVP blocker triage gate

- Validation area: blocker classification and next-action routing.
- Prior parent/artifact dependency: this matrix, T003 expected-red tests, and later T004-T007 execution artifacts.
- Required user workflow or system behavior: failed gates must be classified as blocker, expected-red gap, manual-smoke-needed, environment-unavailable, or deferred-non-MVP only when the boundary allows deferral.
- Automated validation expectation: T003 should add expected-red expectations for blocker evidence shape and gate status reporting.
- Smoke/manual validation expectation: manual triage records blocker cause, affected gate, evidence, owner decision needed, and whether implementation work is required.
- Evidence to capture: gate id, status, blocker reason, failing evidence, required next task, and explicit non-completion note.
- Pass condition: blockers are visible and routed to the correct later child task without weakening boundaries.
- Fail/blocker condition: blocker suppressed, reclassified as pass without evidence, or used to claim MVP complete prematurely.
- Explicit boundary assertions: no MVP completion claim, no end-to-end usability pass claim, generated context artifacts are evidence only and not roadmap truth.

## T003 Handoff

`PHASE8-IMPL-022-T003` is ready/active next. It should convert this MVP end-to-end usability validation matrix and acceptance gates decision into expected-red end-to-end MVP smoke/contract tests.

T003 must remain tests-first expected-red only. It must not implement the smoke harness, backend code, routes, frontend code, package/dependency changes, runtime extraction, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, model/Ollama calls, candidate persistence, review queue entries, apply-promotion changes, approved memory/canon mutation, training artifacts, generated prose, rewrite, continuation, or outline.
