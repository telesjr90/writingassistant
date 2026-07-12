# PHASE8-IMPL-023-T019B — Subtxt Integration-Path Decision

> **Superseded authorization point (2026-07-11):**
> `docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`
> supersedes `Live Subtxt runtime: OWNER-BLOCKED`, the licensing/authorization
> reopening condition, and any use of those points to limit implementation.
> Full Subtxt runtime is authorized and planned under PHASE8-IMPL-025 T005/T006.
> The T019A technical inventory, this record's historical rationale, the
> completed app-owned rubric path, identity separation, fail-closed behavior,
> candidate-only status, owner review, and all no-prose/no-truth/no-mutation
> boundaries remain valid.

## Decision

```
Live Subtxt runtime: OWNER-BLOCKED
App-owned Subtxt-informed semantic-rubric path: ACCEPTED
Automatic Dramatica/Storyform truth: FORBIDDEN
Claiming Subtxt execution without a real authorized runtime: FORBIDDEN
```

## Rationale

- The local Subtxt checkout at `.external_sources/subtxt-docs` is a documentation/reference repository, not runtime code. The package name is `nuxt-ui-pro-template-docs` and its scripts are Nuxt documentation-site commands (build, dev, generate, lint, postinstall, preview, typecheck), not Subtxt analysis commands.
- No supported Subtxt CLI, importable analysis package, local API, validator, executable analysis engine, or other callable runtime surface was found during T019A probing.
- `OMI_LIVE_SUBTXT_COMMAND` and `OMI_LIVE_SUBTXT_PATH` are configuration placeholders only and do not establish runtime availability. The T019A preflight always reports `subtxt_live_runtime_available: False`.
- Treating documentation/reference availability as runtime availability would be misleading and violate the project's safety boundaries.
- The owner still requires useful structural diagnostic support for the MVP, and Subtxt's high-level structural and diagnostic concepts (throughlines, story points, conflict sources, etc.) can inform an app-owned implementation.
- The honest implementation path is an app-owned semantic rubric informed by allowed high-level concepts, with strict labeling and safety boundaries, never presented as Subtxt runtime output.
- An actual Subtxt runtime may be reconsidered later only when the owner provides or approves a concrete callable surface with installation procedure, input/output contracts, licensing review, credential/privacy boundaries, fail-closed behavior, automated contract tests, manual real-runtime validation, and proof of no prose/persistence/canon/promotion side effects.

## License Boundary

- The local `.external_sources/subtxt-docs` README declares CC BY-NC-SA 4.0.
- The inspected repository has no root license file beyond the README declaration.
- T019B does not determine whether future commercial redistribution or adaptation is licensed.
- Application code must not copy documentation passages, proprietary examples, screenshots, page structures, or substantial source wording.
- Future implementation must use original app-owned wording and abstractions.
- Any distribution or commercial licensing question remains an owner/legal-review item.
- T019B performs no copying, adaptation, vendoring, or redistribution.

## Accepted Future Rubric Boundary

The future app-owned rubric may only produce review material such as:

- structural diagnostic candidates;
- conflict diagnostic candidates;
- throughline-context questions;
- story-point/context questions;
- source-of-conflict hypotheses;
- subject-versus-conflict questions;
- ambiguity or insufficient-evidence findings;
- owner-review diagnostic questions.

Every future result must:

- include evidence excerpts;
- include source locators;
- identify the app-owned rubric/model/tool source;
- use uncertainty and support labels;
- remain pending owner decision;
- remain candidate-review material;
- be rejectable by the owner;
- fail closed when unsupported or unsafe.

It must not:

- assert a definitive Storyform;
- assert OS/MC/IC/RS throughlines as truth;
- assert problem, solution, concern, issue, domain, approach, dynamics, or signposts as truth;
- assert relationships, conflict sources, continuity, causality, or canon as truth;
- rewrite, improve, fix, continue, outline, or generate story prose;
- persist automatically;
- mutate Memory/Canon;
- create promotion records;
- run apply-promotion;
- impersonate Subtxt;
- claim official Subtxt compatibility or endorsement.

## Future Implementation Labeling

Require future user-facing and internal labels to distinguish:

```
App-owned Subtxt-informed diagnostic support
```

from forbidden wording such as:

```
Subtxt runtime result
Live Subtxt analysis
Official Subtxt diagnosis
Subtxt-confirmed Storyform
```

## Reopening Condition

The live-runtime owner block may be reconsidered only if a later owner-controlled task provides:

- an exact runtime/API/CLI/library identity;
- authorization to use it;
- installation or access procedure;
- input and output contracts;
- licensing/terms review;
- credential and privacy boundaries where relevant;
- fail-closed behavior;
- automated contract tests;
- manual real-runtime validation;
- proof of no prose, persistence, canon, or promotion side effects.

## Existing Contract Preservation

- T009 `omi_subtxt_diagnostic_handoff.v1` fixture contract is preserved unchanged.
- T009 support label `Subtxt diagnostic support only` is preserved unchanged.
- T019A preflight `subtxt_live_runtime_available: False` is preserved unchanged.
- Existing application contracts describe Subtxt as rubric/diagnostic guidance only and currently report `executes_subtxt: False`. These facts are preserved.

## Result

PASS — owner-controlled integration-path decision recorded.

The live-runtime subpath is owner-blocked, but the decision task itself is not blocked.
