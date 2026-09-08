# Official Subtxt/Dramatica Is an Optional Paid Integration

Date: 2026-09-07

## Scope

This decision reconciles current `PHASE8-IMPL-025` task status, dependencies,
and MVP acceptance after the owner reclassified official Subtxt/Dramatica as
an optional paid integration. It does not authorize application code changes,
runtime execution, account or credential actions, or T007 implementation.

## Owner decision

The required MVP path is the free/local tool stack. Official paid
Subtxt/Dramatica real execution is optional and must not block MVP completion.
No paid subscription, token, API key, or API execution is required for MVP.

Real execution remains mandatory for integrations that current authority
classifies as MVP-required. Any future claim that the official paid
Subtxt/Dramatica integration itself is fully operational still requires a
successful bounded real execution through the applicable application path.
The lack of paid entitlement or runtime is therefore a valid fail-closed
optional-feature state, not an MVP failure.

This decision supersedes current roadmap language that makes paid official
Subtxt execution a required MVP gate. The earlier general real-tool execution
decision remains historically valid and continues to govern MVP-required
tools; its prior application to official Subtxt is qualified by this later
scope decision.

## Accepted T006 foundation and closeout

The application-side T006 milestone at commit
`23d4825da9a257180cdc0d1d1239ce13b4e01f78`
(`feat(analysis): integrate official Subtxt adapter (T006)`) remains accepted.
This includes:

- official adapter identity `subtxt` and implementation kind
  `official_external`;
- application operation `analyze-subtxt`, allowlist/blocklist enforcement,
  and fail-closed runtime, preflight, request, and result validation;
- normalized-evidence-backed candidate conversion with T002/T003
  source/run/hash/artifact/evidence lineage;
- immutable raw artifact and evidence-ledger integration, with exact native
  opaque runtime output kept separate from app-owned mapping;
- deterministic/mock validation, candidate-only persistence, grouped review,
  and the bounded semantic-guardrail seam; and
- no prose generation, truth selection, automatic approval, promotion,
  apply-promotion, or Memory/Canon mutation.

T006 is accepted/closed as the optional paid-integration foundation. T006G
remains `NOT_EXECUTED_RUNTIME_UNAVAILABLE`; T006K's truthful zero-available-
runtime evidence remains historical evidence. No real official Subtxt API,
runtime, or model call is claimed, and no production runner or T003-to-official
runtime connection is invented. Future paid runner implementation, T003
wiring, provisioning, and real execution are separately authorized optional
debt.

## Current optional paid-runtime reality

The completed external-verification investigation identified the current
official paid integration as the Dramatica Narrative Platform API, with the
documented endpoint:

`POST https://platform.dramatica.com/api/v1/evaluations/storytelling`

The investigation recorded these access requirements: a verified active
Dramatica account, active Dramatica Pro, API access by request, a separate API
agreement, a bearer/public API key, and `api:evaluate` scope. Published Pro
pricing observed during that investigation was `$200/month` or `$2000/year`.
The public provisioning workflow remains partial, and no authenticated real
call has occurred. These facts are recorded from the completed investigation
and were not independently re-researched for this reconciliation.

## Required free/local MVP path

The required MVP path uses the applicable free/local contributors already in
current `PHASE8-IMPL-025` authority: spaCy, BookNLP, local Ollama/qwen3:8b,
Story Check through the authorized local runtime path, the NCP local/schema
gateway when its task becomes applicable, and app-owned deterministic/rubric
contributors within their existing accepted scopes.

This classification does not claim that all contributors have already passed
their current T002/T003 layered execution gates. Historical real runs remain
foundation evidence only, and each MVP-required contributor retains its
existing current-layer validation debt.

## Dependency and frontier effects

- T007 remains `planned` and not begun, continues to depend on completed/PASS
  T003, and becomes the next dependency-eligible application frontier after
  this T006 closeout.
- T008 remains `planned` and not begun. Its hard MVP dependencies are T004 and
  T007, including T004's required current-layer BookNLP execution and T007's
  required current-layer Ollama/qwen3:8b plus Story Check execution.
- T008 must validate actual current-layer output from every contributor that
  current free/local authority classifies as MVP-required. Optional official
  Subtxt absence cannot block T008 or MVP acceptance.
- When configured and available, official Subtxt output may participate in
  T008 and must pass the same evidence, provenance, classification,
  guardrail, candidate-only, and owner-control requirements. Its absence is a
  fail-closed optional-feature state, never a silent fallback to an app-owned
  Subtxt identity.

## Future optional paid-integration contract

The following owner-accepted directions remain controlling for any separately
authorized future paid integration:

1. D1 — The current official evaluation endpoint may specialize application
   operation `analyze-subtxt`; the manifest operation remains
   `analyze-subtxt`.
2. D2 — Outbound `storytelling` must be reconstructed only from exact verified
   normalized-evidence spans. The evidence ledger remains content-free. Raw or
   whole-source silent substitution is forbidden. Initial real paid validation
   uses one eligible evidence span for one official evaluation call unless a
   later explicit owner decision broadens it.
3. D3 — Native `target` or structural evaluation input must come from a
   pre-existing typed structural hypothesis. Official Subtxt/Dramatica
   evaluates the supplied hypothesis and must not choose structural truth.
   Initial real paid validation requires an explicitly owner-selected eligible
   hypothesis.

These future requirements are optional-integration gates, not MVP gates.

## Identity and safety preservation

The app-owned `subtxt_informed_rubric` and its internal
`app_owned_subtxt_informed_rubric` identity remain separate from official
`subtxt`. They cannot impersonate official Subtxt, and their execution is not
evidence that Dramatica or Subtxt executed. Optional official Subtxt absence
must fail closed under the official identity rather than fall back to the
app-owned rubric.

All analysis-only, candidate-first, evidence/provenance-backed, pending,
non-canon, owner-review, no-prose, no-truth-selection, no-auto-approval,
no-auto-promotion, no-apply-promotion, and no direct Memory/Canon mutation
boundaries remain unchanged.
